"""Desktop authentication must not depend on a persistent Chromium cookie jar."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch as mock_patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('desktop_cookie', ROOT/'patches/patch-desktop-auth-cookie.py')
PATCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PATCH)


class DesktopAuthCookie(unittest.TestCase):
    def fixture(self):
        return '\n'.join(old for old, _ in PATCH.REPLACEMENTS)

    def test_complete_state_and_idempotence(self):
        original = self.fixture()
        updated = PATCH.transform(original)
        self.assertEqual(PATCH.transform(updated), updated)
        self.assertNotIn('session.defaultSession.cookies.get', updated)

    def test_unknown_partial_and_duplicate_states_never_write(self):
        original = self.fixture()
        updated = PATCH.transform(original)
        bad_sources = [
            'unknown', original + PATCH.START,
            original.replace(PATCH.WELCOME, ''),
            original + '\nconnectDesktopWelcome(url)',
            updated.replace(PATCH.NEW_START, PATCH.START),
            updated.replace('credentials: "omit"', 'credentials: "include"', 1),
            updated.replace(PATCH.MARKER, PATCH.MARKER + '-unknown'),
            updated + '\n' + PATCH.HELPER,
        ]
        for source in bad_sources:
            with self.subTest(source=source[:80]), tempfile.TemporaryDirectory() as directory:
                path = Path(directory)/PATCH.TARGET
                path.parent.mkdir(parents=True)
                path.write_text(source)
                with self.assertRaises(ValueError):
                    PATCH.main(directory)
                self.assertEqual(path.read_text(), source)
                self.assertEqual(list(path.parent.iterdir()), [path])

    def test_syntax_failure_keeps_original(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/PATCH.TARGET
            path.parent.mkdir(parents=True)
            source = self.fixture() + '\nfunction broken( {'
            path.write_text(source)
            with self.assertRaises(subprocess.CalledProcessError):
                PATCH.main(directory)
            self.assertEqual(path.read_text(), source)
            self.assertEqual(list(path.parent.iterdir()), [path])

    def real_source(self):
        app = Path(os.environ.get('DSH_TEST_APP', '/usr/lib/deepseek-harness/resources/app'))
        if not (app/PATCH.TARGET).is_file():
            self.skipTest('DSH_TEST_APP must provide a real payload')
        source = (app/PATCH.TARGET).read_text()
        if source.startswith(PATCH.MARKER + '\n'):
            # Final-package runs also need an unpatched input for write-failure tests.
            original = source[len(PATCH.MARKER) + 1:]
            for old, new in reversed(PATCH.REPLACEMENTS):
                self.assertEqual(original.count(new), 1)
                original = original.replace(new, old)
            self.assertEqual(PATCH.transform(original), source)
            source = original
        return app, source

    def test_atomic_write_preserves_permissions_and_repeat(self):
        _, source = self.real_source()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/PATCH.TARGET
            path.parent.mkdir(parents=True)
            path.write_text(source)
            path.chmod(0o640)
            PATCH.main(directory)
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)
            updated = path.read_bytes()
            PATCH.main(directory)
            self.assertEqual(path.read_bytes(), updated)

    def test_failed_replace_cleans_temporary(self):
        _, source = self.real_source()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/PATCH.TARGET
            path.parent.mkdir(parents=True)
            path.write_text(source)
            with mock_patch.object(PATCH.os, 'replace', side_effect=OSError('replace failed')):
                with self.assertRaises(OSError):
                    PATCH.main(directory)
            self.assertEqual(path.read_text(), source)
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_real_http_websocket_and_restart_paths(self):
        app, source = self.real_source()
        with tempfile.TemporaryDirectory() as directory:
            module = Path(directory)/'main.mjs'
            module.write_text(PATCH.transform(source))
            result = subprocess.run(
                ['node', str(ROOT/'tests/desktop-auth-cookie.mjs'), str(module), str(app)],
                capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
