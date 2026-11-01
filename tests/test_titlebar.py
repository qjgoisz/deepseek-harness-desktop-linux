"""Titlebar stages must be coherent and must not corrupt completed trees."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch as mock_patch

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'patches/patch-titlebar.py'
spec = importlib.util.spec_from_file_location('titlebar', PATCH)
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)


def fixture(blocks=None):
    blocks = blocks or ('', '')
    return '\n'.join(w + ('\n' + b if b else '') for w, b in zip(patch.WINDOWS, blocks))


class Titlebar(unittest.TestCase):
    def test_first_application_and_repeat(self):
        result = patch.transform(fixture())
        self.assertEqual(result, fixture(patch.OVERLAY))
        self.assertEqual(patch.transform(result), result)

    def test_completed_chrome_is_unchanged(self):
        source = fixture(patch.CHROME)
        self.assertEqual(patch.transform(source), source)

    def test_invalid_layouts_never_write(self):
        sources = [
            patch.WINDOWS[0],
            fixture() + patch.WINDOWS[0],
            fixture((patch.OVERLAY[0], '')),
            fixture((patch.OVERLAY[0], patch.CHROME[1])),
            fixture(patch.CHROME) + patch.OVERLAY[0],
            fixture(patch.OVERLAY).replace('height: 40', 'height: 41'),
            fixture(patch.CHROME).replace('hasShadow: true', 'hasShadow: false'),
            fixture() + patch.OVERLAY[0].split(' {', 1)[0] + ' {',
            fixture(patch.CHROME).replace('=== "linux"', "=== 'linux'"),
            fixture(patch.OVERLAY).replace('=== "linux" ?', '=== "linux"  ?'),
            fixture(patch.OVERLAY).replace('} : {},', '} : {} ,'),
        ]
        for source in sources:
            with self.subTest(source=source), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'main.js'
                path.write_text(source)
                result = subprocess.run(['python3', str(PATCH), str(path)], capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(path.read_text(), source)

    def test_atomic_write_preserves_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'main.js'
            path.write_text(fixture())
            path.chmod(0o640)
            subprocess.run(['python3', str(PATCH), str(path)], check=True, capture_output=True)
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)
            self.assertEqual(path.read_text(), fixture(patch.OVERLAY))

    def test_failed_replace_preserves_original_and_cleans_temporary(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'main.js'
            source = fixture()
            path.write_text(source)
            with mock_patch('sys.argv', [str(PATCH), str(path)]), mock_patch.object(
                patch.os, 'replace', side_effect=OSError('replacement failed')
            ):
                with self.assertRaises(OSError):
                    patch.main()
            self.assertEqual(path.read_text(), source)
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_completed_real_payload_is_unchanged(self):
        app = Path(os.environ.get('DSH_TEST_APP', '/usr/lib/deepseek-harness/resources/app'))
        main = app / 'lib/main.js'
        if not main.exists():
            self.skipTest('DSH_TEST_APP must provide a completed Linux payload')
        source = main.read_text()
        self.assertEqual(patch.transform(source), source)
