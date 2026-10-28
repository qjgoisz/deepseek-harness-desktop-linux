// A private dbus-run-session: these notifications never reach the user's desktop bus.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { pathToFileURL } from 'node:url';
const run=promisify(execFile), file=process.env.XDG_CONFIG_HOME+'/kioslaverc';
const proxies=[];
for(const label of ['a','b']){
 const server=createServer((req,res)=>res.end(label));server.listen(0,'127.0.0.1');await once(server,'listening');
 proxies.push({server,url:`http://127.0.0.1:${server.address().port}`});
}
const write=async(mode,url)=>{await fs.writeFile(file+'.tmp',`[Proxy Settings]\nProxyType=${mode}\nhttpProxy=${url}\nhttpsProxy=${url}\nNoProxyFor=localhost,127.0.0.0/8\n`);await fs.rename(file+'.tmp',file);};
const target=new URL('http://private-proxy-test.invalid/');
const proxy=await import(pathToFileURL(process.argv[2]));
const inherited={...process.env};
const env={get:name=>inherited[name]===undefined?undefined:{value:inherited[name]}};
const warn=[];
process.argv[1]='/isolated/dsh-desktop-host/lib/index.js';
await write('1',proxies[0].url);
const stop=await proxy.installDesktopProxyFromEnvironment(env,m=>warn.push(m));
// Prove signal delivery separately: no filesystem watch or periodic refresh can cause this read.
const {monitorKdeProxy}=await import('../patches/system-proxy/desktop-system-proxy.mjs');
let signalReads=0;
const stopSignalProbe=await monitorKdeProxy(env,()=>{},m=>warn.push(m),{
 read:async()=>{signalReads++;return {};},watch:()=>{throw Error('disabled for signal test');},pollMs:60000,debounceMs:10
});
for(let i=0;i<10&&signalReads===1;i++){
 await run('dbus-send',['--session','--type=signal','/KIO/Scheduler','org.kde.KIO.Scheduler.reparseSlaveConfiguration','string:']);
 await new Promise(r=>setTimeout(r,50));
}
assert(signalReads>1,'the KDE D-Bus signal must trigger a read independently of file/poll fallbacks');
await stopSignalProbe();
const request=async()=>await(await fetch(target,{signal:AbortSignal.timeout(2000)})).text();
const until=async test=>{for(let i=0;i<80;i++){if(test())return;await new Promise(r=>setTimeout(r,50));}assert.fail('proxy notification timed out');};
try{
 assert.equal(await request(),'a','system settings must apply during startup without proxy variables');
 await write('1',proxies[1].url);
 await run('dbus-send',['--session','--type=signal','/KIO/Scheduler','org.kde.KIO.Scheduler.reparseSlaveConfiguration','string:']);
 await until(()=>proxy.proxyRouteFor(target).proxy===proxies[1].url);assert.equal(await request(),'b');
 await write('0',proxies[1].url); // File replacement/update fallback also works without a D-Bus signal.
 await until(()=>!proxy.proxyRouteFor(target).proxied);
 assert.equal(process.env.http_proxy,undefined);
 await write('1',proxies[0].url);
 await run('dbus-send',['--session','--type=signal','/KIO/Scheduler','org.kde.KIO.Scheduler.reparseSlaveConfiguration','string:']);
 await until(()=>proxy.proxyRouteFor(target).proxy===proxies[0].url);assert.equal(await request(),'a');
 assert.deepEqual(warn,[]);
 console.log('Real kreadconfig + private KDE D-Bus + automatic Desktop startup + on/off/change: passed');
}finally{
 await stop();
 await Promise.all(proxies.map(({server})=>new Promise(r=>server.close(r))));
}
