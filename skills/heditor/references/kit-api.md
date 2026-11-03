# Kit API (scripts/reelkit)

Import in a cut's `build.py`:
```python
import os, sys; from pathlib import Path
sys.path.insert(0, os.environ.get("HEDITOR_KIT", str(Path.home() / ".heditor/kit")))
import reelkit as rk
```

## Brand and assets
- `rk.load_brand(work)` → dict `name, handle, logo, lang, follow, following, comment, colors{bg,bg2,accent,accent2,alert,ok}` (work/brand.json overrides ~/.heditor/brand.json).
- `rk.setup_assets(work)` copies fonts (all from `~/.heditor/assets/fonts`), `gsap.min.js`, `grain.png`, Lucide licence and the brand logo as `assets/logo.png` into `<work>/composition/assets`.
- Fonts available after setup (file names to use in `@font-face`): `Anton-Regular.ttf`, `VT323-Regular.ttf`, `Geist-VF.ttf`, `Inter-VF.ttf`, `JetBrainsMono-VF.ttf`, `IBMPlexMono-Regular.ttf`, `IBMPlexMono-Bold.ttf`, `PressStart2P-Regular.ttf`, `PlayfairDisplay-VF.ttf`, `PlayfairDisplay-Italic-VF.ttf`, `Fraunces-VF.ttf`, `BebasNeue-Regular.ttf`, `DMSerifDisplay-Regular.ttf`, `Caveat-VF.ttf`, `B612Mono-Regular.ttf`, `B612Mono-Bold.ttf`, `Fredoka-VF.ttf`, `InstrumentSerif-Regular.ttf`, `InstrumentSerif-Italic.ttf` (2.17.0+; older installs: rerun `setup.sh`). Need another? Download it from google/fonts (OFL) into `composition/assets` with its licence.
- `rk.ensure_icons(["name", ...])` downloads Lucide SVGs; `rk.icon(name, cls="ic")` returns inline SVG.
- `rk.setup_assets` also copies the GSAP plugins into `assets/gsap/`; `rk.gsap_plugin_tags(["SplitText", "DrawSVG", ...])` returns the `<script>` tags + `gsap.registerPlugin(...)` for a hand-written page (insert right after `gsap.min.js`). Names: `SplitText`, `DrawSVG`, `MorphSVG`, `MotionPath`, `CustomEase`, `CustomWiggle`, `CustomBounce`, `Text`, `Physics2D`, `PhysicsProps`, `ScrambleText`, `EasePack` (rules in `gsap-craft.md`).
- `import svgkit as sk`: `sk.optimize(src, dst, mode="static"|"draw"|"morph")` → report (bytes, element counts, `visual` diff, `ok`, `check_sheet`); `sk.inline(src, cls, mode, out_dir)` → cleaned inline markup, raises when the optimised SVG does not look like the original. CLI: `heditor svg`.
- `import physkit as pk`: `pk.setup(work)`, `pk.scene(...)`, `pk.rain(...)`, `pk.blast(..., exclude, unlock)`, `pk.bake(work, scene, name)` → `assets/physics-<name>.js`, `pk.land_on(work, scene, {id: t}, name)` (spawns corrected until each body lands on its word), `pk.landings(bake)`, `pk.importmap()`. Body locks: `"lock": "rotation"|"vertical"`, `lockRotationAxes`. Recipe in `physics-3d.md`.
- `svgkit.single_path(svg_text)` → one path `d` for a multi-shape icon (MorphSVG).
- `rk.prepare_camera(work, width=960)` → upscaled, lightly sharpened `camera-hd.mp4` (returns width, height).
- `rk.styled_camera(work, name, vf)` → `camera-<name>.mp4` from camera-hd with an ffmpeg filter chain. Examples: CCTV `eq=saturation=0.25:contrast=1.2,colorbalance=gs=.08,noise=alls=18:allf=t` · pixel `scale=160:-2:flags=neighbor,scale=960:-2:flags=neighbor` · warm film `curves=preset=increase_contrast,colortemperature=temperature=4800,noise=alls=6:allf=t` · radar green `format=gray,format=rgb24,colorchannelmixer=.2:.2:.2:0:.7:.7:.7:0:.25:.25:.25:0`.
- `rk.prepare_voice(work)` → `voice-master.wav` (declip, high-pass, adaptive denoise, -2.5 dB @250 Hz, +2.5 dB @3.2 kHz, de-esser, 3:1 compressor, limiter).

