#!/usr/bin/env node
// shoot.mjs - Step 7 screenshots + layout probes with headless Chrome over CDP. No npm deps (Node >= 22).
//
//   node scripts/shoot.mjs <url> <outDir> [--widths 320,390,768,1280] [--dark] [--reduced] [--viewport-only]
//   node scripts/shoot.mjs <url> <outDir> --jobs jobs.json
//   node scripts/shoot.mjs "<url>?capture" <outDir> --story "#story" --at 0,.15,.3,.5,.7,.9,1 --widths 390,1280
//   add --sheet sheet.png to any run for a contact sheet of every shot (open it and look)
//
// Per width it loads the page, waits for fonts, scrolls the whole page in steps (so play-once
// reveals fire), returns to the top, then saves a full-page PNG (or viewport only) and prints
// probes as JSON: horizontal overflow and its widest offenders, elements still invisible after
// the scroll pass, text clipped by an overflow-hidden box, Thai words split across two lines
// (Intl.Segmenter word boundaries vs the rendered line boxes), interactive targets under 24x24 px,
// loaded fonts, <html lang>, h1 count, images without alt, console errors. Exit code 1 when a probe fails.
// Viewport-only jobs ("full": false) skip the slow full-page scroll pass unless "scrollPass": true.
//
// Job file entries: { name, width, height?, scheme?: "light"|"dark", reduce?: bool, full?: bool,
//   scrollTo?: "css selector" | px, eval?: "js to run before the shot", wait?: ms,
//   hover?: "css selector" | [x, y]  (real mouse move: synthetic PointerEvents don't trigger :hover),
//   report?: "js expression"  (its value is returned in the JSON as `report`),
//   throttle?: 4  (CPU slowdown factor, e.g. to time window.__frame() like a mid-range phone),
//   query?: "?state=empty"  (appended to the URL for this job), scrollPass?: bool }
// Every job runs with the HTTP cache disabled (jobs share one tab; cached images would skew weights).
// LCP: getEntriesByType('largest-contentful-paint') is empty here — use a buffered observer in "report":
//   new Promise((r) => new PerformanceObserver((l) => { const e = l.getEntries().at(-1);
//     r(e && { ms: Math.round(e.startTime), el: e.element && e.element.tagName }); })
//     .observe({ type: 'largest-contentful-paint', buffered: true }))   (use a job without scrollTo)
// Mark scroll-story containers with data-story: their off-beat copy is hidden by design and is not
// reported as invisible (check those beats with viewport jobs instead).
// Story pages: full-page shots of sticky/pinned stories show a frozen stage over an empty runway;
// check stories with viewport-only jobs ("full": false) at scrollTo positions instead.
// --timeout <s> overrides the limit (default 60 s + 20 s per job); on timeout the jobs finished so far
// are still printed.
// Focus emulation is on, so focus/focusin handlers fire in headless runs.
// Chrome: $CHROME, else the usual macOS / Linux paths. Scroll-linked effects are captured at the
// scroll position of the shot; use scrollTo jobs to capture them mid-way.
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';

const VERSION = '2026.10.10-6';
// Thai compounds seen broken mid-word by Chrome's dictionary in design-atlas tests (Oct 2026)
const THAI_COMPOUNDS = ['วิดีโอคอล', 'มือถือ', 'โรงพยาบาล', 'ตัวเอง', 'ใบอนุญาต', 'วันเดียวกัน', 'ส่วนบุคคล', 'รอคิว',
  'ไนอาซินาไมด์', 'ใช้คู่กัน', 'กลับมา', 'หน้าประตู', 'เสี้ยววินาที', 'ชั่วโมง', 'ลำคอ', 'ก่อน', 'คืนเดียว', 'เคลื่อนไหว']
