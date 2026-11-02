#!/usr/bin/env python3
"""Keep Desktop Host authentication in memory instead of Chromium's cookie jar."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

MARKER = '// dsh-desktop-auth-cookie:v1'
TARGET = 'lib/main.js'
AUTH_ERROR = '\tif (response.status !== 303 || cookie === null) throw new Error("Desktop Host authentication failed");'
NEW_AUTH_ERROR = '\tif (response.status !== 303 || cookie === null) throw new Error(`Desktop Host authentication failed (HTTP ${String(response.status)}${cookie === null ? "; missing session cookie" : ""})`);'
HELPER_ANCHOR = '''/**
* Response headers not relayed to the renderer. `set-cookie` would hand the'''
HELPER = '''/** Bind native HTTP requests to one owned Host without a persistent cookie jar. */
function createDesktopHostFetch(hostUrl, cookie) {
	const origin = new URL(hostUrl).origin;
	return (input, init = {}) => {
		const target = new URL(input);
		if (target.origin !== origin || target.username !== "" || target.password !== "") throw new Error("desktop welcome: rejected request outside the owned Host");
		const headers = new Headers(init.headers);
		headers.set("cookie", cookie);
		return fetch(target.href, {
			...init,
			headers,
			credentials: "omit",
			redirect: "error"
		});
	};
}
'''
WELCOME = '''/**
* Authenticate the native HTTP client through the Web application's launch URL.
* @param authenticatedUrl - URL supplied by the running Desktop Host.
* @param send - Electron session fetch, retaining the Web authentication cookie.
* @returns metadata reads and write-only credential operations over standard RPC.
*/
async function connectDesktopWelcome(authenticatedUrl, send, cookies = () => Promise.resolve("")) {
	const origin = new URL(authenticatedUrl).origin;
	const authenticated = await send(authenticatedUrl, { credentials: "include" });
	await authenticated.body?.cancel();
	if (!authenticated.ok) throw new Error("desktop welcome: Web authentication failed");'''
NEW_WELCOME = '''/**
* Connect native operations using the Host cookie already exchanged by the shell.
* @param hostUrl - URL supplied by the running Desktop Host.
* @param send - Origin-bound fetch carrying only that Host's in-memory cookie.
* @returns metadata reads and write-only credential operations over standard RPC.
*/
async function connectDesktopWelcome(hostUrl, send, cookies) {
	const origin = new URL(hostUrl).origin;'''
RPC = '''			method: "POST",
			credentials: "include",
			redirect: "error",'''
NEW_RPC = RPC.replace('"include"', '"omit"')
RPC_ERROR = '\t\tif (!response.ok) throw new Error("desktop welcome: Web request failed");'
NEW_RPC_ERROR = '\t\tif (!response.ok) throw new Error(`desktop welcome: Web request failed (HTTP ${String(response.status)})`);'
START = '''				const ready = await host.start();
				hostCookie = await authenticateWebHost(ready.url);
				hostUrl = ready.url;
				if (ready.injections === void 0) throw new Error("Desktop Host did not provide boot injections");
				injections = ready.injections;
				welcomeBackend = await connectDesktopWelcome(ready.url, (input, init) => net.fetch(input, init), async () => (await session.defaultSession.cookies.get({ url: ready.url })).map((cookie) => `${cookie.name}=${cookie.value}`).join("; "));'''
NEW_START = '''				const ready = await host.start();
				const currentHostCookie = await authenticateWebHost(ready.url);
				hostCookie = currentHostCookie;
				hostUrl = ready.url;
				if (ready.injections === void 0) throw new Error("Desktop Host did not provide boot injections");
				injections = ready.injections;
				welcomeBackend = await connectDesktopWelcome(ready.url, createDesktopHostFetch(ready.url, currentHostCookie), async () => currentHostCookie);'''
ACCOUNT_COMMENT = '* @param cookies - Electron session cookie reader.'
NEW_ACCOUNT_COMMENT = '* @param cookies - Reader for the owned Host\'s in-memory authentication cookie.'
REPLACEMENTS = (
    (AUTH_ERROR, NEW_AUTH_ERROR),
    (HELPER_ANCHOR, HELPER + HELPER_ANCHOR),
    (WELCOME, NEW_WELCOME),
    (RPC, NEW_RPC),
    (RPC_ERROR, NEW_RPC_ERROR),
    (START, NEW_START),
    (ACCOUNT_COMMENT, NEW_ACCOUNT_COMMENT),
)


def transform(source):
    if source.startswith(MARKER + '\n'):
        original = source[len(MARKER) + 1:]
        # Undo in reverse order: the helper replacement includes its old anchor.
        for old, new in reversed(REPLACEMENTS):
            if original.count(new) != 1:
                raise ValueError('Unknown or incomplete Desktop auth cookie patch')
            original = original.replace(new, old)
        if transform(original) != source:
            raise ValueError('Unknown Desktop auth cookie patch layout')
        return source
    if 'dsh-desktop-auth-cookie:' in source or 'createDesktopHostFetch' in source or 'currentHostCookie' in source:
        raise ValueError('Unknown existing Desktop auth cookie implementation')
    for old, new in REPLACEMENTS:
        if source.count(old) != 1:
            raise ValueError('Expected one known Desktop auth cookie anchor')
    # Do not accept an additional cookie-jar connection outside the known call site.
    if source.count('connectDesktopWelcome(') != 2:
        raise ValueError('Unexpected Desktop welcome caller')
    for old, new in REPLACEMENTS:
        source = source.replace(old, new)
    return MARKER + '\n' + source


def main(app):
    target = Path(app) / TARGET
    original = target.read_text()
    updated = transform(original)
    if updated == original:
        return
    fd, temporary = tempfile.mkstemp(prefix='.desktop-auth-cookie-', suffix='.mjs', dir=target.parent)
    try:
        with os.fdopen(fd, 'w') as handle:
            handle.write(updated)
        subprocess.run(['node', '--check', temporary], check=True, capture_output=True)
        os.chmod(temporary, target.stat().st_mode & 0o777)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('Desktop Host authentication: use one in-memory cookie for HTTP and WebSocket')


if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f'Desktop auth cookie patch refused without writing: {error}')
