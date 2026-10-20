#!/usr/bin/env python3
import sys, subprocess, tempfile, re, html, json, argparse, shutil
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'tests'))
parser = argparse.ArgumentParser(description='Check personal sidebar geometry with the bundled sidebar CSS in an isolated headless browser.')
parser.add_argument('--app', type=Path, default=REPO / 'out-x64/resources/app')
parser.add_argument('--browser', default=shutil.which('chromium') or shutil.which('google-chrome'))
args = parser.parse_args()
if not args.browser:
    parser.error('chromium or google-chrome is required; alternatively pass --browser')
from test_kde_material import chrome, material, load
reveal=load('patch-fullscreen-reveal'); rounded=load('patch-personal-rounded')
css_sources=[]
for extra in (chrome.MAIN_EXTRA_CSS,chrome.WELCOME_EXTRA_CSS):
    source=rounded.transform_preload(reveal.transform(material.transform_preload(chrome.PRELOAD_FN.replace('__TITLEBAR_HEIGHT__','48').replace('__EXTRA_CSS__',extra))))
    css_sources.append(source.split('\tconst CSS = `',1)[1].split('`;',1)[0])
sidebar=(args.app / 'dsh/node_modules/@deepseek-ai/dsh-client-ui-sidebar/lib/client.js').read_text()
base_css=json.loads(re.search(r'const css = ("(?:[^"\\]|\\.)*");',sidebar)[1])
classes={key:re.search(r'"'+key+r'": "([^"]+)"',sidebar)[1] for key in ('root','collapsed','toggle','newSession')}
js=r'''
const root=document.documentElement, passed=[];
try {
for(let page=0;page<2;page++) {
 document.querySelector('#chrome').textContent=styles[page];
 for(const width of [264,280,420]) for(const collapsed of [false,true]) {
  root.style.setProperty('--dsh-linux-toggle-left',(width-40)+'px');
  document.querySelector('#sidebar-root').classList.toggle(classes.collapsed,collapsed);
  for(const state of ['normal','maximized','fullscreen']) for(const hover of [false,true]) for(const inactive of [false,true]) {
   root.toggleAttribute('data-fullscreen',state!=='normal');
   root.toggleAttribute('data-dsh-reveal-controls',hover);
   const lights=document.querySelector('#dsh-mac-lights');lights.toggleAttribute('data-inactive',inactive);
   const s=getComputedStyle(lights),toggle=document.querySelector('#toggle'),t=getComputedStyle(toggle),r=toggle.getBoundingClientRect();
   if(s.display!=='flex'||s.opacity!=='1'||s.visibility!=='visible'||s.pointerEvents!=='auto')throw Error('lights hidden');
   const expected=collapsed?128:width-40;
   if(r.x!==expected||r.y!==10||t.translate!=='none')throw Error(JSON.stringify({state,collapsed,width,hover,expected,x:r.x,y:r.y,translate:t.translate}));
   if(collapsed&&document.querySelector('#new').getBoundingClientRect().x!==88)throw Error('new-session moved');
   const b=lights.querySelector('button').getBoundingClientRect();
   if(document.elementFromPoint(b.x+b.width/2,b.y+b.height/2)!==lights.querySelector('button'))throw Error('lights not hit-testable');
   if(getComputedStyle(document.querySelector('#plugin')).translate!=='none')throw Error('plugin moved');
   if(getComputedStyle(document.querySelector('#dsh-fullscreen-reveal')).display!=='none')throw Error('hover strip active');
   passed.push([page,width,collapsed,state,hover,inactive]);
  }
 }
}
document.querySelector('#report').textContent=JSON.stringify({passed:passed.length});
}catch(e){document.querySelector('#report').textContent=JSON.stringify({error:e.message});}
'''
with tempfile.TemporaryDirectory(prefix='dsh-sidebar-geometry-') as directory:
    root=Path(directory);page=root/'test.html'
    page.write_text('<!doctype html><html data-dsh-mac-chrome data-windows-titlebar style="--dsh-windows-titlebar-height:48px"><style>'+base_css+'body{margin:0;min-height:100vh}.shell_sidebarCol{width:280px;height:100vh}</style><style id="chrome"></style><body><aside class="shell_sidebarCol"><div id="sidebar-root" class="'+classes['root']+'"><button id="toggle" class="'+classes['toggle']+'">toggle</button><button id="new" class="'+classes['newSession']+'">new</button></div></aside><button id="plugin" class="plugin_toggle">plugin</button><div id="dsh-fullscreen-reveal"></div><div id="dsh-mac-lights"><button class="close"></button><button class="minimize"></button><button class="maximize"></button></div><pre id="report"></pre><script>const styles='+json.dumps(css_sources)+',classes='+json.dumps(classes)+';'+js+'</script>')
    r=subprocess.run([args.browser,'--headless','--no-sandbox','--disable-gpu','--disable-background-networking','--no-first-run','--user-data-dir='+str(root/'profile'),'--dump-dom',page.as_uri()],capture_output=True,text=True,timeout=30)
    m=re.search(r'<pre id="report">(.*?)</pre>',r.stdout,re.S)
    assert m,r.stderr[-1000:]
    report=json.loads(html.unescape(m[1])); print(report);assert report=={'passed':144},report