const args = process.argv.slice(2);
if (args.includes('--version')) { console.log('shoot.mjs ' + VERSION); process.exit(0); }
if (args.includes('--thai-words')) THAI_COMPOUNDS.push(...args[args.indexOf('--thai-words') + 1].split(',').filter(Boolean));
const flag = (n) => args.includes(n);
const opt = (n, d) => (args.includes(n) ? args[args.indexOf(n) + 1] : d);
const [url, outDir] = args.filter((a, i) => !a.startsWith('--') && !(i > 0 && args[i - 1].startsWith('--') && ['--widths', '--jobs', '--timeout', '--story', '--at', '--sheet', '--thai-words'].includes(args[i - 1])));
if (!url || !outDir) {
  console.error('usage: node shoot.mjs <url> <outDir> [--widths 320,390,768,1280] [--dark] [--reduced] [--viewport-only] [--jobs file.json]');
  process.exit(2);
}
mkdirSync(outDir, { recursive: true });

const storySel = opt('--story'), storyAt = opt('--at', '0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1').split(',').map(Number);
const jobs = opt('--jobs')
  ? JSON.parse(readFileSync(opt('--jobs'), 'utf8'))
  : storySel
  ? opt('--widths', '390,1280').split(',').map(Number).flatMap((w) => storyAt.map((f) => ({
      name: `story-${w}-${String(Math.round(f * 100)).padStart(3, '0')}${flag('--dark') ? '-dark' : ''}`,
      width: w, scheme: flag('--dark') ? 'dark' : 'light', reduce: flag('--reduced'), full: false, story: storySel, at: f })))
  : opt('--widths', '390,1280').split(',').map(Number).map((w) => ({
      name: `shot-${w}${flag('--dark') ? '-dark' : ''}${flag('--reduced') ? '-reduced' : ''}`,
      width: w, scheme: flag('--dark') ? 'dark' : 'light', reduce: flag('--reduced'), full: !flag('--viewport-only'),
    }));

