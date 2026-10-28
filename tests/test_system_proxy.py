"""KDE/v2rayN Desktop bridge, strict payload transforms and real local routing."""
from pathlib import Path
import importlib.util
import os
import shutil
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('patch_system_proxy', ROOT/'patches/patch-system-proxy.py')
PATCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PATCH)


class SystemProxyTests(unittest.TestCase):
    def make_tree(self, root):
        modules = root/'dsh/node_modules/@deepseek-ai'
        proxy = modules/'dsh-http-proxy/lib/index.js'
        boot = modules/'dsh/lib/profile-boot-fixture.js'
        proxy.parent.mkdir(parents=True)
        boot.parent.mkdir(parents=True)
        proxy.write_text('function route(policy,url,proxy){'+PATCH.BYPASS+'}\n'+PATCH.EXPORT+'\n')
        boot.write_text(PATCH.IMPORT+'\nasync function runProfile(options){'+PATCH.CALL+'console.warn);}\n')
        return proxy, boot

    def copy_payload_proxy(self, source, target):
        target.write_bytes(source.read_bytes())
        if PATCH.MARKER in target.read_text():
            # A packaged payload already carries the bridge: exercise its strict idempotent path.
            target.with_name('desktop-system-proxy.mjs').write_bytes(source.with_name('desktop-system-proxy.mjs').read_bytes())
            boot = target.parents[2]/'dsh/lib/profile-boot-fixture.js'
            boot.write_text(boot.read_text().replace(PATCH.IMPORT, PATCH.NEW_IMPORT).replace(PATCH.CALL, PATCH.NEW_CALL))

    def tls_environment(self, root):
        env = os.environ.copy()
        if not shutil.which('openssl'):
            return env
        cert, key = root/'local-test.crt', root/'local-test.key'
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                        '-keyout', str(key), '-out', str(cert), '-days', '1',
                        '-subj', '/CN=proxy-test.invalid', '-addext', 'subjectAltName=DNS:proxy-test.invalid'],
                       check=True, capture_output=True, timeout=10)
        env.update(NODE_EXTRA_CA_CERTS=str(cert), DSH_PROXY_TEST_CERT=str(cert), DSH_PROXY_TEST_KEY=str(key))
        return env

    def test_patch_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_tree(root)
            self.assertEqual(PATCH.main(root), 0)
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(PATCH.main(root), 0)
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_unknown_or_duplicate_payload_is_never_partially_written(self):
        for mode in ['unknown-proxy', 'duplicate-call', 'unknown-installed-adapter', 'foreign-controller']:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                proxy, boot = self.make_tree(root)
                if mode == 'unknown-proxy':
                    proxy.write_text('unknown upstream proxy')
                elif mode == 'duplicate-call':
                    boot.write_text(boot.read_text()+PATCH.CALL)
                elif mode == 'unknown-installed-adapter':
                    proxy.with_name('desktop-system-proxy.mjs').write_text('unknown module')
                else:
                    proxy.write_text(proxy.read_text()+'\nfunction createDesktopProxyController() {}\n')
                before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
                self.assertEqual(PATCH.main(root), 1)
                self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_kde_reader_and_notification_lifecycle(self):
        result = subprocess.run(['node', str(ROOT/'tests/system-proxy-runtime.mjs')], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_real_payload_routes_and_switches_without_interrupting_stream(self):
        app = Path(os.environ.get('DSH_TEST_APP', '/usr/lib/deepseek-harness/resources/app'))
        modules = app/'dsh/node_modules'
        proxy = modules/'@deepseek-ai/dsh-http-proxy/lib/index.js'
        if not proxy.is_file() or not (modules/'undici').is_dir():
            self.skipTest('set DSH_TEST_APP to a real DSH payload for local routing integration')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_tree(root)
            target = root/'dsh/node_modules/@deepseek-ai/dsh-http-proxy/lib/index.js'
            self.copy_payload_proxy(proxy, target)
            (target.parent.parent/'package.json').write_text('{"type":"module"}')
            self.assertEqual(PATCH.main(root), 0)
            # Test-only export: the installed bridge exposes only the Desktop entry function.
            target.write_text(target.read_text()+'\nexport { createDesktopProxyController };\n')
            (root/'dsh/node_modules/undici').symlink_to(modules/'undici')
            result = subprocess.run(['node', str(ROOT/'tests/system-proxy-runtime.mjs'), str(target)],
                                    env=self.tls_environment(root), capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            if shutil.which('openssl'):
                self.assertIn('Real HTTP + HTTPS CONNECT routing', result.stdout)

    def test_real_kde_dbus_and_automatic_startup(self):
        if not all(shutil.which(tool) for tool in ['dbus-run-session', 'dbus-send', 'kreadconfig6']):
            self.skipTest('KDE/D-Bus tools unavailable')
        app = Path(os.environ.get('DSH_TEST_APP', '/usr/lib/deepseek-harness/resources/app'))
        modules = app/'dsh/node_modules'
        source = modules/'@deepseek-ai/dsh-http-proxy/lib/index.js'
        if not source.exists():
            self.skipTest('real DSH payload unavailable')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_tree(root)
            target = root/'dsh/node_modules/@deepseek-ai/dsh-http-proxy/lib/index.js'
            self.copy_payload_proxy(source, target)
            (target.parent.parent/'package.json').write_text('{"type":"module"}')
            self.assertEqual(PATCH.main(root), 0)
            (root/'dsh/node_modules/undici').symlink_to(modules/'undici')
            config = root/'config'
            config.mkdir()
            env = {'PATH': os.environ['PATH'], 'HOME': str(root), 'XDG_CONFIG_HOME': str(config),
                   'XDG_CURRENT_DESKTOP': 'KDE', 'KDE_SESSION_VERSION': '6', 'LANG': 'C.UTF-8'}
            result = subprocess.run(['dbus-run-session', '--', 'node', str(ROOT/'tests/system-proxy-dbus.mjs'), str(target)],
                                    env=env, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_build_installs_bridge(self):
        self.assertIn('patches/patch-system-proxy.py', (ROOT/'scripts/build/tree.sh').read_text())
