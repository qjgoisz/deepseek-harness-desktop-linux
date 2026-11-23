#!/usr/bin/env node
// Run with --experimental-import-meta-resolve to resolve from each consumer.
import { readFileSync, statSync } from 'node:fs';
import { createRequire } from 'node:module';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const resources = process.argv[2];
if (!resources) {
  console.error('Usage: node --experimental-import-meta-resolve check-agent-dependencies.mjs <resources>');
  process.exit(2);
}

const modules = resolve(resources, 'app/dsh/node_modules');
const require = createRequire(join(modules, '@deepseek-ai/dsh-sandbox-local/package.json'));
const { parse } = require('acorn');
const packages = [
  'dsh-agent-preset',
  'dsh-agent-preset-registry',
  'dsh-sandbox-local',
  'dsh-shell',
  'dsh-ptc-runtime',
  'dsh-workflow',
];
let checked = 0;
let failed = false;

for (const name of packages) {
  const entry = join(modules, '@deepseek-ai', name, 'lib/index.js');
  const parent = pathToFileURL(entry);
  const { body } = parse(readFileSync(entry, 'utf8'), { ecmaVersion: 'latest', sourceType: 'module' });
  const imports = new Set(body.map(node => node.source?.value)
    .filter(source => typeof source === 'string' && source.startsWith('@deepseek-ai/')));
  for (const source of imports) {
    try {
      const target = new URL(import.meta.resolve(source, parent));
      // import.meta.resolve can return a file URL for a missing export target.
      if (!statSync(target).isFile()) throw new Error('resolved path is not a file');
      checked++;
    } catch (error) {
      console.error(`Agent 预设依赖无法解析：${name}/lib/index.js → ${source} (${error.code ?? error.message})`);
      failed = true;
    }
  }
}
if (failed) process.exit(1);
console.log(`Agent 预设依赖检查通过（${checked} 个静态导入）`);
