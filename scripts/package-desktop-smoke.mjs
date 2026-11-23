// Runs inside the isolated display and network created by verify-package.py.
import { spawn, spawnSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { fileURLToPath } from 'node:url';

const [launcher, resources, displayMode] = process.argv.slice(2);
const backend = displayMode === 'wayland' ? 'wayland' : 'x11';
const primary = join(resources, 'runtime/primary-runtime');
const manifest = JSON.parse(readFileSync(join(primary, 'runtime.json'), 'utf8'));
const profile = join(process.env.XDG_CONFIG_HOME, 'desktop');
const helpers = dirname(fileURLToPath(import.meta.url));

async function evaluate(url, expression) {
  const socket = new WebSocket(url);
  try {
    return await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('桌面调试接口响应超时')), 2500);
      socket.addEventListener('open', () => socket.send(JSON.stringify({
        id: 1, method: 'Runtime.evaluate',
        params: { expression, returnByValue: true, awaitPromise: true },
      })), { once: true });
      socket.addEventListener('message', event => {
        const result = JSON.parse(event.data);
        if (result.id !== 1) return;
        clearTimeout(timer);
        resolve(result.result?.result?.value);
      });
      const disconnected = () => {
        clearTimeout(timer);
        reject(new Error('桌面调试接口已断开'));
      };
      socket.addEventListener('error', disconnected, { once: true });
      socket.addEventListener('close', disconnected, { once: true });
    });
  } finally {
    socket.close();
  }
}

function run(command, args, capture = false) {
  const result = spawnSync(command, args, {
    stdio: ['ignore', capture ? 'pipe' : 'inherit', 'inherit'], encoding: 'utf8', timeout: 20_000,
  });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`检查命令失败：${command}（${result.status ?? result.signal}）`);
  return result.stdout?.trim();
}

async function main() {
  const version = run(join(resources, 'runtime/cli/bin/dsh'), ['--version'], true);
  if (version !== manifest.desktopVersion) {
    throw new Error(`包内 CLI 版本 ${version} 与运行时清单 ${manifest.desktopVersion} 不一致`);
  }
  console.log(`包内 CLI：${version}`);
  if (manifest.pnpmMode === 'system') {
    run('/usr/bin/pnpm', ['--version']);
  } else {
    run(process.execPath, [join(primary, 'dependencies/pnpm/bin/pnpm.mjs'), '--version']);
  }
  run(process.execPath, ['--experimental-import-meta-resolve',
    join(helpers, 'check-agent-dependencies.mjs'), resources]);
  run(process.execPath, [join(helpers, 'verify-image-worker.cjs'), resources]);

  const child = spawn(launcher, [`--ozone-platform=${backend}`, '--no-sandbox', '--disable-gpu',
    '--disable-dev-shm-usage', `--user-data-dir=${profile}`, '--remote-debugging-port=0'],
  { stdio: 'ignore' });
  let launchError;
  child.on('error', error => { launchError = error; });
  const deadline = Date.now() + 45_000;
  try {
    while (Date.now() < deadline) {
      if (launchError) throw launchError;
      if (child.exitCode !== null || child.signalCode !== null) {
        throw new Error(`包内桌面入口提前退出（${child.exitCode ?? child.signalCode}）`);
      }
      let pages = [];
      try {
        const port = Number(readFileSync(join(profile, 'DevToolsActivePort'), 'utf8').split('\n')[0]);
        if (port > 0 && port < 65536) {
          const response = await fetch(`http://127.0.0.1:${port}/json/list`,
            { signal: AbortSignal.timeout(1000) });
          pages = await response.json();
        }
      } catch {
        // DevToolsActivePort is created asynchronously during Electron startup.
      }
      for (const page of pages.filter(target => target.type === 'page')) {
        if (page.url.endsWith('/welcome.html')) {
          await evaluate(page.webSocketDebuggerUrl, 'window.dshWelcome?.skip()').catch(() => {});
        }
        if (page.url === 'dsh-app://app/' &&
            await evaluate(page.webSocketDebuggerUrl,
              '/新会话|New (chat|session)|工作区|Workspace/i.test(document.body?.innerText ?? "")')
              .catch(() => false)) {
          const maps = readFileSync(`/proc/${child.pid}/maps`, 'utf8');
          if (!maps.includes(join(resources, 'netlink-guard/libdsh-netlink-guard.so'))) {
            throw new Error('包内桌面启动器未加载 Netlink 退避守卫');
          }
          writeFileSync(join(helpers, 'desktop-tested'), displayMode);
          console.log(`最终包验证通过：${displayMode} 主界面和 Netlink 守卫`);
          return;
        }
      }
      await delay(400);
    }
    throw new Error('包内桌面入口未在时限内渲染主界面');
  } finally {
    child.kill('SIGTERM');
    child.unref();
  }
}

main().catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
