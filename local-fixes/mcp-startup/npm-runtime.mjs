import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';

export function assertWritable(directory) {
  let current = directory;
  while (!fs.existsSync(current)) {
    const parent = path.dirname(current);
    if (parent === current) throw Error("Cannot find existing parent for " + directory);
    current = parent;
  }
  if (!fs.statSync(current).isDirectory()) throw Error("Installation path is not a directory: " + current);
  try { fs.accessSync(current, fs.constants.W_OK | fs.constants.X_OK); }
  catch { throw Error("npm installation path is not writable: " + current + "; choose a writable npm prefix. Nothing installed."); }
}

export function configuredRuntime(run = args => execFileSync('npm', args, {encoding:'utf8', stdio:['ignore','pipe','pipe']})) {
  // Effective prefix alone always has a default. Require a configured source.
  const listing = run(['config','list']);
  let source = '', explicit = false;
  for (const line of listing.split(/\r?\n/)) {
    const section = /^; "([^"]+)" config from /.exec(line);
    if (section) source = section[1];
    if (/^prefix\s*=/.test(line) && ['user','global','env','cli'].includes(source)) explicit = true;
  }
  if (!explicit) throw Error('No explicit npm global prefix. Set one with npm config set prefix /absolute/user/path, then retry. Nothing installed.');
  const prefix = run(['config','get','prefix']).trim();
  if (!path.isAbsolute(prefix) || prefix === '/' || /^(?:\/usr|\/etc|\/bin|\/sbin|\/lib|\/var|\/opt|\/proc|\/sys|\/dev)(?:\/|$)/.test(prefix)) throw Error('npm prefix must be an absolute user-writable directory outside system paths');
  const runtime = path.join(prefix, 'lib', 'dsh-mcp-remote-0.15.1');
  assertWritable(prefix);
  assertWritable(path.dirname(runtime));
  assertWritable(runtime);
  return runtime;
}

export function verifyRuntime(runtime) {
  const pkg = JSON.parse(fs.readFileSync(path.join(runtime,'node_modules/mcp-remote/package.json'),'utf8'));
  if (pkg.version !== '0.15.1') throw Error('Expected installed mcp-remote 0.15.1');
  const entry = path.join(runtime,'node_modules/mcp-remote/dist/proxy.js');
  fs.accessSync(entry);
  return entry;
}
