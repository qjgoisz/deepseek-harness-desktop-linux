import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
const [moduleFile, dir] = process.argv.slice(2);
const { Config, apply } = await import(pathToFileURL(moduleFile));
const server = path.join(dir, 'server.mjs');
fs.writeFileSync(server, `
import fs from 'node:fs';import readline from 'node:readline';
fs.appendFileSync(process.env.PROBE_LOG,JSON.stringify({pid:process.pid,event:'spawn'})+'\\n');
readline.createInterface({input:process.stdin}).on('line',line=>{
const m=JSON.parse(line);fs.appendFileSync(process.env.PROBE_LOG,JSON.stringify({pid:process.pid,event:m.method})+'\\n');
if(m.id===undefined)return;
let result;
if(m.method==='initialize'){if(process.env.WAIT_INIT)return;result={protocolVersion:'2025-11-25',capabilities:{tools:{}},serverInfo:{name:'fixture',version:'1'}};}
else if(m.method==='tools/list'){result={tools:[{name:'echo',inputSchema:{type:'object',properties:{},additionalProperties:false}}]};if(process.env.DROP_ONCE&&!fs.existsSync(process.env.DROP_ONCE)){fs.writeFileSync(process.env.DROP_ONCE,'1');setTimeout(()=>process.exit(0),50);}}
else if(m.method==='tools/call')result={content:[{type:'text',text:'ok'}]};
else {process.stdout.write(JSON.stringify({jsonrpc:'2.0',id:m.id,error:{code:-32601,message:'Unsupported'}})+'\\n');return;}
process.stdout.write(JSON.stringify({jsonrpc:'2.0',id:m.id,result})+'\\n');
});`);
function context() {
  const effects=[], tools=new Map();
  const ctx={root:{},fiber:{},logger:{info(){},warn(){},error(){}}, get(){},on(){},inject(){},
    effect(f){ const dispose=f(); if(dispose)effects.push(dispose); },
    tools:{register(t){assert(!tools.has(t.name));tools.set(t.name,t);return()=>tools.delete(t.name);}}};
  return {ctx,tools,dispose:async()=>{for(const f of effects.reverse())await f();}};
}
for(const mode of [undefined,'legacy']) {
  const log=path.join(dir,String(mode)+'.jsonl'), c=context();
  const config=Config({transport:'stdio',serverName:'Fixture',command:process.execPath,args:[server],env:{PROBE_LOG:log},cwd:dir,failOnStartupError:true,...(mode?{versionNegotiation:mode}:{})});
  assert.equal(config.versionNegotiation,mode??'auto');
  try {
    await apply(c.ctx,config);
    assert.equal(c.tools.size,1);
    await c.tools.values().next().value.execute({}, {signal:new AbortController().signal});
  } finally { await c.dispose(); }
  assert.equal(c.tools.size,0);
  const events=fs.readFileSync(log,'utf8').trim().split('\n').map(JSON.parse);
  const pids=events.filter(e=>e.event==='spawn').map(e=>e.pid);
  assert.equal(pids.length, mode==='legacy'?1:2);
  assert.equal(events.filter(e=>e.event==='tools/call').length,1);
  for(const pid of pids) assert.throws(()=>process.kill(pid,0),{code:'ESRCH'});
}
assert.throws(()=>Config({transport:'stdio',serverName:'bad',command:process.execPath,versionNegotiation:'bogus'}));
assert.equal(Config({transport:'streamable-http',serverName:'http',url:'http://127.0.0.1',versionNegotiation:'legacy'}).versionNegotiation,'legacy');
async function until(predicate) {const start=Date.now();while(!predicate()){if(Date.now()-start>4000)throw Error('Timeout');await new Promise(r=>setTimeout(r,10));}}
// A reconnect uses the same explicit policy and creates one fresh generation.
{
  const c=context(),log=path.join(dir,'reconnect.jsonl');
  const config=Config({transport:'stdio',serverName:'Reconnect',command:process.execPath,args:[server],env:{PROBE_LOG:log,DROP_ONCE:path.join(dir,'dropped')},cwd:dir,versionNegotiation:'legacy',failOnStartupError:true,reconnect:{enabled:true,initialDelayMs:10,maxDelayMs:10,maxAttempts:2}});
  try {await apply(c.ctx,config);await until(()=>fs.readFileSync(log,'utf8').split('tools/list').length===3);await new Promise(r=>setTimeout(r,30));assert.equal(c.tools.size,1);}finally{await c.dispose();}
  const events=fs.readFileSync(log,'utf8').trim().split('\n').map(JSON.parse);
  assert.equal(events.filter(e=>e.event==='spawn').length,2);
  assert(!events.some(e=>e.event==='server/discover'));
  for(const e of events.filter(e=>e.event==='spawn'))assert.throws(()=>process.kill(e.pid,0),{code:'ESRCH'});
}
// Disposal while initialize is pending closes the owned server and settles boot.
{
  const c=context(),log=path.join(dir,'cancel.jsonl');
  const config=Config({transport:'stdio',serverName:'Cancel',command:process.execPath,args:[server],env:{PROBE_LOG:log,WAIT_INIT:'1'},cwd:dir,versionNegotiation:'legacy',reconnect:{enabled:false}});
  const boot=apply(c.ctx,config);
  try{await until(()=>fs.existsSync(log));}finally{await c.dispose();await boot;}
  const pid=JSON.parse(fs.readFileSync(log,'utf8').split('\n')[0]).pid;
  assert.throws(()=>process.kill(pid,0),{code:'ESRCH'});
}
const c=context();
await assert.rejects(apply(c.ctx,{versionNegotiation:'bogus'}),/invalid versionNegotiation/);
const bad=Config({transport:'stdio',serverName:'bad',command:'/no/such/mcp',failOnStartupError:true,versionNegotiation:'legacy',reconnect:{enabled:false}});
try {await assert.rejects(apply(c.ctx,bad),/initial connection/);} finally {await c.dispose();}
console.log('PASS: default auto=2 processes; legacy=1; tools/call; disposal; reconnect; startup cancellation; invalid modes; strict startup failure');
