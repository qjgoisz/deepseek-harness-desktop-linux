import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import path from 'node:path';
import {configure} from '../local-fixes/mcp-startup/configure.mjs';
const require=createRequire(path.resolve(process.argv[2], 'dsh/package.json'));
const yaml=require('js-yaml');
const node='/fixed/node',entry='/fixed/mcp/dist/proxy.js';
const source=`# Keep this comment and !js expression byte-for-byte
- insert:
    - id: mcp-wolfram
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: Wolfram
        transport: stdio
        command: wolfram
        args: ['-run', 'original']
    - id: mcp-openalex
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: OpenAlex
        transport: stdio
        command: npx
        args:
          - '-y'
          - 'mcp-remote@0.15.1'
          - 'https://example.invalid/mcp'
          - '--header'
          - 'X-Test: keep'
        env:
          TEST: keep
    - id: mcp-exa
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: Exa
        transport: stdio
        command: npx
        args: ['-y', 'mcp-remote@0.15.1', 'https://example.invalid/?login']
- id: unrelated
  name: other
  config:
    expression: !js ctx => ctx.get('x')
`;
const updated=configure(source,yaml,node,entry);
assert.equal(configure(updated,yaml,node,entry),updated);
assert(updated.includes(source.slice(source.indexOf('- id: unrelated'))));
assert(updated.includes('TEST: keep'));
assert(!updated.includes('command: npx'));
assert.equal(updated.match(/versionNegotiation: legacy/g).length,3);
assert.equal(updated.match(/startupMode: background/g).length,3);
const strict=configure(source.replace('serverName: Exa','serverName: Exa\n        failOnStartupError: true'),yaml,node,entry);
assert.equal(strict.match(/startupMode: background/g).length,2);
assert.equal(strict.match(/startupMode: blocking/g).length,1);
assert.throws(()=>configure(source.replace('serverName: Exa','serverName: Exa\n        startupMode: unknown'),yaml,node,entry));
for(const s of [source.replace('mcp-remote@0.15.1','mcp-remote@0.16.0'),source.replace('serverName: Exa','serverName: Other'),source+'\n'+source])assert.throws(()=>configure(s,yaml,node,entry));
console.log('PASS: targeted YAML edits; tags/comments/headers/env preserved; idempotent; unknown/duplicate refused');
