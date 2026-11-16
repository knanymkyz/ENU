const { chromium } = require('playwright');
(async () => {
  const [,, out, floor, toggles, w, scheme] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +(w||1500), height: 1100 }, colorScheme: scheme||'light' });
  const fs = require('fs'); const body = fs.readFileSync('/home/user/ENU/agents/A5_plan/LIB_A5.html','utf8');
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">'+body+'</body></html>');
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.waitForTimeout(800);
  if (floor) await p.click(`.tabs button[data-f="${floor}"]`);
  for (const t of (toggles||'').split(',').filter(Boolean)) await p.check('#'+t);
  if (out.includes('full')) await p.screenshot({ path: out, fullPage: true });
  else { const el = await p.$(`.svgbox[data-f="${floor||1}"]`); await el.screenshot({ path: out }); }
  console.log('errs', errs.length, errs.join('|'), 'scrollW', await p.evaluate(()=>document.documentElement.scrollWidth));
  await b.close();
})();
