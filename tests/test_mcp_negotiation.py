"""Per-server MCP negotiation, exercised against the real installed payload."""
from pathlib import Path
import importlib.util
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('mcp_patch', ROOT/'patches/patch-mcp-negotiation.py')
PATCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PATCH)


class McpNegotiationTests(unittest.TestCase):
    def fixture(self):
        return PATCH.CLIENT + '\n' + PATCH.FIELD + '\n' + PATCH.FIELD + '\n' + PATCH.APPLY + '\n' + PATCH.AWAIT

    def test_transform_idempotence_and_fail_closed(self):
        original = self.fixture()
        patched = PATCH.transform(original)
        self.assertEqual(PATCH.transform(patched), patched)
        for source in [original+PATCH.CLIENT, original.replace(PATCH.FIELD, '', 1), patched.replace(PATCH.NEW_CLIENT, PATCH.CLIENT)]:
            with self.assertRaises(ValueError):
                PATCH.transform(source)

    def test_v1_upgrade_and_unknown_background_layout(self):
        original = self.fixture()
        v1 = original
        for old, new, count in PATCH.V1_REPLACEMENTS:
            v1 = v1.replace(old, new)
        v1 = PATCH.V1_MARKER + '\n' + v1
        self.assertEqual(PATCH.transform(v1), PATCH.transform(original))
        for source in [v1.replace(PATCH.V1_APPLY, PATCH.APPLY),
                       PATCH.transform(original).replace(PATCH.NEW_AWAIT, PATCH.AWAIT),
                       original + PATCH.AWAIT]:
            with self.assertRaises(ValueError):
                PATCH.transform(source)

    def test_real_payload_and_process_lifecycle(self):
        app = Path(os.environ.get('DSH_TEST_APP', '/usr/lib/deepseek-harness/resources/app'))
        package = app/'dsh/node_modules/@deepseek-ai/dsh-mcp-client'
        if not package.exists():
            self.skipTest('DSH_TEST_APP must point to a real application payload')
        with tempfile.TemporaryDirectory(prefix='dsh-mcp-test-') as d:
            root = Path(d)
            # Real dependencies, isolated patched entry; never touch the installation.
            (root/'node_modules').symlink_to(app/'dsh/node_modules', target_is_directory=True)
            target = root/'client.mjs'
            target.write_text(PATCH.transform((package/'lib/index.js').read_text()))
            result = subprocess.run(['node', str(ROOT/'tests/mcp-negotiation-runtime.mjs'), str(target), str(root)], capture_output=True, text=True, timeout=25)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_targeted_profile_edits(self):
        app = Path(os.environ.get('DSH_TEST_APP', '/usr/lib/deepseek-harness/resources/app'))
        if not (app/'dsh/node_modules/js-yaml').exists():
            self.skipTest('DSH_TEST_APP must provide js-yaml')
        result = subprocess.run(['node', str(ROOT/'tests/mcp-startup-config.mjs'), str(app)], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_background_lifecycle_and_real_cordis(self):
        app = Path(os.environ.get('DSH_TEST_APP', '/usr/lib/deepseek-harness/resources/app'))
        package = app/'dsh/node_modules/@deepseek-ai/dsh-mcp-client'
        if not package.exists():
            self.skipTest('DSH_TEST_APP must point to a real application payload')
        with tempfile.TemporaryDirectory(prefix='dsh-mcp-test-') as d:
            root = Path(d)
            (root/'node_modules').symlink_to(app/'dsh/node_modules', target_is_directory=True)
            target = root/'client.mjs'
            target.write_text(PATCH.transform((package/'lib/index.js').read_text()))
            result = subprocess.run(['node', str(ROOT/'tests/mcp-background-runtime.mjs'), str(target), str(root)], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_configure_refuses_old_core_or_wrong_remote_without_writing(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            app = root/'app'
            module = app/'dsh/node_modules/@deepseek-ai/dsh-mcp-client/lib/index.js'
            module.parent.mkdir(parents=True)
            profile = root/'profile'
            profile.mkdir()
            config = profile/'cordis.patch.yml'
            config.write_text('original settings\n')
            remote = root/'remote/node_modules/mcp-remote'
            remote.mkdir(parents=True)
            (remote/'package.json').write_text('{"version":"0.15.2"}')
            for marker in [PATCH.V1_MARKER, PATCH.MARKER]:
                module.write_text(marker+'\n')
                result = subprocess.run(['node', str(ROOT/'local-fixes/mcp-startup/configure.mjs'), '--app', str(app), '--profile', str(profile), '--runtime', str(root/'remote'), '--node', shutil.which('node'), '--apply'], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 1)
                self.assertIn('v2 MCP startup patch' if marker == PATCH.V1_MARKER else 'mcp-remote 0.15.1', result.stderr)
                self.assertEqual(config.read_text(), 'original settings\n')
                self.assertEqual(list(profile.iterdir()), [config])
