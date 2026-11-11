// Export each carousel slide to a 1080x1350 PNG using Playwright + system Chrome.
//   node assets/export-png.js "assets/WWC ADS TEST.html" assets/export
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const htmlPath = path.resolve(process.argv[2] || 'assets/WWC ADS TEST.html');
  const outDir = path.resolve(process.argv[3] || 'assets/export');
  fs.mkdirSync(outDir, { recursive: true });

  let browser;
  try { browser = await chromium.launch({ channel: 'chrome' }); }
  catch (e) { browser = await chromium.launch(); } // fall back to Playwright's bundled Chromium
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  await page.goto('file://' + htmlPath, { waitUntil: 'networkidle' });

  // Print media => deck-stage lays every slide out at authored size in flow.
  await page.emulateMedia({ media: 'print' });
  // Give web fonts + layout a beat to settle.
  await page.evaluate(() => document.fonts.ready);
  await page.waitForSelector('html[data-fit="done"]', { timeout: 10000 }).catch(() => console.warn('fit script did not finish'));
  await page.waitForTimeout(800);

  const sections = await page.$$('deck-stage > section');
  console.log('Found ' + sections.length + ' slides');
  const files = [];
  for (let i = 0; i < sections.length; i++) {
    const file = path.join(outDir, 'slide-' + String(i + 1).padStart(2, '0') + '.png');
    await sections[i].screenshot({ path: file, omitBackground: !!process.env.TRANSPARENT });
    files.push(file);
    console.log('  wrote ' + path.basename(file));
  }

  await browser.close();
  console.log('Done: ' + files.length + ' PNGs in ' + outDir);
})().catch((e) => { console.error(e); process.exit(1); });
