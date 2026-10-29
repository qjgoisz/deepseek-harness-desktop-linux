#!/usr/bin/env python3
"""Expose per-server MCP negotiation and supervised optional background startup."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

MARKER = '// dsh-linux-mcp-negotiation:v2'
V1_MARKER = '// dsh-linux-mcp-negotiation:v1'
CLIENT = 'versionNegotiation: { mode: "auto" },'
NEW_CLIENT = 'versionNegotiation: { mode: config.versionNegotiation ?? "auto" },'
FIELD = '\tserverName: z.string().required().pattern(SERVER_NAME_PATTERN),'
V1_FIELD = FIELD + '\n\tversionNegotiation: z.union([z.const("auto"), z.const("legacy")]).default("auto"),'
NEW_FIELD = V1_FIELD + '\n\tstartupMode: z.union([z.const("blocking"), z.const("background")]).default("blocking"),'
APPLY = 'async function apply(ctx, config) {'
V1_APPLY = APPLY + '\n\tif (!["auto", "legacy"].includes(config.versionNegotiation ?? "auto")) throw new TypeError("mcp-client: invalid versionNegotiation");'
NEW_APPLY = V1_APPLY + '\n\tif (!["blocking", "background"].includes(config.startupMode ?? "blocking")) throw new TypeError("mcp-client: invalid startupMode");'
AWAIT = '\tconst outcome = await connection.ready;'
NEW_AWAIT = '''\t// The connection owns tool synchronization, retries and disposal in either mode.
\t// Register all teardown hooks before releasing the loader's startup barrier.
\tif (config.startupMode === "background" && !config.failOnStartupError) {
\t\tctx.logger.info(`mcp-client(${config.serverName}): connecting in background; tools will appear after synchronization`);
\t\tvoid connection.ready.then((outcome) => {
\t\t\tif (stopping) return;
\t\t\tif (outcome.error !== void 0) ctx.logger.warn(`mcp-client(${config.serverName}): background initialization failed; see connection diagnostics and reconnect policy`);
\t\t\telse ctx.logger.info(`mcp-client(${config.serverName}): background initialization complete`);
\t\t}).catch(() => {
\t\t\tif (!stopping) ctx.logger.error(`mcp-client(${config.serverName}): background initialization rejected; reload the plugin or restart the Host to retry`);
\t\t});
\t\treturn;
\t}
''' + AWAIT

V1_REPLACEMENTS = [(CLIENT, NEW_CLIENT, 1), (FIELD, V1_FIELD, 2), (APPLY, V1_APPLY, 1)]
REPLACEMENTS = [(CLIENT, NEW_CLIENT, 1), (FIELD, NEW_FIELD, 2), (APPLY, NEW_APPLY, 1), (AWAIT, NEW_AWAIT, 1)]


def unpatch(source, marker, replacements):
    original = source[len(marker) + 1:]
    for old, new, count in replacements:
        if original.count(new) != count:
            raise ValueError('Unknown or incomplete existing MCP startup patch')
        original = original.replace(new, old)
    return original


def transform(source):
    if source.startswith(MARKER + '\n'):
        original = unpatch(source, MARKER, REPLACEMENTS)
        if transform(original) != source:
            raise ValueError('Incomplete existing negotiation patch')
        return source
    if source.startswith(V1_MARKER + '\n'):
        source = unpatch(source, V1_MARKER, V1_REPLACEMENTS)
    if 'dsh-linux-mcp-negotiation:' in source or 'config.versionNegotiation' in source or 'config.startupMode' in source:
        raise ValueError('Unknown MCP startup implementation')
    for old, new, count in REPLACEMENTS:
        if source.count(old) != count:
            raise ValueError(f'Expected {count} matches for {old}')
        source = source.replace(old, new)
    return MARKER + '\n' + source


def main(app):
    target = Path(app)/'dsh/node_modules/@deepseek-ai/dsh-mcp-client/lib/index.js'
    original = target.read_text()
    updated = transform(original)
    if updated == original:
        print('MCP startup patch already applied')
        return
    fd, temporary = tempfile.mkstemp(prefix='.mcp-negotiation-', suffix='.mjs', dir=target.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(updated)
        subprocess.run(['node', '--check', temporary], check=True, capture_output=True)
        os.chmod(temporary, target.stat().st_mode & 0o777)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('MCP startup patch: auto/legacy; blocking/background (defaults auto/blocking; strict services always wait)')


if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f'MCP patch refused without writing: {error}')
