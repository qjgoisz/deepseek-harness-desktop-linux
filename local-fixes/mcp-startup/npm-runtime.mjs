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

export const REMOTE_VERSION = '0.15.1';

export function configuredGlobalPackage(run = args => execFileSync('npm', args, {encoding:'utf8', stdio:['ignore','pipe','pipe']})) {
  // Effective prefix alone always has a default. Require a configured source.
  const listing = run(['config','list','--global']);
  let source = '', explicit = false;
  for (const line of listing.split(/\r?\n/)) {
    const section = /^; "([^"]+)" config from /.exec(line);
    if (section) source = section[1];
    if (/^prefix\s*=/.test(line) && ['user','global','env','cli'].includes(source)) explicit = true;
  }
  if (!explicit) throw Error('No explicit npm global prefix. Set one with npm config set prefix /absolute/user/path, then retry. Nothing installed.');
  const prefix = run(['config','get','prefix','--global']).trim();
  if (!path.isAbsolute(prefix) || prefix === '/' || /^(?:\/usr|\/etc|\/bin|\/sbin|\/lib|\/var|\/opt|\/proc|\/sys|\/dev)(?:\/|$)/.test(prefix)) throw Error('npm prefix must be an absolute user-writable directory outside system paths');
  const root = run(['root','--global','--prefix',prefix]).trim();
  const packageDirectory = path.join(root, 'mcp-remote');
  assertWritable(prefix);
  assertWritable(root);
  assertWritable(packageDirectory);
  return {prefix, packageDirectory};
}

export function verifyPackage(packageDirectory) {
  const manifest = path.join(packageDirectory, 'package.json');
  if (!fs.existsSync(manifest)) throw Error('Install mcp-remote@' + REMOTE_VERSION + ' first: ' + packageDirectory);
  const pkg = JSON.parse(fs.readFileSync(manifest, 'utf8'));
  if (pkg.version !== REMOTE_VERSION) throw Error('Expected installed mcp-remote ' + REMOTE_VERSION + ' in ' + packageDirectory);
  const entry = path.join(packageDirectory, 'dist/proxy.js');
  fs.accessSync(entry, fs.constants.R_OK);
  return entry;
}

export function verifyRuntime(runtime) {
  return verifyPackage(path.join(runtime, 'node_modules/mcp-remote'));
}
