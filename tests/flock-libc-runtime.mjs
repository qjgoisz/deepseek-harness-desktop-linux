import fs from 'node:fs';import vm from 'node:vm';import path from 'node:path';import assert from 'node:assert/strict';import {spawn} from 'node:child_process';import {pathToFileURL} from 'node:url';
const [moduleFile,root,role]=process.argv.slice(2);
if(role){
 const {tryLockExclusive}=await import(pathToFileURL(moduleFile));const fd=fs.openSync(root,'a');
 try{await tryLockExclusive(fd);console.log('locked');if(role==='hold'){process.stdin.once('data',()=>{fs.closeSync(fd);process.exit(0);});}else{fs.closeSync(fd);}}catch(e){fs.closeSync(fd);console.log(e.code);process.exitCode=2;}
}else{
 const source=fs.readFileSync(moduleFile,'utf8').replace(/^import .*;$/gm,'').replace('export async function','async function');
 for(const initial of [false,true])for(const glibc of [true,false])for(const failure of [false,true]){
  let calls=0,loaded;const report={excludeNetwork:initial,getReport(){calls++;assert.equal(this.excludeNetwork,true);if(failure)throw Error('probe failure');return{header:glibc?{glibcVersionRuntime:'test'}:{}};}};
  const require=filename=>{loaded=filename;return{tryLock(fd,done){done(0);}}};require.resolve=()=>'/pkg/package.json';
  const sandbox={process:{platform:'linux',arch:'x64',report},createRequire:()=>require,join:path.join,dirname:path.dirname,getSystemErrorName:()=>''};
  vm.createContext(sandbox);vm.runInContext(source.replaceAll('import.meta.url',"'file:///fixture.mjs'"),sandbox);
  if(failure)await assert.rejects(sandbox.tryLockExclusive(1),/probe failure/);else{await sandbox.tryLockExclusive(1);await sandbox.tryLockExclusive(1);assert.equal(calls,1);assert.equal(loaded,`/pkg/bin/${glibc?'glibc':'musl'}/system.node`);}
  assert.equal(report.excludeNetwork,initial);
 }
 for(const platform of ['darwin','win32','linux']){
  let calls=0,loaded;const require=f=>{loaded=f;return{tryLock(fd,done){done(0);}}};require.resolve=()=>'/pkg/package.json';
  const report={getReport(){calls++;return{header:{}};}};
  const sandbox={process:{platform,arch:'x64',report},createRequire:()=>require,join:path.join,dirname:path.dirname,getSystemErrorName:()=>''};vm.createContext(sandbox);vm.runInContext(source.replaceAll('import.meta.url',"'file:///fixture.mjs'"),sandbox);
  if(platform==='darwin'){await sandbox.tryLockExclusive(1);assert.equal(loaded,'/pkg/bin/system.node');}
  else await assert.rejects(sandbox.tryLockExclusive(1),platform==='linux'?/excludeNetwork support/:/not supported/);
  assert.equal(calls,0);
 }
 const lock=path.join(root,'actual.lock');
 function child(role){return spawn(process.execPath,[new URL(import.meta.url).pathname,moduleFile,lock,role],{stdio:['pipe','pipe','pipe']});}
 async function first(c){return await new Promise((r,j)=>{let s='';c.stdout.on('data',b=>{s+=b;if(s.includes('\n'))r(s.trim());});c.once('error',j);c.once('exit',()=>{if(!s)j(Error('child exited without lock result'));});});}
 async function tryOnce(){let c=child('try'),line=await first(c);await new Promise(r=>c.once('close',r));return line;}
 for(const abrupt of [false,true]){
  let holder=child('hold');try{
   assert.equal(await first(holder),'locked');assert.match(await tryOnce(),/EAGAIN|EWOULDBLOCK/);
   const closed=new Promise(r=>holder.once('close',r));if(abrupt)holder.kill('SIGKILL');else holder.stdin.write('release\n');await closed;
   assert.equal(await tryOnce(),'locked');
  }finally{if(holder.exitCode===null)holder.kill('SIGKILL');}
 }
 console.log('Restoration, glibc/musl selection, failure propagation, binding cache, cross-process contention and normal/abnormal release passed');
}
