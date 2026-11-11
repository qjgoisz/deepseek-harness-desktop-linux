// Real payload functions, synthetic credentials and loopback HTTP/WebSocket only.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import http from 'node:http';
import * as crypto from 'node:crypto';
import { createRequire } from 'node:module';

const [mainPath, appPath] = process.argv.slice(2);
const main = fs.readFileSync(mainPath, 'utf8');
const connection = fs.readFileSync(`${appPath}/dsh/node_modules/@deepseek-ai/dsh-client-connection/lib/index.js`, 'utf8');
const require = createRequire(`${appPath}/package.json`);
const { WebSocket, WebSocketServer } = require('ws');
const authContext = { ...crypto, Buffer, URL, Headers, WeakMap, credentialKey: () => '' };
class Clock extends Date { static offset = 0; static now() { return Date.now() + this.offset; } }
authContext.Date = Clock;
vm.runInNewContext(connection.slice(connection.indexOf('const AUTH_RECORD_KEY ='), connection.indexOf('//#region lib/types/rpc.js')) + '\nthis.Auth = BrowserAuth;', authContext);
const newAuth = () => new authContext.Auth({}, crypto.randomBytes(32), 30);

let requests = [];
let mode = 'ok';
let expectedCookie;
const storedCookies = new Set(['unrelated']);
const cookieJar = {
  async get({ url }) {
    assert.equal(new URL(url).hostname, '127.0.0.1');
    return [...storedCookies].map(name => ({ name }));
  },
  async remove(url, name) {
    assert.equal(new URL(url).hostname, '127.0.0.1');
    storedCookies.delete(name);
  },
};
const context = vm.createContext({
  URL, Headers, AbortSignal, Buffer, setTimeout, clearTimeout, WebSocket,
  randomUUID: crypto.randomUUID,
  REMOTE_STREAM_MUX_PATH: '/api/remote.stream.mux',
  parseRemoteStreamServerMessage: JSON.parse,
  session: { defaultSession: { cookies: cookieJar } },
  net: { fetch() { throw Error('Electron cookie-jar fetch'); } },
  fetch: async (input, init) => {
    requests.push({ url: new URL(input), cookie: new Headers(init?.headers).get('cookie'), redirect: init?.redirect });
    return fetch(input, init);
  },
});
function between(source, start, end) {
  const from = source.indexOf(start);
  assert(from >= 0, `missing section ${start}`);
  const to = source.indexOf(end, from);
  assert(to > from, `missing section end ${end}`);
  return source.slice(from, to);
}
vm.runInContext(
  between(main, 'async function authenticateWebHost(', '/**\n* Response headers not relayed') +
  between(main, 'function accountView(', '//#region lib/types/update-journal.js'), context);
const boot = between(main, '\t\t\t\tconst ready = await host.start();', '\n\t\t\t\tanalyticsEnabled =');
vm.runInContext(`async function start(host) {
  let hostCookie, hostUrl, injections, welcomeBackend;
  ${boot}
  return { cookie: hostCookie, url: hostUrl, backend: welcomeBackend };
}`, context);

const fakeAccount = { status: 'signed-out', attempt: null, links: { usageUrl: 'https://example.invalid/usage', topUpUrl: 'https://example.invalid/top-up' } };
const servers = new Set();
const sockets = new Set();
async function host() {
  const auth = newAuth();
  let rootCalls = 0;
  const server = http.createServer(async (req, res) => {
    if (req.url.startsWith('/?') || req.url === '/') {
      rootCalls++;
      if (auth.authorizeIndex(req, res)) res.end('index');
      return;
    }
    if (!auth.isAuthenticated(req)) { res.writeHead(401); res.end(); return; }
    if (mode === 'redirect') { res.writeHead(302, { location: 'http://127.0.0.1:1/should-not-follow' }); res.end(); return; }
    if (mode === '431') { res.writeHead(431); res.end(); return; }
    let body = '';
    for await (const data of req) body += data;
    const frame = JSON.parse(body);
    const values = {
      'productAnalytics/enabled': false,
      'settings/describe': { namespaces: [{ ns: 'locale', value: {} }] },
      'llm/listConfigurableProviders': [],
      'account/getState': fakeAccount,
    };
    res.setHeader('content-type', 'application/json');
    res.end(JSON.stringify({ type: 'server-response', rpcId: frame.rpcId, result: { ok: true, value: values[frame.method] ?? null } }));
  });
  const wss = new WebSocketServer({ noServer: true });
  server.on('upgrade', (req, socket, head) => {
    if (!auth.isAuthenticated(req) || req.headers.cookie !== expectedCookie) {
      socket.end('HTTP/1.1 401 Unauthorized\r\nConnection: close\r\n\r\n'); return;
    }
    wss.handleUpgrade(req, socket, head, ws => {
      sockets.add(ws);
      ws.on('close', () => sockets.delete(ws));
      ws.on('message', raw => {
        const message = JSON.parse(raw.toString());
        if (message.endpoint === 'account/watch') {
          const value = { type: 'snapshot', state: fakeAccount };
          ws.send(JSON.stringify({ type: 'item', streamId: message.streamId, value }));
        }
      });
    });
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  servers.add(server);
  const url = auth.authenticatedUrl(`http://127.0.0.1:${server.address().port}/`);
  return { auth, url, server, wss, get rootCalls() { return rootCalls; }, async stop() {
    wss.close(); server.closeAllConnections();
    await new Promise(resolve => server.close(resolve)); servers.delete(server);
  } };
}
async function watch(backend) {
  let stop;
  try {
    const state = await new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(Error('account WebSocket did not connect')), 2000);
      stop = backend.account.watch(value => { clearTimeout(timeout); resolve(value); }, () => {}, () => {});
    });
    assert.equal(state.status, 'signed-out');
  } finally { stop?.(); }
}

