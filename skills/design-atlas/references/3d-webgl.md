# 3D on the web: three.js and friends

> Read when: a brief asks for 3D, WebGL, WebGPU, shaders, particles, a product viewer, a "wow" hero, a scroll-driven camera, Spline, glTF/GLB assets, Gaussian splats, or when a 3D page is slow, janky, inaccessible or blank on some devices.

**Contents:** Does 3D earn its place · Tech selection · WebGPU and TSL status · Recipes · glTF pipeline · Lighting · Post-processing · Performance budgets · Fallbacks and context loss · Accessibility · Loading UX · Gaussian splatting · Reference sites · Learning links · Pitfalls · Sources

**Provenance.** Versions are from npm, 2026-10-10. Recipes were type-checked (`tsc --strict`), built with Vite, and run in headless Chrome on WebGL2; all programs linked and all scenes drew frames. **Related:** `motion.md` and `scroll-parallax.md` (choreography) · `ai-assets-higgsfield.md` (AI plates, loops, image-to-3D) · `accessibility.md`.

## Does 3D earn its place?

Ship 3D only when it carries information or is the experience itself. If removing it loses no information and no conversion, ship a poster or a video loop instead.

| 3D earns it | 3D hurts |
|---|---|
| The object must be inspected from angles: product, configurator, packaging, hardware. | It decorates a task page: checkout, forms, dashboards, docs. |
| Spatial relationships are the content: maps, globes, architecture, anatomy, exploded views tied to copy. | It would be the LCP element for a mobile-heavy or low-end audience. |
| The experience is the deliverable: a launch microsite, portfolio or game. | A 6–10 s video loop gives the same impression for far less (see `ai-assets-higgsfield.md`). |
| The interaction teaches: rotate to reveal, scrub to assemble. | It hides or delays the headline, the CTA or the price. |

**Cost ladder.** Pick the cheapest rung that delivers the idea: CSS 3D → image sequence or video loop → `<model-viewer>` → Spline embed → three.js/R3F/Threlte/TresJS → WebGPU compute or Gaussian splats.

**Gate before building** (all must be yes): a poster rendered from the same camera exists and is the LCP element · content and CTAs work with the canvas removed · there is a reduced-motion state, plus a pause control if motion runs > 5 s · budgets are agreed · the scene was tested on a mid-range Android phone.

## Tech selection (as of 2026-10-10)

| Option | Version | Pick when | Watch out |
|---|---|---|---|
| CSS 3D transforms | platform | Card tilt, flips, layered "fake 3D" heroes. No JS. | No lighting or meshes. Give each object its own `perspective()`; a shared `preserve-3d` stage intersects planes. Keep `left`/`top` integer (see Pitfalls). |
| Spline (`@splinetool/runtime` 2.0.75, `react-spline` 4.1.0) | V2 editor 2026-08-21 | Designers author the scene, states and events visually. V2 uses a "TSL-based WebGPU backend by default, WebGL as fallback" and has an MCP for agents. | Standalone WebGL runtime is ≈565 KB gz; physics WASM adds ≈573 KB gz. Self-host `.splinecode` (CORS). The `/next` import gives a blurred SSR placeholder. `renderOnDemand` defaults to true. |
| three.js | r186 (0.186.1, 2026-09-24) | Any framework or none; full control. | ≈188 KB gz untreeshaken (`three.module` + `three.core`). Pin the version: breaking changes land monthly. |
| React Three Fiber + drei | fiber 9.8.1, drei 10.7.9 | React 19 apps: declarative scenes, Suspense loading, helpers. | Peer `react >=19 <19.4`. React 18 needs fiber@8 + drei@9. fiber 10 and drei 11 are alpha; don't ship them. |
| Threlte | `@threlte/core` 8.6.1 | Svelte 5 apps. | Peers `svelte >=5`, `three >=0.172`. |
| TresJS | `@tresjs/core` 5.9.3 | Vue ≥3.4 and Nuxt apps. | Helpers live in `@tresjs/cientos`. |
| OGL | 1.0.11 (2025-01) | One shader effect (hover plane, gradient, particles) at a fraction of three's size. | Minimal API; releases are infrequent. |
| Babylon.js | 9.30.0 | Game-like apps: inspector, physics, GUI, XR; strong WebGPU. | Full UMD is ≈1.8 MB gz. Import `@babylonjs/core` ES modules to tree-shake. |
| PlayCanvas | 2.23.2 | Editor-based teams, games, splats (SOG). | Full engine ≈638 KB gz. |
| `<model-viewer>` | 4.4.0 (peer three ^0.183) | Product viewer or AR with zero 3D code: `poster`, `loading="lazy"`, `reveal="manual"`. | Bundle ≈282 KB gz with a locked three; don't mix it with your own three. |
| three.js WebGPU (`three/webgpu` + TSL) | r186 | Greenfield work, GPU compute particles, shaders written once for WGSL and GLSL. | ≈199 KB gz build. The manual still calls it experimental (next section). |
| Spark (`@sparkjsdev/spark`) | 2.3.1 | Gaussian splats in a three scene. | ≈914 KB gz. |