## Words and captions
- `import triage as tr`: `tr.voiced_chunks(db, win, thr, gap, min_len)` → `[[a, b], ...]` runs above `thr` dB merged across gaps shorter than `gap`; `tr.classify(chunks, lang)` labels `[{"a", "b", "text", "words"}]` in place (`keep`, `retake`, `false_start`, `editor`, `noise`, with a `note`); `tr.is_editor(text, lang)`, `tr.aside_intent(text, lang)` (`cut`/`redo`/`marker`/`note`), `tr.instructions(chunks, lang)` (asides with neighbours and action), `tr.chunk_issues(chunk, lang, forbid)` (stutter, repeat, aside_inside, self_correction, forbidden, unclear with word times), `tr.tech_report(video, chunks)` (clipping, sounds outside speech, duplicated frames, set jumps between kept chunks), `tr.build_report(...)`, `tr.triage(video, model, lang, thr, gap, forbid, tech)` → report. CLI: `heditor triage`; procedure in `raw-takes.md`.
- `import textnorm as tn`: `tn.tokens(text)`, `tn.notation_tokens(text, lang)` (contractions, number words, times and split brand words folded), `tn.same_notation(a, b, lang)`. Used by `asr-check` and triage.
- `rk.load_words(path, censor=None)` → `[{word, shown, start, end}]` sorted.
- `rk.finder(words)` → `f(token, after=0.0)` returns the start of the first matching word (case/punctuation-insensitive) after a time. Use it for key moments.
- `rk.captions(words, voice_end, max_words=3, max_chars=17)` → groups `{id, start, end, text, words}`; never overlapping.
- `rk.captions_html(caps)` / `rk.captions_js(caps, mode="text"|"pill")` → default caption band (Anton, uppercase, y 1222–1472). Write your own renderer for world-native captions but keep `plan["captions"]` identical to what appears.

## Page skeleton (optional)
`rk.page(title, duration, card_w, card_h, face_origin, videos, scenes_html, css, js, keys, caps, world_back="", overlays="", caption_mode="text", brand_work=work, plugins=(), caption_pill=("#000000", "#ffd84d"))` (`caption_pill`: active-word text and pill colours in pill mode) builds a HyperFrames page with:
`#stage > #world > #bg, world_back, #glow-a/#glow-b, .floor, #horizon, .speed, #rig-aura, #rig > #squeeze > #frame > #cam-zoom > #cam-breath > #cam-jump > videos, #cam-tint, #cam-scan, #cam-over, #border; scenes_html; overlays; #vignette; .conf` + caption band + `#grain`, `#flash` + `audio#master`. CSS variables `--bg --bg2 --accent --accent2 --alert --ok` come from the brand.
- `rk.rig_states(card_w, card_h)` → `{"hero": {...}, "top": {...}}` (add your own states, e.g. `pip`). `keys["rig"] = [[t, state, dur], ...]`.
- `rk.SAFE_TOP = 270`, `rk.CARD_BOTTOM_MAX = 1200`, `rk.PANEL_TOP_MIN = 670`.
- Writing your own page is encouraged for creative formats. Requirements: root `<main id="stage" data-composition-id="main" data-start="0" data-duration=".." data-width="1080" data-height="1920" data-fps="30">`; media as `.clip` elements with `data-start`, `data-duration`, `data-track-index` (unique per track); `<audio class="clip" src="assets/master.wav">`; one paused GSAP timeline registered as `window.__timelines.main`; deterministic (seeded random only, no Date/Math.random).

