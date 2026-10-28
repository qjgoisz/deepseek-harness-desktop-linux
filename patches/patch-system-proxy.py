#!/usr/bin/env python3
"""Install the Desktop-only KDE proxy bridge into an extracted application tree."""
from pathlib import Path
import os
import sys
import tempfile

SOURCE = Path(__file__).with_name('system-proxy')
MARKER = '/* dsh-linux-system-proxy-v1:'
IMPORT = 'import { installProxyFromEnvironment } from "@deepseek-ai/dsh-http-proxy";'
CALL = 'const disposeProxy = await installProxyFromEnvironment(options.environment,'
EXPORT = 'export { clearedProxyEnv, installProxyFromEnvironment, proxyEnvironmentForChild, proxyRouteFor };'
BYPASS = 'return bypassesProxy(policy.noProxy, url) ? void 0 : proxy;'
NEW_IMPORT = IMPORT.replace('installProxyFromEnvironment', 'installDesktopProxyFromEnvironment')
NEW_CALL = CALL.replace('installProxyFromEnvironment', 'installDesktopProxyFromEnvironment')
NEW_EXPORT = EXPORT.replace('clearedProxyEnv,', 'clearedProxyEnv, installDesktopProxyFromEnvironment,')
NEW_BYPASS = ('return (bypassesProxy(policy.noProxy, url) || '
              '(policy.desktopSystem && desktopIpv4Bypass(policy.noProxy, url))) ? void 0 : proxy;')


def unique_replace(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f'expected one upstream match: {old[:90]}')
    return source.replace(old, new)


def transformations(app):
    modules = app / 'dsh/node_modules/@deepseek-ai'
    proxy = modules / 'dsh-http-proxy/lib/index.js'
    candidates = [p for p in (modules / 'dsh/lib').glob('*.js')
                  if CALL in p.read_text() or NEW_CALL in p.read_text()]
    if len(candidates) != 1:
        raise ValueError('expected one profile-boot module')
    boot = candidates[0]
    source, entry = proxy.read_text(), boot.read_text()
    controller = (SOURCE / 'proxy-controller.js').read_text()
    adapter = proxy.with_name('desktop-system-proxy.mjs')
    adapter_source = (SOURCE / adapter.name).read_text()
    if MARKER in source:
        # A repeated build is safe; an edited/unknown bridge is never silently replaced.
        original, tail = source.split(MARKER, 1)
        if MARKER + tail != controller or not adapter.exists() or adapter.read_text() != adapter_source:
            raise ValueError('existing system-proxy bridge differs from this patch')
        unique_replace(original, NEW_EXPORT, EXPORT)
        unique_replace(original, NEW_BYPASS, BYPASS)
        unique_replace(entry, NEW_IMPORT, IMPORT)
        unique_replace(entry, NEW_CALL, CALL)
        return {}
    if adapter.exists():
        raise ValueError('unexpected existing desktop-system-proxy.mjs')
    if any(name in source for name in ('function desktopIpv4Bypass(',
                                       'function createDesktopProxyController(',
                                       'function installDesktopProxyFromEnvironment(')):
        raise ValueError('upstream proxy controller layout is unknown')
    source = unique_replace(source, EXPORT, NEW_EXPORT)
    source = unique_replace(source, BYPASS, NEW_BYPASS)
    entry = unique_replace(entry, IMPORT, NEW_IMPORT)
    entry = unique_replace(entry, CALL, NEW_CALL)
    return {proxy: source + '\n' + controller, boot: entry, adapter: adapter_source}


def atomic_write(path, data, mode=0o644):
    fd, temporary = tempfile.mkstemp(prefix='.system-proxy-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(data)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main(app):
    originals = {}
    written = []
    try:
        changes = transformations(Path(app))
        originals = {p: (p.read_text(), p.stat().st_mode & 0o777) if p.exists() else None for p in changes}
        for path, data in changes.items():
            atomic_write(path, data, originals[path][1] if originals[path] else 0o644)
            written.append(path)
    except (OSError, ValueError) as error:
        for path in reversed(written):
            if originals[path] is None:
                path.unlink()
            else:
                atomic_write(path, *originals[path])
        print(f'系统代理补丁失败，未保留部分改动：{error}', file=sys.stderr)
        return 1
    print('系统代理补丁：KDE/v2rayN Desktop Host（已应用或与现有补丁一致）')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1]))
