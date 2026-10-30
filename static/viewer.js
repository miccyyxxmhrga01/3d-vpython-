/* Camera and display adapter for the Python model. Architectural geometry lives in house.py. */
"use strict";

(() => {
  const $id = id => document.getElementById(id);
  const viewport = $id("viewport");
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n));
  const mix = (a, b, t) => a.map((x, i) => x + (b[i] - x) * t);
  const sub = (a, b) => a.map((x, i) => x - b[i]);
  const add = (a, b) => a.map((x, i) => x + b[i]);
  const length = a => Math.hypot(...a);
  const normalize = a => a.map(x => x / (length(a) || 1));
  const multiply = (a, s) => a.map(x => x * s);
  const rgb = hex => {
    const n = parseInt(hex.slice(1), 16);
    return vec((n >> 16 & 255) / 255, (n >> 8 & 255) / 255, (n & 255) / 255);
  };
  let model, scene, keyLight, fillLight;
  const groups = new Map();
  let mode = "overview", targetProgress = 0, progress = 0;
  let roofHidden = false, evening = false, ready = false;
  let pos = [25, 16, 30], look = [0, 2.1, 2.5];
  let orbitYaw = .74, orbitPitch = .37, orbitRadius = 40;
  let yawOffset = 0, pitchOffset = 0, freeYaw = 0, freePitch = 0;
  let dragging = false, lastPointer, lastFrame = 0, pendingResize = true;
  let announcementTimer;
  const keys = new Set();
  const pointers = new Map();
  let pinchDistance = 0;

  function announce(message) {
    $id("announcement").textContent = message;
    $id("announcement").classList.add("show");
    clearTimeout(announcementTimer);
    announcementTimer = setTimeout(() => $id("announcement").classList.remove("show"), 2200);
  }

  function routeAt(t) {
    const scaled = clamp(t, 0, 1) * (model.route.length - 1);
    const i = Math.min(Math.floor(scaled), model.route.length - 2);
    const u = scaled - i;
    // Linear positions keep the camera within the modeled doorway/stair route.
    // Smoothing is applied to progress, rather than curves cutting room corners.
    const a = model.route[i], b = model.route[i + 1];
    return {pos: mix(a.pos, b.pos, u), target: mix(a.target, b.target, u), room: u < .5 ? a.room : b.room};
  }

  function lookWithOffset(from, target) {
    const direction = normalize(sub(target, from));
    const yaw = Math.atan2(direction[0], direction[2]) + yawOffset;
    const pitch = clamp(Math.asin(direction[1]) + pitchOffset, -1.22, 1.22);
    return add(from, [Math.sin(yaw) * Math.cos(pitch) * 5, Math.sin(pitch) * 5,
                      Math.cos(yaw) * Math.cos(pitch) * 5]);
  }

  function updateGroups() {
    for (const [name, objects] of groups) {
      const visible = name === "roof" ? !roofHidden : true;
      for (const object of objects) object.visible = visible;
    }
    $id("roof-toggle").setAttribute("aria-pressed", String(roofHidden));
    $id("roof-toggle").querySelector("span").textContent = roofHidden ? "Show roof" : "Hide roof";
  }

  function setActiveRoom(room) {
    document.querySelectorAll(".room-link").forEach(button => {
      const active = button.dataset.view === room;
      button.classList.toggle("active", active);
      if (active) button.setAttribute("aria-current", "location");
      else button.removeAttribute("aria-current");
    });
  }

  function updateLabels() {
    let room, name, note;
    if (mode === "tour") {
      room = routeAt(progress).room;
      const stop = model.stops.find(s => s.id === room);
      name = stop?.name || (room === "staircase" ? "The staircase" : "The approach");
      note = room === "bedroom" ? "First floor · Eye level" : "Ground floor · Eye level";
      $id("walkthrough-hint").textContent = "Scroll to keep exploring";
      $id("tour-position").textContent = `${Math.round(progress * 100)}% of your walkthrough`;
      $id("enter-house").querySelector("span").textContent = "Back to the exterior";
    } else if (mode === "free") {
      room = ""; name = "Free exploration"; note = "W A S D to walk";
      $id("walkthrough-hint").textContent = "Scroll to rejoin the tour";
      $id("tour-position").textContent = "Exploring freely";
      $id("enter-house").querySelector("span").textContent = "Back to the exterior";
    } else {
      room = mode;
      name = mode === "terrace" ? "Pool & terrace" : "Exterior overview";
      note = mode === "terrace" ? "Outdoor living · Eye level" : "Warm modern · South-east view";
      $id("walkthrough-hint").textContent = "Scroll to step inside";
      $id("tour-position").textContent = mode === "terrace" ? "A moment outside" : "Outside, looking in";
      $id("enter-house").querySelector("span").textContent = "Enter the house";
    }
    setActiveRoom(room === "approach" || room === "staircase" ? "entrance" : room);
    $id("scene-name").textContent = name;
    $id("scene-note").textContent = note;
    $id("tour-progress").style.width = `${(mode === "tour" || mode === "free") ? progress * 100 : 0}%`;
    $id("tour-slider").value = Math.round(targetProgress * 1000);
  }

  function setView(view, t = 0) {
    if (!ready) return;
    keys.clear();
    yawOffset = 0; pitchOffset = 0;
    mode = view;
    if (view === "tour") {
      targetProgress = t;
      if (reducedMotion) progress = t;
    } else {
      progress = targetProgress = 0;
      if (view === "overview") {
        const d = sub(model.overview.pos, model.overview.target);
        orbitRadius = length(d); orbitYaw = Math.atan2(d[0], d[2]);
        orbitPitch = Math.asin(d[1] / orbitRadius);
      }
    }
    scene.up = vec(0, 1, 0);
    scene.fov = view === "tour" ? 1.25 : view === "terrace" ? 1.1 : .8;
    updateGroups();
    updateLabels();
  }

  function enterFreeMode() {
    if (mode === "free") return;
    if (mode === "overview") {
      const entrance = routeAt(.18);
      pos = entrance.pos; look = entrance.target;
      progress = targetProgress = .18;
    }
    const d = normalize(sub(look, pos));
    freeYaw = Math.atan2(d[0], d[2]);
    freePitch = Math.asin(clamp(d[1], -1, 1));
    mode = "free";
    scene.fov = 1.25;
    scene.up = vec(0, 1, 0);
    updateGroups();
    announce("Free exploration · W A S D to walk, drag to look");
  }

  function moveFree(dt) {
    let dx = 0, dz = 0;
    const speed = keys.has("shift") ? 3.4 : 1.9;
    const forward = [Math.sin(freeYaw), 0, Math.cos(freeYaw)];
    const right = [-forward[2], 0, forward[0]];
    if (keys.has("w")) { dx += forward[0]; dz += forward[2]; }
    if (keys.has("s")) { dx -= forward[0]; dz -= forward[2]; }
    if (keys.has("d")) { dx += right[0]; dz += right[2]; }
    if (keys.has("a")) { dx -= right[0]; dz -= right[2]; }
    const magnitude = Math.hypot(dx, dz) || 1;
    const step = speed * dt / magnitude;
    const next = [clamp(pos[0] + dx * step, -11.5, 11.5), pos[1], clamp(pos[2] + dz * step, -6, 18)];
    // Walk on the staircase and upper floor. The guided tour is the simplest
    // way to change levels. Free walking cannot step off the upper-floor edge.
    if (pos[1] > 4.8 && (next[0] < 1.4 || next[0] > 9 || next[2] < -5.9 || next[2] > 6.1)) return;
    const eyeBottom = next[1] - .3, eyeTop = next[1] + .12;
    const blocked = model.objects.some(o => {
      if (o.kind !== "box" || o.group === "roof" || o.group === "landscape" || o.group === "water" || o.opacity < .5) return false;
      if (o.rotation) return false;
      if (o.size[1] < .35 || o.pos[1] + o.size[1] / 2 < eyeBottom || o.pos[1] - o.size[1] / 2 > eyeTop) return false;
      return Math.abs(next[0] - o.pos[0]) < o.size[0] / 2 + .15 && Math.abs(next[2] - o.pos[2]) < o.size[2] / 2 + .15;
    });
    if (!blocked) pos = next;
  }

  function toggleRoof() {
    roofHidden = !roofHidden;
    updateGroups();
    announce(roofHidden ? "Roof hidden" : "Roof restored");
  }

  function toggleLighting() {
    evening = !evening;
    scene.background = rgb(evening ? "#b6b8ad" : "#e4e6dc");
    scene.ambient = evening ? vec(.38, .35, .29) : vec(.63, .63, .59);
    keyLight.color = evening ? vec(.75, .53, .31) : vec(.57, .53, .43);
    fillLight.color = evening ? vec(.17, .20, .23) : vec(.19, .22, .20);
    $id("light-toggle").setAttribute("aria-pressed", String(evening));
    $id("light-toggle").querySelector("span").textContent = evening ? "Golden hour" : "Daylight";
    announce(evening ? "Golden hour lighting" : "Daylight lighting");
  }

  function buildObject(item) {
    const p = vec(...item.pos);
    const options = {canvas: scene, pos: p, color: rgb(model.materials[item.material]),
      shininess: ["metal", "brass", "glass", "water"].includes(item.material) ? .7 : 0,
      opacity: item.opacity ?? 1, emissive: item.emissive || false};
    let object;
    if (item.kind === "cylinder") {
      object = cylinder({...options, axis: item.axis ? vec(...item.axis) : vec(0, item.size[1], 0), radius: item.size[0] / 2});
    } else {
      options.size = vec(...item.size);
      object = item.kind === "ellipsoid" ? ellipsoid(options) : box(options);
    }
    if (item.rotation) object.rotate({angle: item.rotation, axis: vec(0, 1, 0), origin: p});
    if (!groups.has(item.group)) groups.set(item.group, []);
    groups.get(item.group).push(object);
  }

  function resize() {
    const bounds = viewport.getBoundingClientRect();
    if (bounds.width < 1 || bounds.height < 1) return;
    scene.width = Math.round(bounds.width);
    scene.height = Math.round(bounds.height);
    pendingResize = false;
  }

  function frame(time) {
    const dt = Math.min((time - (lastFrame || time)) / 1000, .05);
    lastFrame = time;
    if (pendingResize) resize();
    const alpha = reducedMotion ? 1 : 1 - Math.exp(-dt * 5.8);
    let desiredPos, desiredLook;
    if (mode === "tour") {
      progress += (targetProgress - progress) * (reducedMotion ? 1 : 1 - Math.exp(-dt * 8));
      const route = routeAt(progress);
      desiredPos = route.pos;
      desiredLook = lookWithOffset(route.pos, route.target);
    } else if (mode === "overview") {
      const center = model.overview.target;
      desiredPos = add(center, [Math.sin(orbitYaw) * Math.cos(orbitPitch) * orbitRadius,
        Math.sin(orbitPitch) * orbitRadius, Math.cos(orbitYaw) * Math.cos(orbitPitch) * orbitRadius]);
      desiredLook = center;
    } else if (mode === "free") {
      moveFree(dt);
      desiredPos = pos;
      desiredLook = add(pos, [Math.sin(freeYaw) * Math.cos(freePitch) * 5, Math.sin(freePitch) * 5,
        Math.cos(freeYaw) * Math.cos(freePitch) * 5]);
    } else {
      const view = model.terrace;
      desiredPos = view.pos;
      desiredLook = lookWithOffset(view.pos, view.target);
    }
    pos = mix(pos, desiredPos, alpha);
    look = mix(look, desiredLook, alpha);
    scene.camera.pos = vec(...pos);
    scene.camera.axis = vec(...sub(look, pos));
    updateLabels();
    requestAnimationFrame(frame);
  }

  function scrollTour(delta) {
    if (!ready || Math.abs(delta) < .00001) return;
    if (mode !== "tour") setView("tour", mode === "free" ? progress : 0);
    targetProgress = clamp(targetProgress + delta, 0, 1);
    yawOffset *= .9; pitchOffset *= .9;
  }

  function setupControls() {
    $id("enter-house").addEventListener("click", () => {
      setView(mode === "tour" || mode === "free" ? "overview" : "tour", .18);
      viewport.focus({preventScroll: true});
    });
    document.querySelectorAll(".room-link").forEach(button => button.addEventListener("click", () => {
      const stop = model.stops.find(s => s.id === button.dataset.view);
      if (stop) setView("tour", stop.progress);
      else setView(button.dataset.view);
    }));
    $id("view-exterior").addEventListener("click", () => setView("overview"));
    $id("reset-view").addEventListener("click", () => setView("overview"));
    $id("roof-toggle").addEventListener("click", toggleRoof);
    $id("light-toggle").addEventListener("click", toggleLighting);
    $id("fullscreen").addEventListener("click", async () => {
      try {
        if (document.fullscreenElement) await document.exitFullscreen();
        else await $id("viewer-shell").requestFullscreen();
      } catch { announce("Full screen isn’t available in this browser."); }
    });
    $id("tour-slider").addEventListener("input", e => {
      const t = Number(e.target.value) / 1000;
      if (mode !== "tour") setView("tour", t);
      targetProgress = t;
    });
    viewport.addEventListener("wheel", e => {
      e.preventDefault();
      const pixels = e.deltaY * (e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? 600 : 1);
      scrollTour(clamp(pixels, -200, 200) * .0002);
    }, {passive: false, capture: true});
    viewport.addEventListener("contextmenu", e => e.preventDefault());
    viewport.addEventListener("pointerdown", e => {
      if (!ready) return;
      viewport.focus({preventScroll: true});
      viewport.setPointerCapture(e.pointerId);
      pointers.set(e.pointerId, [e.clientX, e.clientY]);
      if (pointers.size === 2) {
        const [a, b] = [...pointers.values()]; pinchDistance = Math.hypot(a[0] - b[0], a[1] - b[1]);
      }
      lastPointer = [e.clientX, e.clientY]; dragging = true;
      viewport.classList.add("dragging");
    });
    viewport.addEventListener("pointermove", e => {
      if (!dragging || !pointers.has(e.pointerId)) return;
      pointers.set(e.pointerId, [e.clientX, e.clientY]);
      if (pointers.size === 2) {
        const [a, b] = [...pointers.values()];
        const distance = Math.hypot(a[0] - b[0], a[1] - b[1]);
        scrollTour((distance - pinchDistance) * .0009);
        pinchDistance = distance;
      } else {
        const dx = e.clientX - lastPointer[0], dy = e.clientY - lastPointer[1];
        if (mode === "overview") {
          orbitYaw -= dx * .007;
          orbitPitch = clamp(orbitPitch + dy * .006, .08, 1.25);
        } else if (mode === "tour" || mode === "terrace") {
          yawOffset -= dx * .005;
          pitchOffset = clamp(pitchOffset + dy * .004, -.8, .8);
        } else if (mode === "free") {
          freeYaw -= dx * .005;
          freePitch = clamp(freePitch + dy * .004, -1.2, 1.2);
        }
      }
      lastPointer = [e.clientX, e.clientY];
    });
    function endPointer(e) {
      pointers.delete(e.pointerId);
      dragging = pointers.size > 0;
      if (!dragging) viewport.classList.remove("dragging");
      if (pointers.size === 1) lastPointer = [...pointers.values()][0];
    }
    viewport.addEventListener("pointerup", endPointer);
    viewport.addEventListener("pointercancel", endPointer);
    document.addEventListener("keydown", e => {
      if (!ready || /INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
      const key = e.key.toLowerCase();
      if (["w", "a", "s", "d", "arrowup", "arrowdown", " "].includes(key)) e.preventDefault();
      if (key === "escape") setView("overview");
      if (key === "r" && !e.repeat) toggleRoof();
      if (key === "l" && !e.repeat) toggleLighting();
      if (key === "arrowdown" || key === " ") scrollTour(.018);
      if (key === "arrowup") scrollTour(-.018);
      if (["w", "a", "s", "d"].includes(key)) { enterFreeMode(); keys.add(key); }
      if (key === "shift") keys.add(key);
    });
    document.addEventListener("keyup", e => keys.delete(e.key.toLowerCase()));
    window.addEventListener("blur", () => { keys.clear(); pointers.clear(); dragging = false; viewport.classList.remove("dragging"); });
    document.addEventListener("visibilitychange", () => { if (document.hidden) keys.clear(); });
  }

  function toggleHelp(open) {
    $id("help-panel").hidden = !open;
    $id("help-toggle").setAttribute("aria-expanded", String(open));
  }
  $id("help-toggle").addEventListener("click", () => toggleHelp($id("help-panel").hidden));
  $id("close-help").addEventListener("click", () => toggleHelp(false));
  $id("retry").addEventListener("click", () => location.reload());

  async function start() {
    try {
      if (typeof window.canvas !== "function") throw new Error("VPython’s engine is missing. Reinstall with python -m pip install -r requirements.txt, then restart main.py.");
      const response = await fetch("/api/house");
      if (!response.ok) throw new Error("The Python model could not be loaded. Restart main.py and reload this page.");
      model = await response.json();
      window.__context = {glowscript_container: window.jQuery(viewport)};
      const bounds = viewport.getBoundingClientRect();
      scene = canvas({width: Math.round(bounds.width), height: Math.round(bounds.height),
        background: rgb("#e4e6dc"), ambient: vec(.63, .63, .59), autoscale: false,
        userspin: false, userzoom: false, userpan: false, fov: .8});
      scene.lights = [];
      keyLight = distant_light({canvas: scene, direction: vec(-.5, 1, .8), color: vec(.57, .53, .43)});
      fillLight = distant_light({canvas: scene, direction: vec(.8, .3, -.5), color: vec(.19, .22, .20)});
      // Build in batches so the browser can paint loading feedback on slower GPUs.
      for (let i = 0; i < model.objects.length; i++) {
        buildObject(model.objects[i]);
        if (i % 180 === 179) await new Promise(requestAnimationFrame);
      }
      const links = $id("room-links");
      model.stops.forEach((stop, i) => {
        const button = document.createElement("button");
        button.className = "room-link";
        button.dataset.view = stop.id;
        button.innerHTML = `<span class="room-number">0${i + 1}</span><span><strong></strong><small></small></span><svg class="room-chevron"><use href="#i-chevron"/></svg>`;
        button.querySelector("strong").textContent = stop.name;
        button.querySelector("small").textContent = stop.detail;
        links.appendChild(button);
      });
      ready = true;
      pos = [...model.overview.pos]; look = [...model.overview.target];
      setView("overview");
      setupControls();
      new ResizeObserver(() => { pendingResize = true; }).observe(viewport);
      $id("enter-house").disabled = false;
      $id("loading").hidden = true;
      requestAnimationFrame(frame);
      // A read-only diagnostic is useful when customizing the Python model.
      window.houseViewer = {get state() { return {mode, progress, targetProgress, pos: [...pos], roofHidden, evening, objects: model.objects.length}; }};
    } catch (error) {
      console.error(error);
      $id("loading").hidden = true;
      $id("error-panel").hidden = false;
      $id("error-message").textContent = error.message || "Enable WebGL in your browser, then try again.";
    }
  }
  start();
})();
