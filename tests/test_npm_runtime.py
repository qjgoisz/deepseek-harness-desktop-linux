"""npm prefix discovery and permission checks without real installations."""
from pathlib import Path
import subprocess
import unittest
ROOT = Path(__file__).resolve().parents[1]
class NpmRuntime(unittest.TestCase):
    def test_explicit_prefix_and_permissions(self):
        r = subprocess.run(['node', str(ROOT/'tests/npm-runtime.mjs')], capture_output=True, text=True, timeout=20)
        self.assertEqual(r.returncode, 0, r.stdout+r.stderr)
