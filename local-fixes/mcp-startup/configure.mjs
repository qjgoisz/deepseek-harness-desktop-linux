#!/usr/bin/env node
// Only explicitly selected services change. Preserve all unrelated YAML bytes.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { isDeepStrictEqual } from 'node:util';
import { fileURLToPath } from 'node:url';

export function configure(source, yaml, node, entry) {
  const schema = yaml.DEFAULT_SCHEMA.extend([
    new yaml.Type('tag:yaml.org,2002:js', { kind: 'scalar', construct: x => x }),
    new yaml.Type('!js', { kind: 'scalar', construct: x => x }),
  ]);
  const load = text => yaml.load(text, { schema });
  const original = load(source), expected = structuredClone(original);
  const selected = new Map([['mcp-wolfram', 'Wolfram'], ['mcp-openalex', 'OpenAlex'], ['mcp-exa', 'Exa']]);
  const found = new Map();
  function walk(x) {
    if (!x || typeof x !== 'object') return;
    if (selected.has(x.id)) {
      if (found.has(x.id) || x.name !== '@deepseek-ai/dsh-mcp-client' || x.config?.serverName !== selected.get(x.id) || x.config.transport !== 'stdio') throw Error('Unexpected MCP entry: ' + x.id);
      const c = x.config;
      if (c.versionNegotiation !== undefined && c.versionNegotiation !== 'auto' && c.versionNegotiation !== 'legacy') throw Error('Unknown negotiation setting');
      if (c.startupMode !== undefined && c.startupMode !== 'blocking' && c.startupMode !== 'background') throw Error('Unknown startup mode');
      c.versionNegotiation = 'legacy';
      c.startupMode = c.failOnStartupError ? 'blocking' : 'background';
      if (x.id !== 'mcp-wolfram') {
        if (c.command === 'npx' && c.args?.[0] === '-y' && c.args?.[1] === 'mcp-remote@0.15.1') c.args = [entry, ...c.args.slice(2)];
        else if (c.command !== node || c.args?.[0] !== entry) throw Error('Remote command differs from expected version; inspect before changing');
        c.command = node;
      }
      found.set(x.id, c);
    }
    for (const v of Object.values(x)) walk(v);
  }
  walk(expected);
  if (found.size !== selected.size) throw Error('Expected exactly three selected MCP entries');
  let updated = source;
  for (const [id, config] of found) {
    const pattern = new RegExp('^( *)- id: ' + id + '\\r?$', 'gm');
    const matches = [...updated.matchAll(pattern)];
    if (matches.length !== 1) throw Error('Unexpected YAML layout: ' + id);
    const m = matches[0], indent = m[1].length;
    const rest = updated.slice(m.index + m[0].length);
    const boundary = new RegExp('\\n(?= {0,' + indent + '}\\S)').exec(rest);
    const end = boundary ? m.index + m[0].length + boundary.index : updated.length;
    let block = updated.slice(m.index, end);
    const ci = ' '.repeat(indent + 4);
    function replaceOne(pattern, replacement) {
      pattern.lastIndex = 0;
      if ([...block.matchAll(pattern)].length !== 1) throw Error('Ambiguous config field in ' + id);
      block = block.replace(pattern, () => replacement);
    }
    const mode = new RegExp('^' + ci + 'versionNegotiation:.*$', 'gm');
    if (mode.test(block)) replaceOne(mode, ci + 'versionNegotiation: legacy');
    else replaceOne(new RegExp('^' + ci + 'serverName:.*$', 'gm'), block.match(new RegExp('^' + ci + 'serverName:.*$', 'm'))[0] + '\n' + ci + 'versionNegotiation: legacy');
    const startup = new RegExp('^' + ci + 'startupMode:.*$', 'gm');
    if (startup.test(block)) replaceOne(startup, ci + 'startupMode: ' + config.startupMode);
    else replaceOne(mode, ci + 'versionNegotiation: legacy\n' + ci + 'startupMode: ' + config.startupMode);
    if (id !== 'mcp-wolfram') {
      replaceOne(new RegExp('^' + ci + 'command:.*$', 'gm'), ci + 'command: ' + JSON.stringify(node));
      replaceOne(new RegExp('^' + ci + 'args:[^\\n]*(?:\\n' + ci + '  [^\\n]*)*', 'gm'), ci + 'args:\n' + config.args.map(a => ci + '  - ' + JSON.stringify(a)).join('\n'));
    }
    updated = updated.slice(0, m.index) + block + updated.slice(end);
  }
  if (!isDeepStrictEqual(load(updated), expected)) throw Error('YAML verification failed; refusing partial/unrelated changes');
  return updated;
}

function main() {
  const args = process.argv.slice(2), apply = args.includes('--apply');
  function flag(name) { const i = args.indexOf(name); if (i < 0 || !args[i + 1]) throw Error('Required ' + name); return path.resolve(args[i + 1]); }
  const app = flag('--app'), profile = flag('--profile'), runtime = flag('--runtime'), node = flag('--node');
  fs.accessSync(node, fs.constants.X_OK);
  const module = path.join(app, 'dsh/node_modules/@deepseek-ai/dsh-mcp-client/lib/index.js');
  if (!fs.readFileSync(module, 'utf8').startsWith('// dsh-linux-mcp-negotiation:v2\n')) throw Error('Install/apply the v2 MCP startup patch first; configuration has not changed');
  const pkg = JSON.parse(fs.readFileSync(path.join(runtime, 'node_modules/mcp-remote/package.json')));
  if (pkg.version !== '0.15.1') throw Error('Expected installed mcp-remote 0.15.1');
  const entry = path.join(runtime, 'node_modules/mcp-remote/dist/proxy.js');
  fs.accessSync(entry);
  const require = createRequire(path.join(app, 'dsh/package.json'));
  const target = path.join(profile, 'cordis.patch.yml'), source = fs.readFileSync(target, 'utf8');
  const updated = configure(source, require('js-yaml'), node, entry);
  if (updated === source) { console.log('Already configured'); return; }
  if (!apply) { console.log('Validated: only Wolfram/OpenAlex/Exa negotiation/startup modes and two remote commands would change; strict servers remain blocking. Use --apply to write with backup.'); return; }
  const backup = target + '.before-mcp-startup-' + new Date().toISOString().replaceAll(':', '-');
  const temporary = target + '.mcp-startup-' + process.pid;
  fs.writeFileSync(backup, source, { flag: 'wx', mode: 0o600 });
  try {
    fs.writeFileSync(temporary, updated, { flag: 'wx', mode: fs.statSync(target).mode & 0o777 });
    if (fs.readFileSync(target, 'utf8') !== source) throw Error('Configuration changed concurrently; retry after stopping DSH');
    fs.renameSync(temporary, target);
  } finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
  console.log('Configured. Backup: ' + backup);
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { main(); } catch (e) { console.error(e.message); process.exitCode = 1; }
}
