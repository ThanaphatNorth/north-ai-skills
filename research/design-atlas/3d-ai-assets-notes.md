# Raw notes: 3D on the web + AI-generated visual assets (Higgsfield first)

Collected 2026-10-10 for `skills/design-atlas/references/3d-webgl.md` and `ai-assets-higgsfield.md`.
Every bullet names its source. "local test" = run in this session's scratchpad with ffmpeg 9.0.2 / OpenCV 5.0.0 / numpy 2.0.2 on macOS.
Web-search budget ran out near the end; items marked (unverified) were not re-checked.

## 1. Library versions (npm registry, queried 2026-10-10 with `npm view <pkg> dist-tags` / `time`)
| package | latest | published | other tags / peers |
|---|---|---|---|
| three | 0.186.1 (r186) | 2026-09-24 | — |
| @react-three/fiber | 9.8.1 | 2026-09-24 | peer react `>=19 <19.4`, three `>=0.156`; alpha 10.0.0-alpha.5 |
| @react-three/drei | 10.7.9 | 2026-09-25 | peer react ^19, fiber ^9.0.0, three >=0.159; alpha 11.0.0-alpha.7 |
| @react-three/postprocessing | 3.2.0 | — | peer postprocessing ^6.36, fiber >=9.7 |
| postprocessing | 6.39.5 | — | beta 7.0.0-beta.16 |
| @threlte/core | 8.6.1 | 2026-09-24 | peer svelte >=5, three >=0.172 |
| @tresjs/core | 5.9.3 | 2026-10-06 | peer vue >=3.4 |
| ogl | 1.0.11 | 2025-01-27 | — |
| @babylonjs/core | 9.30.0 | 2026-10-08 | — |
| playcanvas | 2.23.2 | 2026-10-09 | lts 1.77.0 |
| @google/model-viewer | 4.4.0 | 2026-10-09 | peer three ^0.183.0 |
| @splinetool/runtime | 2.0.75 | — | — |
| @splinetool/react-spline | 4.1.0 | 2025-07-15 | — |
| @gltf-transform/cli | 4.5.1 | 2026-09-28 | — |
| @sparkjsdev/spark | 2.3.1 | 2026-10-01 | — |
| @lumaai/luma-web | 0.2.2 | 2024-03-06 | no release since → treat as stale |
| gsap | 3.15.0 | — | @gsap/react 2.1.2 |
| lenis | 1.3.26 | — | — |
| react | 19.3.0 | — | — |

## 2. Bundle weights (jsDelivr files, gzip -9 measured locally)
- three@0.186.1 `three.module.min.js` 87 KB gz, imports `three.core.js` (core.min 101 KB gz) → ~188 KB gz untreeshaken WebGL build.
- `three.webgpu.min.js` 199 KB gz (+ imports three.core.js).
- @google/model-viewer@4.4.0 `model-viewer.min.js` 282 KB gz (bundles its renderer).
- @splinetool/runtime@2.0.75: `runtime.js` is a 36 KB gz loader importing ~100 chunks; shipped `runtime.standalone.webgl.js.gz` = 577,942 B, `runtime.standalone.webgpu.min.js.gz` = 493,575 B; optional `physics.wasm.gz` 586,267 B, `hana-ui.wasm.gz` 1,096,745 B (jsDelivr package listing).
- babylonjs@9.30.0 UMD `babylon.js` 1,809 KB gz (full, untreeshaken; ES `@babylonjs/core` tree-shakes).
- playcanvas@2.23.2 `playcanvas.min.mjs` 638 KB gz.
- Spark 2.3.1 `spark.module.js` 914 KB gz.

