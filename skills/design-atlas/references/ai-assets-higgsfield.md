# AI-generated visual assets for UI (Higgsfield first)

> Read when: a page needs a hero background loop, product shots, a "fake 3D" camera move, parallax layers, a scroll-scrubbed sequence, image-to-3D, or any generated image or video; when a Higgsfield MCP is connected; or when an AI video hero shows a ghost double, a jumping loop seam, jitter, or a huge file.

**Contents:** Higgsfield product surface · When to generate · MCP workflow · Asset recipes · Prompt patterns · Post-processing and encoding · Licensing and brand safety · Tool comparison · Pitfalls · Sources

**Related:** `3d-webgl.md` (real-time 3D, glTF pipeline) · `scroll-parallax.md` (scroll choreography) · `motion.md` · `accessibility.md`.

**Verification.** Every ffmpeg, Python and HTML recipe here was run on 2026-10-10 (ffmpeg 9.0.2, OpenCV 5.0, headless Chrome). No Higgsfield generation was run: generation spends credits.

## Higgsfield product surface (as of 2026-10-10)

Higgsfield (higgsfield.ai, founded 2023) is a creator platform that wraps third-party image and video models plus its own models, presets and apps behind one credit balance. Its home page claims "30+ models" and "40+ creative AI tools". Reuters reported a $400M Series B at a $5.4B valuation in August 2026.

**Model ids** are from a read-only MCP snapshot taken 2026-10-10. They change often, so re-check with `models_explore` before relying on one.

