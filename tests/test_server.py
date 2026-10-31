"""The HTML controls must reach Python even while VPython is loading."""
from functools import partial
from http.server import ThreadingHTTPServer
from queue import Queue
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from main import HouseHandler


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.commands = Queue(maxsize=2)
        handler = partial(HouseHandler, commands=self.commands,
                          state={"value": {"ready": False}}, scene_url="http://127.0.0.1:9999/")
        self.log_patch = patch.object(HouseHandler, "log_message", return_value=None)
        self.log_patch.start()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/command"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.log_patch.stop()

    def post(self, body):
        return urlopen(Request(self.url, data=body))

    def test_room_click_before_scene_is_ready_is_queued(self):
        with self.post(b"action=living") as response:
            self.assertEqual(response.status, 204)
        self.assertEqual(self.commands.get_nowait(), "living")

    def test_unknown_control_does_not_reach_the_scene(self):
        with self.assertRaises(HTTPError) as raised:
            self.post(b"action=unknown")
        self.assertEqual(raised.exception.code, 400)
        self.assertTrue(self.commands.empty())

    def test_full_control_queue_returns_an_error_without_blocking(self):
        self.commands.put_nowait("living")
        self.commands.put_nowait("kitchen")
        with self.assertRaises(HTTPError) as raised:
            self.post(b"action=bedroom")
        self.assertEqual(raised.exception.code, 503)


if __name__ == "__main__":
    unittest.main()
