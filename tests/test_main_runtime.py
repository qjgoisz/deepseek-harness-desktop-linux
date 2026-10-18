"""Runtime-layout compatibility across official Desktop payload versions."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'patches/patch-main.py'
SPEC = importlib.util.spec_from_file_location('patch_main', PATCH)
MAIN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MAIN)


class MainRuntime(unittest.TestCase):
    def test_resources_override_keeps_both_supported_pnpm_layouts(self):
        for segments in ['"runtime", "pnpm"',
                         '"runtime", "primary-runtime", "dependencies", "pnpm"']:
            with self.subTest(segments=segments):
                entry = f'join(process.resourcesPath, {segments}, "bin", "pnpm.mjs")'
                source = f'const pnpm = development ? customEntry : {entry};'
                self.assertEqual(MAIN.rewrite_pnpm_path(source),
                                 source.replace('process.resourcesPath', 'desktopResourcesRoot()'))

    def test_unknown_or_ambiguous_pnpm_layout_fails(self):
        old = 'join(process.resourcesPath, "runtime", "pnpm", "bin", "pnpm.mjs")'
        new = 'join(process.resourcesPath, "runtime", "primary-runtime", "dependencies", "pnpm", "bin", "pnpm.mjs")'
        for source in ['unrecognized upstream layout', old + old, old + new]:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    MAIN.rewrite_pnpm_path(source)

    def test_incomplete_patch_does_not_write_partial_changes(self):
        # One real match followed by missing upstream anchors must not corrupt
        # the file and make the next build fail on already-patched code.
        source = 'if (!["win32", "darwin"].includes(process.platform)) throw Error();\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'main.js'
            path.write_text(source)
            result = subprocess.run(['python3', str(PATCH), str(path)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(path.read_text(), source)

    def test_sharp_facade_reports_the_bundled_worker_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy2(ROOT / 'install-image-worker.sh', root)
            shutil.copytree(ROOT / 'image-worker-src', root / 'image-worker-src')
            modules = root / 'out-x64/resources/app/dsh/node_modules'
            packages = ['sharp', '@img/colour', '@img/sharp-linux-x64',
                        '@img/sharp-libvips-linux-x64', 'detect-libc', 'semver']
            for package in packages:
                (modules / package).mkdir(parents=True)
            native = {'name': 'sharp', 'version': '0.35.5',
                      'engines': {'node': '>=20.9.0'}, 'license': 'Apache-2.0'}
            (modules / 'sharp/package.json').write_text(json.dumps(native))
            result = subprocess.run(['bash', str(root / 'install-image-worker.sh'), 'out-x64', 'x64'],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            facade = json.loads((modules / 'sharp/package.json').read_text())
            worker = root / 'out-x64/resources/image-worker/worker-modules/node_modules/sharp/package.json'
            self.assertEqual(facade['version'], json.loads(worker.read_text())['version'])
            self.assertEqual(facade['version'], native['version'])
            self.assertEqual(facade['main'], './dist/index.cjs')


if __name__ == '__main__':
    unittest.main()
