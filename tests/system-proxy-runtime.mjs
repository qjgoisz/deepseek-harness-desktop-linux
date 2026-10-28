import assert from 'node:assert/strict';
import { EventEmitter } from 'node:events';
import { createServer } from 'node:http';
import { createServer as createHttpsServer } from 'node:https';
import { connect } from 'node:net';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import { once } from 'node:events';
import { pathToFileURL } from 'node:url';
import { readKdeProxy, shouldFollowKde, monitorKdeProxy, KDE_SIGNAL } from '../patches/system-proxy/desktop-system-proxy.mjs';
const snapshot = values => ({ get: name => values[name] === undefined ? undefined : { value: values[name] } });
const kde = snapshot({ XDG_CURRENT_DESKTOP: 'KDE', KDE_SESSION_VERSION: '6' });
const host = '/payload/dsh-desktop-host/lib/index.js';
assert(shouldFollowKde(kde, 'linux', host));
for (const [values, platform, entry] of [[{XDG_CURRENT_DESKTOP:'GNOME'},'linux',host],
  [{XDG_CURRENT_DESKTOP:'KDE',HTTPS_PROXY:'http://explicit:8080'},'linux',host],
  [{XDG_CURRENT_DESKTOP:'KDE',DSH_DESKTOP_SYSTEM_PROXY:'0'},'linux',host],
  [{XDG_CURRENT_DESKTOP:'KDE'},'darwin',host], [{XDG_CURRENT_DESKTOP:'KDE'},'linux','/cli.js']])
  assert(!shouldFollowKde(snapshot(values),platform,entry));
assert(shouldFollowKde(snapshot({XDG_CURRENT_DESKTOP:'KDE',https_proxy:' ',NO_PROXY:'example.org'}),'linux',host));
const reader = fields => async (bin,args,options) => {
  assert.equal(bin,'kreadconfig6'); assert(options.timeout); assert(options.maxBuffer);
  assert.equal(args[args.length-2],'--key');
  return {stdout:fields[args.at(-1)]??''};
};
assert.deepEqual(await readKdeProxy(kde,reader({ProxyType:'0',httpProxy:'http://stale:1'})),{});
const manual={ProxyType:'1',httpProxy:'http://127.0.0.1:10808',NoProxyFor:'localhost,10.0.0.0/8,api.example.org'};
assert.deepEqual(await readKdeProxy(kde,reader(manual)),{http_proxy:manual.httpProxy,no_proxy:manual.NoProxyFor});
assert((await readKdeProxy(snapshot({no_proxy:' ',NO_PROXY:'private.example'}),reader(manual))).no_proxy.endsWith(',private.example'));
for(const change of [{ProxyType:'2'},{ReversedException:'true'},{httpProxy:'socks5://localhost:10808'},
  {NoProxyFor:'2001:db8::/32'},{NoProxyFor:'10.0.0.0/99'},{NoProxyFor:'<local>'},{NoProxyFor:'*example.org'},{httpProxy:'http://localhost:1/path'}])
  await assert.rejects(readKdeProxy(kde,reader({...manual,...change})));
