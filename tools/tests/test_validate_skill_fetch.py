"""The two real fetchers, urllib and curl, against a web server on this machine: no outside network."""
import http.server
import os
import shutil
import sys
import threading
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import validate_skill  # noqa: E402


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200 if self.path == "/ok" else 404)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *args):
        pass


class LocalServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.base = "http://127.0.0.1:%d" % cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def closed_port(self):
        """A port on this machine nothing listens on."""
        probe = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        port = probe.server_address[1]
        probe.server_close()
        return "http://127.0.0.1:%d/ok" % port

    def test_urllib_reports_the_status_code(self):
        self.assertEqual(validate_skill._urllib_status(self.base + "/ok"), (self.base + "/ok", 200))
        self.assertEqual(validate_skill._urllib_status(self.base + "/gone"), (self.base + "/gone", 404))

    def test_urllib_names_the_error_when_nothing_answers(self):
        url = self.closed_port()
        self.assertEqual(validate_skill._urllib_status(url), (url, "URLError"))

    def test_curl_reports_the_status_code(self):
        self.assertIsNotNone(shutil.which("curl"), "this test needs curl on PATH (the Jira scripts need it too)")
        self.assertEqual(validate_skill.curl_status(self.base + "/ok"), 200)
        self.assertEqual(validate_skill.curl_status(self.base + "/gone"), 404)

    def test_curl_says_so_when_nothing_answers(self):
        self.assertIsNotNone(shutil.which("curl"), "this test needs curl on PATH (the Jira scripts need it too)")
        self.assertEqual(validate_skill.curl_status(self.closed_port()), "curl-fail")

    def test_a_machine_without_curl_gets_the_error_name_not_a_crash(self):
        path = os.environ["PATH"]
        os.environ["PATH"] = ""
        try:
            self.assertEqual(validate_skill.curl_status(self.base + "/ok"), "FileNotFoundError")
        finally:
            os.environ["PATH"] = path

    def test_check_url_falls_back_to_curl_and_keeps_the_better_answer(self):
        self.assertEqual(validate_skill.check_url(self.base + "/ok"), (self.base + "/ok", 200))
        self.assertEqual(validate_skill.check_url(self.base + "/gone"), (self.base + "/gone", 404))


if __name__ == "__main__":
    unittest.main()
