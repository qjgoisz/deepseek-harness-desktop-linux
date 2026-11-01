import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {configuredRuntime, assertWritable} from '../local-fixes/mcp-startup/npm-runtime.mjs';
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'dsh-npm-prefix-'));
const run=(source,prefix=temp)=>args=>args.includes('get') ? prefix+'\n' : source;
try {
 for (const source of ['user','global','env','cli']) {
  assert.equal(configuredRuntime(run(`; "${source}" config from test\nprefix = "${temp}"\n`)),path.join(temp,'lib/dsh-mcp-remote-0.15.1'));
 }
 for(const text of ['', '; "builtin" config from test\nprefix = "/usr/local"\n','; "user" config from test\n; prefix = "/old" ; overridden by env\n']) {
  assert.throws(()=>configuredRuntime(run(text)), /No explicit/);
 }
 for(const prefix of ['relative','/','/usr/local','/etc/foo'])assert.throws(()=>configuredRuntime(run('; "user" config from test\nprefix = configured',prefix)),/absolute user-writable/);
 const file=path.join(temp,'file');fs.writeFileSync(file,'x');assert.throws(()=>assertWritable(file),/not a directory/);
 const blocked=path.join(temp,'blocked');fs.mkdirSync(blocked,0o500);
 assert.throws(()=>configuredRuntime(run('; "user" config from test\nprefix = configured',blocked)),/not writable/);
 fs.chmodSync(blocked,0o700);
 fs.mkdirSync(path.join(temp,'lib'));fs.chmodSync(path.join(temp,'lib'),0o500);
 assert.throws(()=>configuredRuntime(run('; "env" config from test\nprefix = configured')),/not writable/);
 fs.chmodSync(path.join(temp,'lib'),0o700);
 fs.mkdirSync(path.join(temp,'lib/dsh-mcp-remote-0.15.1'),{mode:0o500});
 assert.throws(()=>configuredRuntime(run('; "user" config from test\nprefix = configured')),/not writable/);
 fs.chmodSync(path.join(temp,'lib/dsh-mcp-remote-0.15.1'),0o700);
 const bin=path.join(temp,'bin');fs.mkdirSync(bin);
 fs.writeFileSync(path.join(bin,'npm'), `#!${process.execPath}
const args=process.argv.slice(2);
if(args[0]==='config'&&args[1]==='list') console.log(process.env.TEST_LISTING||'');
else if(args[0]==='config'&&args[1]==='get') console.log(process.env.TEST_PREFIX);
else if(args[0]==='ci') process.exit(19);
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
 assert.notEqual(result.status,0);assert(result.stderr.includes('npm ci failed'));
 assert.deepEqual(fs.readdirSync(path.join(target,'lib')),[]);
 const runtime=path.join(target,'lib/dsh-mcp-remote-0.15.1');
 fs.mkdirSync(path.join(runtime,'node_modules/mcp-remote/dist'),{recursive:true});
 fs.writeFileSync(path.join(runtime,'node_modules/mcp-remote/package.json'),JSON.stringify({version:'0.15.1'}));
 fs.writeFileSync(path.join(runtime,'node_modules/mcp-remote/dist/proxy.js'),'');
 const manifests=fileURLToPath(new URL('../local-fixes/mcp-startup/runtime/',import.meta.url));
 for(const name of ['package.json','package-lock.json'])fs.copyFileSync(path.join(manifests,name),path.join(runtime,name));
 result=spawnSync(process.execPath,[installer,'--apply'],{env,encoding:'utf8'});
 assert.equal(result.status,0,result.stderr);
 fs.appendFileSync(path.join(runtime,'package-lock.json'),' ');
 result=spawnSync(process.execPath,[installer,'--apply'],{env,encoding:'utf8'});
 assert.notEqual(result.status,0);assert(result.stderr.includes('differs'));
 console.log('PASS: explicit prefix sources, missing/default prefix, unsafe paths, existing/nonexisting parents and write permissions');
} finally { fs.rmSync(temp,{recursive:true,force:true}); }
