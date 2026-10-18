#!/usr/bin/env python3
"""Run actual DOM click navigation in headless Chromium, without npm installs."""
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
CASES = r'''
async function scenario(mode, language = 'zh') {
  document.body.innerHTML = `<aside data-pane="sidebar"><div class="shell_settingsArea">
    <button id="account">avatar</button></div>
    <button id="main">usage</button><button id="toggle">arrow</button></aside>`;
  const trigger = document.querySelector('#account');
  let triggerClicks = 0, settingsClicks = 0, usageClicks = 0, toggles = 0;
  const usageLabel = language === 'zh' ? '使用统计' : 'Usage Statistics';
  const panel = () => {
    const dialog = document.createElement('div');
    dialog.setAttribute('role', 'dialog');
    dialog.dataset.shortcutModal = 'settings';
    dialog.innerHTML = '<nav><button>' + usageLabel + '</button></nav>';
    dialog.querySelector('button').onclick = () => usageClicks++;
    document.body.append(dialog);
  };
  if (mode !== 'legacy') {
    trigger.setAttribute('aria-haspopup', 'menu');
    trigger.setAttribute('aria-expanded', 'false');
  }
  const menu = () => {
    const list = document.createElement('div');
    list.setAttribute('role', 'menu');
    list.innerHTML = '<button role="menuitem"><span class="menu_itemLabel">' +
      (mode === 'unknown' ? 'Other' : language === 'zh' ? '设置' : 'Settings') + '</span></button>' +
      '<button role="menuitem">退出登录</button>';
    list.firstElementChild.onclick = () => {
      settingsClicks++;
      trigger.setAttribute('aria-expanded', 'false');
      list.remove();
      setTimeout(panel, 10);
    };
    list.lastElementChild.onclick = () => { throw new Error('must never select sign out'); };
    document.body.append(list);
  };
  trigger.onclick = () => {
    triggerClicks++;
    if (mode === 'legacy') { setTimeout(panel, 10); return; }
    if (trigger.getAttribute('aria-expanded') === 'true') {
      trigger.setAttribute('aria-expanded', 'false');
      document.querySelector('[role="menu"]')?.remove();
    } else {
      trigger.setAttribute('aria-expanded', 'true');
      setTimeout(menu, 10);
    }
  };
  document.querySelector('#main').onclick = () => openUsageSettings(() => usageLabel);
  document.querySelector('#toggle').onclick = () => toggles++;
  if (mode === 'existing') panel();
  if (mode === 'unrelated') document.body.insertAdjacentHTML('beforeend', '<div role="dialog">unrelated</div>');
  if (mode === 'already-menu') { trigger.setAttribute('aria-expanded', 'true'); menu(); }
  document.querySelector('#toggle').click();
  if (triggerClicks || settingsClicks || usageClicks || toggles !== 1) throw new Error('arrow opens settings');
  document.querySelector('#main').click();
  await new Promise(resolve => setTimeout(resolve, mode === 'unknown' ? 1200 : 200));
  const expected = {
    modern: [1, 1, 1], legacy: [1, 0, 1], existing: [0, 0, 1],
    unrelated: [0, 0, 0], 'already-menu': [0, 1, 1], unknown: [2, 0, 0],
  }[mode];
  if (JSON.stringify([triggerClicks, settingsClicks, usageClicks]) !== JSON.stringify(expected))
    throw new Error(mode + ': ' + JSON.stringify({triggerClicks, settingsClicks, usageClicks}));
  if (document.querySelector('[role="menu"]')) throw new Error(mode + ': menu left open');
  return mode + '/' + language;
}
(async () => {
  try {
    const passed = [];
    for (const mode of ['modern', 'legacy', 'existing', 'unrelated', 'already-menu', 'unknown'])
      passed.push(await scenario(mode));
    passed.push(await scenario('modern', 'en'));
    document.body.innerHTML = '<pre id="report"></pre>';
    document.querySelector('#report').textContent = JSON.stringify({passed});
  } catch (error) {
    document.body.innerHTML = '<pre id="report"></pre>';
    document.querySelector('#report').textContent = JSON.stringify({error: error.message});
  }
})();
'''

with tempfile.TemporaryDirectory(prefix='dsh-usage-browser-') as directory:
    page = Path(directory) / 'test.html'
    page.write_text('<!doctype html><body><script>' + (BASE / 'open-usage-settings.js').read_text() + CASES + '</script>')
    result = subprocess.run([shutil.which('chromium'), '--headless', '--no-sandbox', '--disable-gpu',
                             '--user-data-dir=' + str(Path(directory) / 'profile'), '--dump-dom',
                             '--virtual-time-budget=5000', page.as_uri()],
                            capture_output=True, text=True, timeout=20)
    match = re.search(r'<pre id="report">(.*?)</pre>', result.stdout, re.S)
    assert match, result.stdout + result.stderr
    report = json.loads(html.unescape(match[1]))
    assert 'error' not in report, report
    assert len(report['passed']) == 7, report
    print(json.dumps(report, ensure_ascii=False))
