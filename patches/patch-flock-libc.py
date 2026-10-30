#!/usr/bin/env python3
"""Keep lazy libc detection from collecting synchronous network diagnostics."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

MARKER = '// dsh-linux-flock-libc:v1'
OLD = '        const report = process.report.getReport();'
NEW = '''        // Only the libc header is needed; reverse DNS can block the Host.
        const diagnostic = process.report;
        if (typeof diagnostic.excludeNetwork !== 'boolean')
            throw new Error('flock libc detection requires report.excludeNetwork support');
        const previousExcludeNetwork = diagnostic.excludeNetwork;
        let report;
        try {
            diagnostic.excludeNetwork = true;
            report = diagnostic.getReport();
        } finally {
            diagnostic.excludeNetwork = previousExcludeNetwork;
        }'''
TARGET = 'dsh/node_modules/@deepseek-ai/node-addon-system/lib/flock.js'


def transform(source):
    if source.startswith(MARKER + '\n'):
        original = source[len(MARKER)+1:]
        if original.count(NEW) != 1:
            raise ValueError('Unknown or incomplete flock libc patch')
        original = original.replace(NEW, OLD)
        if transform(original) != source:
            raise ValueError('Unknown flock libc patch layout')
        return source
    if 'dsh-linux-flock-libc:' in source or 'excludeNetwork' in source:
        raise ValueError('Unknown existing libc implementation')
    if source.count(OLD) != 1 or source.count('process.report.getReport()') != 1:
        raise ValueError('Expected one known libc diagnostic call')
    return MARKER + '\n' + source.replace(OLD, NEW)


def main(app):
    target = Path(app)/TARGET
    original = target.read_text()
    updated = transform(original)
    if updated == original:
        return
    fd, temporary = tempfile.mkstemp(prefix='.flock-libc-', suffix='.mjs', dir=target.parent)
    try:
        with os.fdopen(fd, 'w') as handle:
            handle.write(updated)
        subprocess.run(['node', '--check', temporary], check=True, capture_output=True)
        os.chmod(temporary, target.stat().st_mode & 0o777)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('Flock libc detection: exclude network diagnostics, restore prior setting')


if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f'Flock libc patch refused without writing: {error}')
