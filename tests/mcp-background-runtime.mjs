import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const [moduleFile,dir]=process.argv.slice(2);
const plugin=await import(pathToFileURL(moduleFile)),{Config,apply}=plugin;
const require=createRequire(moduleFile);
const {Context}=await import(pathToFileURL(require.resolve('@deepseek-ai/cordis')));
const server=fileURLToPath(new URL('./fixtures/delayed-mcp-server.mjs',import.meta.url));
const rejected=[];process.on('unhandledRejection',error=>rejected.push(error));
let sequence=0;
const results=[];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function until(predicate){const at=Date.now();while(!predicate()){assert(Date.now()-at<4000,'condition timed out');await sleep(5);}}
async function promptly(promise){let timer;try{return await Promise.race([promise,new Promise((_,reject)=>timer=setTimeout(()=>reject(Error('startup barrier was not released')),700))]);}finally{clearTimeout(timer);}}
function read(log){return fs.existsSync(log)?fs.readFileSync(log,'utf8').trim().split('\n').filter(Boolean).map(JSON.parse):[];}
function fixture(options={}){
  const label=String(++sequence),log=path.join(dir,label+'.jsonl'),gate=path.join(dir,label+'.gate');
  const config=Config({transport:'stdio',serverName:'Fixture',command:process.execPath,args:[server],cwd:dir,versionNegotiation:'legacy',startupMode:'background',reconnect:{enabled:false},...options,env:{MCP_TEST_LOG:log,...options.env}});
  return {config,log,gate,open:()=>fs.writeFileSync(gate,'1')};
}
function context(owner={}){
  const effects=[],tools=new Map(),logs=[];let alive=true,late=0,section,resources,disposed;
  const ctx={root:owner,fiber:{},logger:Object.fromEntries(['info','warn','error'].map(level=>[level,m=>logs.push([level,m])])),get(){},on(){},
    effect(f){const d=f();if(d)effects.push(d);},
    inject(names,callback){
      if(names[0]==='systemPrompt')callback({systemPrompt:{section:s=>{section=s;},getSectionOrder:()=>0}});
      if(names[0]==='mcpResources')callback({mcpResources:{register:(_,r)=>{resources=r;}}});
    },
    tools:{register(t){if(!alive){late++;throw Error('late registration');}assert(!tools.has(t.name));tools.set(t.name,t);return()=>tools.delete(t.name);}}
  };
  return {ctx,tools,logs,instructions:()=>section?.text(),resource:()=>resources,late:()=>late,
    dispose(){if(disposed)return disposed;alive=false;return disposed=(async()=>{for(const d of effects.reverse())await d();})();}};
}
async function scenario(name,options,body){
  const f=fixture(options),c=context();
  try{await body(f,c);}finally{await c.dispose();}
  await sleep(10);
  assert.equal(c.tools.size,0);assert.equal(c.late(),0);assert.equal(rejected.length,0);
  for(const e of read(f.log).filter(e=>e.event==='spawn'))assert.throws(()=>process.kill(e.pid,0),{code:'ESRCH'});
  results.push(name);
}

await scenario('background releases boot before initialize; tools/instructions/resources arrive later',{},async(f,c)=>{
  f.config.env.MCP_TEST_GATE_PHASE='initialize';f.config.env.MCP_TEST_GATE=f.gate;
  await promptly(apply(c.ctx,f.config));
  assert.equal(c.tools.size,0);assert.equal(c.instructions(),'');
  await assert.rejects(c.resource().request({method:'resources/list'},{signal:new AbortController().signal}),/disconnected/);
  await until(()=>read(f.log).some(e=>e.event==='initialize'));
  f.open();await until(()=>c.tools.size===1&&c.instructions().includes('Fixture instructions'));
  const tool=c.tools.values().next().value;
  await tool.execute({}, {signal:new AbortController().signal});
  assert.deepEqual(await c.resource().request({method:'resources/list'},{signal:new AbortController().signal}),{resources:[]});
});

await scenario('default startup mode preserves the blocking barrier',{startupMode:undefined},async(f,c)=>{
  // A schema default must preserve the old API contract, including non-Desktop callers.
  delete f.config.startupMode;
  f.config.env.MCP_TEST_GATE_PHASE='initialize';f.config.env.MCP_TEST_GATE=f.gate;
  let done=false;const boot=apply(c.ctx,f.config).then(()=>{done=true;});
  try{await until(()=>read(f.log).some(e=>e.event==='initialize'));assert.equal(done,false);f.open();await boot;assert.equal(c.tools.size,1);}finally{f.open();await boot;}
});