const CHROME = [process.env.CHROME, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'].find((p) => p && existsSync(p));
if (!CHROME) { console.error('Chrome not found; set $CHROME'); process.exit(2); }

const profile = mkdtempSync(join(tmpdir(), 'shoot-'));
const port = 9300 + Math.floor(Math.random() * 600);
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`,
  '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', '--force-color-profile=srgb', 'about:blank'],
  { stdio: 'ignore' });
const cleanup = () => { try { chrome.kill('SIGKILL'); } catch {} try { rmSync(profile, { recursive: true, force: true }); } catch {} };
const limitMs = opt('--timeout') ? +opt('--timeout') * 1000 : 60_000 + 20_000 * jobs.length;  // WebGL pages need longer
const report = [];
const hardStop = setTimeout(() => {
  console.error(`timeout: gave up after ${limitMs / 1000} s; printing the ${report.length} finished job(s)`);
  cleanup(); console.log(JSON.stringify(report, null, 1)); process.exit(2);
}, limitMs);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function pageWs() {
  for (let i = 0; i < 75; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
      const p = list.find((t) => t.type === 'page');
      if (p) return p.webSocketDebuggerUrl;
    } catch {}
    await sleep(200);
  }
  throw new Error('Chrome did not start');
}

let failed = false;
try {
  const ws = new WebSocket(await pageWs());
  await new Promise((r) => ws.addEventListener('open', r, { once: true }));
  let id = 0;
  const pending = new Map();
  const listeners = [];
  ws.addEventListener('message', (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const { res, rej } = pending.get(m.id); pending.delete(m.id);
      m.error ? rej(new Error(m.error.message)) : res(m.result);
    } else listeners.forEach((fn) => fn(m));
  });
  const send = (method, params = {}) => new Promise((res, rej) => {
    const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params }));
  });
  const evaluate = async (expression) =>
    (await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true })).result.value;
  const once = (method) => new Promise((r) => {
    const fn = (m) => { if (m.method === method) { listeners.splice(listeners.indexOf(fn), 1); r(m.params); } };
    listeners.push(fn);
  });

  await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setFocusEmulationEnabled', { enabled: true });
  await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true });
  let consoleErrors = [];
  listeners.push((m) => {
    if (m.method === 'Runtime.exceptionThrown') consoleErrors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
    if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') consoleErrors.push(m.params.args.map((a) => a.value ?? a.description).join(' '));
  });

  for (const job of jobs) {
    consoleErrors = [];
    const height = job.height ?? (job.width < 768 ? 844 : 800);
    await send('Emulation.setDeviceMetricsOverride', { width: job.width, height, deviceScaleFactor: 1, mobile: job.width < 768 });
    await send('Emulation.setEmulatedMedia', { features: [
      { name: 'prefers-color-scheme', value: job.scheme || 'light' },
      { name: 'prefers-reduced-motion', value: job.reduce ? 'reduce' : 'no-preference' }] });
    await send('Emulation.setCPUThrottlingRate', { rate: job.throttle || 1 });
    const loaded = once('Page.loadEventFired');
    await send('Page.navigate', { url: url + (job.query || '') });
    await Promise.race([loaded, sleep(30_000)]);
    await evaluate('Promise.race([document.fonts.ready.then(() => true), new Promise((r) => setTimeout(() => r(false), 5000))])');
    await sleep(800);
    const H = await evaluate('document.documentElement.scrollHeight');
    if (job.scrollPass ?? job.full !== false) {         // fire play-once reveals before a full-page shot
      const stepY = Math.max(Math.round(height * 0.6), Math.ceil(H / 40));   // ≤ ~40 steps even on very long pages
      for (let y = 0; y <= H; y += stepY) { await evaluate(`scrollTo(0, ${y})`); await sleep(120); }
      await sleep(400);
    }
    let target = 0;
    if (job.story) {
      target = await evaluate(`(() => { const s = document.querySelector(${JSON.stringify(job.story)}); if (!s) return 0;
        const top = s.getBoundingClientRect().top + scrollY; return Math.round(top + ${job.at} * Math.max(0, s.offsetHeight - innerHeight)); })()`);
    } else if (typeof job.scrollTo === 'string') {
      target = await evaluate(`(() => { const e = document.querySelector(${JSON.stringify(job.scrollTo)}); if (!e) return 0;
        return Math.round(e.getBoundingClientRect().top + scrollY - innerHeight * 0.3); })()`);
    } else if (typeof job.scrollTo === 'number') target = job.scrollTo;
    await evaluate(`scrollTo(0, ${target})`);
    // capture-mode pages: approach the target in small steps so trails/particles look as they do mid-scroll
    await evaluate(`(() => { if (typeof window.__frame !== 'function') return; const y = ${target};
      for (let i = 14; i >= 0; i--) { scrollTo(0, Math.max(0, y - i * 7)); window.__frame(33); }
      for (let i = 0; i < 6; i++) window.__frame(33); })()`);
    await sleep(600);
    if (job.hover) {
      const [hx, hy] = Array.isArray(job.hover) ? job.hover : await evaluate(`(() => { const e = document.querySelector(${JSON.stringify(job.hover)});
        if (!e) return [0, 0]; const r = e.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()`);
      for (let i = 1; i <= 8; i++) {   // approach the target so proximity effects (magnetic, trails) react
        await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: hx - 80 + i * 10, y: hy - 40 + i * 5 });
        await sleep(40);
      }
      await sleep(job.wait ?? 400);
    }
    if (job.eval) { await evaluate(job.eval); await sleep(job.wait ?? 400); }
    const reported = job.report ? await evaluate(job.report) : undefined;

    const probe = await evaluate(`(() => {
      const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
      const label = (e) => (e.getAttribute('aria-label') || e.textContent || e.tagName).trim().replace(/\\s+/g, ' ').slice(0, 40);
      const W = ${job.width}; // the emulated width: mobile emulation zooms out to fit wide content, so innerWidth can lie
      const wide = [...document.body.querySelectorAll('*')].filter((e) => { const r = e.getBoundingClientRect();
        return r.right > W + 1 && getComputedStyle(e).position !== 'fixed'; })
        .slice(0, 5).map((e) => e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\\s+/)[0] : '') + ' right=' + Math.round(e.getBoundingClientRect().right));
      const effOpacity = (e) => { let o = 1;            // opacity multiplies down the tree; visibility inherits
        for (let n = e; n && n.nodeType === 1; n = n.parentElement) { const st = getComputedStyle(n); o *= parseFloat(st.opacity); if (o < 0.05) break; }
        return getComputedStyle(e).visibility === 'hidden' ? 0 : o; };
      const invisible = [...document.body.querySelectorAll('h1,h2,h3,p,li,img,figure,section > *,[data-reveal]')]
        .filter((e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && effOpacity(e) < 0.05
          && !e.closest('[aria-hidden="true"], [data-story]'); })   // [data-story]: beats are hidden off-beat by design
        .slice(0, 8).map(label);
      const small = [...document.querySelectorAll('a,button,summary,input,select,textarea,[role=button]')].filter(vis)
        .filter((e) => { const r = e.getBoundingClientRect(); return (r.width < 24 || r.height < 24) && !(e.tagName === 'A' && getComputedStyle(e).display === 'inline'); })
        .slice(0, 8).map((e) => label(e) + ' ' + Math.round(e.getBoundingClientRect().width) + 'x' + Math.round(e.getBoundingClientRect().height));
      const clipped = [...document.body.querySelectorAll('*')].filter((e) => {
        if (e.closest('[aria-hidden="true"], [data-story]')) return false;
        if (e.clientWidth <= 2 || e.clientHeight <= 2) return false;   // visually-hidden (sr-only) text is clipped on purpose
        const st = getComputedStyle(e);
        if (st.overflowX === 'visible' && st.overflowY === 'visible') return false;
        if (st.textOverflow === 'ellipsis' || (st.webkitLineClamp && st.webkitLineClamp !== 'none')) return false;  // deliberate truncation
        if (![...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) return false;
        return e.scrollHeight > e.clientHeight + 2 || e.scrollWidth > e.clientWidth + 2;
      }).slice(0, 6).map((e) => label(e) + ' ' + e.clientWidth + 'x' + e.clientHeight + ' (content ' + e.scrollWidth + 'x' + e.scrollHeight + ')');
      const thaiSplit = [];
      // Chrome's line breaker and Intl.Segmenter share ICU's Thai dictionary, so breaks inside a segmenter
      // word only catch forced breaks; real-world bad breaks fall where that dictionary is wrong. Also check
      // compounds seen split in Chrome (extend with --thai-words a,b,c).
      const compounds = ${JSON.stringify(THAI_COMPOUNDS)};
      const spansLines = (node, i, len) => { const r = document.createRange(); r.setStart(node, i); r.setEnd(node, i + len);
        const tops = [...new Set([...r.getClientRects()].filter((q) => q.width > 0).map((q) => Math.round(q.top)))];
        return tops.length > 1 && Math.max(...tops) - Math.min(...tops) > 4; };
      { const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
        while ((n = walker.nextNode()) && thaiSplit.length < 12) {
          if (!/[\u0E00-\u0E7F]/.test(n.data) || !n.parentElement || n.parentElement.closest('script,style,[aria-hidden="true"]')) continue;
          for (const c of compounds) { let i = n.data.indexOf(c); while (i >= 0) { if (spansLines(n, i, c.length)) thaiSplit.push(c); i = n.data.indexOf(c, i + 1); } }
        } }
      if (typeof Intl.Segmenter === 'function') {
        const seg = new Intl.Segmenter('th', { granularity: 'word' });
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let n, budget = 6000;
        while ((n = walker.nextNode()) && thaiSplit.length < 12 && budget > 0) {
          const p = n.parentElement;
          if (!p || !/[\u0E00-\u0E7F]/.test(n.data) || p.closest('script,style,[aria-hidden="true"]')) continue;
          for (const w of seg.segment(n.data)) {
            if (--budget <= 0) break;
            if (!w.isWordLike || w.segment.length < 2 || !/[\u0E00-\u0E7F]/.test(w.segment)) continue;
            const r = document.createRange(); r.setStart(n, w.index); r.setEnd(n, w.index + w.segment.length);
            const tops = [...new Set([...r.getClientRects()].filter((q) => q.width > 0).map((q) => Math.round(q.top)))];
            if (tops.length > 1 && Math.max(...tops) - Math.min(...tops) > 4) thaiSplit.push(w.segment);
          }
        }
      }
      return {
        clippedText: clipped, thaiWordSplits: thaiSplit,
        overflowX: Math.max(document.documentElement.scrollWidth, innerWidth) - W, overflowOffenders: wide,
        invisibleAfterScroll: invisible, smallTargets: small,
        fonts: [...new Set([...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family.replace(/"/g, '')))],
        lang: document.documentElement.lang || null, h1Count: document.querySelectorAll('h1').length,
        imgsMissingAlt: [...document.images].filter((i) => !i.hasAttribute('alt')).length,
        docHeight: document.documentElement.scrollHeight,
      };
    })()`);
    const shot = job.full === false
      ? await send('Page.captureScreenshot', { format: 'png' })
      : await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true,
          clip: { x: 0, y: 0, width: job.width, height: probe.docHeight, scale: 1 } });
    const file = join(outDir, job.name + '.png');
    mkdirSync(dirname(file), { recursive: true });
    writeFileSync(file, Buffer.from(shot.data, 'base64'));
    const problems = [];
    if (probe.overflowX > 0) problems.push(`horizontal overflow ${probe.overflowX}px`);
    if (probe.invisibleAfterScroll.length) problems.push('content still invisible after scrolling');
    if (probe.clippedText.length) problems.push('text clipped by an overflow box');
    if (probe.thaiWordSplits.length) problems.push('Thai words split across lines (protect with .nw or <wbr>)');
    if (probe.smallTargets.length) problems.push('targets under 24x24');
    if (!probe.lang) problems.push('<html> has no lang');
    if (probe.h1Count !== 1) problems.push(`${probe.h1Count} h1 elements`);
    if (probe.imgsMissingAlt) problems.push(`${probe.imgsMissingAlt} img without alt`);
    if (consoleErrors.length) problems.push('console errors');
    if (problems.length) failed = true;
    report.push({ job: job.name, width: job.width, scheme: job.scheme || 'light', reduce: !!job.reduce, file,
      result: problems.length ? 'CHECK' : 'PASS', problems, ...probe, consoleErrors,
      ...(job.report ? { report: reported } : {}) });
  }
  const sheet = opt('--sheet');
  if (sheet && report.length) {   // contact sheet: a local HTML grid of the shots, rendered by the same Chrome
    const tiles = report.map((r) => `<figure><img src="${r.job}.png"><figcaption>${r.job} · ${r.result}${r.problems.length ? ' · ' + r.problems.join('; ') : ''}</figcaption></figure>`).join('');
    const html = `<!doctype html><meta charset="utf-8"><style>body{margin:0;padding:16px;background:#1b1c20;font:12px system-ui;color:#ddd}
      main{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}figure{margin:0}
      img{width:100%;max-height:560px;object-fit:cover;object-position:top;border-radius:6px;background:#000;display:block}
      figcaption{margin-top:4px;line-height:1.35}</style><main>${tiles}</main>`;
    const sheetHtml = join(outDir, '_sheet.html'); writeFileSync(sheetHtml, html);
    await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 1000, deviceScaleFactor: 1, mobile: false });
    const ld = once('Page.loadEventFired'); await send('Page.navigate', { url: 'file://' + (sheetHtml.startsWith('/') ? '' : process.cwd() + '/') + sheetHtml }); await ld;
    await evaluate('Promise.all([...document.images].map((i) => i.decode().catch(() => 0))).then(() => true)');
    const hgt = await evaluate('document.documentElement.scrollHeight');
    const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip: { x: 0, y: 0, width: 1600, height: hgt, scale: 1 } });
    writeFileSync(sheet, Buffer.from(shot.data, 'base64'));
    console.error('sheet: ' + sheet);
  }
  ws.close();
} catch (e) {
  console.error(e.message); failed = true;
} finally {
  clearTimeout(hardStop);
  cleanup();
}
console.log(JSON.stringify(report, null, 1));
process.exit(failed ? 1 : 0);
