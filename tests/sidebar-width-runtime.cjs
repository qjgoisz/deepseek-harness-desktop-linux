const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

// Execute the measurement code shipped in the preload, including the width
// guard. Replay animation frames on both sides of the button's position clamp.
const source = fs.readFileSync(0, 'utf8');
const start = source.indexOf('const width = Math.round(sidebar.getBoundingClientRect().width);');
const end = source.indexOf('\n\t\t}', start);
assert(start !== -1 && end > start, 'measurement block missing');
const code = source.slice(start, end);
const values = new Map();
let actualWidth = 280;
const context = {
  sidebar: { getBoundingClientRect: () => ({ width: actualWidth }) },
  root: { style: {
    getPropertyValue: key => values.get(key) ?? '',
    setProperty: (key, value) => values.set(key, value),
  } },
};
for (const width of [280, 264, 180, 129, 128, 119, 108, 80, 40, 0, 32, 88, 120, 0, 264, 420, 0]) {
  actualWidth = width;
  vm.runInNewContext(`{\n${code}\n}`, context);
  assert.equal(values.get('--dsh-linux-sidebar-width'), `${width}px`, `stale strip at width ${width}`);
  assert.equal(values.get('--dsh-linux-toggle-left'), `${Math.max(88, width - 40)}px`);
}
console.log('sidebar background tracks every animation frame, including zero');
