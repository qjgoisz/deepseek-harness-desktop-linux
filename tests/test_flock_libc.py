"""Network-free libc detection without weakening real kernel file locks."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('flock_patch', ROOT/'patches/patch-flock-libc.py')
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)

class FlockLibcTests(unittest.TestCase):
    def test_strict_transform_and_idempotence(self):
        source = 'function probe() {\n' + patch.OLD + '\n}\n'
        updated = patch.transform(source)
        self.assertEqual(patch.transform(updated), updated)
        for bad in [source+patch.OLD, 'unknown', updated.replace('finally', 'catch'), source.replace('getReport()', 'getReport(new Error())')]:
            with self.assertRaises(ValueError): patch.transform(bad)

    def test_unknown_file_is_not_partially_written(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)/patch.TARGET
            target.parent.mkdir(parents=True)
            target.write_text('unknown upstream')
            with self.assertRaises(ValueError): patch.main(d)
            self.assertEqual(target.read_text(), 'unknown upstream')

    def test_syntax_failure_does_not_replace_target(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)/patch.TARGET
            target.parent.mkdir(parents=True)
            source = 'function broken( {\n' + patch.OLD
            target.write_text(source)
            with self.assertRaises(subprocess.CalledProcessError): patch.main(d)
            self.assertEqual(target.read_text(), source)
            self.assertFalse(list(target.parent.glob('.flock-libc-*')))

    def test_real_payload_and_file_lock_semantics(self):
        app = Path(os.environ.get('DSH_TEST_APP', '/usr/lib/deepseek-harness/resources/app'))
        source = app/patch.TARGET
        if not source.exists(): self.skipTest('DSH_TEST_APP must provide a real payload')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'node_modules').symlink_to(app/'dsh/node_modules', target_is_directory=True)
            module = root/'flock.mjs'
            module.write_text(patch.transform(source.read_text()))
            result = subprocess.run(['node', str(ROOT/'tests/flock-libc-runtime.mjs'), str(module), str(root)], capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