await scenario('strict service waits despite background configuration',{failOnStartupError:true},async(f,c)=>{
  f.config.env.MCP_TEST_GATE_PHASE='initialize';f.config.env.MCP_TEST_GATE=f.gate;
  let done=false;const boot=apply(c.ctx,f.config).then(()=>{done=true;});
  try{await until(()=>read(f.log).some(e=>e.event==='initialize'));assert.equal(done,false);f.open();await boot;assert.equal(c.tools.size,1);}finally{f.open();await boot;}
});

await scenario('strict initial failure still rejects loader startup',{failOnStartupError:true,command:'/no/such/mcp'},async(f,c)=>{
  await assert.rejects(apply(c.ctx,f.config),/initial connection/);
});

await scenario('optional failure is contained and reported',{command:'/no/such/mcp'},async(f,c)=>{
  await promptly(apply(c.ctx,f.config));
  await until(()=>c.logs.some(([level,m])=>level==='warn'&&m.includes('background initialization failed')));
  assert.equal(c.tools.size,0);
});

for(const phase of ['initialize','tools/list','server/discover']){
  await scenario('shutdown while '+phase+' is pending',{versionNegotiation:phase==='server/discover'?'auto':'legacy'},async(f,c)=>{
    f.config.env.MCP_TEST_GATE_PHASE=phase;f.config.env.MCP_TEST_GATE=f.gate;
    await promptly(apply(c.ctx,f.config));await until(()=>read(f.log).some(e=>e.event===phase));
    await c.dispose();f.open();await sleep(30);assert.equal(c.tools.size,0);
  });
}

await scenario('initial failure reconnects in background and publishes tools',{
  reconnect:{enabled:true,initialDelayMs:10,maxDelayMs:20,maxAttempts:2},env:{MCP_TEST_FIRST_FAIL_FILE:path.join(dir,'first-failure')}
},async(f,c)=>{
  await promptly(apply(c.ctx,f.config));await until(()=>c.tools.size===1);
  assert.equal(read(f.log).filter(e=>e.event==='spawn').length,2);
  assert(!read(f.log).some(e=>e.event==='server/discover'));
});

await scenario('shutdown cancels reconnect backoff',{
  reconnect:{enabled:true,initialDelayMs:150,maxDelayMs:150,maxAttempts:2},env:{MCP_TEST_FIRST_FAIL_FILE:path.join(dir,'backoff-failure')}
},async(f,c)=>{
  await promptly(apply(c.ctx,f.config));await until(()=>c.logs.some(([,m])=>m.includes('retrying in')));
  await c.dispose();await sleep(220);assert.equal(read(f.log).filter(e=>e.event==='spawn').length,1);
});

await scenario('tool list change after background readiness is synchronized',{
  env:{MCP_TEST_CHANGE_FILE:path.join(dir,'tool-change')}
},async(f,c)=>{
  await apply(c.ctx,f.config);await until(()=>c.tools.size===1);
  fs.writeFileSync(f.config.env.MCP_TEST_CHANGE_FILE,'1');await until(()=>c.tools.size===2);
});

// Use actual Cordis fibers for HMR/unload: the loader must settle before the gate,
// and a new instance with the same server namespace must not inherit old tools.
{
  const ctx=new Context(),tools=new Map();
  ctx.provide('tools',{register(t){assert(!tools.has(t.name));tools.set(t.name,t);return()=>tools.delete(t.name);}});
  const f=fixture();f.config.env.MCP_TEST_GATE_PHASE='initialize';f.config.env.MCP_TEST_GATE=f.gate;
  let fiber=ctx.plugin(plugin,f.config);
  try{
    await promptly(fiber.await());assert.equal(tools.size,0);
    await until(()=>read(f.log).some(e=>e.event==='initialize'));
    fiber.dispose();await fiber.await();
    f.open();await sleep(30);assert.equal(tools.size,0);
    fiber=ctx.plugin(plugin,f.config);await fiber.await();await until(()=>tools.size===1);
    await fiber.restart();await until(()=>tools.size===1);
  }finally{fiber.dispose();await fiber.await();ctx.fiber.dispose();await ctx.fiber.await();}
  assert.equal(tools.size,0);
  for(const e of read(f.log).filter(e=>e.event==='spawn'))assert.throws(()=>process.kill(e.pid,0),{code:'ESRCH'});
  results.push('real Cordis background activation, unload and HMR restart');
}
assert.equal(Config({transport:'stdio',serverName:'Default',command:process.execPath}).startupMode,'blocking');
assert.equal(Config({transport:'streamable-http',serverName:'Http',url:'http://127.0.0.1',startupMode:'background'}).startupMode,'background');
assert.throws(()=>Config({transport:'stdio',serverName:'Invalid',command:process.execPath,startupMode:'unknown'}));
await assert.rejects(apply(context().ctx,{startupMode:'unknown'}),/invalid startupMode/);
assert.equal(rejected.length,0);
console.log(JSON.stringify({passed:results.length,cases:results}));
