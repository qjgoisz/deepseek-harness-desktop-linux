#!/usr/bin/env python3
"""Opt-in local repair of dsh-usage 0.4.4, independent of Desktop packaging."""
import argparse
import difflib
from pathlib import Path
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
MARKER = '// dsh-usage-settings-navigation:v1'


def patched(source):
    if MARKER in source:
        return source
    anchor = '\t\tfunction openUsageSettings(label) {'
    if source.count(anchor) != 1:
        raise ValueError('Expected exactly one openUsageSettings function; inspect the new plugin version first')
    start = source.index(anchor)
    end = source.index('\n\t\t/**\n\t\t* Mount the sidebar foot card', start)
    old = source[start:end]
    if '[class*=\\"settingsArea\\"] button' not in old or 'tries <= 20' not in old:
        raise ValueError('Unknown navigation implementation; refusing to replace it')
    replacement = '\n'.join('\t\t' + line for line in (BASE / 'open-usage-settings.js').read_text().rstrip().splitlines())
    return source[:start] + replacement + source[end:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=Path, default=Path.home() / '.dsh/profiles/desktop')
    parser.add_argument('--apply', action='store_true', help='write the tested patch, with original-file backups')
    args = parser.parse_args()
    targets = [args.profile / 'node_modules/@linxin666' / name / 'lib/client.js'
               for name in ('dsh-usage', 'dsh-web-all')]
    changes = []
    for target in targets:
        if not target.exists():
            continue
        source = target.read_text()
        updated = patched(source)
        if updated == source:
            print('Already patched:', target)
            continue
        with tempfile.NamedTemporaryFile(suffix='.cjs', mode='w') as tmp:
            tmp.write(updated)
            tmp.flush()
            subprocess.run(['node', '--check', tmp.name], check=True)
        changes.append((target, source, updated))
    if not changes:
        print('No files need changes')
        return
    # Validate every target before touching either installed bundle.
    for target, source, updated in changes:
        backup = target.with_name('client.js.before-usage-settings-fix')
        if args.apply:
            if backup.exists():
                raise RuntimeError(f'Backup already exists: {backup}; inspect before applying')
    for target, source, updated in changes:
        if args.apply:
            backup = target.with_name('client.js.before-usage-settings-fix')
            backup.write_text(source)
            target.write_text(updated)
            print('Patched:', target, '\nBackup:', backup)
        else:
            print(''.join(difflib.unified_diff(source.splitlines(True), updated.splitlines(True),
                                            fromfile=str(target), tofile=str(target) + ' (fixed)')))


if __name__ == '__main__':
    main()
