/** KDE/v2rayN integration. Loaded only by the Desktop Host, never by CLI/workers. */
import { execFile, spawn } from 'node:child_process';
import { watch } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';
import { promisify } from 'node:util';
const run = promisify(execFile);
export const KDE_SIGNAL = "type='signal',path='/KIO/Scheduler',interface='org.kde.KIO.Scheduler',member='reparseSlaveConfiguration'";
const proxyNames = ['http_proxy', 'https_proxy', 'all_proxy'];
export function shouldFollowKde(env, platform = process.platform, entry = process.argv[1] ?? '') {
  return platform === 'linux' && entry.endsWith('/dsh-desktop-host/lib/index.js') &&
    /kde|plasma/i.test(env.get('XDG_CURRENT_DESKTOP')?.value ?? '') &&
    env.get('DSH_DESKTOP_SYSTEM_PROXY')?.value !== '0' &&
    !proxyNames.some(name => [name, name.toUpperCase()].some(key => env.get(key)?.value?.trim()));
}
export async function readKdeProxy(env, execute = run) {
  const keys = ['ProxyType', 'httpProxy', 'httpsProxy', 'NoProxyFor', 'ReversedException', 'socksProxy'];
  const preferred = env.get('KDE_SESSION_VERSION')?.value === '5' ? ['kreadconfig5', 'kreadconfig6'] : ['kreadconfig6', 'kreadconfig5'];
  let values;
  for (const bin of preferred) {
    try {
      values = await Promise.all(keys.map(key => execute(bin, ['--file', 'kioslaverc', '--group', 'Proxy Settings', '--key', key],
        { timeout: 2000, maxBuffer: 64 * 1024, encoding: 'utf8', windowsHide: true }).then(result => result.stdout.trim())));
      break;
    } catch (error) { if (error.code !== 'ENOENT') throw Error('Cannot read KDE proxy settings'); }
  }
  if (!values) throw Error('KDE proxy reader is unavailable');
  const [mode, http, https, bypass, reversed, socks] = values;
  if (mode === '' || mode === '0') return {};
  if (mode !== '1') throw Error('KDE automatic/PAC proxy mode is not supported by this adapter');
  if (/^(true|1)$/i.test(reversed)) throw Error('KDE reversed proxy exceptions are not supported');
  if (!http && !https) throw Error(socks ? 'KDE SOCKS-only proxy is not supported' : 'KDE manual proxy has no HTTP endpoint');
  for (const value of [http, https].filter(Boolean)) {
    const url = URL.parse(value);
    if (!url || !['http:', 'https:'].includes(url.protocol) || url.pathname !== '/' || url.search || url.hash)
      throw Error('KDE HTTP proxy endpoint is invalid or unsupported');
  }
  // Upstream understands host/suffix/port exceptions. Add IPv4 CIDR in the controller;
  // refuse unsupported CIDR rather than silently sending bypass traffic to a proxy.
  for (const token of bypass.split(/[,\s]+/).filter(Boolean)) {
    if (token.includes('/') && !validIpv4Cidr(token))
      throw Error('KDE proxy contains an unsupported CIDR exception');
    if (/[<>;?\\]/.test(token) || (token.includes('*') && token !== '*' && !/^\*\.[^*]+$/.test(token)))
      throw Error('KDE proxy contains an unsupported exception syntax');
  }
  const inheritedBypass = ['no_proxy', 'NO_PROXY'].map(name => env.get(name)?.value?.trim()).find(Boolean) ?? '';
  return { ...(http ? { http_proxy: http } : {}), ...(https ? { https_proxy: https } : {}),
    no_proxy: [bypass, inheritedBypass].filter(Boolean).join(',') };
}
export function validIpv4Cidr(value) {
  const [ip, prefix, extra] = value.split('/');
  return extra === undefined && /^\d{1,2}$/.test(prefix ?? '') && +prefix <= 32 &&
    ip.split('.').length === 4 && ip.split('.').every(v => /^\d{1,3}$/.test(v) && +v <= 255);
}
/** Own only our monitor, watcher and timers. Never edit desktop settings or signal other apps. */
export async function monitorKdeProxy(env, apply, report, options = {}) {
  const read = options.read ?? (() => readKdeProxy(env));
  const config = env.get('XDG_CONFIG_HOME')?.value || join(homedir(), '.config');
  let stopped = false, revision = 0, timer, watcher, child, last, lastError;
  let queue = Promise.resolve();
  const refresh = async ticket => {
    try {
      const values = await read();
      if (stopped || ticket !== revision) return;
      const signature = JSON.stringify(values);
      if (signature !== last) { await apply(values); last = signature; }
      lastError = undefined;
    } catch (error) {
      if (!stopped && error.message !== lastError) { lastError = error.message; report(error.message); }
    }
  };
  const schedule = () => {
    if (stopped) return;
    const ticket = ++revision;
    clearTimeout(timer);
    timer = setTimeout(() => { queue = queue.then(() => refresh(ticket)); }, options.debounceMs ?? 200);
    timer.unref();
  };
  try {
    watcher = (options.watch ?? watch)(config, (event, name) => {
      if (name === null || String(name) === 'kioslaverc') schedule();
    });
    watcher.on('error', () => { watcher?.close(); watcher = undefined; });
    watcher.unref();
  } catch { /* Periodic read also handles a missing configuration directory. */ }
  try {
    child = (options.spawn ?? spawn)('dbus-monitor', ['--session', KDE_SIGNAL], { stdio: ['ignore', 'pipe', 'ignore'], windowsHide: true });
    let buffer = '';
    child.stdout.on('data', chunk => {
      buffer = (buffer + chunk.toString()).slice(-16384);
      const lines = buffer.split('\n'); buffer = lines.pop();
      if (lines.some(line => line.includes('member=reparseSlaveConfiguration'))) schedule();
    });
    child.on('error', () => {}); // File watch and periodic reads remain available.
  } catch { /* No new mandatory D-Bus package dependency. */ }
  const poll = setInterval(schedule, options.pollMs ?? 30000); poll.unref();
  queue = refresh(++revision);
  await queue;
  return async () => {
    stopped = true; ++revision; clearTimeout(timer); clearInterval(poll); watcher?.close();
    if (child && child.exitCode === null && !child.killed) child.kill('SIGTERM');
    await queue;
  };
}