## JS helpers (BASE_JS, available inside `js`)
`S(sel, vars, t)` set · `TO(sel, vars, t)` to · `FT(sel, from, to, t)` fromTo · `out(sel, t, vars)` fade out · `pop(sel, t)` · `shake(t, amp)` on `#world` · `flash(t, peak, dur, color)` · `punch(t, scale, hold, back)` camera zoom · `rig(state, t, dur)` · `confetti(t, x, y)` · `speedlines(t)` · `rnd()` seeded (`keys["seed"]`) · `scramble(sel, text, t, dur, chars?, fps?)` deterministic decode/scramble of a text element (precomputed with `rnd()`; use it instead of ScrambleTextPlugin, which calls `Math.random`). `K` = keys, `D` = duration. `K.segments` (from `rk.jump_segments`) drives jump-cut zoom 1.0↔1.075 and 1.5% breathing on `#cam-jump/#cam-breath`.

## Face tracking
`faces = rk.track_faces(work, video="camera-hd.mp4", step=0.2)` (MediaPipe) → `qa/face-track.json`; `rk.jump_segments(work, faces, voice_end)` → segments between EDL cuts with the median face centre (never smoothed across a cut). Use the face centre for zoom origins and to place graphics on the opposite side.

## depthkit (layered / 2.5D / 3D)
`import depthkit as dk` (same folder as reelkit). `dk.person_matte(work)` → `camera-alpha.webm` + `matte-person.mp4`; `dk.depth_map(work, fps)` → `depth.mp4`; `dk.depth_look(work, name, vf_bg)`, `dk.edge_look(work, name, color, source)`, `dk.dots_look(work, name, color, step)` → `camera-<name>.mp4`; `dk.plane_matrix3d(w, h, quad)` → CSS `matrix3d`; `dk.track_points(work, t0, pts, t1)`; `dk.track_hands(work, t0, t1)`; `dk.to_stage(pt, video_size, box)`; `dk.setup_three(work)` copies three.js for offline 3D; `dk.still_layers(src, out_dir)` splits a still into a background and a soft front layer for 2.5D parallax. All outputs are frame-for-frame with `camera-hd.mp4` and rebuilt when stale. CLI: `heditor matte|depth|look|hands|plane`. Details and recipes: `depth-and-3d.md`.

## Generated media (`import genkit as gk`, optional HeyGen)
- `gk.upload(path|url|asset_id)` → `{"type": "asset_id"|"url", ...}` (uploads once, cached by content hash); `gk.identity_image(look_id|path)` → local image of an identity source; `gk.estimate(kind, mode, res, units, billing)` and `gk.rate(...)` (measured history in `~/.heditor/heygen-usage.json` first); `gk.record(work, entry)` → `<work>/gen/gen.json`.
- CLI: `heditor gen status|persona|clip|talk|resume` (see `generation.md`); every command prints the plan and the estimate and spends nothing without `--yes`.

## Hook tests (`import splice as sp`)
- `sp.find_cut(video, t0, t1)` → first black frames after a lit one, the biggest picture jumps and the audio level at each (the splice frame).
- `sp.splice(opening_work, body_mp4, out_mp4, cut_frame=K, xfade_ms=8, match=True, overlay=None, overlay_until=None, overlay_fade=(0.30, 0.25), crf=14)` → joins `round(D·fps)` frames of the opening's render and its `master.wav` to the delivered body from frame K (body audio decoded whole, cut by sample, never processed), encodes once and writes `<out>.splice.json` (frame counts, gain, loudness at the splice, body/opening audio correlation and lag, frame differences, `ok`). CLI: `heditor splice`. Procedure in `hook-variants.md`.

## Plan formats
- Sound event: `{"time": s, "category": "whoosh", "variant": 0, "gain_db": -14, "rate": 1.0, "length": 0.6, "context": "why"}`. Categories: `rk.sfx_library().keys()`.
- Music section: `{"start", "end", "mode": "full|radio|lowpass|muffled|vhs|retro|silence", "gain_db", "track", "src" (seconds inside the track), "fade_in", "fade_out"}`. `rk.music_path("music:955")` → local file.
- `rk.mix(work, plan, rk.sfx_library(), ...)` → writes `master.wav` (two-pass loudnorm -14 LUFS) and `qa/balance.json` (balance, `mix_profile`, `music_presence_pct`, `music_gaps`, `long_filtered_sections`, `asr_check_required`); returns the balance. Targets come from the profile in `plan["mix"]` (`"voice"` default, `"presence"` for paid ads/creative mode, or `{"profile": ..., <overrides>}`); `rk.MIX_PROFILES`, `rk.mix_targets(plan)`, `rk.presence_levels(x, hop)`, `rk.music_gaps(...)`. A build may define `sfx_lib()` to extend the library (e.g. synthesized sounds).
- `plan["duck_open"] = [[t0, t1], ...]`: declared pauses where the ducking opens at once (hits and swells at full level).
- `heditor music <music:ID|file> [out.json]` (`music_profile.py`): tempo, energy/s, kick/bass per second, breakdowns, kick entries, lifts — to choose each section's `src`.