## WebGPU and TSL status (2026-10)

**Browser support** (web.dev, 2025-11-25): Chrome/Edge 113+ on Windows (D3D12), macOS and ChromeOS · Chrome Android 121+ (Android 12+, Qualcomm/ARM GPUs) · Firefox 141 on Windows and 145 on macOS Tahoe ARM64 · Safari 26 on macOS, iOS, iPadOS and visionOS. Linux, Firefox Android and Intel Macs are still "in progress", so always keep a WebGL2 path.

**How `WebGPURenderer` behaves (three.js manual):**

- It falls back to WebGL2 automatically; `forceWebGL: true` forces that path for testing.
- Init is async. Use `setAnimationLoop()` or `await renderer.init()`; otherwise `render()` throws `.render() called before the backend is initialized`.
- It does not support `ShaderMaterial`, `RawShaderMaterial`, `onBeforeCompile` or `EffectComposer`. Port materials to node materials and TSL. Post-processing becomes a TSL graph run by `THREE.RenderPipeline`, which was called `PostProcessing` before r183; the old name still works but warns.
- `WebGLRenderer` remains "the recommended choice for pure WebGL 2 applications" but gets no larger features. Recent changes: r181 removed WebGL1 code, r183 deprecated `Clock` for `Timer`, r184 added a NodeMaterial compatibility layer.

**Which renderer:** stay on `WebGLRenderer` when you depend on `@react-three/postprocessing` (peer `postprocessing ^6.36`), drei GLSL materials such as `MeshTransmissionMaterial`, or Codrops-style GLSL. Pick `WebGPURenderer` + TSL for greenfield work or compute (`webgpu_compute_particles*`), and test it with `forceWebGL: true` and on Firefox for Linux.

```tsx
// R3F 9 + WebGPU (fiber v9 migration guide). Node materials only; drei GLSL materials won't run.
import * as THREE from 'three/webgpu'
<Canvas gl={async (props) => { const r = new THREE.WebGPURenderer(props as any); await r.init(); return r }} />
```
```js
// TSL post-processing, r186 (examples/webgpu_postprocessing_bloom.html)
import * as THREE from 'three/webgpu'; import { pass } from 'three/tsl'
import { bloom } from 'three/addons/tsl/display/BloomNode.js'   // also DepthOfFieldNode, SSRNode, GTAONode
const pipeline = new THREE.RenderPipeline(renderer)
const color = pass(scene, camera).getTextureNode('output')
pipeline.outputNode = color.add(bloom(color))                     // call pipeline.render() each frame
```

## Recipes

Shared imports for the R3F recipes:

```tsx
import { Suspense, useEffect, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame, useThree, type CanvasProps } from '@react-three/fiber'
import { Bounds, Environment, MeshTransmissionMaterial, PerformanceMonitor, useGLTF, useScroll, useTexture } from '@react-three/drei'
import * as THREE from 'three'
```

### 1. Minimal R3F scene: Suspense, loader, poster fallback

The real `<img>` poster is the LCP element and also the fallback when WebGL is missing or Data Saver is on. The canvas fades in only after the GLB has resolved.

```tsx
function can3D() {
  if (typeof window === 'undefined') return false
  const conn = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection
  if (conn?.saveData) return false                                   // Data Saver → poster only
  return !!document.createElement('canvas').getContext('webgl2')
}
function Model({ url, onReady }: { url: string; onReady: () => void }) {
  const { scene } = useGLTF(url)                                     // Draco + Meshopt decoders on by default
  useEffect(() => onReady(), [onReady])                              // fires once the glb resolved
  return <primitive object={scene} />
}
export function Hero3D({ src, poster, alt }: { src: string; poster: string; alt: string }) {
  const [on] = useState(can3D)
  const [ready, setReady] = useState(false)
  return (
    <figure style={{ position: 'relative', aspectRatio: '16 / 9', margin: 0 }}>
      <img src={poster} alt={alt} fetchPriority="high" decoding="async"
        style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
      {on && (
        <Canvas frameloop="demand" dpr={[1, 2]} camera={{ position: [0, 0, 4], fov: 35 }} aria-hidden
          style={{ position: 'absolute', inset: 0, opacity: ready ? 1 : 0, transition: 'opacity .4s' }}>
          <Suspense fallback={null}>
            <Environment files="/env/studio_1k.hdr" />               {/* self-host; drei presets hit a CDN */}
            <Bounds fit clip observe margin={1.1}><Model url={src} onReady={() => setReady(true)} /></Bounds>
          </Suspense>
        </Canvas>
      )}
    </figure>
  )
}
```

- `frameloop="demand"` suits static or controls-driven scenes; drei controls call `invalidate()` themselves, so call it only after manual mutations. Low→high swap: `<Suspense fallback={<Model url="/low.glb" />}>`. Call `useGLTF.preload(url)` only once the section nears the viewport.
- R3F v9 no longer converts texture props to sRGB: set `texture.colorSpace = THREE.SRGBColorSpace` for custom materials.

