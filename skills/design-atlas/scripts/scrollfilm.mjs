#!/usr/bin/env node
// scrollfilm.mjs - render a scroll-through film of a page (QA for scroll stories). No npm deps (Node >= 22).
//
//   node scripts/scrollfilm.mjs <url> <outDir> [--size 1280x800] [--seconds 18] [--fps 30]
//                               [--story "#story"] [--mp4 film.mp4] [--scan scan.png]
//                               [--scheme light|dark] [--reduced]
// The colour scheme is pinned (default light) so the film never follows the host OS theme.
//
// Scrolls from the top to the end of --story (default: the whole page) on an eased timeline with a
// 1.6 s hold at each end, saving one JPEG per frame. If the page exposes window.__frame(dtMs)
// (a "capture mode", e.g. ?capture in examples/*), each frame is stepped deterministically;
// otherwise it waits two animation frames per step (real-time effects will look sped up/slowed down).
// With ffmpeg on PATH it encodes --mp4 (H.264, yuv420p, faststart) and a 1-fps --scan contact sheet:
// look at the scan before sending a film to anyone.
import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const VERSION = '2026.10.10-4';
const args = process.argv.slice(2);
if (args.includes('--version')) { console.log('scrollfilm.mjs ' + VERSION); process.exit(0); }
const opt = (n, d) => (args.includes(n) ? args[args.indexOf(n) + 1] : d);
const pos = args.filter((a, i) => !a.startsWith('--') && !(i > 0 && args[i - 1].startsWith('--')));
const [url, out] = pos;
if (!url || !out) { console.error('usage: node scrollfilm.mjs <url> <outDir> [--size WxH] [--seconds N] [--fps N] [--story sel] [--mp4 file] [--scan file] [--scheme light|dark] [--reduced]'); process.exit(2); }
if (pos.length > 2) { console.error(`unexpected arguments: ${pos.slice(2).join(' ')} (use --size WxH --seconds N)`); process.exit(2); }
const [W, H] = opt('--size', '1280x800').split('x').map(Number);
const scheme = opt('--scheme', 'light'), reduced = args.includes('--reduced');
const FPS = +opt('--fps', '30'), N = Math.round(+opt('--seconds', '18') * FPS), story = opt('--story', '');
const CHROME = [process.env.CHROME, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'].find((p) => p && existsSync(p));
if (!CHROME) { console.error('Chrome not found; set $CHROME'); process.exit(2); }
mkdirSync(out, { recursive: true });

const profile = mkdtempSync(join(tmpdir(), 'film-'));
const port = 9900 + Math.floor(Math.random() * 90);
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`,
  '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', '--force-color-profile=srgb', 'about:blank'], { stdio: 'ignore' });
const stop = () => { try { chrome.kill('SIGKILL'); } catch {} try { rmSync(profile, { recursive: true, force: true }); } catch {} };
const hard = setTimeout(() => { console.error('timeout: gave up after 15 min'); stop(); process.exit(2); }, 900_000);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const within = (p, ms, what) => Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error(`${what} took over ${ms / 1000} s`)), ms))]);
const log = (m) => console.error(`[scrollfilm] ${m}`);

let code = 0;
try {
  let wsUrl;
  for (let i = 0; i < 75 && !wsUrl; i++) {
    try { wsUrl = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === 'page')?.webSocketDebuggerUrl; } catch {}
    if (!wsUrl) await sleep(200);
  }
  if (!wsUrl) throw new Error('Chrome did not start');
  const ws = new WebSocket(wsUrl); await new Promise((r) => ws.addEventListener('open', r, { once: true }));
  let id = 0; const pend = new Map(); const lis = [];
  ws.addEventListener('message', (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
    else lis.forEach((f) => f(m));
  });
  const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
  const ev = async (expression) => (await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true })).result.value;

  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 768 });
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: scheme },
    { name: 'prefers-reduced-motion', value: reduced ? 'reduce' : 'no-preference' }] });
  const loaded = new Promise((r) => lis.push((m) => m.method === 'Page.loadEventFired' && r()));
  log(`loading ${url} at ${W}x${H}, ${scheme}${reduced ? ', reduced motion' : ''}`);
  await send('Page.navigate', { url }); await within(loaded, 30_000, 'page load');
  await within(ev('document.fonts.ready.then(() => new Promise((r) => setTimeout(r, 500)))'), 10_000, 'fonts');
  const L = await ev(`(() => { const s = ${JSON.stringify(story)} && document.querySelector(${JSON.stringify(story)});
    return s ? s.offsetTop + s.offsetHeight - innerHeight : document.documentElement.scrollHeight - innerHeight; })()`);
  const stepped = await ev('typeof window.__frame === "function"');
  const dwell = Math.round(1.6 * FPS), move = Math.max(1, N - 2 * dwell);
  const ease = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const dt = (1000 / FPS).toFixed(2);
  log(`${N} frames, ${stepped ? 'stepped via window.__frame' : 'real-time'}, scroll length ${L}px`);
  for (let k = 0; k < N; k++) {
    if (k % FPS === 0) log(`frame ${k}/${N}`);
    const x = k < dwell ? 0 : k >= N - dwell ? 1 : (k - dwell) / move;
    const y = Math.round(L * (0.85 * x + 0.15 * ease(x)));
    await within(ev(stepped ? `scrollTo(0, ${y}); window.__frame(${dt}); true`
      : `scrollTo(0, ${y}); new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => r(true))))`), 20_000, `frame ${k} step`);
    const shot = await within(send('Page.captureScreenshot', { format: 'jpeg', quality: 88 }), 20_000, `frame ${k} capture`);
    writeFileSync(join(out, `f${String(k).padStart(4, '0')}.jpg`), Buffer.from(shot.data, 'base64'));
  }
  ws.close();
  console.log(`frames: ${N} at ${FPS} fps, scroll length ${L}px, ${stepped ? 'stepped via window.__frame' : 'real-time (no __frame hook)'}`);
} catch (e) {
  console.error(e.message); code = 1;
} finally { clearTimeout(hard); stop(); }

const mp4 = opt('--mp4'), scan = opt('--scan');
if (!code && (mp4 || scan)) {
  const has = spawnSync('ffmpeg', ['-version']).status === 0;
  if (!has) { console.error('ffmpeg not found: frames kept, no mp4/scan'); }
  else {
    if (mp4) {
      const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', join(out, 'f%04d.jpg'),
        '-c:v', 'libx264', '-crf', '22', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', mp4], { stdio: 'inherit' });
      if (r.status === 0) console.log(`mp4: ${mp4}`); else code = 1;
    }
    if (scan && mp4) {
      const rows = Math.max(1, Math.ceil(N / FPS / 6));   // one tile per second, 6 per row, no empty rows
      const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', mp4, '-vf', `fps=1,scale=320:-1,tile=6x${rows}`, '-frames:v', '1', scan], { stdio: 'inherit' });
      if (r.status === 0) console.log(`scan: ${scan}`); else code = 1;
    }
  }
}
process.exit(code);
