/* dsh-linux-system-proxy-v1: appended inside dsh-http-proxy's own module scope. */
function desktopIpv4Bypass(noProxy, url) {
  const toNumber = ip => {
    const parts = ip.split('.');
    if (parts.length !== 4 || parts.some(p => !/^\d{1,3}$/.test(p) || +p > 255)) return;
    return parts.reduce((n, p) => n * 256 + +p, 0) >>> 0;
  };
  const ip = toNumber(url.hostname);
  if (ip === undefined) return false;
  return noProxy.split(/[,\s]+/).some(entry => {
    const match = /^(\d+(?:\.\d+){3})\/(\d{1,2})$/.exec(entry);
    if (!match || +match[2] > 32) return false;
    const network = toNumber(match[1]);
    const mask = +match[2] === 0 ? 0 : (0xffffffff << (32 - +match[2])) >>> 0;
    return network !== undefined && ((ip & mask) >>> 0) === ((network & mask) >>> 0);
  });
}
/** A single owner replaces dispatchers atomically; retired streams drain without blocking updates. */
async function createDesktopProxyController(report) {
  const undici = await import('undici');
  const previous = { dispatcher: undici.getGlobalDispatcher(), active, installed, inheritedProxyEnv, env: snapshotProxyEnv() };
  let current, disposed = false;
  const retired = new Map();
  const retire = agent => {
    if (!agent) return;
    const closing = Promise.resolve().then(() => agent.close()).catch(() => report('Retired proxy connections could not close cleanly'));
    retired.set(agent, closing);
    closing.finally(() => retired.delete(agent));
  };
  return {
    async update(values) {
      if (disposed) return;
      const env = { get: name => values[name] === undefined ? undefined : { value: values[name] } };
      const { policy, diagnostics } = resolveProxyPolicy(env);
      for (const diagnostic of diagnostics) report(diagnostic.message);
      // Mark only system policies: CLI/environment-only NO_PROXY semantics stay unchanged.
      const nextPolicy = { ...policy, desktopSystem: true };
      const agent = policy.source === 'none' ? new undici.Agent() : await createPolicyDispatcher(nextPolicy);
      if (disposed) { await agent.close(); return; }
      const old = current;
      undici.setGlobalDispatcher(agent);
      active = nextPolicy; installed = policy.source === 'none' ? undefined : agent;
      inheritedProxyEnv = Object.fromEntries(Object.values(POLICY_ENV_NAMES).flat().map(name => [name, values[name]]));
      writeProxyEnv(Object.fromEntries(Object.entries(POLICY_ENV_NAMES).flatMap(([field, names]) => names.map(name => [name, policy[field] || undefined]))));
      current = agent;
      retire(old);
    },
    async dispose() {
      if (disposed) return;
      disposed = true;
      undici.setGlobalDispatcher(previous.dispatcher);
      active = previous.active; installed = previous.installed; inheritedProxyEnv = previous.inheritedProxyEnv;
      writeProxyEnv(previous.env);
      retire(current);
      // Shutdown only: bound retirement after the Host has already disposed its tasks.
      const agents = [...retired.keys()];
      let timer;
      await Promise.race([Promise.all([...retired.values()]), new Promise(resolve => {
        timer = setTimeout(() => { for (const agent of agents) agent.destroy().catch(() => {}); resolve(); }, 5000);
        timer.unref();
      })]);
      clearTimeout(timer);
    }
  };
}
async function installDesktopProxyFromEnvironment(env, report) {
  // Keep the pure policy module browser-loadable and leave CLI/worker launches on upstream behavior.
  if (process.platform !== 'linux' || !(process.argv[1] ?? '').endsWith('/dsh-desktop-host/lib/index.js'))
    return installProxyFromEnvironment(env, report);
  const { shouldFollowKde, monitorKdeProxy } = await import('./desktop-system-proxy.mjs');
  if (!shouldFollowKde(env)) return installProxyFromEnvironment(env, report);
  const controller = await createDesktopProxyController(report);
  await controller.update({});
  let stop;
  try { stop = await monitorKdeProxy(env, values => controller.update(values), report); }
  catch (error) { await controller.dispose(); throw error; }
  return async () => { await stop(); await controller.dispose(); };
}