### 2. Scroll-linked camera

**Preferred: native scroll drives the camera through GSAP ScrollTrigger.** Keyboard, screen readers, anchors and the scrollbar keep working. Pin the canvas (`position: fixed` or `sticky`) behind a tall DOM section.

```tsx
// gsap 3.15 · @gsap/react 2.1
import gsap from 'gsap'; import { ScrollTrigger } from 'gsap/ScrollTrigger'; import { useGSAP } from '@gsap/react'
gsap.registerPlugin(ScrollTrigger, useGSAP)
export function ScrollCamera({ trigger }: { trigger: string }) {         // e.g. '#story'
  const camera = useThree((s) => s.camera)
  const invalidate = useThree((s) => s.invalidate)                       // works with frameloop="demand"
  const target = useRef(new THREE.Vector3())
  useGSAP(() => {
    const look = () => { camera.lookAt(target.current); invalidate() }
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) { camera.position.set(0, 0.5, 2); look(); return }
    gsap.timeline({ defaults: { ease: 'none' }, onUpdate: look,
      scrollTrigger: { trigger, start: 'top top', end: 'bottom bottom', scrub: 0.6, invalidateOnRefresh: true } })
      .to(camera.position, { x: 2, y: 1, z: 3 })
      .to(target.current, { x: 0.5, y: 0.3 }, '<')
      .to(camera.position, { x: 0, y: 0.5, z: 2 })
  }, { dependencies: [camera, trigger] })                                // useGSAP reverts on unmount
  return null
}
```

**Full-screen experiences only: drei `ScrollControls`.** It owns its own scroll container and exposes `useScroll()` with a damped `offset` (0–1) plus `range()`, `curve()` and `visible()`. Put DOM copy in `<Scroll html>`. Never nest it inside a normally scrolling page: it captures the wheel and adds a second scrollbar.

```tsx
function Rig() {
  const scroll = useScroll()
  useFrame(({ camera }) => { const t = scroll.range(0, 1); camera.position.set(Math.sin(t * Math.PI) * 3, 1, 4 - 2 * t); camera.lookAt(0, 0, 0) })
  return null
}   // <ScrollControls pages={3} damping={0.2}><Rig /><Model /><Scroll html>…sections…</Scroll></ScrollControls>
```

### 3. Image hover distortion on a plane (WebGLRenderer: it uses `ShaderMaterial`)

```tsx
const vertexShader = /* glsl */ `
  uniform float uHover; uniform vec2 uMouse; uniform float uTime; varying vec2 vUv;
  void main() {
    vUv = uv; vec3 p = position; float d = distance(uv, uMouse);
    p.z += uHover * 0.08 * smoothstep(0.5, 0.0, d) * sin(d * 20.0 - uTime * 4.0);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
  }`
const fragmentShader = /* glsl */ `
  uniform sampler2D uMap; uniform float uHover; uniform vec2 uMouse; varying vec2 vUv;
  void main() {
    vec2 dir = vUv - uMouse; float k = uHover * 0.035 * smoothstep(0.5, 0.0, length(dir));
    vec3 c = vec3(texture2D(uMap, vUv + dir * k).r, texture2D(uMap, vUv).g, texture2D(uMap, vUv - dir * k).b);
    gl_FragColor = vec4(c, 1.0);
    #include <colorspace_fragment>
  }`
export function HoverImage({ url, width = 1.6 }: { url: string; width?: number }) {
  const map = useTexture(url, (t) => { t.colorSpace = THREE.SRGBColorSpace })
  const mat = useRef<THREE.ShaderMaterial>(null!), hover = useRef(0)
  const uniforms = useMemo(() => ({ uMap: { value: map }, uHover: { value: 0 }, uTime: { value: 0 },
    uMouse: { value: new THREE.Vector2(0.5, 0.5) } }), [map])
  useFrame((_, dt) => {
    const u = mat.current.uniforms
    u.uHover.value = THREE.MathUtils.damp(u.uHover.value, hover.current, 6, dt); u.uTime.value += dt
  })
  const img = map.image as HTMLImageElement
  return (
    <mesh onPointerMove={(e) => { if (e.uv) mat.current.uniforms.uMouse.value.copy(e.uv) }}
      onPointerOver={() => { hover.current = 1 }} onPointerOut={() => { hover.current = 0 }}>
      <planeGeometry args={[width, (width * img.height) / img.width, 32, 32]} />
      <shaderMaterial ref={mat} uniforms={uniforms} vertexShader={vertexShader} fragmentShader={fragmentShader} />
    </mesh>
  )
}
```

**Galleries:** keep the real `<img>` in the DOM for semantics and SEO, sync each plane to its image's `getBoundingClientRect()` on scroll and resize, and use one canvas for all images, never one per image. Touch has no hover: drive `uHover` from scroll velocity or a tap, or skip the effect.

