#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {assertWritable, configuredGlobalPackage, REMOTE_VERSION, verifyPackage} from './npm-runtime.mjs';

try {
  if (process.argv.slice(2).some(x=>x!=='--apply')) throw Error('Usage: node install-runtime.mjs [--apply]');
  const {prefix, packageDirectory} = configuredGlobalPackage();
  assertWritable(path.join(prefix, 'bin'));
  if (fs.existsSync(packageDirectory)) {
    console.log('Verified existing global entry: ' + verifyPackage(packageDirectory));
  } else if (!process.argv.includes('--apply')) {
    console.log('Validated npm prefix. Package would be installed at ' + packageDirectory + '; use --apply.');
  } else {
    const spec = 'mcp-remote@' + REMOTE_VERSION;
    try {
      execFileSync('npm', ['install', '--global', '--prefix', prefix, '--ignore-scripts', '--no-audit', '--no-fund', spec], {stdio:['ignore','pipe','pipe']});
    } catch (error) {
      throw Error('npm global install failed for ' + spec + ' (status ' + (error.status ?? 'unknown') + '). Check npm output, network and prefix.');
    }
    console.log('Installed global entry: ' + verifyPackage(packageDirectory));
  }
} catch(e) { console.error(e.message); process.exitCode=1; }