## 3. three.js WebGPURenderer / TSL (primary sources)
- Manual (repo `manual/pages/webgpurenderer.html` @ r186): WebGPURenderer = "modern alternative" to WebGLRenderer; WebGPU backend with automatic WebGL 2 fallback; node materials; TSL "transpiled to WGSL or GLSL depending on the available backend"; new post stack with MRT. Import `three/webgpu`, TSL from `three/tsl`. Async init: use `setAnimationLoop()` or `await renderer.init()`. `forceWebGL: true` to force WebGL2 backend. Migration: "Custom materials based on ShaderMaterial, RawShaderMaterial and modifications of built-in materials via onBeforeCompile() are not supported" → port to node materials/TSL; "EffectComposer ... not supported". "The renderer itself is still in an experimental state". WebGLRenderer "still maintained and the recommended choice for pure WebGL 2 applications" but no larger new features planned. https://github.com/mrdoob/three.js/blob/r186/manual/pages/webgpurenderer.html
- Source r186 `src/renderers/common/Renderer.js`: `render()` throws `.render() called before the backend is initialized. Use "await renderer.init();"`; WebGPURenderer constructor falls back with warn "WebGPU is not available, running under WebGL2 backend." Device-lost handler `onDeviceLost`.
- Source r186 `src/renderers/common/PostProcessing.js`: "@deprecated since r183. Use RenderPipeline instead. PostProcessing has been renamed to RenderPipeline." `Three.WebGPU.js` exports RenderPipeline, DirectRenderPipeline (r186), PostProcessing (deprecated alias).
- Example `webgpu_postprocessing_bloom.html` @ r186: `import * as THREE from 'three/webgpu'; import { pass } from 'three/tsl'; import { bloom } from 'three/addons/tsl/display/BloomNode.js'; renderPipeline = new THREE.RenderPipeline(renderer); renderPipeline.outputNode = scenePassColor.add(bloomPass); renderPipeline.render();` and `timer = new THREE.Timer(); timer.connect(document)` (Clock deprecated r183).
- Releases page (https://github.com/mrdoob/three.js/releases): r186 (24 Sep): compileComputeAsync, DirectRenderPipeline, MSAA for WebXR WebGPU; WebGLRenderer SunLight w/ cascaded shadows; PCFSoftShadowMap code removed + warning; `Source`→`TextureSource`. r185 (1 Jul): render to texture arrays, WebXR with WebGPU. r184 (16 Apr): compileAsync non-blocking; TSL compile ~3x faster; WebGLRenderer NodeMaterial compatibility layer; HTMLTexture. r183 (20 Feb): Clock deprecated; TSL spec `TSL.md`; RenderPipeline. r181: deprecate renderAsync()/computeAsync(); WebGLRenderer removed WebGL 1 code.
- r186 example list (`examples/files.json`): webgpu_gaussian_splat (uses `three/addons/objects/GaussianSplat.js`, SPLATLoader, SPZLoader), webgpu_compute_particles*, webgpu_tsl_* (galaxy, raging_sea, vfx_flames, vfx_tornado, procedural_terrain, halftone…), webgpu_postprocessing_bloom/dof/ssr, webgl_loader_gltf_compressed, webgl_loader_texture_ktx2, webgl_lod, webgl_batch_lod_bvh, webgl_instancing_performance, webgl_points_waves, webgl_materials_physical_transmission.
- WebGLRenderer r186 source: `onContextLost(event){ event.preventDefault(); ... _isContextLost = true }`, listens `webglcontextrestored`, has `forceContextLoss()`.

## 4. WebGPU browser support (web.dev, 2025-11-25, François Beaufort) https://web.dev/blog/webgpu-supported-major-browsers
- Chrome/Edge 113+: Windows (D3D12), macOS, ChromeOS. Android: Chrome 121+, Android 12+, Qualcomm/ARM GPUs. Linux "in progress".
- Firefox 141 Windows; Firefox 145 macOS Tahoe 26 on ARM64; Linux, Android, Intel Macs "in progress".
- Safari 26: macOS Tahoe 26, iOS 26, iPadOS 26, visionOS 26.
- Ecosystem list: Babylon.js, PlayCanvas, Three.js, Unity, TypeGPU… Babylon Snapshot Rendering "~10x faster".
- Secondary (unverified): a 2026 migration blog reports a black canvas on Firefox/Linux — consistent with "Linux in progress".

## 5. React Three Fiber v9 (https://r3f.docs.pmnd.rs/tutorials/v9-migration-guide)
- "compatibility release for React 19"; React 18 → fiber@8, React 19 → fiber@9.
- `gl` prop callback receives constructor props; may return a promise → WebGPU: `gl={async (props) => { const r = new THREE.WebGPURenderer(props as any); await r.init(); return r }}`; WebGPU support "work in progress".
- StrictMode now inherited from react-dom root; remove inner StrictMode.
- Automatic sRGB conversion of texture props removed → set `texture.colorSpace` yourself for custom materials.
- `Props`→`CanvasProps`; `MeshProps` etc. removed → `ThreeElements['mesh']`.
- Scaling performance page (https://r3f.docs.pmnd.rs/advanced/scaling-performance): `frameloop="demand"` + `invalidate()`; reuse geometry/material; useLoader cache; instancedMesh; drei `<Detailed distances={[0,10,20]}>`; nested Suspense low→high model; `<PerformanceMonitor onIncline={() => setDpr(2)} onDecline={() => setDpr(1)}>`; `flipflops={3} onFallback`; `performance={{ min: 0.5 }}` + `regress()`; startTransition.

## 6. drei docs
- PerformanceMonitor (https://drei.docs.pmnd.rs/performances/performance-monitor): ms 250, iterations 10, threshold 0.75, bounds default `refreshrate > 90 ? [50, 90] : [50, 60]`, flipflops Infinity, factor 0.5, step 0.1; onIncline/onDecline/onChange/onFallback; `usePerformanceMonitor`.
- ScrollControls (https://drei.docs.pmnd.rs/controls/scroll-controls): pages (default 1), distance 1, damping 0.2, maxSpeed Infinity, horizontal, infinite (experimental), enabled, style, eps, prepend; `useScroll()` → offset 0–1 damped, delta, range(start,len,margin), curve(), visible(); `<Scroll>` (canvas content) and `<Scroll html>` (DOM).
- MeshTransmissionMaterial (https://drei.docs.pmnd.rs/shaders/mesh-transmission-material): samples 6, resolution fullscreen default, thickness, roughness, chromaticAberration 0.03, anisotropicBlur 0.1, distortion, backside (more cost), transmissionSampler (uses three's internal buffer; can't see other transmissive objects), buffer (share). "can still be expensive as it causes an additional render pass of the scene"; "Low samples and low resolution will make it faster"; roughness → "consider using a tiny resolution, for instance 32x32 pixels".
- Environment (https://drei.docs.pmnd.rs/staging/environment): presets are HDRI Haven assets on GitHub; "preset property is not meant to be used in production environments and may fail as it relies on CDNs"; `files` supports .hdr, .exr, gainmap .jpg (HDRJPGLoader) / .webp; gainmap smallest footprint; `background` true/false/"only"; `ground` projection; `frames={Infinity}` live env; environmentIntensity (three ≥0.163).
- useGLTF (https://drei.docs.pmnd.rs/loaders/gltf-use-gltf): `useGLTF(path, useDraco = true, useMeshOpt = true, extendLoader?)`; Draco decoders default to `https://www.gstatic.com/draco/v1/decoders/`; `useGLTF.setDecoderPath`; `useGLTF.preload(url)`; KTX2 via `extendLoader` + `KTX2Loader.detectSupport(gl)`.

## 7. glTF-Transform CLI (source `packages/cli/src/cli.ts` main branch, v4.5.1)
- `optimize` defaults: `--compress meshopt` (choices draco|meshopt|quantize|false), `--texture-compress auto` (ktx2|webp|avif|auto|false), `--texture-size 2048`, `--simplify true` (+ --simplify-error, --simplify-ratio, --simplify-lock-border), `--instance true` (--instance-min), `--palette true`, `--flatten true`, `--join true`, `--prune true`, `--sparse true`, `--meshopt-level high`.
- `--texture-compress ktx2` path: UASTC (level 4, rdo, rdoLambda 4) for `{normalTexture,occlusionTexture,metallicRoughnessTexture}`, ETC1S (quality 255) for the rest; requires KTX-Software (`toktx`/`ktx`) installed. Standalone `etc1s` / `uastc` commands with `--slots`, `--resize`, `--jobs`.
- Doc page example: `gltf-transform optimize input.glb output.glb --compress draco --texture-compress webp`; `gltf-transform inspect input.glb` (https://gltf-transform.dev/cli).

## 8. Spline
- react-spline README (https://github.com/splinetool/react-spline): `npm install @splinetool/react-spline @splinetool/runtime`; `<Spline scene="https://prod.spline.design/…/scene.splinecode" />`; `@splinetool/react-spline/next` renders a server-side blurred placeholder; `React.lazy` for deferred load; `onLoad(app)`; events `onSplineMouseDown`… ; `renderOnDemand` default true; runtime API `findObjectByName`, `findObjectById`, `emitEvent`, `emitEventReverse`, `setZoom`; self-host .splinecode to avoid CORS.
- Spline V2 changelog (2026-08-21, https://updates.spline.design/changelog/introducing-spline-v2): "complete rebuild of our 3d editor for the agentic era"; "New TSL-based WebGPU backend by the default, WebGL as fallback"; MCP: "External agents (Claude Code, Cursor, etc.) drive the 3D editor through MCP tools"; AI chat agent generates editable scenes; smaller base runtime; Cloner uses GPU instancing.
- Secondary (createwith.com / thenewstack, via search): exports to vanilla JS, three.js, React, Next.js, R3F; community advice <150k polys (unverified, third-party).

## 9. model-viewer (README + `src/features/loading.ts`, https://github.com/google/model-viewer)
- Web component, three.js peer ("strongly recommend you keep your three.js version locked"); last 2 major versions of evergreen browsers. `loading` = auto|lazy|eager; `reveal` = auto|manual; `poster` attribute. 4.4.0 peer three ^0.183.0.

## 10. Gaussian splatting
- Spark (https://github.com/sparkjsdev/spark README; https://sparkjs.dev): "advanced 3D Gaussian Splatting renderer for THREE.js", built by World Labs, MIT; WebGL2 (98%+ devices); formats .PLY (+compressed), .SPZ, .SPLAT, .KSPLAT, .SOG; dynamic splat editing, shader graph; usage `new SparkRenderer({ renderer })`, `new SplatMesh({ url })`.
- three.js r186 has `GaussianSplat` addon + SPLAT/SPZ loaders (webgpu_gaussian_splat example).
- @lumaai/luma-web last release 0.2.2 (2024-03) → stale.

## 11. Reference sites (Awwwards etc.)
- Awwwards annual winners page (https://www.awwwards.com/annual-awards/winners, 2025 edition): Site of the Year **Lando Norris** (43 votes); Developer Site of the Year **Messenger** (54); E-commerce **Scout Motors**; Agency **Immersive Garden**; Studio **Malvah**; Independent **Louis Paquet**; Users' Choice **Lando Norris**.
- Sites of the Year listing (https://www.awwwards.com/websites/sites_of_the_year/): Lando Norris 2025 (OFF+BRAND.), Messenger 2025 (abeto), Igloo Inc 2024 (abeto), Don't Board Me 2024 (The First The Last), Opal Tadpole 2024 (Claudio Guglieri), Lusion v3 2023 (Lusion), Noomo Agency 2023, Mana Yerba Mate 2023 (Louis Paquet).
- abeto on X (https://x.com/abeto_co/status/1900152588768579701): "We won Site of the Year and Developer Site of the Year on @awwwards with our project for Igloo Inc." Igloo X post Mar 13 2025.
- Lando Norris (https://www.awwwards.com/sites/lando-norris): SOTD 17 Nov 2025 8.18; OFF+BRAND.; https://landonorris.com/; tags WebGL, GSAP, Webflow, 3D. DesignRush: cursor-reactive blob overlays echo helmet graphics.
- Messenger (https://www.awwwards.com/sites/messenger): SOTD 10 Nov 2025; abeto; https://messenger.abeto.co; tags 3D, WebGL, WebSockets, Three.js, Storytelling.
- Igloo Inc (https://www.awwwards.com/sites/igloo-inc; case study https://awwwards.com/igloo-inc-case-study.html): SOTD 23 Jul 2024; abeto + Bureaux; https://www.igloo.inc/; Three.js, three-mesh-bvh, Svelte, GSAP, Vite; Houdini + Blender; custom VDB-to-browser volume exporter, custom geometry exporter; UI rendered in WebGL; SDF text scramble avoids style recalcs; intro real-time not pre-rendered; textures/shaders loaded+compiled at load and in background; per-project procedural ice.
- Bruno Simon portfolio case study (https://www.awwwards.com/brunos-portfolio-case-study.html, 2026-03-11): three.js + TSL, WebGPU with WebGL fallback; Blender object names drive behaviour; ~78,400 grass blades merged into one geometry; instancing for trees/benches etc.; frustum culling; palette texture for colours; ETC1S/UASTC textures; Draco (quantization); mobile preset disables water blur + DOF, lowers shadow map res; inputs keyboard/mouse/touch/gamepad; repo folio-2025 MIT. 2019 version at https://2019.bruno-simon.com.
- utsubo "8 Best Three.js Websites of 2026" (https://www.utsubo.com/blog/best-threejs-websites-2026; note: Utsubo lists its own IVRESS): Oryzo (Lusion, Awwwards SOTM Apr 2026, inertial product render + Z-depth scroll, https://oryzo.ai/); IVRESS (Utsubo, WebGPURenderer + TSL with WebGL fallback, FWA SOTM May 2026); Lacoste Ace Breaker (branded brick-breaker); Shopify Editions Spring 2026 (scroll-sequenced reveal, particle type); Hubtown (Unseen Studio, SOTD Jun 2026, hero monolith + mouse reveal); Explore Primland (SOTD Feb 2026, terrain flythrough, fog, scroll camera); Cartier Watches & Wonders (Immersive Garden; six scrollable alcoves; Three.js, GLSL, GSAP, Lenis, Web Audio).
- GitHub globe (https://github.blog/engineering/engineering-principles/how-we-built-the-github-globe/, Dec 2020, Tobias Ahlin): three.js; ~12,000 five-sided circles instead of textures; halo via backside shader; circle density scales with machine performance; 5-part series incl. performance.
- Codrops: Motion hover effects with image distortions (2019) https://tympanus.net/codrops/2019/10/21/how-to-create-motion-hover-effects-with-image-distortions-using-three-js/ ; Interactive WebGL Hover Effects https://tympanus.net/codrops/?p=49069 ; Mouse-following square lens (2026-08-25) https://tympanus.net/codrops/2026/08/25/building-a-mouse-following-square-lens-effect-with-three-js-and-glsl/ ; tag page https://tympanus.net/codrops/tag/three-js/ (403 to fetcher).
- Active Theory: named in brief; not re-verified this session.

## 12. Accessibility / platform
- WCAG 2.2 SC 2.2.2 Pause, Stop, Hide (A): moving content that starts automatically, lasts >5 s, and is presented in parallel with other content needs pause/stop/hide (https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) → applies to hero loops and ambient 3D.
- SC 2.3.3 Animation from Interactions (AAA): parallax "often non-essential"; technique C39 prefers-reduced-motion (https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html).
- MDN Autoplay guide (https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Autoplay): autoplay allowed if muted / volume 0, or user interacted, or allowlisted, or iframe Permissions Policy; `playsinline` "required for autoplay in Safari"; play() promise rejects `NotAllowedError` → show play button; prefer `autoplay` attribute.
- MDN `prefers-reduced-data`: Experimental, "not supported by any user agent" (https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-data).
- MDN `NetworkInformation.saveData`: limited availability, not Baseline (https://developer.mozilla.org/en-US/docs/Web/API/NetworkInformation/saveData); Save-Data request header.
- MDN webglcontextlost (https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/webglcontextlost_event): test with `gl.getExtension("WEBGL_lose_context").loseContext()`.
- caniuse AV1 (https://caniuse.com/av1): Chrome 70+, Firefox 67+, Edge 121+ (Edge 116–120 unsupported), Safari macOS/iOS 17.0–26.x "Partial" (hardware decoder dependence not stated on page).
- caniuse HEVC (https://caniuse.com/hevc): Safari 13+ supported; Chrome 107+ partial; Edge partial; Firefox 137+ partial.

## 13. ffmpeg local tests (ffmpeg 9.0.2, synthetic 4 s 1280×720 30 fps periodic loop)
- H.264 `-c:v libx264 -preset slow -crf 23 -profile:v high -pix_fmt yuv420p -movflags +faststart -an` → avc1 High L3.1 (720p) / L4.0 (1080p), moov at byte 36 (faststart OK).
- HEVC `-c:v libx265 -preset slow -crf 28 -tag:v hvc1 -pix_fmt yuv420p -movflags +faststart` → codec tag hvc1, Main L93 (720p) / L120 (1080p).
- AV1 `-c:v libsvtav1 -preset 6 -crf 35 -pix_fmt yuv420p -movflags +faststart` → av01 Main level 5 (720p) / 8 (1080p). libsvtav1 crf range 0–63, preset −2..13 (`ffmpeg -h encoder=libsvtav1`).
- VP9 `-c:v libvpx-vp9 -crf 33 -b:v 0 -row-mt 1 -deadline good -cpu-used 2` → webm OK; libvpx-vp9 crf −1..63.
- Scrub variants: all-intra `-g 1` = 2,653,826 B vs GOP 5 (`-g 5 -keyint_min 5 -sc_threshold 0 -bf 0`) = 354,210 B vs normal 332,844 B on the same clip → all-intra ≈ 8× GOP-5.
- Codecs strings derived: 1080p30 `avc1.640028`, `hvc1.1.6.L120.B0`, `av01.0.08M.08`.
- Posters: `-frames:v 1 -q:v 2 poster.jpg` OK; AVIF via `-c:v libsvtav1 -crf 30 poster.avif` OK (5 KB); this ffmpeg build lacks libwebp → use `cwebp`.
- Loop seam check script (PSNR last→first vs median adjacent-frame PSNR): seamless 120-frame loop seam 39.09 dB vs adjacent median 39.07; duplicated end frame (121 frames, last = first) seam 73.0 dB → drop last frame → 39.08; broken loop (105 frames) seam 15.3 dB; 0.5 s crossfade (`xfade` head/tail) raised it to 30.8 dB (not exact; regenerate with start=end for a true seam).
- Still→video registration (ORB matches + least squares for s, dx, dy with outlier trimming): synthetic drift s=1.012, dx=7.3, dy=−4.1 recovered as 1.01166 / 7.32 / −4.13 (3012/3314 inliers); PSNR vs frame: naive resize 16.58 dB → registered 31.36 dB.
- Ping-pong loop (`reverse` + `trim=start_frame=1:end_frame=N-1` + `concat`) on the broken 105-frame clip → 208 frames, seam 39.06 dB = adjacent median 39.07 dB (seamless by construction).
- The seam script and registration script were re-extracted from the final `ai-assets-higgsfield.md` and re-run: identical results.
- Hero `<video>` markup test (headless Chrome 156, `--autoplay-policy=user-gesture-required`): sources attached via `data-src`, muted `play()` succeeded, `currentSrc` = AV1 file, `canPlayType` "probably" for `av01.0.08M.08`, `hvc1.1.6.L120.B0`, `avc1.640028`; pause button revealed on `playing`.

## 13b. R3F recipe verification (scratch Vite project; react 19.3.0, three 0.186.1, fiber 9.8.1, drei 10.7.9, gsap 3.15.0, @gsap/react 2.1.2, TS 5.9.3 strict)
- `tsc --noEmit` exit 0 for the recipes as extracted from the final `3d-webgl.md` (8 tsx + 1 ts blocks); `vite build` OK.
- Headless Chrome (SwiftShader WebGL2): R3F canvas 12 programs linked, 0 link failures, 0 shader errors, frames rendered (calls=8, tris=27,160); blob canvas 1 program, 16 draws; GLB exported with GLTFExporter and loaded through `useGLTF`.
- Found while testing: a wrapper that spreads `{...props}` then sets its own `onCreated` silently drops the caller's `onCreated` (fixed in the recipe by destructuring and chaining).
- Console warning `THREE.Clock: This module has been deprecated. Please use THREE.Timer instead.` comes from R3F 9.8.1 (`dist/events-*.esm.js` instantiates `THREE.Clock`) with three r186.
- three r186 OrbitControls sets `domElement.style.touchAction = 'none'` on connect (examples/jsm/controls/OrbitControls.js:508).
- r186 TSL bloom usage: `pass(scene, camera).getTextureNode('output')` → `color.add(bloom(color))` on `THREE.RenderPipeline`.

## 14. Higgsfield (higgsfield.ai)
- Home page (fetched 2026-10-10, https://higgsfield.ai/): Seedance 2.5 (Top), Higgsfield Genjutsu (New), Cinema Studio 4.0, Nano Banana 2.1 (New), Higgsfield Katana, Ads Studio / Ad Multiplier, AI Influencer, "Higgsfield MCP for Claude", "Supercomputer" agent, "Dots" (MCP for ChatGPT), Visual Effects presets (Floating fall, High flip, Burning man, Studio slide, Incline, Act natural, Eyes in, Street colossus, Melting, Wild ride, Cutout, World morphing, Smash and grab, Selfception, Lacewalker), Global Film Festival; "30+ models", "40+ creative AI tools", 4.5M video generations/day; schema text names Sora 2, Kling 3.0, Veo 3.1; founded 2023.
- Apps page (https://higgsfield.ai/apps): Virality Predictor, Expand image, Angles 2.0 ("Generate any angle view for any image"), Shots ("9 unique shots from one image"), Transitions, Skin Enhancer, Relight ("Adjust lighting position, color, and brightness"), Face Swap, Recast, Video Background Remover, Background Remover, Breakdown ("Split any image into its individual components"), Click to Ad, Bullet Time Scene / Bullet Time White (product spin), JSON-LD also lists 3D Rotation, 3D Render, 3D Figure.
- DoP help page (https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-dop, published 2026-08-02): "DoP (Director of Photography) is Higgsfield's native image-to-video model"; appears as "Higgsfield Standard" in the selector; preset categories Effects, Basic Camera Control, Epic Camera Control, Catch the Pulse; Mix combines presets; 3 or 5 s; seed + steps.
- DoP history (search results, Higgsfield blog): DoP I2V-01-preview announced 2025-03-30 with 50+ camera motions (bullet time, crash zoom, robo arm); Apr 24 2025 update → 80+ styles, Turbo model.
- Soul (search results): launched 2025-06-26 (https://higgsfield.ai/posts/50ogWiu9kVYbWw3spQjWIR), 50+ presets, camera-like grain/flash; Soul 2.0 = in-house foundation image model with reference mode + Soul ID (character consistency, ~20+ photos); Soul Cinema variant (third-party guide). Exact Soul 2.0 date not verified.
- Ownership/commercial (help center, published 2026-08-02, https://higgsfield.ai/creator-hub/help-center/account-and-privacy/who-owns-my-generations-and-can-i-use-them-commercially): Terms §4.4 — Higgsfield does not claim ownership of inputs/outputs; "The Terms of Use do not restrict commercial use of outputs"; watermarks embedded on plans that include them; "Paid plans include watermark-free downloads"; limited license to host/process and train models (not Enterprise); §5.1(ii)(b) you're responsible for third-party rights; §5.3 no images of other people without permission.
- MCP blog (https://higgsfield.ai/blog/Generate-AI-Videos-From-Claude-with-Higgsfield-MCP, 2026-05-08): URL https://mcp.higgsfield.ai, OAuth via Higgsfield account, draws on existing credits, warns "Always Allow" lets Claude act without asking.
- Pricing page fetch returned no plan data (client-rendered) → plan prices not verified.
- Funding (Reuters via BNN Bloomberg 2026-08-17 and others): $400M Series B at $5.4B valuation (Aug 2026); $1.3B in Jan 2026.
- MCP snapshot by coordinator (research/design-atlas/higgsfield-mcp-snapshot.md, 2026-10-10): workflows (product-photoshoot, brand-asset-creation, video-editing, website-builder-flow, …); video models Cinema Studio Video 3.0/4.0, Kling 3.0 / Omni / Turbo / 2.6, Seedance 2.0 / Mini / 2.5, MiniMax H3 / Hailuo 2.3, FLUX 3 Video, Grok Video 1.5, Wan 2.6; utilities Video Background Remover, Reframe, Topaz (2160p + interpolation), Topaz Hyperion (SDR→HDR), Video Deflicker, Genjutsu; image models FLUX 3 Image, FLUX.2 Pro Outpaint, GPT Image 2.5 (`background: transparent`), Nano Banana 2.1 (inpaint, up to 8:1), Marketing Studio Image; 3D: SAM 3 3D Objects, Meshy v5/v7 (PBR, remesh, 100–300k target polys, rigging), Tripo H3.1, Hunyuan3D v3/3.1; `start_image` + `end_image` roles; audio on by default; `unlim.available: false`. Coordinator-reported ids: cinematic_studio_video_4_0, kling3_0, kling_o3_flf, seedance_2_0 / seedance_2_5, flux_3_image, flux_2_pro_outpaint, gpt_image_2_5, nano_banana_2_1, topaz_video, video_background_remover, reframe, meshy_v7_image_to_3d, tripo_h3_1_image_to_3d, hunyuan3d_v3.
- MCP tool names observed in this session's deferred-tool list (not called): balance, show_plans_and_credits, transactions, models_explore, get_workflow_instructions, get_workflow_bundle_file, get_presets, get_preset_instructions, execute_preset, generate_image(_batch), generate_video(_batch), generate_3d, generate_audio, remove_background, upscale_image, upscale_video, outpaint_image, reframe, motion_control, media_upload / media_confirm / media_import_url, jobs_wait, show_generations, manage_reference_elements, scene_builder_3d_* (create_project, generate_angles, generate_video, get_glb, get_blend, run_python…), create_website / deploy_website / publish_website / website_status. MCP server instructions: 3D scenes/location angles → `get_preset_instructions { preset: "/3d-jutsu" }`; multi-step videos → `get_workflow_instructions` first; websites → workflow "website-builder-flow"; browsing presets never authorizes `execute_preset`.

## 15. Other generators (for the comparison table)
- OpenAI Sora: API deprecation notice 2026-03-24, removal 2026-09-24 for Videos API, sora-2, sora-2-pro and snapshots, no replacement listed (https://developers.openai.com/api/docs/deprecations). Consumer app reportedly closed 2026-04-26 (secondary: invideo/rangy blogs, unverified).
- Google Veo 3.1: announced 2025-10-15; first + last frame; 8 s clips with audio; same image as first and last frame = loop (third-party: getimg.ai, replicate blog, runcomfy); resolution/pricing conflicting (unverified).
- Runway: Gen-4.5 unveiled 2025-12-01 (eWeek via search); Aleph = edit existing footage (relight, weather, reframe) (third-party).
- Luma Ray3 / Ray 3.2: 16-bit EXR HDR; `loop: true` for 5 s clips; 10 s clips text-only without start/end/loop (Replicate readme via search).
- Midjourney Video V1: 2025-06-18, image-to-video, 4 × 5 s clips, extend to 21 s; loop + end frame added later in 2025 (third-party).
- Spline AI: in-editor agent + MCP (V2, 2026-08-21).
- Rive (https://rive.app/): "interactive experience engine"; Editor or CLI (agent) authoring; open-source runtimes web, iOS, Android, Flutter, React, Unity, Unreal; Rive Renderer GPU vector engine.
- Meshy / Tripo / Hunyuan3D / SAM 3 3D: via Higgsfield snapshot. Rodin (Hyper3D): not verified.
