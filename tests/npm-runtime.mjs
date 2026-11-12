import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {configuredGlobalPackage, assertWritable} from '../local-fixes/mcp-startup/npm-runtime.mjs';
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'dsh-npm-prefix-'));
const run=(source,prefix=temp)=>args=>{
  if (args[0] === 'root') return path.join(prefix,'lib/node_modules')+'\n';
  return args.includes('get') ? prefix+'\n' : source;
};
try {
 for (const source of ['user','global','env','cli']) {
  assert.deepEqual(configuredGlobalPackage(run(`; "${source}" config from test\nprefix = "${temp}"\n`)),{
   prefix:temp, packageDirectory:path.join(temp,'lib/node_modules/mcp-remote')
  });
 }
 for(const text of ['', '; "builtin" config from test\nprefix = "/usr/local"\n','; "user" config from test\n; prefix = "/old" ; overridden by env\n']) {
  assert.throws(()=>configuredGlobalPackage(run(text)), /No explicit/);
 }
 for(const prefix of ['relative','/','/usr/local','/etc/foo'])assert.throws(()=>configuredGlobalPackage(run('; "user" config from test\nprefix = configured',prefix)),/absolute user-writable/);
 const file=path.join(temp,'file');fs.writeFileSync(file,'x');assert.throws(()=>assertWritable(file),/not a directory/);
 const blocked=path.join(temp,'blocked');fs.mkdirSync(blocked,0o500);
 assert.throws(()=>configuredGlobalPackage(run('; "user" config from test\nprefix = configured',blocked)),/not writable/);
 fs.chmodSync(blocked,0o700);
 fs.mkdirSync(path.join(temp,'lib'));fs.chmodSync(path.join(temp,'lib'),0o500);
 assert.throws(()=>configuredGlobalPackage(run('; "env" config from test\nprefix = configured')),/not writable/);
 fs.chmodSync(path.join(temp,'lib'),0o700);
 const root=path.join(temp,'lib/node_modules');
 fs.mkdirSync(root,{mode:0o500});
 assert.throws(()=>configuredGlobalPackage(run('; "user" config from test\nprefix = configured')),/not writable/);
 fs.chmodSync(root,0o700);
 const bin=path.join(temp,'bin');fs.mkdirSync(bin);
 fs.writeFileSync(path.join(bin,'npm'), `#!${process.execPath}
const args=process.argv.slice(2);
if(args[0]==='config'&&args[1]==='list') console.log(process.env.TEST_LISTING||'');
else if(args[0]==='config'&&args[1]==='get') console.log(process.env.TEST_PREFIX);
else if(args[0]==='root') console.log(process.env.TEST_PREFIX+'/lib/node_modules');
else if(args[0]==='install') {
  if (!args.includes('--global') || args[args.indexOf('--prefix')+1] !== process.env.TEST_PREFIX ||
      !args.includes('mcp-remote@0.15.1')) process.exit(20);
  if (!process.env.TEST_INSTALL_OK) process.exit(19);
  const fs=require('node:fs');
  const dir=process.env.TEST_PREFIX+'/lib/node_modules/mcp-remote';
  fs.mkdirSync(dir+'/dist',{recursive:true});
  fs.writeFileSync(dir+'/package.json',JSON.stringify({version:'0.15.1'}));
  fs.writeFileSync(dir+'/dist/proxy.js','');
}
else process.exit(20);
`,{mode:0o755});
 const installer=fileURLToPath(new URL('../local-fixes/mcp-startup/install-runtime.mjs',import.meta.url));
 const target=path.join(temp,'fresh-prefix');
 const env={...process.env,PATH:bin+path.delimiter+process.env.PATH,TEST_PREFIX:target,TEST_LISTING:''};
 let result=spawnSync(process.execPath,[installer,'--apply'],{env,encoding:'utf8'});
 assert.notEqual(result.status,0);assert(!fs.existsSync(target));
 env.TEST_LISTING='; "user" config from test\nprefix = configured';
 result=spawnSync(process.execPath,[installer],{env,encoding:'utf8'});
 assert.equal(result.status,0,result.stderr);assert(!fs.existsSync(target));
 result=spawnSync(process.execPath,[installer,'--apply'],{env,encoding:'utf8'});
 assert.notEqual(result.status,0);assert(result.stderr.includes('status 19'));
 assert(!fs.existsSync(target));
 env.TEST_INSTALL_OK='1';
 result=spawnSync(process.execPath,[installer,'--apply'],{env,encoding:'utf8'});
 assert.equal(result.status,0,result.stderr);
 assert(result.stdout.includes('Installed global entry'));
 delete env.TEST_INSTALL_OK;
 result=spawnSync(process.execPath,[installer,'--apply'],{env,encoding:'utf8'});
 assert.equal(result.status,0,result.stderr);
 assert(result.stdout.includes('Verified existing global entry'));
 const manifest=path.join(target,'lib/node_modules/mcp-remote/package.json');
 fs.writeFileSync(manifest,JSON.stringify({version:'0.15.2'}));
 result=spawnSync(process.execPath,[installer,'--apply'],{env,encoding:'utf8'});
 assert.notEqual(result.status,0);assert(result.stderr.includes('Expected installed mcp-remote 0.15.1'));
 assert.equal(JSON.parse(fs.readFileSync(manifest,'utf8')).version,'0.15.2');
 console.log('PASS: npm global installation, explicit prefix, write permissions and existing version checks');
} finally { fs.rmSync(temp,{recursive:true,force:true}); }