## Format profiles (`import formats as fm`)
- `fm.get(key)` → profile for `9:16` (default), `16:9`, `16:9-4k`, `1:1`, `4:5` (aliases: `landscape`, `youtube`, `square`, `portrait`, `1920x1080`…): `width`, `height`, `safe` (Rect), `safe_top`, `caption` (Rect), `caption_px`, `caption_chars`, `caption_lines`, `lower_third`, `layouts` (`pip`, `screen`, `speaker`, `side` → `{"screen": Rect|None, "camera": Rect|None, "captions": Rect}`).
- `fm.of_work(work)` reads `plan.json` / `long.json` / `edl.json` `format`; `fm.crop_for(w, h, fmt, cx, cy)` ffmpeg crop that fills a profile; `fm.cover(box, w, h, focus)`, `fm.zoom_transform(box, region)`, `fm.check_layouts(fmt)`; `profile.thumb(width=…)` contact-sheet cell with the right aspect.
- Reels: `rk.page(..., fmt="1:1")` changes only the canvas; `prepare_cut(..., crop="fit:1:1")` crops the source to a profile.

## Long form (`import longkit as lk`, `longform as lf`, `stylepacks as sp`, `longmix`)
- `lk.build(work, lower_thirds=[...], set_pieces=[...], callouts=None|[...], layouts=None|[...], track="music:<id>", fmt=None, out_dir=None, extra_css="", extra_js="")` → writes `composition/index.html` (whole timeline), `plan.json` (`mode: "long"`, `format`, `style`, `kind`, `voice_offset`, `voice_end`, `captions`, `chapters`, `layouts`, `segments`, `sound_events`, `music`, `loudness`, `allowed_numbers`) and `segments/seg-NNN/` (one HyperFrames composition per render segment). Set piece kinds: `title`, `concept_map`, `checklist`, `callout`, `custom` (see `long-form.md`).
- `lk.Timeline` (`js(t0, code, t1, cap)`, `el(t0, t1, html, cap)`, `sfx(t, category, gain_db, context)`) and `lk.write_page(T, cfg, start, end, media)`: a segment page plays the global GSAP timeline from `start` (`tl.tweenFromTo`), so frames match the whole page.
- `sp.get(slug, overrides)` → resolved style pack (palette, fonts, captions, frame, overlay, transition, chapter_card, lower_third, camera_grade, sfx, music, long_notes); `sp.css_vars(pack)`; `sp.SLUGS` (every named style).
- `lf.propose_edl(words, db, t0, range, cfg)`, `lf.keep_ranges(range, cuts, fps, exclude)`, `lf.edl_chunks(keeps)`, `lf.remap_words(words, chunks, drop)`, `lf.out_to_source / source_to_out`, `lf.suggest_chapters / validate_chapters / youtube_timestamps`, `lf.cue_groups / to_srt / to_vtt`, `lf.plan_segments(duration, fps, max_len, cut_points, avoid)`, `lf.retention_plan(words, start, end, kind)`, `lf.estimate_render(seconds, fps, history, workers)`, `lf.CADENCE`.
- `longmix.mix(work, plan, rk.sfx_library())`: block-wise voice-first mix (bounded memory), same balance targets as `rk.mix`, loudness from `plan["loudness"]`.
- CLI equivalents: `heditor long <subcommand>` (`scripts/reelkit/long_cli.py`); QA: `longqa.run(work, final)`; sync: `camera_sync_check.sync_against_source(work)`.
