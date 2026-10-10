# Higgsfield MCP surface — snapshot 2026-10-10

Read-only calls made from this session (`get_workflow_instructions` with no argument, `models_explore list/recommend`). No generation was run, no credits spent. Model lists change often; re-check with `models_explore` before relying on an id.

## Workflows the MCP bundles (`get_workflow_instructions`)
ad-multiplier, ads-studio, brand-asset-creation (logos, identity, brand kits, mockups, recolor/export of official logos), character-sheet, faceless-video, katana (edit/remix source footage), narration, product-photoshoot (packshots, lifestyle, hero banners, CGI-style product images), thumbnail-generation, ugc-video, video-editing (Higgsedit motion graphics, shaders, overlays, title cards), video-montage, website-builder-flow (builds/deploys sites on Higgsfield: `website` = independent brand, `app` = Higgsfield-integrated, `game`).

Design-relevant: **product-photoshoot** (hero/product stills), **brand-asset-creation** (logo work, brand kits), **video-editing** (motion graphics), **website-builder-flow** (only when the user wants the site hosted on Higgsfield).

## Video models seen (`models_explore list type=video`, first 40)
- Higgsfield **Cinema Studio Video 3.0 / 4.0** — cinema-grade; 4.0 exposes camera body, lens, aperture, pacing, genre, era, lighting rig, color palette controls; modes t2v / omni_reference / video_edit / video_extension; 4–30 s.
- **Kling 3.0** (start+end frame, multi-shot, 4k mode), **Kling 3.0 Omni** (up to 7 reference images; frames variant with first/last frame), Kling 3.0 Turbo, Kling 2.6, Kling 3.0 Omni Edit.
- **Seedance 2.0 / 2.0 Mini / 2.5** (Bytedance) — reference-driven, consistent identity, start/end frames, up to 4k (2.0 std), 2.5 adds video edit/extension, 4–30 s.
- **MiniMax H3 / H3 Max**, Minimax Hailuo 2.3 (start/end frame).
- FLUX 3 Video (BFL) — start/end frame, image + video references, 5–20 s; FLUX 3 Video Edit.
- Grok Video 1.5 / 1.5 Lite (xAI), Wan 2.6, Happy Horse.
- Utilities: Video Background Remover, Reframe (change aspect), Topaz (upscale to 2160p + frame interpolation), Topaz Hyperion (SDR→HDR), Bytedance Video Upscale (to 4k, 24–60 fps), Video Upscale, Video Deflicker, Genjutsu (motion transfer).
- Many models accept **`start_image` + `end_image`** roles → set both to the same still for a seamless loop; most generate audio by default → turn it off for UI background loops (`sound: off` / `generate_audio: false`).

## Image models (recommend for "website hero with negative space / product shot")
Marketing Studio Image, DTC Ads (`ms_image`, needs a style id), **FLUX 3 Image** (up to 10 reference images, 4k), **FLUX.2 Pro Outpaint** (extend canvas per side — useful to widen a hero to 21:9 or add headline space), **GPT Image 2.5** (supports `background: transparent` — useful for layered parallax cut-outs; strong text rendering), **Nano Banana 2.1** (Google; 4k, inpaint with mask, extreme ratios up to 8:1).

## 3D models (`models_explore list type=3d`)
SAM 3 3D Objects (Meta, single image → textured GLB), Meshy Image/Multi-Image to 3D (v5/v7; texture, PBR, quad remesh, target polycount 100–300k, rigging + 600+ animation clips), Meshy 6 Text to 3D, Meshy Remesh/Retexture, Tripo Text to 3D and Tripo H3.1 image/multiview to 3D, Hunyuan3D v3 / v3.1 (Tencent), SAM 3 3D Body. Output is GLB → run through `gltf-transform` (meshopt/Draco, KTX2) before shipping to the web.

## Account state at snapshot
`unlim.available: false` — generations would spend credits. Always call `balance` and quote the cost before generating, and get the user's go-ahead.
