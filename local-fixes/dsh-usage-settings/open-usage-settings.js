// dsh-usage-settings-navigation:v1
function openUsageSettings(label) {
  const wanted = label();
  const findPanel = () => [...document.querySelectorAll('[role="dialog"]')].find(panel =>
    panel.matches('[data-shortcut-modal="settings"]') ||
    [...panel.querySelectorAll('nav button')].some(row => row.textContent?.trim() === wanted));
  const pick = panel => {
    const row = [...panel.querySelectorAll('nav button')].find(row => row.textContent?.trim() === wanted);
    row?.click();
  };
  const existing = findPanel();
  if (existing) { pick(existing); return; }
  // Do not open settings behind an unrelated modal dialog.
  if (document.querySelector('[role="dialog"]')) return;
  const column = document.querySelector('[data-pane="sidebar"], [class*="sidebarCol"]');
  const trigger = column?.querySelector('[class*="settingsArea"] button');
  if (!trigger) return;
  const accountMenu = trigger.getAttribute('aria-haspopup') === 'menu';
  const previousMenus = new Set(document.querySelectorAll('[role="menu"]'));
  const wasOpen = trigger.getAttribute('aria-expanded') === 'true';
  if (!accountMenu || !wasOpen) trigger.click();
  let selectedSettings = false;
  let tries = 0;
  const attempt = () => {
    const panel = findPanel();
    if (panel) { pick(panel); return; }
    if (accountMenu && !selectedSettings && trigger.getAttribute('aria-expanded') === 'true') {
      // Only inspect the menu opened by this trigger; never activate a row
      // in another plugin's already-open menu. DSH provides no menu item id.
      const menus = [...document.querySelectorAll('[role="menu"]')].filter(menu =>
        !previousMenus.has(menu) || wasOpen && previousMenus.size === 1);
      const rows = menus.flatMap(menu => [...menu.querySelectorAll('button[role="menuitem"]')]);
      const settings = rows.find(row => {
        const text = row.querySelector('[class*="itemLabel"]')?.textContent?.trim() ?? row.textContent?.trim();
        return !row.disabled && (/^(设置|Settings)$/i.test(text ?? '') ||
          /^(Control|Meta)\+,$/i.test(row.getAttribute('aria-keyshortcuts') ?? ''));
      });
      if (settings) { selectedSettings = true; settings.click(); }
    }
    if (++tries <= 20) window.setTimeout(attempt, 50);
    else if (accountMenu && !wasOpen && trigger.getAttribute('aria-expanded') === 'true') {
      // If a future DSH changes the menu contract, undo the menu we opened.
      trigger.click();
    }
  };
  window.setTimeout(attempt, 0);
}