### 4. Points / particle field

```tsx
export function Particles({ count = 4000, radius = 4 }: { count?: number; radius?: number }) {
  const ref = useRef<THREE.Points>(null!)
  const positions = useMemo(() => {                                      // uniform inside a sphere
    const a = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) { const r = radius * Math.cbrt(Math.random()), th = Math.random() * 2 * Math.PI, ph = Math.acos(2 * Math.random() - 1)
      a.set([r * Math.sin(ph) * Math.cos(th), r * Math.sin(ph) * Math.sin(th), r * Math.cos(ph)], i * 3) }
    return a
  }, [count, radius])
  useFrame((_, dt) => { ref.current.rotation.y += dt * 0.03 })
  return (
    <points ref={ref}>
      <bufferGeometry><bufferAttribute attach="attributes-position" args={[positions, 3]} /></bufferGeometry>
      <pointsMaterial size={0.02} sizeAttenuation color="#9bb4ff" transparent opacity={0.8} depthWrite={false} blending={THREE.AdditiveBlending} />
    </points>
  )
}
```

The field is one draw call; the real cost is overdraw (count × on-screen point area × blended layers). By count: ≤ ~50k → CPU updates are fine · ≤ ~200k → animate in the vertex shader (time uniform + per-point seed attribute) · beyond → GPU compute (`webgpu_compute_particles`, or GPGPU ping-pong).

### 5. Animated gradient / noise blob background (vanilla three)

This is the cheapest "alive" hero: one quad at half resolution, paused offscreen, frozen under reduced motion. Behind it, set a CSS gradient in the same colours as the no-JS fallback. Take brand colours from `color.md`; `THREE.Color` converts sRGB hex to linear.

```ts
const frag = /* glsl */ `
  uniform float uTime; uniform vec2 uRes; uniform vec3 uA, uB, uC; varying vec2 vUv;
  float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  float noise(vec2 p) { vec2 i = floor(p), f = fract(p), u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1, 0)), u.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), u.x), u.y); }
  float fbm(vec2 p) { float v = 0.0, a = 0.5; for (int i = 0; i < 4; i++) { v += a * noise(p); p *= 2.0; a *= 0.5; } return v; }
  void main() {
    vec2 p = (vUv - 0.5) * vec2(uRes.x / uRes.y, 1.0) * 1.6; float t = uTime * 0.05;
    float n = fbm(p + vec2(t, -t) + fbm(p * 1.5 - t));               // domain warp → organic blobs
    vec3 col = mix(uA, uB, smoothstep(0.25, 0.75, n));
    col = mix(col, uC, smoothstep(0.55, 0.9, fbm(p * 0.8 - t * 1.3)));
    gl_FragColor = vec4(col, 1.0);
    #include <colorspace_fragment>
    gl_FragColor.rgb += (hash(gl_FragCoord.xy) - 0.5) / 255.0;       // dither: no 8-bit banding
  }`
export function mountBlob(canvas: HTMLCanvasElement, colors: [string, string, string] = ['#0b1020', '#3b5bfd', '#ff6ad5']) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, powerPreference: 'low-power' })
  renderer.setPixelRatio(0.5)                                          // soft content: half-res is invisible
  const uniforms = { uTime: { value: 0 }, uRes: { value: new THREE.Vector2(1, 1) },
    uA: { value: new THREE.Color(colors[0]) }, uB: { value: new THREE.Color(colors[1]) }, uC: { value: new THREE.Color(colors[2]) } }
  const material = new THREE.ShaderMaterial({ uniforms, fragmentShader: frag,
    vertexShader: 'varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }' })
  const scene = new THREE.Scene(); scene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), material))
  const camera = new THREE.OrthographicCamera()
  const timer = new THREE.Timer(); timer.connect(document)             // r183+: Timer replaces Clock
  const draw = () => renderer.render(scene, camera)
  const resize = () => { renderer.setSize(canvas.clientWidth, canvas.clientHeight, false)
    uniforms.uRes.value.set(canvas.clientWidth, canvas.clientHeight); draw() }
  const ro = new ResizeObserver(resize); ro.observe(canvas)
  const reduce = matchMedia('(prefers-reduced-motion: reduce)')
  const loop = (t: number) => { timer.update(t); uniforms.uTime.value = timer.getElapsed(); draw() }
  const io = new IntersectionObserver(([e]) => renderer.setAnimationLoop(e.isIntersecting && !reduce.matches ? loop : null))
  io.observe(canvas)
  return () => { io.disconnect(); ro.disconnect(); renderer.setAnimationLoop(null); timer.dispose(); material.dispose(); renderer.dispose() }
}
```

### 6. Glass / transmission (expensive)

drei `MeshTransmissionMaterial` "causes an additional render pass of the scene" for each material, every frame. Keep `samples` 4–6 and `resolution` 256–512 (for rough glass the docs suggest "a tiny resolution, for instance 32x32"), `backside={false}`, and share one `buffer`/`transmissionSampler`. Use one hero glass object per view, never on instanced meshes, and never stacked with bloom + DOF on mobile.

