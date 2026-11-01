#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {configuredRuntime,verifyRuntime} from './npm-runtime.mjs';

try {
  if (process.argv.slice(2).some(x=>x!=='--apply')) throw Error('Usage: node install-runtime.mjs [--apply]');
  const runtime = configuredRuntime();
  const source = path.join(path.dirname(fileURLToPath(import.meta.url)), 'runtime');
  if (fs.existsSync(runtime)) {
    verifyRuntime(runtime);
    for (const name of ['package.json','package-lock.json']) {
      if (!fs.readFileSync(path.join(runtime,name)).equals(fs.readFileSync(path.join(source,name)))) throw Error('Existing runtime manifest/lock differs; inspect before replacing');
    }
    console.log('Verified existing runtime: '+runtime);
  } else if (!process.argv.includes('--apply')) {
    console.log('Validated npm prefix. Runtime would be installed at '+runtime+'; use --apply.');
  } else {
    const parent = path.dirname(runtime);
    fs.mkdirSync(parent,{recursive:true});
    const stage = fs.mkdtempSync(path.join(parent,'.dsh-mcp-remote-'));
    try {
      for (const name of ['package.json','package-lock.json']) fs.copyFileSync(path.join(source,name),path.join(stage,name));
      try {
        execFileSync('npm',['ci','--prefix',stage,'--ignore-scripts','--no-audit','--no-fund'],{stdio:['ignore','pipe','pipe']});
      } catch { throw Error('npm ci failed; temporary installation removed. Check npm network/proxy configuration and retry.'); }
      verifyRuntime(stage);
      if (fs.existsSync(runtime)) throw Error('Runtime appeared concurrently; refusing replacement');
      fs.renameSync(stage,runtime);
    } finally { fs.rmSync(stage,{recursive:true,force:true}); }
    console.log('Installed locked runtime: '+runtime);
  }
} catch(e) { console.error(e.message); process.exitCode=1; }
