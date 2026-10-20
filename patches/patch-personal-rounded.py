#!/usr/bin/env python3
"""Personal solid rounded windows with persistent fullscreen controls."""
from pathlib import Path
import sys

LEGACY_CSS = '''
/* dsh-personal-rounded:v1 */
html[data-dsh-mac-chrome] {
    background: linear-gradient(transparent, transparent) !important;
}
html[data-dsh-mac-chrome] body {
    background: rgb(from var(--dsw-alias-bg-base, #202020) r g b / 1) !important;
    clip-path: inset(0 round 12px);
}
html[data-dsh-mac-chrome][data-fullscreen] body { clip-path: none; }
'''

CSS = LEGACY_CSS.replace('dsh-personal-rounded:v1', 'dsh-personal-rounded:v2') + '''
/* Personal controls stay visible and clickable, regardless of hover or focus.
   Keep the native state/pointer bridge for Wayland titlebar double-clicks. */
html[data-dsh-mac-chrome][data-fullscreen] #dsh-mac-lights {
    display: flex !important; opacity: 1 !important; visibility: visible !important;
    pointer-events: auto !important; transition: none !important;
}
html[data-dsh-mac-chrome][data-fullscreen] #dsh-fullscreen-reveal { display: none !important; }
/* Reserve the same room as the revealed toolbar, without hover animation.
   Scope the toggle to the sidebar so plugin panel controls stay in place. */
html[data-dsh-mac-chrome][data-fullscreen] [class*="_sidebarCol"] button[class*="_toggle"],
html[data-dsh-mac-chrome][data-fullscreen] [class*="_collapsed"] button[class*="_newSession"] {
    translate: 76px 0 !important; transition: none !important;
}
'''

def transform_preload(src):
    if '/* dsh-personal-rounded:v2 */' in src:
        if src.count(CSS) != 1:
            raise ValueError('Unknown or duplicate personal window styles')
        return src
    if '/* dsh-personal-rounded:v1 */' in src:
        if src.count(LEGACY_CSS) != 1:
            raise ValueError('Unknown or duplicate previous personal window styles')
        return src.replace(LEGACY_CSS, CSS, 1)
    anchor = '\tconst CSS = `'
    policy = 'if (kdeSession && !kdeBlurReady) root.dataset.dshOpaqueSidebar = "";'
    if src.count(anchor) != 1 or src.count(policy) != 1:
        raise ValueError('Unknown chrome preload; refusing partial personal patch')
    # Force solid on every Linux desktop, including first-run welcome pages.
    src = src.replace(policy, 'if (process.platform === "linux") root.dataset.dshOpaqueSidebar = "";', 1)
    end = src.index('`;', src.index(anchor))
    return src[:end] + CSS + src[end:]

def transform_main(src):
    if '// dsh-personal-solid:v1' in src:
        return src
    anchor = '\tconst configureKdeBlur = (window) => {'
    if src.count(anchor) != 1:
        raise ValueError('Unknown KDE material handler')
    return src.replace(anchor, anchor + '\n\t\t// dsh-personal-solid:v1\n\t\treturn Promise.resolve(false);', 1)

def main(app_dir):
    root = Path(app_dir) / 'lib'
    pending = {root/'main.js': transform_main((root/'main.js').read_text())}
    for name in ('preload-app.cjs', 'preload-welcome.cjs'):
        path = root / name
        pending[path] = transform_preload(path.read_text())
    for path, text in pending.items():
        if path.read_text() != text:
            path.write_text(text)
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1]))