// Watcher delivery, split D-Bus lines, duplicate suppression, read failures and owned-child teardown.
const watchEmitter=new EventEmitter();let closed=false,killed=false;
watchEmitter.unref=()=>{};watchEmitter.close=()=>{closed=true;};
const child=new EventEmitter();child.stdout=new EventEmitter();child.exitCode=null;child.kill=()=>{killed=true;};
let values={},fail=false;const applied=[],warnings=[];
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const until=async test=>{for(let i=0;i<100;i++){if(test())return;await wait(10);}assert.fail('timed out');};
const stop=await monitorKdeProxy(kde,v=>{applied.push(v);},m=>warnings.push(m),{
  read:async()=>{if(fail)throw Error('read failure');return values;},
  watch:(dir,callback)=>{watchEmitter.on('change',callback);return watchEmitter;},
  spawn:(command,args)=>{assert.equal(command,'dbus-monitor');assert.deepEqual(args,['--session',KDE_SIGNAL]);return child;},
  debounceMs:5,pollMs:10000
});
assert.deepEqual(applied,[{}]);values={http_proxy:'http://127.0.0.1:1'};
child.stdout.emit('data',Buffer.from('signal interface=org.kde.KIO.Scheduler; member=reparseSlave'));
child.stdout.emit('data',Buffer.from('Configuration\n'));await until(()=>applied.length===2);
watchEmitter.emit('change','rename','kioslaverc');await wait(20);assert.equal(applied.length,2);
fail=true;watchEmitter.emit('change','change','kioslaverc');await until(()=>warnings.length===1);assert.equal(applied.length,2);
fail=false;values={};watchEmitter.emit('change','rename','kioslaverc');await until(()=>applied.length===3);
await stop();assert(closed&&killed);values={http_proxy:'http://127.0.0.1:2'};watchEmitter.emit('change','change','kioslaverc');await wait(20);assert.equal(applied.length,3);
console.log('KDE parsing, scope, notifications, failure retention and cleanup: passed');
if(!process.argv[2])process.exit(0);
// The remaining checks use copied real DSH code, real Undici and local mock CONNECT proxies.
const proxy=await import(pathToFileURL(process.argv[2]));
const request=url=>fetch(url,{signal:AbortSignal.timeout(4000)});
const phase=name=>{if(process.env.DSH_PROXY_TEST_TRACE)console.log(name);};
const target=new URL('http://proxy-test.invalid/');
const listen=async server=>{server.listen(0,'127.0.0.1');await once(server,'listening');return server.address().port;};
let finishStream;const sockets=new Set(),connectLabels=[];
let secureServer,securePort;
if(process.env.DSH_PROXY_TEST_CERT){
 secureServer=createHttpsServer({cert:fs.readFileSync(process.env.DSH_PROXY_TEST_CERT),key:fs.readFileSync(process.env.DSH_PROXY_TEST_KEY)},(req,res)=>res.end('secure'));
 securePort=await listen(secureServer);
}
const makeProxy=async label=>{
 const server=createServer((req,res)=>{phase('HTTP request '+label);if(req.url.endsWith('/stream')){res.write('old');finishStream=()=>res.end('end');}else res.end(label);});server.on('connection',s=>{phase('socket '+label);sockets.add(s);s.on('close',()=>sockets.delete(s));});
 server.on('connect',(req,socket,head)=>{phase('CONNECT '+label);socket.on('error',()=>{});
  if(securePort){
   connectLabels.push(label);
   const upstream=connect(securePort,'127.0.0.1',()=>{socket.write('HTTP/1.1 200 Connection Established\r\n\r\n');if(head.length)upstream.write(head);socket.pipe(upstream).pipe(socket);});
   upstream.on('error',()=>socket.destroy());socket.on('close',()=>upstream.destroy());return;
  }
  socket.write('HTTP/1.1 200 Connection Established\r\n\r\n');
  socket.once('data',data=>{phase('request data '+label);
   if(data.toString().includes('/stream ')){
    socket.write('HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\nConnection: close\r\n\r\n3\r\nold\r\n');
    finishStream=()=>socket.end('3\r\nend\r\n0\r\n\r\n');
   }else socket.end(`HTTP/1.1 200 OK\r\nContent-Length: ${label.length}\r\nConnection: close\r\n\r\n${label}`);
  });
 });
 const port=await listen(server);return {server,url:`http://127.0.0.1:${port}`};
};
const a=await makeProxy('proxy-a'),b=await makeProxy('proxy-b');
const local=createServer((req,res)=>res.end('direct'));const port=await listen(local);
const names=['http_proxy','https_proxy','no_proxy','HTTP_PROXY','HTTPS_PROXY','NO_PROXY'];
const saved=Object.fromEntries(names.map(n=>[n,process.env[n]]));
const controller=await proxy.createDesktopProxyController(m=>{throw Error(m);});
try {
 phase('enable-a');await controller.update({http_proxy:a.url,no_proxy:'10.0.0.0/8,api.example.org'});
 phase('request-a');assert.equal(await (await request(target)).text(),'proxy-a');
 assert.equal(proxy.proxyRouteFor(new URL('http://10.3.4.5/')).proxied,false);
 assert.equal(proxy.proxyRouteFor(new URL('http://api.example.org/')).proxied,false);
 assert.equal(proxy.proxyRouteFor(new URL('http://127.1.2.3/')).proxied,false);
 assert.equal(await (await request(`http://127.0.0.1:${port}/`)).text(),'direct');
 assert.equal(proxy.proxyEnvironmentForChild().NODE_USE_ENV_PROXY,'1');
 assert.equal(proxy.proxyRouteFor(new URL('https://proxy-test.invalid/')).proxy,a.url);
 if(securePort){assert.equal(await(await request('https://proxy-test.invalid/')).text(),'secure');assert.equal(connectLabels.at(-1),'proxy-a');}
 phase('stream');const stream=await request(new URL('/stream',target));await until(()=>!!finishStream);
 phase('enable-b');await controller.update({http_proxy:b.url});
 assert.equal(await (await request(target)).text(),'proxy-b');
 if(securePort){assert.equal(await(await request('https://proxy-test.invalid/')).text(),'secure');assert.equal(connectLabels.at(-1),'proxy-b');}
 finishStream();assert.equal(await stream.text(),'oldend');
 assert.equal(proxy.proxyEnvironmentForChild().http_proxy,b.url);
 const childResult=await new Promise((resolve,reject)=>{
  const child=spawn(process.execPath,['-e',`fetch(${JSON.stringify(target.href)},{signal:AbortSignal.timeout(2500)}).then(async r=>console.log(await r.text())).catch(()=>process.exit(1))`],
    {env:{...process.env,...proxy.proxyEnvironmentForChild()},stdio:['ignore','pipe','pipe']});
  let text='';child.stdout.on('data',b=>text+=b);child.stderr.resume();
  child.on('error',reject);child.on('exit',code=>code===0?resolve(text.trim()):reject(Error('proxy child failed')));
 });
 assert.equal(childResult,'proxy-b');
 await controller.update({});
 assert.equal(proxy.proxyRouteFor(target).proxied,false);
 assert.deepEqual(proxy.proxyEnvironmentForChild(),{});
 assert.equal(process.env.http_proxy,undefined);
 assert.equal(await (await request(`http://127.0.0.1:${port}/`)).text(),'direct');
 await controller.update({http_proxy:a.url});phase('request-a');assert.equal(await (await request(target)).text(),'proxy-a');
} finally {
 phase('dispose');await controller.dispose();phase('disposed');
 for(const n of names)assert.equal(process.env[n],saved[n],n);
 for(const s of sockets)s.destroy();
 phase('close-servers');await Promise.all([a.server,b.server,local,secureServer].filter(Boolean).map(server=>new Promise(r=>server.close(r))));
}
console.log((securePort?'Real HTTP + HTTPS CONNECT routing':'Real HTTP proxy routing')+', hot switch, active stream, bypass, child env and disable/re-enable: passed');
