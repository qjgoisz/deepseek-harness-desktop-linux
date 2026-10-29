// Offline MCP fixture. Gates expose actual process/lifecycle races without network or credentials.
import fs from 'node:fs';
import readline from 'node:readline';
const env=process.env;
function log(event){if(env.MCP_TEST_LOG)fs.appendFileSync(env.MCP_TEST_LOG,JSON.stringify({pid:process.pid,event})+'\n');}
function once(file){if(!file)return false;try{fs.writeFileSync(file,'1',{flag:'wx'});return true;}catch(e){if(e.code!=='EEXIST')throw e;return false;}}
log('spawn');
if(once(env.MCP_TEST_FIRST_FAIL_FILE))process.exit(1);
const send=m=>process.stdout.write(JSON.stringify({jsonrpc:'2.0',...m})+'\n');
let changed=false;
const change=env.MCP_TEST_CHANGE_FILE&&setInterval(()=>{
  if(!changed&&fs.existsSync(env.MCP_TEST_CHANGE_FILE)){changed=true;send({method:'notifications/tools/list_changed'});}
},10);
change?.unref();
readline.createInterface({input:process.stdin}).on('line',async line=>{
  const m=JSON.parse(line);log(m.method);
  if(m.id===undefined)return;
  if(m.method===env.MCP_TEST_GATE_PHASE)while(!fs.existsSync(env.MCP_TEST_GATE))await new Promise(r=>setTimeout(r,5));
  if(m.method==='server/discover'||(m.method==='initialize'&&env.MCP_TEST_INIT_ERROR)){
    send({id:m.id,error:{code:-32601,message:'Fixture refuses request'}});return;
  }
  let result;
  if(m.method==='initialize')result={protocolVersion:'2025-11-25',capabilities:{tools:{listChanged:true},resources:{}},serverInfo:{name:'fixture',version:'1'},instructions:'Fixture instructions'};
  else if(m.method==='tools/list'){
    const tool=name=>({name,inputSchema:{type:'object',properties:{},additionalProperties:false}});
    result={tools:changed?[tool('echo'),tool('second')]:[tool('echo')]};
    if(once(env.MCP_TEST_DROP_FILE))setTimeout(()=>process.exit(0),30);
  }else if(m.method==='tools/call')result={content:[{type:'text',text:'ok'}]};
  else if(m.method==='resources/list')result={resources:[]};
  else{send({id:m.id,error:{code:-32601,message:'Unknown request'}});return;}
  send({id:m.id,result});
});
