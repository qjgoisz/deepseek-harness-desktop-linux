"""Verify in-memory Desktop Host authentication in the current Desktop payload."""
import os
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DesktopAuthCookie(unittest.TestCase):
    def test_real_http_websocket_and_restart_paths(self):
        app = Path(os.environ.get('DSH_TEST_APP', ROOT / 'out-x64/resources/app'))
        main = app / 'lib/main.js'
        if not main.is_file():
            self.skipTest('DSH_TEST_APP must provide a built Desktop payload')

        result = subprocess.run(
            ['node', str(ROOT / 'tests/desktop-auth-cookie.mjs'), str(main), str(app.resolve())],
            capture_output=True, text=True, timeout=45)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
