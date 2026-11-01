#!/usr/bin/env python3
"""Apply Linux titlebar intermediates once; reject partial or unknown layouts."""
from pathlib import Path
import os
import re
import sys
import tempfile

WINDOWS = (
    (
        '\t\t...process.platform === "win32" && primary ? {\n'
        '\t\t\ttitleBarStyle: "hidden",\n'
        '\t\t\ttitleBarOverlay: {\n'
        '\t\t\t\theight: 40,\n'
        '\t\t\t\tcolor: chromeFallbackFill(),\n'
        '\t\t\t\tsymbolColor: nativeTheme.shouldUseDarkColors ? "#f9fafb" : "#0f1115"\n'
        '\t\t\t}\n'
        '\t\t} : {},'
    ),
    (
        '\t\t...platform === "win32" ? {\n'
        '\t\t\ttitleBarStyle: "hidden",\n'
        '\t\t\ttitleBarOverlay: {\n'
        '\t\t\t\tcolor: "#00000000",\n'
        '\t\t\t\tsymbolColor: "#0F1115",\n'
        '\t\t\t\theight: 42\n'
        '\t\t\t},\n'
        '\t\t\tbackgroundMaterial: "acrylic"\n'
        '\t\t} : {},'
    ),
)
OVERLAY = (
    (
        '\t\t...process.platform === "linux" && primary ? {\n'
        '\t\t\ttitleBarStyle: "hidden",\n'
        '\t\t\ttitleBarOverlay: {\n'
        '\t\t\t\theight: 40,\n'
        '\t\t\t\tsymbolColor: nativeTheme.shouldUseDarkColors ? "#f9fafb" : "#0f1115"\n'
        '\t\t\t}\n'
        '\t\t} : {},'
    ),
    (
        '\t\t...platform === "linux" ? {\n'
        '\t\t\ttitleBarStyle: "hidden",\n'
        '\t\t\ttitleBarOverlay: {\n'
        '\t\t\t\theight: 42,\n'
        '\t\t\t\tsymbolColor: nativeTheme.shouldUseDarkColors ? "#f9fafb" : "#0f1115"\n'
        '\t\t\t}\n'
        '\t\t} : {},'
    ),
)
CHROME = (
    (
        '\t\t...process.platform === "linux" && primary ? {\n'
        '\t\t\ttitleBarStyle: "hidden",\n'
        '\t\t\ttransparent: true,\n'
        '\t\t\tbackgroundColor: "#00000000",\n'
        '\t\t\thasShadow: true\n'
        '\t\t} : {},'
    ),
    (
        '\t\t...platform === "linux" ? {\n'
        '\t\t\ttitleBarStyle: "hidden",\n'
        '\t\t\tframe: false,\n'
        '\t\t\ttransparent: true\n'
        '\t\t} : {},'
    ),
)


def transform(source):
    # Catch altered whitespace/quotes and extra Linux spreads too, rather than
    # mistake an unfamiliar existing branch for an untouched upstream file.
    linux_spreads = re.findall(r"\.\.\.\s*(?:process\.)?platform\s*===\s*[\"']linux[\"']", source)
    if len(linux_spreads) != sum(source.count(block.split(' {', 1)[0] + ' {') for block in OVERLAY):
        raise ValueError('Unknown Linux titlebar condition')
    states = []
    for windows, overlay, chrome in zip(WINDOWS, OVERLAY, CHROME):
        if source.count(windows) != 1:
            raise ValueError('Unknown or duplicate Windows titlebar anchor')
        prefix = overlay.split(' {', 1)[0] + ' {'
        branches = re.findall(re.escape(prefix) + r'.*?\t\t} : {},', source, re.S)
        if source.count(prefix) != len(branches) or len(branches) > 1:
            raise ValueError('Incomplete or duplicate Linux titlebar branch')
        if not branches:
            states.append('original')
        elif branches[0] == overlay and windows + '\n' + overlay in source:
            states.append('overlay')
        elif branches[0] == chrome and windows + '\n' + chrome in source:
            states.append('chrome')
        else:
            raise ValueError('Unknown Linux titlebar layout')
    if len(set(states)) != 1:
        raise ValueError('Partially patched titlebar windows')
    if states[0] != 'original':
        return source
    for windows, overlay in zip(WINDOWS, OVERLAY):
        source = source.replace(windows, windows + '\n' + overlay)
    return source


def main():
    path = Path(sys.argv[1])
    source = path.read_text(encoding='utf-8')
    updated = transform(source)
    if updated == source:
        print('Linux titlebar already applied (overlay/chrome)')
        return
    fd, temporary = tempfile.mkstemp(prefix='.titlebar-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(updated)
        os.chmod(temporary, path.stat().st_mode & 0o777)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('Linux titlebar applied to both windows')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        raise SystemExit(f'Titlebar patch refused without writing: {error}')
