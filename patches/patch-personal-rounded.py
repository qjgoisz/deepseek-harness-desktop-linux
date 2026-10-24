#!/usr/bin/env python3
"""Personal solid rounded windows with persistent fullscreen controls."""
from pathlib import Path
import sys

LEGACY_MEASUREMENT = '''\t\t\t\tconst toggleLeft = `${Math.max(88, width - 40)}px`;
\t\t\t\tif (root.style.getPropertyValue("--dsh-linux-toggle-left") !== toggleLeft) {
\t\t\t\t\troot.style.setProperty("--dsh-linux-sidebar-width", `${width}px`);
\t\t\t\t\troot.style.setProperty("--dsh-linux-toggle-left", toggleLeft);
\t\t\t\t}'''

MEASUREMENT = '''\t\t\t\t// Track the actual strip width even after the button position clamps.
\t\t\t\tconst sidebarWidth = `${width}px`;
\t\t\t\tif (root.style.getPropertyValue("--dsh-linux-sidebar-width") !== sidebarWidth) {
\t\t\t\t\troot.style.setProperty("--dsh-linux-sidebar-width", sidebarWidth);
\t\t\t\t}
\t\t\t\tconst toggleLeft = `${Math.max(88, width - 40)}px`;
\t\t\t\tif (root.style.getPropertyValue("--dsh-linux-toggle-left") !== toggleLeft) {
\t\t\t\t\troot.style.setProperty("--dsh-linux-toggle-left", toggleLeft);
\t\t\t\t}'''

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

PERSISTENT_CSS = LEGACY_CSS.replace('dsh-personal-rounded:v1', 'dsh-personal-rounded:v2') + '''
/* Personal controls stay visible and clickable, regardless of hover or focus.
   Keep the native state/pointer bridge for Wayland titlebar double-clicks. */
html[data-dsh-mac-chrome][data-fullscreen] #dsh-mac-lights {
    display: flex !important; opacity: 1 !important; visibility: visible !important;
    pointer-events: auto !important; transition: none !important;
}
html[data-dsh-mac-chrome][data-fullscreen] #dsh-fullscreen-reveal { display: none !important; }
'''

PREVIOUS_CSS = PERSISTENT_CSS + '''/* Reserve the same room as the revealed toolbar, without hover animation.
   Scope the toggle to the sidebar so plugin panel controls stay in place. */
html[data-dsh-mac-chrome][data-fullscreen] [class*="_sidebarCol"] button[class*="_toggle"],
html[data-dsh-mac-chrome][data-fullscreen] [class*="_collapsed"] button[class*="_newSession"] {
    translate: 76px 0 !important; transition: none !important;
}
'''

CSS = PERSISTENT_CSS.replace('dsh-personal-rounded:v2', 'dsh-personal-rounded:v3') + '''
/* Use ordinary-window positions in every native window state. The state
   selector keeps these rules as specific as the legacy fullscreen overrides. */
html[data-dsh-mac-chrome]:is([data-fullscreen], :not([data-fullscreen])) [class*="_sidebarCol"] button[class*="_toggle"] {
    left: var(--dsh-linux-toggle-left, 240px) !important; right: auto !important;
    translate: none !important; transition: none !important;
}
html[data-dsh-mac-chrome]:is([data-fullscreen], :not([data-fullscreen])) [class*="_sidebarCol"] [class*="_collapsed"] button[class*="_toggle"] {
    left: 128px !important;
}
html[data-dsh-mac-chrome]:is([data-fullscreen], :not([data-fullscreen])) [class*="_sidebarCol"] [class*="_collapsed"] button[class*="_newSession"] {
    left: 88px !important; translate: none !important; transition: none !important;
}
'''

def transform_preload(src):
    # The old shared guard left a 0..128px strip behind during collapse because
    # toggleLeft had already reached its 88px minimum. Upgrade existing v3 trees
    # too, keeping this correction in the personal layer.
    if src.count(LEGACY_MEASUREMENT) == 1 and MEASUREMENT not in src:
        src = src.replace(LEGACY_MEASUREMENT, MEASUREMENT, 1)
    elif src.count(MEASUREMENT) != 1 or LEGACY_MEASUREMENT in src:
        raise ValueError('Unknown or duplicate sidebar measurement')
    if '/* dsh-personal-rounded:v3 */' in src:
        if src.count(CSS) != 1 or src.count('/* dsh-personal-rounded:') != 1:
            raise ValueError('Unknown or duplicate personal window styles')
        return src
    for version, previous in ((1, LEGACY_CSS), (2, PREVIOUS_CSS)):
        if f'/* dsh-personal-rounded:v{version} */' in src:
            if src.count(previous) != 1 or src.count('/* dsh-personal-rounded:') != 1:
                raise ValueError('Unknown or duplicate previous personal window styles')
            return src.replace(previous, CSS, 1)
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