```tsx
export function Glass({ low }: { low: boolean }) {            // low ← PerformanceMonitor onDecline/onFallback
  return (
    <mesh><torusKnotGeometry args={[0.8, 0.28, 160, 24]} />
      {low ? <meshPhysicalMaterial transmission={1} thickness={0.5} roughness={0.15} ior={1.4} />
           : <MeshTransmissionMaterial samples={4} resolution={512} thickness={0.5} roughness={0.15} chromaticAberration={0.04} anisotropicBlur={0.1} backside={false} />}
    </mesh>
  )
}
```

### 7. Live canvas: pause offscreen, adaptive DPR, context-loss recovery

```tsx
export function LiveCanvas({ poster, children, onCreated, ...props }: CanvasProps & { poster: string }) {
  const wrap = useRef<HTMLDivElement>(null)
  const [inView, setInView] = useState(false), [dpr, setDpr] = useState(1.5)
  const [lost, setLost] = useState(false), [gen, setGen] = useState(0)        // gen++ remounts after restore
  useEffect(() => {
    const io = new IntersectionObserver(([e]) => setInView(e.isIntersecting), { rootMargin: '200px' })
    io.observe(wrap.current!); return () => io.disconnect()
  }, [])
  return (
    <div ref={wrap} style={{ position: 'absolute', inset: 0 }}>
      {lost && <img src={poster} alt="" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }} />}
      <Canvas key={gen} {...props} frameloop={inView && !lost ? 'always' : 'never'} dpr={dpr}
        onCreated={(state) => {
          const c = state.gl.domElement
          c.addEventListener('webglcontextlost', () => setLost(true))            // three already calls preventDefault()
          c.addEventListener('webglcontextrestored', () => { setLost(false); setGen((g) => g + 1) })
          onCreated?.(state)                                                    // don't swallow the caller's handler
        }}>
        <PerformanceMonitor bounds={(hz) => (hz > 90 ? [50, 90] : [45, 60])} flipflops={3}
          onIncline={() => setDpr(2)} onDecline={() => setDpr(1)} onFallback={() => setDpr(1)} />
        {children}
      </Canvas>
    </div>
  )
}
```

`PerformanceMonitor` defaults: 250 ms samples, 10 iterations, threshold 0.75, bounds `hz > 90 ? [50, 90] : [50, 60]`. It measures continuous rendering only, so it does nothing under `frameloop="demand"`. Test context loss with `renderer.forceContextLoss()` or `gl.getExtension('WEBGL_lose_context').loseContext()`.

## glTF pipeline: Blender → glTF → gltf-transform