try {
  // Reproduce the unpatched overflow without using any user's cookie values.
  const old = await host();
  const stale = Array.from({ length: 100 }, (_, i) => {
    let cookie;
    const url = new URL(old.url);
    old.auth.authorizeIndex({ method: 'GET', url: url.pathname + url.search, headers: { host: `127.0.0.1:${20000 + i}` } }, {
      writeHead(status, headers) { cookie = headers['set-cookie'].split(';')[0]; }, end() {},
    });
    return cookie;
  });
  assert(new Set(stale.map(value => value.split('=')[0])).size === 100);
  for (const value of stale) storedCookies.add(value.split('=')[0]);
  const before = old.rootCalls;
  const crowded = await fetch(old.url, { redirect: 'manual', headers: { Cookie: stale.join('; ') } });
  assert.equal(crowded.status, 431); await crowded.body?.cancel();
  assert.equal(old.rootCalls, before, 'parser rejects request before authentication');

  const first = await context.start({ start: async () => ({ url: old.url, injections: [] }) });
  expectedCookie = first.cookie;
  assert.equal(old.rootCalls, 1, 'launch token is exchanged once without Chromium redirect/cookie storage');
  assert.equal(await first.backend.analyticsEnabled(), false);
  assert.equal((await first.backend.read()).loggedIn, false);
  await watch(first.backend);
  assert.deepEqual([...storedCookies], ['unrelated']);
  // Each Host uses its own cookie, and RPC rejects redirects.
  const other = await host();
  const second = await context.start({ start: async () => ({ url: other.url, injections: [] }) });
  assert.equal(await second.backend.analyticsEnabled(), false);
  assert.equal(await first.backend.analyticsEnabled(), false, 'a new backend must not replace the old adapter cookie');
  await watch(first.backend);
  const mismatch = await fetch(new URL('/', other.url), { headers: { cookie: first.cookie } });
  assert.equal(mismatch.status, 401); await mismatch.body?.cancel();
  assert.equal(old.auth.isAuthenticated({ headers: { host: new URL(old.url).host, cookie: first.cookie } }, true), false);
  const tampered = await fetch(new URL('/', old.url), { headers: { cookie: first.cookie + 'tampered' } });
  assert.equal(tampered.status, 401); await tampered.body?.cancel();
  Clock.offset = 31 * 86400000;
  assert.equal(old.auth.isAuthenticated({ headers: { host: new URL(old.url).host, cookie: first.cookie } }), false);
  Clock.offset = 0;
  mode = 'redirect'; await assert.rejects(first.backend.analyticsEnabled(), /fetch failed/);
  mode = '431'; await assert.rejects(first.backend.analyticsEnabled(), /Web request failed/);
  mode = 'ok';
  const firstHostRequests = requests.filter(r => r.url.origin === new URL(old.url).origin && r.url.pathname.startsWith('/api/'));
  assert(firstHostRequests.length > 0);
  assert(firstHostRequests.every(r => r.cookie === first.cookie && r.redirect === 'error'));
  await other.stop(); await old.stop();

  // New port and signing secret each time; old adapters keep their captured cookie.
  for (let i = 0; i < 100; i++) {
    const next = await host();
    const result = await context.start({ start: async () => ({ url: next.url, injections: [] }) });
    expectedCookie = result.cookie;
    assert.equal(await result.backend.analyticsEnabled(), false);
    assert.equal(next.rootCalls, 1);
    assert.equal(result.cookie.split(';').length, 1);
    if (i === 99) await watch(result.backend);
    await next.stop();
  }
  context.fetch = async () => new Response('', { status: 431 });
  await assert.rejects(context.authenticateWebHost('http://127.0.0.1/'), /Desktop Host authentication failed/);
  context.fetch = async () => new Response('', { status: 303 });
  await assert.rejects(context.authenticateWebHost('http://127.0.0.1/'), /Desktop Host authentication failed/);
  console.log('Desktop auth: HTTP, WebSocket, 100 starts, isolation, expiry and redirects passed');
} finally {
  for (const socket of sockets) socket.terminate();
  for (const server of servers) { server.closeAllConnections(); server.close(); }
}
