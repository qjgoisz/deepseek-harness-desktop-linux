import importlib.util
from pathlib import Path
import unittest
import tempfile

spec = importlib.util.spec_from_file_location('rounded', Path(__file__).resolve().parents[1]/'patches/patch-personal-rounded.py')
rounded = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rounded)

class PersonalRoundedTests(unittest.TestCase):
    def test_layer_is_idempotent_and_keeps_controls(self):
        original = '\tconst CSS = `\n/* fullscreen controls */\n`;\nif (kdeSession && !kdeBlurReady) root.dataset.dshOpaqueSidebar = "";'
        result = rounded.transform_preload(original)
        self.assertEqual(result, rounded.transform_preload(result))
        self.assertIn('/* fullscreen controls */', result)
        self.assertIn('clip-path: inset(0 round 12px)', result)
        self.assertIn('[data-fullscreen] body { clip-path: none; }', result)
        self.assertIn('if (process.platform === "linux")', result)
    def test_unknown_payload_fails_without_changes(self):
        with self.assertRaises(ValueError): rounded.transform_preload('new unknown preload')
        with self.assertRaises(ValueError): rounded.transform_main('new unknown main')
    def test_native_blur_disabled_idempotently(self):
        result = rounded.transform_main('\tconst configureKdeBlur = (window) => {\nreturn request;\n};')
        self.assertIn('return Promise.resolve(false)', result)
        self.assertEqual(result, rounded.transform_main(result))

    def test_upgrade_existing_personal_preloads(self):
        from test_kde_material import chrome, material
        from test_fullscreen_reveal import reveal
        for extra in (chrome.MAIN_EXTRA_CSS, chrome.WELCOME_EXTRA_CSS):
            source = chrome.PRELOAD_FN.replace('__TITLEBAR_HEIGHT__', '48').replace('__EXTRA_CSS__', extra)
            source = reveal.transform(material.transform_preload(source))
            fresh = rounded.transform_preload(source)
            for previous in (rounded.LEGACY_CSS, rounded.PREVIOUS_CSS):
                legacy = fresh.replace(rounded.CSS, previous)
                self.assertEqual(rounded.transform_preload(legacy), fresh)
            self.assertEqual(rounded.transform_preload(fresh), fresh)
            self.assertIn(reveal.JS, fresh)  # Keep state sync and Wayland double-click restore.

    def test_bad_legacy_welcome_leaves_all_files_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'lib'
            root.mkdir()
            original = '\tconst CSS = `\n`;\nif (kdeSession && !kdeBlurReady) root.dataset.dshOpaqueSidebar = "";'
            sources = {
                'main.js': '\tconst configureKdeBlur = (window) => {\nreturn request;\n};',
                'preload-app.cjs': original,
                'preload-welcome.cjs': original + rounded.LEGACY_CSS + rounded.LEGACY_CSS,
            }
            for name, source in sources.items():
                (root / name).write_text(source)
            with self.assertRaises(ValueError):
                rounded.main(directory)
            self.assertEqual(sources, {p.name: p.read_text() for p in root.iterdir()})