**1. Blender.** Model to budget: delete hidden faces, merge static meshes (Bruno Simon's 2026 portfolio merges ~78,400 grass blades into one geometry), use a palette texture for flat-coloured props, apply modifiers, keep +Y up. Export **glTF Binary (.glb)** with compression off; gltf-transform compresses better.

**2. Inspect:** `npx @gltf-transform/cli inspect in.glb`.

**3. Optimize** (`@gltf-transform/cli` 4.5.1). The `optimize` defaults are `--compress meshopt`, `--texture-compress auto` and `--texture-size 2048`, with simplify, instance, palette, join, flatten and prune all on.

```bash
npx @gltf-transform/cli optimize in.glb out.glb --compress meshopt --texture-compress webp --texture-size 2048   # web default
npx @gltf-transform/cli optimize in.glb out.glb --compress meshopt --texture-compress ktx2 --texture-size 2048   # needs KTX-Software (ktx/toktx); UASTC for normal/occlusion/metalRough, ETC1S for the rest
npx @gltf-transform/cli optimize in.glb out.glb --simplify false --texture-compress ktx2                          # hero model: keep silhouettes exact
```

**Meshopt or Draco.** Meshopt decodes fast. Draco is often smaller on dense scans but needs a WASM decoder. drei `useGLTF` handles both and loads Draco from gstatic unless you call `useGLTF.setDecoderPath('/draco/')`.

**WebP or KTX2.** WebP only shrinks the download; on the GPU it is full RGBA. KTX2 also shrinks GPU memory. Load it with `KTX2Loader.detectSupport(renderer)` via drei's `extendLoader`.

GPU memory per texture (RGBA8 = w × h × 4 B × 4/3 for mips):

| Texture | Uncompressed | KTX2 → BC7/ASTC 4×4 (8 bpp) | ETC1S → BC1/ETC (4 bpp) |
|---|---|---|---|
| 2048² | ≈ 21.3 MiB | ≈ 5.3 MiB | ≈ 2.7 MiB |
| 4096² | ≈ 85.3 MiB | ≈ 21.3 MiB | ≈ 10.7 MiB |

**Starting budgets** (house rule; measure and adjust): hero GLB ≤ 2 MB transferred; total 3D above the fold ≤ 3–4 MB including the library; textures ≤ 2048² on mobile. Image-to-3D output (Meshy, Tripo: 100–300k triangles, 2–4K textures) always goes through this pipeline; see `ai-assets-higgsfield.md`.

## Lighting

- **IBL first.** Use `<Environment files="/env/studio_1k.hdr" />` with a self-hosted 1K file; a gain-map `.jpg`/`.webp` is smallest. drei says `preset` "is not meant to be used in production … relies on CDNs".
- **Bake static light.** Bake lighting and AO in Blender Cycles; glTF `occlusionTexture` is wired automatically. A fully baked scene on `MeshBasicMaterial` needs no lights and no shadow maps: the cheapest high-end look.
- **Shadows.** Each shadow-casting light re-renders the scene into a depth map. Use one directional light with a 1024–2048 map at most, and fake contact shadows with drei `ContactShadows` or a baked blob.

## Post-processing

- **Cost.** Each full-screen effect is ≥ 1 extra full-resolution pass: bloom is a mip chain, DOF needs depth + blur, SSAO/SSR/GTAO cost most. **Mobile:** ≤ 2 cheap effects (selective bloom + vignette/tone mapping), DOF off; Bruno Simon's mobile preset drops water blur and DOF and lowers shadow resolution.
- **Library.** WebGL: `@react-three/postprocessing` 3.2 (postprocessing 6) merges effects into one pass. WebGPU: `RenderPipeline` + TSL nodes. For one glowing object, use an emissive map + additive sprite instead of full-scene bloom.

## Performance budgets and techniques

Measure before tuning: `renderer.info.render.calls`, `.triangles`, `renderer.info.memory`, or `r3f-perf`, on a mid-range Android over a throttled connection.

Starting budgets (house rule, not a standard):

| Metric | Mobile mid-range | Desktop |
|---|---|---|
| Frame time | 16.7 ms (30 fps only for heavy scenes with smooth motion) | 16.7 ms (8.3 ms on 120 Hz if light) |
| Draw calls | ≤ 100 | ≤ 300 |
| Triangles drawn | ≤ 300k | ≤ 1.5M |
| Texture GPU memory | ≤ 64 MiB | ≤ 256 MiB |
| DPR | clamp `[1, 2]`, start 1.5 | `[1, 2]` |

Techniques, highest payoff first:

1. Clamp DPR (`dpr={[1, 2]}`): a 3× phone at full DPR renders 2.25× the pixels of 2×. Then `frameloop="demand"` when static and `'never'` offscreen.
2. Instance repeated props (`<instancedMesh>`, drei `<Instances>`); merge static geometry and reuse materials (each material = a program + state changes).
3. LOD (drei `<Detailed distances={[0, 10, 20]}>`) + frustum culling; KTX2 power-of-two textures; dispose on route change.
4. Adaptive quality: `PerformanceMonitor` lowers DPR → drops post → swaps glass for physical; `performance={{ min: 0.5 }}` + `regress()` while moving. Mutate refs in `useFrame`, never React state per frame.

## Fallbacks and context loss

| Condition | Detect | Serve |
|---|---|---|
| No WebGL2 | `getContext('webgl2')` is null | Poster from the same camera and crop |
| No WebGPU | `navigator.gpu` missing or `requestAdapter()` returns null | `WebGPURenderer` falls back to WebGL2 itself; test it |
| Data Saver | `navigator.connection?.saveData` (Chromium only). `prefers-reduced-data` is experimental and unsupported. | Poster; don't download the GLB |
| Weak GPU | `PerformanceMonitor.onFallback`, or a tier from `detect-gpu` 5.x | Pre-rendered video loop or poster |
| Reduced motion | `matchMedia('(prefers-reduced-motion: reduce)')` | Static frame or final pose; no auto-rotate, no scrub |
| Context lost | `webglcontextlost` (WebGPU: `renderer.onDeviceLost`) | Poster, then remount on `webglcontextrestored` |

Contexts do get lost in real use: GPU resets, backgrounded tabs, too many canvases. Never create one WebGL context per card; use one shared canvas with scissor (drei `<View>`).

## Accessibility

- **Canvas is decorative by default.** Mark it `aria-hidden` and keep meaning in DOM. If the 3D conveys information, add a text equivalent or a `<figcaption>`.
- **WCAG 2.2.2 Pause, Stop, Hide (A).** Auto-starting motion that lasts more than 5 s and sits beside other content needs a visible pause control. This covers rotating heroes, particle fields and blob backgrounds.
- **WCAG 2.3.3 (AAA)** calls parallax "often non-essential". Under `prefers-reduced-motion` (technique C39), show the final state, don't scrub the camera, and keep fades ≤ 200 ms.
- **Keyboard.** Interactive 3D needs DOM buttons for the same actions (rotate, next part, reset) with visible focus. Build hotspots with drei `<Html>`, not canvas-only hit tests.
- **Don't trap scroll.** Set `OrbitControls enableZoom={false}` on in-page heroes (else the wheel zooms instead of scrolling). OrbitControls also sets `touch-action: none` on the canvas, so on touch disable the controls or add "Tap to interact". Never hijack scroll speed (see `scroll-parallax.md`).

## Loading UX

1. Paint the poster first: it is the LCP. Reserve its box with `aspect-ratio`.
2. Lazy-load the 3D bundle (`React.lazy` or `import()`) about one viewport ahead.
3. Show progress only after ~1 s (drei `useProgress`, thin bar). Full-screen loaders belong only to sites where the 3D *is* the product (Igloo Inc, Bruno Simon).
4. Cross-fade canvas over poster (300–500 ms) after the first frame that includes the model.
5. Compile before reveal with `await renderer.compileAsync(scene, camera)`. Igloo Inc compiles shaders during load and in the background.

## Gaussian splatting (2026-10)

- **Spark 2.3.1** (World Labs, MIT) is the default splat renderer for three.js: WebGL2, claims "98%+" device reach, reads `.ply`/`.spz`/`.splat`/`.ksplat`/`.sog`, mixes splats with meshes. Usage: `new SparkRenderer({ renderer })` + `new SplatMesh({ url })`.
- **three.js r186** ships a `GaussianSplat` addon with SPLAT/SPZ loaders (`webgpu_gaussian_splat`). **PlayCanvas** (SuperSplat, SOG) is strongest for authoring and compression. **`@lumaai/luma-web`** is stale (0.2.2, last release 2024-03).

Use splats for photoreal captured places and products. Use meshes when you need relighting, collisions or a small payload. Compress to `.spz` or `.sog`, stream or LOD large files, and keep a poster or video fallback.

## Reference sites (verified 2026-10-10)

| Site | Studio · recognition | Learn from it |
|---|---|---|
| landonorris.com | OFF+BRAND · Awwwards Site of the Year 2025 + Users' Choice | WebGL + GSAP on Webflow; cursor-reactive blobs echo the helmet graphics. Brand carried by shader motion, not a heavy scene. |
| messenger.abeto.co | abeto · Developer Site of the Year 2025 | Three.js + WebSockets multiplayer storytelling: shared presence is the hook. |
| igloo.inc | abeto + Bureaux · Site of the Year 2024 + Developer SOTY 2024 | Three.js + Svelte + GSAP; custom VDB volumes; UI rendered in WebGL; SDF text scramble; real-time intro instead of video; background shader compiles. |
| oryzo.ai | Lusion · Awwwards SOTM Apr 2026 + Developer Award | One inertial product render with a Z-depth scroll camera. |
| Lusion v3 (studio site) | Lusion · Sites of the Year page, 2023 | Craft benchmark: physics, fluid and particles tied to cursor and scroll. |
| Bruno Simon portfolio (2019 version: 2019.bruno-simon.com) | 2026 rebuild, Awwwards case study | WebGPU + TSL with WebGL fallback; Blender names drive physics; merged grass; instancing; palette texture; ETC1S/UASTC; Draco; mobile preset. |
| cartier.com/en-fr/watchesandwonders | Immersive Garden (Agency of the Year 2025) · SOTD | Six scrollable 3D alcoves, one per watch; Three.js, GLSL, GSAP, Lenis, Web Audio. |
| explore.ownprimland.com | SOTD Feb 2026 | Scroll-driven terrain flythrough with atmospheric fog. |
| shopify.com/editions/spring2026 | Shopify | Scroll-sequenced product reveal with particle-dispersing type. |
| hubtown.co.in | Unseen Studio · SOTD Jun 2026 | One hero monolith with a mouse reveal beats a full world. |
| brand.ivress.co.jp | Utsubo · FWA SOTM May 2026 (from Utsubo's own list) | WebGPURenderer with WebGL fallback; shaders written once in TSL. |
| github.com home globe | GitHub (2020 write-up) | Textureless data viz (~12k instanced circles); density scaled to device performance. |
| Don't Board Me · Opal Tadpole · Active Theory | Sites of the Year page 2024 · studio | Browse for character 3D and restrained product 3D (not re-verified). |

## Learning links

- **three.js examples** (https://threejs.org/examples/, r186 names): `webgpu_postprocessing_bloom`, `webgpu_compute_particles`, `webgpu_tsl_galaxy`, `webgpu_tsl_raging_sea`, `webgpu_gaussian_splat`, `webgl_loader_gltf_compressed`, `webgl_loader_texture_ktx2`, `webgl_instancing_performance`, `webgl_lod`, `webgl_points_waves`, `webgl_materials_physical_transmission`.
- **Codrops:** three.js tag https://tympanus.net/codrops/tag/three-js/ · distortion hover (2019) https://tympanus.net/codrops/2019/10/21/how-to-create-motion-hover-effects-with-image-distortions-using-three-js/ · interactive WebGL hover https://tympanus.net/codrops/?p=49069 · mouse-following lens with RGB shift (2026-08) https://tympanus.net/codrops/2026/08/25/building-a-mouse-following-square-lens-effect-with-three-js-and-glsl/. Porting old tutorials: `PlaneBufferGeometry` → `PlaneGeometry`, and add `colorSpace` + `<colorspace_fragment>`.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Blank canvas on the WebGPU path | `render()` before init | `setAnimationLoop` or `await renderer.init()`; in R3F, an async `gl` factory |
| Shaders or effects vanish on `three/webgpu` | `ShaderMaterial`, `onBeforeCompile` and `EffectComposer` are unsupported | Stay on `WebGLRenderer`, or port to TSL + `RenderPipeline` |
| `THREE.Clock: This module has been deprecated` in the console | R3F 9.8.1 still uses `Clock` with three r186 (seen in this session's test) | Harmless. In your own code use `THREE.Timer` (`connect(document)`, `update(t)`, `getElapsed()`) |
| Washed-out or dark textures in custom materials | R3F v9 removed auto-sRGB on texture props | `texture.colorSpace = SRGBColorSpace` plus `#include <colorspace_fragment>` |
| Page won't scroll on phones over the hero | OrbitControls sets `touch-action: none`, and zoom eats the wheel | `enableZoom={false}`; tap-to-interact on touch |
| A wrapper's `onCreated` never fires | `{...props}` spread, then the wrapper sets its own `onCreated` (found in this session's test) | Destructure `onCreated` and call `onCreated?.(state)` |
| Jank and a hot device on 3× phones | Unclamped DPR; rendering offscreen | `dpr={[1, 2]}`, `frameloop` `demand`/`never`, `PerformanceMonitor` |
| Layered CSS-3D or parallax hero jitters by 1 px; loop seam shows | Fractional `left`/`top` snaps to whole pixels; a shared `preserve-3d` stage intersects planes | Integer static layout; move only via `translate3d`; own `perspective()` per object |
| Poster and canvas don't line up at the fade | Poster rendered with a different camera, crop or aspect | Render the poster from the scene camera at the hero aspect, with the same `object-fit` |
| "Too many active WebGL contexts" / lost context | One canvas per card | One shared canvas (drei `<View>`); handle `webglcontextlost` |
| HDRI fails in production | drei `Environment preset` loads from a CDN | Self-host `files="/env/x_1k.hdr"` |
| 3D bundle delays LCP and TBT | Eager import of three or Spline | Lazy-load on approach; poster `<img fetchpriority="high">` as the LCP |
| Black canvas on Firefox/Linux with WebGPU | Platform support still "in progress" | Feature-detect; test the fallback with `forceWebGL: true` |

## Sources

- three.js WebGPURenderer manual (r186) — https://github.com/mrdoob/three.js/blob/r186/manual/pages/webgpurenderer.html · releases r181–r186 — https://github.com/mrdoob/three.js/releases · r186 source/examples — https://github.com/mrdoob/three.js/tree/r186 · https://threejs.org/examples/
- WebGPU is now supported in major browsers (web.dev, 2025-11-25) — https://web.dev/blog/webgpu-supported-major-browsers · R3F v9 migration — https://r3f.docs.pmnd.rs/tutorials/v9-migration-guide · R3F scaling performance — https://r3f.docs.pmnd.rs/advanced/scaling-performance
- drei — https://drei.docs.pmnd.rs/performances/performance-monitor · https://drei.docs.pmnd.rs/controls/scroll-controls · https://drei.docs.pmnd.rs/shaders/mesh-transmission-material · https://drei.docs.pmnd.rs/staging/environment · https://drei.docs.pmnd.rs/loaders/gltf-use-gltf
- glTF-Transform CLI — https://gltf-transform.dev/cli · https://github.com/donmccurdy/glTF-Transform/blob/main/packages/cli/src/cli.ts · react-spline — https://github.com/splinetool/react-spline · Spline V2 — https://updates.spline.design/changelog/introducing-spline-v2 · model-viewer — https://github.com/google/model-viewer · Spark — https://sparkjs.dev/ · https://github.com/sparkjsdev/spark
- Awwwards — https://www.awwwards.com/annual-awards/winners · https://www.awwwards.com/websites/sites_of_the_year/ · https://www.awwwards.com/sites/lando-norris · https://www.awwwards.com/sites/messenger · https://awwwards.com/igloo-inc-case-study.html · https://www.awwwards.com/brunos-portfolio-case-study.html
- abeto SOTY post — https://x.com/abeto_co/status/1900152588768579701 · npm registry (versions, 2026-10-10) — https://www.npmjs.com/ · Best Three.js websites of 2026 (Utsubo) — https://www.utsubo.com/blog/best-threejs-websites-2026 · How we built the GitHub globe — https://github.blog/engineering/engineering-principles/how-we-built-the-github-globe/
- WCAG 2.2 Understanding 2.2.2 — https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html · 2.3.3 — https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html · MDN — https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/webglcontextlost_event · https://developer.mozilla.org/en-US/docs/Web/API/NetworkInformation/saveData · https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-data