| Area | What exists | Verified via |
|---|---|---|
| In-house image | **Soul** (launched 2025-06-26; 50+ style presets, camera-like grain and flash). **Soul 2.0** (reference mode, **Soul ID** character consistency trained on about 20+ photos). Soul Cinema. | Higgsfield blog and help center (search results); Soul 2.0 date unverified |
| Hosted image | Nano Banana 2.1 (Google; 4K, mask inpaint, ratios up to 8:1) `nano_banana_2_1`. FLUX 3 Image (≤10 references, 4K) `flux_3_image`. FLUX.2 Pro Outpaint `flux_2_pro_outpaint`. GPT Image 2.5 (`background: transparent`, good text) `gpt_image_2_5`. Marketing Studio Image. | MCP snapshot; home page |
| In-house video and camera | **Cinema Studio Video 3.0 / 4.0** `cinematic_studio_video_4_0`: camera body, lens, aperture, pacing, genre, era, lighting rig, palette; t2v, omni-reference, edit, extend; 4–30 s. **DoP** ("Director of Photography", shown as "Higgsfield Standard"): image-to-video camera presets in Effects, Basic Camera Control, Epic Camera Control and Catch the Pulse; "Mix" combines presets; 3 or 5 s. **Genjutsu** (motion transfer and object replace). | MCP snapshot; DoP help page (2026-08); home page |
| Hosted video | Kling 3.0 `kling3_0` (start+end frame, multi-shot, 4K mode); Kling 3.0 Omni and first/last-frame `kling_o3_flf` (≤7 references); Kling 3.0 Turbo and 2.6. Seedance 2.0, 2.0 Mini, 2.5 `seedance_2_0` / `seedance_2_5` (reference-driven identity, start/end frames, 2.5 adds edit and extend, 4–30 s). MiniMax H3 and Hailuo 2.3. FLUX 3 Video. Grok Video 1.5. Wan 2.6. Veo 3.1 is listed on the home page and in the May 2026 MCP post. | MCP snapshot; home page; Higgsfield MCP blog |
| Sora 2 | Still named in home-page text, but OpenAI removed the Videos API and every `sora-2*` model on **2026-09-24**. Treat it as unavailable. | OpenAI deprecations page |
| Effects and apps | Visual Effects presets (e.g. Floating fall, Studio slide, World morphing, Cutout). Apps: Angles 2.0 (new view angles of an image), Shots (9 shots from one image), Transitions, Relight, Expand image, Breakdown (split an image into components), Background Remover, Video Background Remover, Bullet Time Scene/White (product spin), Click to Ad; 3D Rotation, 3D Render and 3D Figure are listed. | /apps page |
| Product and marketing | Marketing Studio, Ads Studio / Ad Multiplier. MCP workflows: `product-photoshoot` (packshots, lifestyle, hero banners, CGI-style), `brand-asset-creation` (logos, kits, mockups), `video-editing` (motion graphics, title cards). | MCP snapshot; home page |
| 3D | `generate_3d` → GLB with Meshy v5/v7 `meshy_v7_image_to_3d` (PBR, remesh, 100–300k target polys, rigging), Tripo H3.1 `tripo_h3_1_image_to_3d`, Hunyuan3D v3/3.1 `hunyuan3d_v3`, SAM 3 3D. There is also a `scene_builder_3d_*` toolset (GLB/.blend export, new angles) reached through the `/3d-jutsu` preset. | MCP snapshot and tool list |
| Upscale and utility | Topaz video upscale to 2160p with frame interpolation (`topaz_video`), Topaz Hyperion (SDR→HDR), Bytedance Video Upscale (4K, 24–60 fps), Video Deflicker, `upscale_image`, `reframe` (change aspect), `outpaint_image`, `remove_background`, `video_background_remover`. | MCP snapshot |
| Site builder | `website-builder-flow` workflow plus `create_website` / `deploy_website` / `publish_website`. These host the site **on Higgsfield**; use them only when the user wants that. | MCP snapshot and tool list |
| Agents | Higgsfield MCP at `https://mcp.higgsfield.ai` (OAuth, spends the account's credits), the "Supercomputer" agent, and "Dots" for ChatGPT. | Higgsfield MCP blog (2026-05-08); home page |

**Not verified:** plan prices and credit cost per model (the pricing page renders client-side and returned no data); which models are in "unlimited" offers (the snapshot account had `unlim.available: false`); and Soul 2.0's release date.

## When to generate (and when not)

**Generate:**

- Ambient hero loops and atmosphere plates.
- Lifestyle and context shots around a real product.
- Textures and backgrounds.
- Mood frames and storyboards.
- "Fake 3D" camera moves over a still.
- Concept image-to-3D that then goes through the glTF pipeline.

**Don't generate:**

- Pack shots that must match the real SKU (colours, ports, labels, legal text). Shoot or render the real thing instead, and use AI only for the scene around it.
- Identifiable real people without consent.
- Logos and wordmarks. Use the vector original, and use `brand-asset-creation` only to mock up around it.
- Charts, UI screenshots, or anything that claims to be factual.

**Never bake headlines, CTAs or Thai/any copy into pixels.** Keep text in HTML: it stays accessible, translatable, crisp, and in real fonts (see `typography-layout.md`). Generated Thai glyphs are unreliable.

**Cheaper alternatives first:**

- A shader blob (`3d-webgl.md` recipe 5) or a CSS gradient beats a video loop for abstract motion.
- Rive beats video when the motion must react to state or input.

## MCP workflow (when a Higgsfield MCP is connected)

Hard rules for the agent:

- Never call `generate_*`, `execute_preset`, `upscale_*`, `outpaint_image`, `remove_background`, `reframe`, `motion_control`, website deploy or publish tools, or batch tools without the user's explicit go-ahead **for that run**. Browsing presets never authorizes `execute_preset`.
- Read-only discovery is fine at any time: `balance`, `show_plans_and_credits`, `models_explore`, `get_workflow_instructions`, `get_presets`, `get_preset_instructions`.

1. **Spec the asset.** Write down:
   - placement and aspect at each breakpoint (16:9 desktop, 4:5 or 9:16 mobile, 21:9 ultra-wide)
   - duration and whether it loops
   - layers needed
   - which side holds the headline (negative space)
   - palette words
   - deliverable sizes
   - fallback poster
2. **Discover and quote.**
   - Call `balance`.
   - Call `models_explore` (list or recommend) for candidate models, then quote exact prices with `generate_image` / `generate_video` and `get_cost: true` (returns credits, submits nothing; `models_explore` does not show prices).
   - For multi-step videos, call `get_workflow_instructions` with no argument. For stills, use `product-photoshoot` or `brand-asset-creation`.
   - Tell the user: "Plan: 4 stills on <model> + 2 × 6 s videos on <model> + 1 upscale ≈ <credits>; balance <n>. Proceed?"
   - Wait for a clear yes. Third-party guides report video calls of tens of credits each (unverified), so call `balance` again afterwards and report actual spend.
3. **Stills first.** Run `generate_image` with 3–4 variants at the final aspect, with negative space on the headline side.
   - Let the user pick one.
   - `outpaint_image` (FLUX.2 Pro Outpaint) widens to 21:9 or adds headline room without re-rolling.
   - `upscale_image` only on the pick.
4. **Layers (if parallax).**
   - `remove_background` on the subject, or generate the subject on `background: transparent` (GPT Image 2.5).
   - Generate the empty background plate separately, at the same lens, horizon and light.
5. **Animate the pick.** Run `generate_video` with the still as `start_image`.
   - For a loop, set `end_image` to the same still.
   - Turn audio off (`sound: off` / `generate_audio: false`); most models generate audio by default.
   - Use 4–8 s and one slow camera move.
6. **Finish.**
   - `upscale_video` (Topaz) only if the source is under the display size.
   - `reframe` for extra aspects.
   - Download the files, then do all of §Post-processing locally: encode, seam check, register stills, take posters from frames.
7. **3D.** `generate_3d` (Meshy, Tripo, Hunyuan3D) gives a GLB. Run `gltf-transform optimize` before shipping, and set budgets per `3d-webgl.md`.

### Photoreal stills pipeline (run end to end on 2026-10-10)

What replaced drawn SVG products, food, people and places on four test sites (22 images, 48.5 credits, about 10 minutes):

| Need | Model | Settings | Credits (2K, observed) |
|---|---|---|---|
| Scene plates, editorial shots, macro, lifestyle, people | `nano_banana_2_1` | `resolution: "2k"`, aspect per slot | 2 |
| Cut-out objects for layering (products, dishes, bottles) | `gpt_image_2_5` | `quality: "high"`, `background: "transparent"`, `resolution: "2k"` | 2.75 |
| Multi-reference consistency (same product in many shots) | `flux_3_image` | up to 10 `image_references` | 3 |

1. **Inventory the slots** from the page: every drawn real-world thing → one image (aspect, cut-out or plate, where the copy sits, palette hex, lighting that matches the scene).
2. **Quote and ask**: `get_cost` per model × slot count; tell the user the total and the balance; wait for yes.
3. **Submit with `generate_image_batch`** (≤ 12 per call; smaller groups of ~6 avoid rate limits). Items that return `submission_failed … 429` were never submitted and cost nothing — resubmit only those indices after the first jobs finish. Log every `index → job_id` to a file before polling so nothing is double-submitted.
4. **Poll with `jobs_wait`** (≤ 12 jobs, 15 s), then show the whole set once with `show_generation_by_ids`; download each `result_url` (PNG, alpha kept for transparent jobs) and check the balance afterwards to report actual spend.
5. **Sets in one call**: for families of objects (eight dishes, a product range), generate one transparent grid ("4 columns × 2 rows, generous space, nothing touching") and split it locally by connected alpha regions — one call instead of eight, and a shared light and style:

```python
from PIL import Image; import numpy as np
im = Image.open('grid.png').convert('RGBA'); mask = np.array(im)[:, :, 3] > 24
# label connected regions on a 4× downsampled mask (BFS), keep regions > 2000 cells,
# sort by row then column, crop each bounding box (+8 px) and save as its own PNG
```

6. **Integrate, don't paste** (`creative-direction.md` §5): contact shadows under cut-outs, rim light in the brand accent, scrims for copy (alpha derived from tokens), edge fades into the page background, WebP at 1×/2× with budgets below.

Consistency rules learned from integrating these sets (each mismatch was visible on the finished pages):
- **One product, many shots: generate the hero cut-out first, then every other shot of that product with it as a reference** (`flux_3_image` `image_references`, or a GPT Image 2.5 edit of the cut-out). Independent prompts gave a sneaker whose editorial and macro shots had a different sole and material, and a serum whose lifestyle bottle had a different collar and label.
- **One camera for a set**: write the same angle and lens into every prompt of a family ("straight top-down 90°, 50 mm, soft window light from upper right"). A high-angle rice pot among straight-down dishes reads as pasted in.
- **Resolution for full-bleed plates**: a 2K plate is soft on 1920 px retina screens — generate at 4K or `upscale_image` the one plate that fills the viewport.
- **Variants by recolour** (a shoe in another colourway) are cheap and convincing, but they share a silhouette with the original: flag them in the spec and never use two on the same screen.
- **Day → night**: a daylight photo placed in a night story looks fake; regenerate with night lighting, or re-light it (one practical light, everything else falling to the night colour, lifted blacks) and say so in the spec.

Prompt template that held up: *subject + materials* ("charcoal-black engineered knit upper, lime-green (#C6F432) foam midsole") · *framing* ("side profile facing right", "top-down", "three-quarter top view") · *light* ("soft key from top-left, crisp rim light", "backlit so the drop glows amber") · *setting or transparency* · *room for copy* ("left third darker and calmer for a headline") · "photorealistic, no text, no logos, no brand marks". People: hide faces unless a face is the point, and treat generated people as placeholders (below).

**Fallback without the MCP.** The agent writes the spec, prompts and model choice, and the user generates in the Higgsfield web app (or Midjourney, Runway, Veo, Kling…) and drops the files in the repo. The agent then does every local step: encode, seam, registration, posters, markup. If generation isn't available at all, ship the shader or CSS alternative.

## Asset recipes

**Hero background loop.**

- A still with a calm centre of interest goes to `start_image` = `end_image`, with "subtle ambient motion, locked camera, no cuts" and audio off, 5–8 s.
- Check the seam (§Post-processing). If the model can't close the loop, use ping-pong (forward + reverse; seamless by construction, fine for drifting light, smoke, fabric, water) or a crossfade.

**Product shots.**

- Composite the real product render or photo into a generated scene with matched light direction and lens. Use the `product-photoshoot` workflow or the Relight app.
- Never let a model "redraw" the product: check logos, ports, colours and text against the real SKU.

**"Fake 3D" parallax hero from a camera preset.**

- One still plus a DoP or Cinema Studio camera move (dolly-in, arc left or right, crane) gives 2.5D depth for free.
- Moves that don't return to the start can't loop. Use ping-pong, or play once and hold the last frame. Use `video.currentTime` scrubbing for scroll control.

**True parallax: separate layers.** Build 3–4 layers: background plate, mid-ground, subject cut-out (transparent PNG/WebP), and optional foreground particles.

- Animate each layer only with `translate3d` (pointer or scroll), at depth factors such as 0.2 / 0.5 / 1.0.
- Keep each layer's static box on whole pixels, and give each object its own `perspective()`.
- If the background is a generated *video*, register every still overlay to the video's frames first (see Pitfalls). Never assume the still and the video share a pixel grid.

**Image-to-video for scroll-scrubbed sequences.** A camera orbit or exploded-view clip (Bullet Time White, 3D Rotation, or a Cinema Studio orbit) works well. Then either:

- encode all-intra or GOP ≤ 5 and set `video.currentTime` from scroll progress, or
- extract frames to WebP/AVIF and draw them to a `<canvas>`.

All-intra is about 8× the size of GOP 5 on the test clip, so cap scrub clips at about 3–5 s, 720–1080p.

**Style and character consistency.**

- Fix the reference set: Soul ID or character sheet (`get_workflow_instructions {workflow:"character-sheet"}`), 3–10 references for FLUX 3 / Kling Omni / Seedance.
- Keep one model per campaign, and save prompt, seed, model id and references in a provenance log.
- Re-use the exact palette words and lens and light phrasing.

## Prompt patterns for UI assets

Build each prompt from these slots, in order:

1. **Subject** and setting.
2. **Composition.** For example "subject on right third, clean empty negative space on the left half for a headline, low horizon".
3. **Lens and camera.** For example "35mm, eye level, f/2.8, shallow depth".
4. **Light.** For example "soft key from upper left, warm rim light, overcast diffused".
5. **Palette.** Brand words, for example "deep navy, electric violet accents, warm off-white".
6. **Grade and texture.** For example "subtle film grain, low contrast, matte".
7. **Exclusions.** "no text, no letters, no logos, no watermark, no people".
8. **Aspect.**

**Video prompts.** Describe what moves, what stays, how fast, and that there are no cuts. For example: "slow 5% dolly-in, steam drifting upward, camera horizon locked, no cuts, no zoom pulses, seamless loop".

**Examples:**

- *SaaS hero (16:9):* "Abstract glass ribbons floating in a dark studio, ribbons on the right third, empty dark negative space on the left half, 50mm, soft top light with violet rim light, palette deep navy and electric violet with off-white highlights, subtle grain, no text, no logos".
- *Wellness app (4:5 mobile):* "Morning light through linen curtains onto a ceramic cup on a wooden table, subject in lower third, calm empty wall above for a headline, 35mm eye level, soft window light from left, palette sage green, oat, warm white, no text, no people".
- *Loop motion:* "Locked camera. Only the curtains sway gently and dust motes drift in the light beam. 6 seconds, no cuts, last frame matches first."

## Post-processing and encoding

Every command below ran on ffmpeg 9.0.2. Strip audio for UI loops (`-an`), and take the poster from the encoded video's frame 0.

```bash
# H.264 baseline (every browser); 1080p30 → avc1.640028
ffmpeg -i master.mov -an -c:v libx264 -preset slow -crf 23 -profile:v high -pix_fmt yuv420p -movflags +faststart hero.h264.mp4
# HEVC for Safari; tag MUST be hvc1 for Apple; 1080p30 → hvc1.1.6.L120.B0
ffmpeg -i master.mov -an -c:v libx265 -preset slow -crf 28 -tag:v hvc1 -pix_fmt yuv420p -movflags +faststart hero.hevc.mp4
# AV1 (SVT-AV1; crf 0–63, preset −2..13); 1080p30 → av01.0.08M.08
ffmpeg -i master.mov -an -c:v libsvtav1 -preset 6 -crf 35 -pix_fmt yuv420p -movflags +faststart hero.av1.mp4
# VP9 WebM (optional; constant quality needs -b:v 0)
ffmpeg -i master.mov -an -c:v libvpx-vp9 -crf 33 -b:v 0 -row-mt 1 -deadline good -cpu-used 2 -pix_fmt yuv420p hero.vp9.webm
# Scroll-scrub variant: keyframe every 5 frames (or -g 1 all-intra, ~8× larger in the test)
ffmpeg -i master.mov -an -c:v libx264 -preset slow -crf 23 -g 5 -keyint_min 5 -sc_threshold 0 -bf 0 -pix_fmt yuv420p -movflags +faststart scrub.mp4
# Posters from the video's own frame 0 (JPEG and AVIF); this build lacks libwebp → use cwebp for WebP
ffmpeg -i hero.h264.mp4 -frames:v 1 -q:v 2 poster.jpg && ffmpeg -i hero.h264.mp4 -frames:v 1 -c:v libsvtav1 -crf 30 poster.avif
# Ping-pong loop (seamless by construction): N = frame count; drops the two duplicated turn-around frames
ffmpeg -i clip.mov -filter_complex "[0:v]split[a][b];[b]reverse,trim=start_frame=1:end_frame=$((N-1)),setpts=PTS-STARTPTS[r];[a][r]concat=n=2:v=1:a=0" pingpong.mov
# Crossfade loop (clip length L, fade D; output L−D long): 15.3 → 30.8 dB on a broken test loop; not exact
ffmpeg -i clip.mov -filter_complex "[0:v]split[x][y];[x]trim=start=D,setpts=PTS-STARTPTS[m];[y]trim=end=D,setpts=PTS-STARTPTS[h];[m][h]xfade=transition=fade:duration=D:offset=L-2D" loop.mov
```

**Loop-seam check.** Compare PSNR(last → first) against the clip's own median adjacent-frame PSNR.

```bash
#!/usr/bin/env bash
set -euo pipefail; in="$1"
n=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$in")
seam=$(ffmpeg -hide_banner -nostats -i "$in" -i "$in" -filter_complex \
  "[0:v]select='eq(n\,$((n-1)))',setpts=0[a];[1:v]select='eq(n\,0)',setpts=0[b];[a][b]psnr" -f null - 2>&1 \
  | sed -n 's/.*average:\([0-9.inf]*\).*/\1/p' | tail -1)
ffmpeg -hide_banner -nostats -loglevel error -i "$in" -i "$in" -filter_complex \
  "[0:v]trim=start_frame=1,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]psnr=stats_file=/tmp/adj.$$.log" -f null - || true
med=$(sed -n 's/.*psnr_avg:\([0-9.inf]*\).*/\1/p' /tmp/adj.$$.log | sort -g | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}')
rm -f /tmp/adj.$$.log; echo "frames=$n seam_psnr=$seam adjacent_median_psnr=$med"
```

**Reading the result.** These are the test-clip numbers:

| Case | Seam PSNR | Adjacent median | Verdict | Action |
|---|---|---|---|---|
| Seamless | 39.09 dB | 39.07 dB | Within ±1–2 dB of median: ship | — |
| Duplicated end frame (start = end) | 73 dB | 39.07 dB | Seam far above median: the loop stutters on a repeated frame | Drop the last frame (`-vf trim=end_frame=$((n-1))`); this one went to 39.08 dB |
| Broken loop | 15.3 dB | 39.07 dB | Seam far below median: visible jump | Regenerate with start = end, ping-pong, or crossfade |

**Markup.** The poster `<img>` is the LCP. Sources are attached only when motion and data are allowed, the first decodable codec wins, the video pauses offscreen, and there is a user pause button (WCAG 2.2.2). This was tested in headless Chrome with a strict autoplay policy: it picked AV1, played muted, and showed the button.

```html
<figure class="hero-media">
  <img src="/hero/poster.jpg" alt="" fetchpriority="high" width="1920" height="1080">
  <video muted loop playsinline preload="none" aria-hidden="true" width="1920" height="1080" poster="/hero/poster.jpg">
    <source data-src="/hero/hero.av1.mp4"  type='video/mp4; codecs="av01.0.08M.08"'>
    <source data-src="/hero/hero.hevc.mp4" type='video/mp4; codecs="hvc1.1.6.L120.B0"'>
    <source data-src="/hero/hero.h264.mp4" type='video/mp4; codecs="avc1.640028"'>
  </video>
  <button type="button" class="hero-toggle" aria-pressed="false" hidden>Pause background video</button>
</figure>
<style>
  .hero-media { position: relative; aspect-ratio: 16 / 9; margin: 0 }
  .hero-media > img, .hero-media > video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover }
  .hero-media > video { opacity: 0; transition: opacity .3s } .hero-media > video.is-playing { opacity: 1 }
</style>
<script type="module">
  const v = document.querySelector('.hero-media video'), btn = document.querySelector('.hero-toggle')
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches && !navigator.connection?.saveData) {
    v.querySelectorAll('source').forEach((s) => { s.src = s.dataset.src }); v.load()
    v.addEventListener('playing', () => { v.classList.add('is-playing'); btn.hidden = false }, { once: true })
    v.play().catch(() => {})                                   // NotAllowedError → the poster simply stays
    new IntersectionObserver(([e]) => {
      if (btn.getAttribute('aria-pressed') === 'true') return  // respect the user's pause
      e.isIntersecting ? v.play().catch(() => {}) : v.pause()
    }).observe(v)
    btn.addEventListener('click', () => { const pause = !v.paused; pause ? v.pause() : v.play()
      btn.setAttribute('aria-pressed', String(pause)); btn.textContent = pause ? 'Play background video' : 'Pause background video' })
  }
</script>
```

**Codec support** (caniuse, 2026-10):

| Codec | Support |
|---|---|
| H.264 | Universal |
| HEVC | Safari 13+; partial in Chrome 107+, Edge, Firefox 137+ (hardware-dependent) |
| AV1 | Chrome 70+, Firefox 67+, Edge 121+; Safari 17+ partial |

Always ship H.264 last as the safety net. MDN: `playsinline` is "required for autoplay in Safari"; muted video may autoplay; handle the `play()` promise rejection.

**Hero media budgets** (house rule; measure on 4G):

| Asset | Budget |
|---|---|
| Desktop loop, 1080p, 6–10 s | ≤ 2.5 MB |
| Mobile loop, 720p | ≤ 1.2 MB |
| Poster | ≤ 150 KB (AVIF/WebP) |
| Scrub clip | ≤ 4 MB |

- Serve a smaller mobile file via JS (`matchMedia('(max-width: 768px)')` picks the 720p `data-src`).
- Lower CRF only after the size check.
- Add subtle grain before encoding smooth gradients; it fights banding better than raising the bitrate.

## Licensing and brand safety

- Generated people are placeholders, never presented as real staff, doctors, patients or customers; label them in the spec ("replace with a real, consenting photo before launch"). Real brands need real product photography or renders from the real CAD/packaging — a generated product that differs from what ships misleads buyers.

**Higgsfield terms** (help center, 2026-08):

- §4.4: Higgsfield "does not claim ownership" of inputs or outputs, and "The Terms of Use do not restrict commercial use of outputs".
- Watermarks are embedded on plans that include them; "Paid plans include watermark-free downloads". Never ship free-tier output in a client deliverable.
- Higgsfield gets a licence to host and process content and to train models (Enterprise excluded).
- §5.1(ii)(b): you are responsible for third-party rights in your inputs.
- §5.3: no images of other people without permission. Identifiable faces also count as personal data under Thailand's PDPA (verify with counsel).

**Hosted models.** Each model's provider (Google, Kling, ByteDance, BFL, OpenAI…) has its own policies. Re-check the current terms for high-stakes campaigns (unverified per model).

**Copyright.** Pure AI output may not be protectable by copyright in some jurisdictions. Don't make a generated image the brand's only trademark asset.

**Brand-safety checklist before shipping:**

- No celebrity or real-person lookalikes.
- No competitor logos or trade dress.
- The product matches the real SKU.
- No fake features or claims.
- Hands, faces and text artifacts have been checked at 100%.
- Cultural and religious symbols have been reviewed for the target market.
- The platform's AI-disclosure rules for ads are followed.
- A provenance log is kept: prompt, model id, seed, date, credits, references and their rights.

## Tool comparison (2026-10)

| Tool | Best for | Frame / loop control | Notes |
|---|---|---|---|
| Higgsfield | One credit pool across many models; camera presets; product, ad and brand workflows; MCP | start/end frames on Kling, Seedance, MiniMax, FLUX 3 Video | Aggregator plus in-house Soul, DoP and Cinema Studio |
| Midjourney | Aesthetic stills and moodboards | V1 video (2025-06-18): image-to-video, 5 s clips extendable to 21 s; loop and end frame added later in 2025 (third-party reports) | Strong art direction; weaker on literal product accuracy |
| Runway | Editing existing footage | Gen-4.5 (2025-12-01) t2v; Aleph edits footage (relight, weather, reframe) | Editing-led workflows |
| Kling 3.0 | Cinematic motion, multi-shot | start + end frame, 4K mode | Also inside Higgsfield |
| Google Veo 3.1 | Realistic motion with native audio | first + last frame (2025-10-15); the same image at both ends makes a loop | ~8 s clips; specs and prices vary by host (unverified) |
| OpenAI Sora 2 | — | — | API removed 2026-09-24; don't plan on it |
| Luma Ray3 / 3.2 | HDR / EXR pipelines | `loop: true` for 5 s clips (Replicate readme) | 16-bit EXR HDR |
| Spline AI | Editable 3D scenes from prompts | n/a | Spline V2 (2026-08-21) agent and MCP; the output is a live web scene (`3d-webgl.md`) |
| Meshy / Tripo / Hunyuan3D / SAM 3 3D | Image → GLB | n/a | Through Higgsfield `generate_3d`; Rodin (Hyper3D) not verified |
| Rive | Interactive UI motion driven by state or input | State machines | Runtimes for web, iOS, Android, Flutter, React, Unity, Unreal; prefer it over video when UI must react |

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Ghost double when a still overlays the AI video (cut-out, mask or poster swap) | The generated video has a slightly different aspect and ~1% shift even when start and end frames equal the still | Register stills to the video: fit scale + dx/dy by least squares (script below), and take posters from the video's own frames, never the source still |
| Layered hero jitters by 1 px; layers swim | Fractional `left`/`top` snaps to whole pixels during animation; a shared `preserve-3d` stage | Integer static layout; move only with `translate3d`; own `perspective()` per object |
| Loop "hiccups" once per cycle | End frame duplicates the start frame (start = end generation) | Seam check; drop the last frame |
| Visible jump at the loop point | The model didn't close the loop | Regenerate with start = end, ping-pong, or crossfade; measure PSNR before shipping |
| Credits drained by re-rolls | Generating video before the still is approved; batch runs on "Always Allow" | Stills first; quote and confirm; `balance` before and after |
| Video loop plays a soundtrack, or the file is bigger than expected | Models generate audio by default | `sound: off` / `generate_audio: false`, plus `-an` on encode |
| HEVC file won't play in Safari | `hev1` tag | `-tag:v hvc1` |
| Hero video starts late | `moov` atom at the end | `-movflags +faststart` (verified: moov at byte ~36) |
| Scroll scrub stutters | Long GOP: each seek decodes from a far keyframe | GOP ≤ 5 or all-intra; or an image sequence on canvas |
| Autoplay doesn't start (browser policy; iOS Low Power Mode is commonly reported) | `play()` rejected with `NotAllowedError` | Poster `<img>` underneath; catch the promise; never rely on motion for content |
| Garbled text, extra fingers, warped logo | Generation artifacts | Keep text in HTML; inspect at 100%; inpaint or regenerate; composite real logos |

**Still → video registration** (OpenCV ≥ 4). On a synthetic 1.2% drift it recovered scale 1.0117 (true 1.012), dx 7.32 (7.3) and dy −4.13 (−4.1), and PSNR against the frame rose from 16.6 dB (naive resize) to 31.4 dB.

```python
# register_still.py STILL.png FRAME.png OUT.png   (FRAME = frame 0 of the encoded video)
import sys, cv2, numpy as np
still_p, frame_p, out_p = sys.argv[1:4]
A, B = cv2.imread(still_p), cv2.imread(frame_p)
ga, gb = (cv2.cvtColor(x, cv2.COLOR_BGR2GRAY) for x in (A, B))
orb = cv2.ORB_create(5000)
ka, da = orb.detectAndCompute(ga, None); kb, db = orb.detectAndCompute(gb, None)
m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(da, db)
p = np.float64([ka[x.queryIdx].pt for x in m]); q = np.float64([kb[x.trainIdx].pt for x in m])
keep = np.ones(len(p), bool)
for _ in range(6):                                   # least squares for x' = s·x + dx, y' = s·y + dy, trimming outliers
    n = keep.sum(); X = np.zeros((2 * n, 3))
    X[0::2, 0], X[0::2, 1] = p[keep, 0], 1
    X[1::2, 0], X[1::2, 2] = p[keep, 1], 1
    s, dx, dy = np.linalg.lstsq(X, q[keep].reshape(-1), rcond=None)[0]
    r = np.hypot(s * p[:, 0] + dx - q[:, 0], s * p[:, 1] + dy - q[:, 1])
    keep = r < max(1.0, 3 * np.median(r[keep]))
h, w = B.shape[:2]
out = cv2.warpAffine(A, np.float64([[s, 0, dx], [0, s, dy]]), (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
cv2.imwrite(out_p, out); print(f"scale={s:.5f} dx={dx:.2f} dy={dy:.2f} inliers={keep.sum()}/{len(p)}")
```

**Applying the registration:**

- Bake the warp into the overlay asset, as the script does; this is preferred.
- Or apply it in CSS on a box the same size as the video: `transform-origin: 0 0; transform: translate(calc(dx / w * 100%), calc(dy / h * 100%)) scale(s)`.
- Re-run it for every regenerated video. Extract the frame with `ffmpeg -i hero.mp4 -frames:v 1 frame0.png`.

## Sources

- Higgsfield home — https://higgsfield.ai/ · Apps — https://higgsfield.ai/apps · DoP help — https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-dop
- Higgsfield ownership and commercial use — https://higgsfield.ai/creator-hub/help-center/account-and-privacy/who-owns-my-generations-and-can-i-use-them-commercially
- Higgsfield MCP for Claude (2026-05-08) — https://higgsfield.ai/blog/Generate-AI-Videos-From-Claude-with-Higgsfield-MCP
- Higgsfield Soul launch post (2025-06-26, seen in search results) — https://higgsfield.ai/posts/50ogWiu9kVYbWw3spQjWIR
- Higgsfield MCP surface snapshot, 2026-10-10 (read-only calls) — `research/design-atlas/higgsfield-mcp-snapshot.md`
- Higgsfield Series B (Reuters via BNN Bloomberg, 2026-08-17) — https://bnnbloomberg.ca/business/company-news/2026/08/17/higgsfields-valuation-soars-fourfold-to-us54-billion-in-six-months-on-ai-content-demand
- OpenAI API deprecations (Sora 2 / Videos API) — https://developers.openai.com/api/docs/deprecations
- Veo 3.1 first/last frame — https://replicate.com/blog/veo-3-1 · https://getimg.ai/blog/google-veo-3-1-review
- Luma Ray 3.2 readme — https://replicate.com/luma/ray-3.2/readme · Midjourney loop/end-frame (third-party) — https://piapi.ai/en/blogs/midjourney-update-august-2025-video-loops-start-end-frames-and-api-access
- Runway Gen-4.5 (eWeek) — https://www.eweek.com/de/news/runway-ai-video-model/ · Spline V2 — https://updates.spline.design/changelog/introducing-spline-v2 · Rive — https://rive.app/
- MDN Autoplay guide — https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Autoplay · NetworkInformation.saveData — https://developer.mozilla.org/en-US/docs/Web/API/NetworkInformation/saveData
- caniuse AV1 — https://caniuse.com/av1 · HEVC — https://caniuse.com/hevc
- WCAG 2.2 Understanding 2.2.2 Pause, Stop, Hide — https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html
- Local verification log (ffmpeg, OpenCV, headless Chrome runs) — `research/design-atlas/3d-ai-assets-notes.md` §13
