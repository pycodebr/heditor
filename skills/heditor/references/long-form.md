# Long-form mode (classes, lives, YouTube videos) and format profiles

heditor's Reels pipeline is built for 30-70 s vertical cuts. Long-form mode edits **minutes to hours** of a
recording into a video for YouTube, a course platform or a feed, in any **format profile** (16:9, 9:16, 1:1,
4:5, 16:9 4K), with the same named styles (as *style packs*) and creative mode (as *set pieces*).

## When to use

| The user wants | Use |
|---|---|
| a 30-70 s vertical clip with a hook, motion graphics and a Follow CTA | Reels workflow (`workflow.md`) |
| a whole class, live, lesson or YouTube video cleaned up (pauses, false starts, repetitions removed) | **long-form** |
| chapters, burned captions and/or SRT/VTT, lower thirds, intro and end cards | **long-form** |
| the same edit in 16:9 and also 1:1 / 4:5 / 9:16 | **long-form** (`--format`) |
| a 90-180 s narrative in 9:16 | Reels workflow with `max_duration` (see troubleshooting) |

Long form is not a long Reel. A 30-minute video with a Reel's graphic density exhausts the viewer and costs
hours of render. The body stays **clean and readable** (screen + camera layouts, captions, small retention
devices); the style lives in the frame, the cards and a handful of **set pieces** at key moments.

## Format profiles (`heditor formats`, `scripts/reelkit/formats.py`)

| Key | Canvas | Safe area (x, y, w, h) | Caption zone (y) | Typical use |
|---|---|---|---|---|
| `9:16` | 1080×1920 | 60, 270, 960, 1300 | 1222-1472 (84 px) | Reels, Shorts, TikTok (the historical numbers) |
| `16:9` | 1920×1080 | 96, 54, 1728, 972 | 880-1020 (50 px, 42 chars/line) | YouTube, classes, lives |
| `16:9-4k` | 3840×2160 | ×2 of 16:9 | ×2 | optional 4K master (≈4× render cost) |
| `1:1` | 1080×1080 | 54, 54, 972, 972 | 860-1020 (48 px) | square feed, LinkedIn |
| `4:5` | 1080×1350 | 54, 68, 972, 1214 | 1110-1280 (52 px) | portrait feed |

Every profile defines the same four **layouts** (rectangles for the screen, the camera and the captions),
adapted to its shape:

| Layout | 16:9 | 9:16 / 1:1 / 4:5 |
|---|---|---|
| `pip` | screen full-bleed, camera window bottom-right above the captions | screen band on top, camera window overlapping its lower-right corner |
| `screen` | screen only; add `"zoom": [x, y, w, h]` (fractions of the screen) to focus on a region | same |
| `speaker` | camera large (1440×810), screen hidden | camera fills the upper part (cover crop on the face) |
| `side` | screen 1216×684 left + camera 560×315 right | stacked: screen on top, camera below |

`formats.check_layouts()` guarantees boxes inside the canvas, captions inside the safe area and no camera over
the captions (`test_formats.py`). The Reel commands read the profile too: `heditor preview` sizes the viewport
from the composition, `heditor finalize` uses the profile's safe top row and sheet aspect, `prepare_cut` accepts
`crop="fit:1:1"` and records `format` in `edl.json`, `rk.page(fmt=...)` changes the canvas. A cut without a
format is 9:16, so existing projects behave exactly as before.

## Workflow

Commands assume `. ~/.heditor/env.sh`. `<work>` is one folder per long edit.

1. **Probe.** `heditor probe <video> 60 600 1800` and look at the frames: camera only, screen share + webcam
   tile (meeting recordings), slides? Measure the crops in source pixels: the shared screen (e.g.
   `crop=1440:810:0:135`) and the speaker (e.g. `crop=420:236:1478:408`, above any name label).
2. **Scaffold.** `heditor new --long <work> <video> --format 16:9 --style <slug|creative> --kind aula|live|youtube
   [--range start,end]`. Edit `<work>/long.json`: `layout_source.screen` / `layout_source.camera` (null camera =
   full frame; no screen = camera-only source), `intro`, `cta`, `exclude`, `asr.prompt`, `loudness`.
3. **Transcribe.** `heditor long transcribe <work>`: ASR in chunks of `asr.chunk_s` (default 300 s) whose
   boundaries sit in silences, one JSON per chunk in `qa/asr/`; re-running skips finished chunks (resume after
   a crash or a timeout); progress, real-time factor and ETA go to `qa/asr/progress.log`. Output:
   `transcript.json` (source times). `small` is the default model (≈1× real time on 3 busy CPU threads);
   use `--model medium` for difficult audio.
4. **Propose the EDL.** `heditor long edl <work>` writes `edl-proposal.json` and the readable
   `qa/edl-proposal.md`. Cut kinds:
   - `pause`: silences (10 ms energy below noise floor + 12 dB) longer than `max_pause` (0.55 s) shortened to
     `keep_pause` (0.30 s; `sentence_pause` 0.42 s after a sentence end). Energy decides, never the ASR timing,
     so a word cannot be cut; ASR timings that spill into a silence are ignored, and only a word with no voiced
     audio outside the cut (a soft word below the threshold or a hallucination) leaves the cut with `apply: false`.
   - `repeat`: an n-gram (1-4 words) immediately repeated ("a gente a gente") → the first copy goes. Emphatic
     doubles ("muito muito") without hesitation are kept.
   - `false_start`: an abandoned fragment followed by a pause and a restart with the same first words (applied
     when ≥ 2 words match or the ASR marks the fragment as cut off; a single repeated content word, as in
     "aplicativos, mobile, aplicativos para celular", is an elaboration and is kept).
   - `filler`: isolated "ãh/hum/uh/eh…" with a pause on one side (per language: "um" is an English filler,
     never a Portuguese one).
   - `edge`: the silence at the range edges and around manual exclusions is trimmed to 0.12 s before the next
     word and 0.18 s after the last one.
   Word-level cuts start and end at the quietest 10 ms window of the word gaps; gaps shorter than 35 ms
   (coarticulated speech) are proposed with `apply: false` and low confidence. **Review before applying**: flip
   `apply`, and add whole passages to remove (chat questions with names, private data, off-topic, technical
   breaks) to `long.json` `exclude` as `[start, end]` source seconds placed in word gaps. Re-running `edl`
   never overwrites a reviewed proposal (it writes `edl-proposal.new.json`; `--force` to replace).
5. **Apply.** `heditor long apply <work>`: one ffmpeg pass selects the kept frames (source frame grid) and
   writes `composition/assets/screen.mp4` (screen crop, native size) and `camera.mp4` (camera crop, 1280 px,
   Lanczos + light sharpening); one streaming pass writes `voice-raw.wav` with 4 ms fades at every junction.
   Picture and voice come from the same frame-aligned ranges, so they stay in sync; frame counts are checked.
   Writes `edl.json` (Reel-compatible `chunks`) and `words.json` remapped to the edited timeline (no second
   ASR). `words-reviewed.json` is regenerated and keeps earlier spelling fixes (matched by source time).
   Then `heditor gaps <work> 0.6` and fix spelling/names in `words-reviewed.json` (never timings). After a new
   transcript or a review-only change, `heditor long apply <work> --words-only` remaps the words without cutting
   the media again.
6. **Chapters.** `heditor long chapters <work> --suggest` proposes boundaries at sentence starts after the
   longest pauses, spaced by the kind (aula 4-10 min, live 6-15 min, youtube 1.5-4 min), with an excerpt of
   each. Write `chapters.json` (`[{"start": s, "title": "..."}]`, edited-voice seconds). Titles summarise what
   is said. `heditor long chapters <work>` validates YouTube's rules (first at 0:00, ≥ 3 chapters, ≥ 10 s each)
   and writes `chapters.txt` for the description (offset by the intro card).
7. **Layouts.** `heditor long layouts <work>` measures screen activity and suggests switches
   (`layouts.suggested.json`: pip by default, side/speaker on long static stretches, at sentence starts). Write
   `layouts.json` (`[{"start": s, "layout": "pip|screen|speaker|side", "zoom": [x, y, w, h]?}]`).
8. **Design.** Fill `<work>/DESIGN.md` (template): kind, format, style pack, layout plan, chapters, set pieces,
   retention cadence, captions, intro/CTA, music.
9. **Build and produce.** Fill `LOWER_THIRDS`, `SET_PIECES`, `CALLOUTS` in `<work>/build.py`, then
   `heditor long produce <work> [music:<id>]`: composition (`composition/index.html`, the whole timeline for
   previews), `plan.json`, render segments (`segments/seg-NNN/`), and the voice-first mix (`master.wav`,
   two-pass loudnorm to `loudness.lufs`, default −14 LUFS). It prints the balance and a render estimate.
10. **QA before render.** `heditor long lint <work>` (HyperFrames lint of the whole page and of every segment,
    0 errors; the duplicated-logo warning of intro + end card is harmless). Then
    `heditor long preview <work> <times>` (contact sheet in `qa/`) and inspect it with vision; `heditor test
    <work>` (the Reel integrity tests in long-form mode); `heditor long sync <work>` (camera, screen and voice
    against the source).
11. **Render.** `heditor long render <work> 2` (see Segmented render).
12. **Finalize.** `heditor long finalize <work> <name>.mp4`: concatenation, one continuous master audio, SRT/VTT,
    `<name>-chapters.txt` and the QA report (`qa/long-report.md`). Review `qa/long-sheet-*.jpg` and
    `qa/seams.jpg` with vision.
13. **Other formats.** `heditor long preview <work> <times> sheet-4x5.jpg --format 4:5` builds the same edit in
    another profile under `<work>/variants/4x5/` (previews only). For a full render in another profile, copy the
    work folder, set `format` in `long.json` and produce/render it.

## Style packs (`heditor long styles`, `scripts/reelkit/stylepacks.py`)

A Reel style is a scene grammar for 60 s; a pack is what keeps its identity on every frame of a long video:

| Token | Contents |
|---|---|
| `palette` | bg, bg2, surface, text, muted, accent, accent2, alert, ok (CSS variables in the composition) |
| `fonts` | display, body, mono, caption (kit fonts; `font_note` names the OFL family for full fidelity) |
| `captions` | weight, case, colour, active word fg/bg (≥ 4.5:1, tested), box, stroke, underline, prefix (`# ` in ide) |
| `frame` | world background, screen/camera radius, camera shape (rect, circle), border, shadow |
| `overlay` | grain, vignette, scanlines, letterbox (documentario: only in speaker layout, intro and cards) |
| `transition` | kind (slide, fade, wipe, flash, glitch, iris, cut, chalk, page), duration, ease |
| `chapter_card` / `lower_third` | card kind (slate, serif, board, terminal, hud, broadcast, record, editorial, neon, app) / strip kind (bar, plate, terminal, chalk, hud, record, tag) |
| `camera_grade` | ffmpeg filter for `camera-<slug>.mp4` (rebuilt when stale, checked by `sync`) |
| `sfx` | chapter, callout, lower third, set piece, transition, CTA tap/done categories |
| `music` | catalog ids and mood from the Reel style; `bed: true` adds a filtered bed under the voice |

Resolution: `BASE` ← family (`organic`, `didactic`, `authority`, `ad`, `layers`, `creator`) ← style ←
`long.json` `style_overrides`. **Creative mode** uses `"style": "creative"` with `style_overrides` (palette,
fonts, card kind, transition) designed for that video, plus custom set pieces.

### Vertical → horizontal adaptation rules

1. **The world moves to the frame.** In 9:16 the world is the whole screen; in 16:9 the screen share needs
   ~70-100 % of the canvas, so the world becomes the background around the boxes (side/speaker layouts), the
   cards, the intro and the close.
2. **Camera roles survive, sizes change.** Card/bubble/monitor → the camera window of `pip`/`side`; "camera fills
   the screen" → `speaker` layout. Never upscale a meeting tile beyond ~3× (1440 px wide is the limit for a
   ~420 px tile).
3. **Captions go down and wider.** Two lines of ≤ 42 characters at 50 px in 16:9 (≤ 30 in 1:1/4:5). World-native
   captions keep their look (dialog box, code comment, chalk line, serif subtitle) but read as subtitles, not
   kinetic words; giant karaoke and one-word captions only inside set pieces.
4. **Scene grammar → set pieces.** The style's signature moves are reserved for the hook, central concepts,
   turns and chapter closes (cadence below). Everything else is layout changes and small devices.
5. **Ad CTAs do not carry over.** Long videos close with Follow (`cta.kind: follow`, the Reel standard) or
   YouTube Subscribe → Subscribed + "Watch next" slots for the end screen (`cta.kind: youtube`, 10 s).
6. **Square/portrait feeds** stack screen above camera (`side` = stack) and keep captions inside the lower
   safe band.

### Every named style in long form

| Style | Family | Captions (font, active word) | Card / lower third / transition | 16:9 adaptation |
|---|---|---|---|---|
| `aeroporto` | organic | IBM Plex Mono, `#000000` on `#ffb000` | terminal / terminal / wipe | Chapters as flights on a split-flap board; radio captions in the bottom band; take-off clearance set piece on each approval/deploy. |
| `chat` | organic | Inter, `#111111` on `#ffe066` | app / tag / slide | Light theme around the screen share; one bubble per sentence; pinned-message chapter cards; bot replies as set pieces. |
| `cinema` | organic | Anton, `#f5c66b` text | slate / bar / slide | Gold-bordered camera card survives as PiP/side; one world change per chapter (card in a shifted palette); object-with-action set pieces only on the hook, central concepts and turns. |
| `documentario` | organic | Fraunces, `#f6efe1` text, underlined | serif / plate / fade | Made for long form: letterbox in speaker layout, intro and cards; serif chapter cards; serif subtitles with an underlined active word; archive grain; rolling credits as the close. |
| `documentario-narrado` | organic | Inter, `#0b0906` on `#f2cf60` | serif / plate / flash | Long-form history documentaries: the night globe bridges the chapters (camera flight, lights and routes on the words), dated cards after a music-only silence → impact → amber flash, film-graded testimony plate on key lines, medallion over the map, voice-over over generated paintings in parallax; next-chapter loop at the close. |
| `game` | organic | VT323, `#0b0b23` on `#ffd84d` | hud / hud / wipe | Chapters are STAGES, concepts unlock skills/items, CONTINUE? closing card; dialog-box captions as a bottom box; pixel camera only inside set pieces. |
| `ide` | organic | JetBrains Mono, `#ffffff` on `#264f78` | terminal / terminal / cut | Best fit for programming classes: the real screen share is the editor, circular webcam bubble, code-comment captions, chapters as file tabs; set pieces: terminal run, diff, test going green. |
| `impacto` | organic | Geist, `#edc580` text | slate / plate / slide | Board of argument cards becomes a side-layout column; coordinated bursts (type + sound + punch-in) on 2-3 lines per chapter. |
| `missao` | organic | Inter, `#ffffff` on `#9c1f6e` | neon / tag / wipe | Chapters as missions with a GPS route between them; character-intro freeze-frame for the lower third; MISSION COMPLETE before the CTA. |
| `podcast` | organic | Anton, `#ffe14d` text | broadcast / bar / wipe | Lives and long conversations: ON AIR sign with the chapter, segment colour per chapter, voice-reactive waveform in the side column; giant karaoke only in set pieces. |
| `ruptura` | organic | Anton, `#000000` on `#ffd84d` | slate / bar / flash | Cold open with the strongest line of the whole recording; camera-as-metaphor moves (clones, split, freeze) become set pieces at the turns; typographic finale before the CTA. |
| `trailer` | organic | Geist, `#03090e` on `#ffffff` | serif / plate / flash | Chapters open as black cards with a wide-tracked sans spelled letter by letter after ~1 s of near-silence and a hit; the speaker full frame in the cool-steel grade with letterbox; words on the wall behind the speaker at key moments; keep the big beats (silence, black, climax) for 3–5 moments. |
| `thriller` | organic | Inter, `#ff3d57` text | terminal / terminal / glitch | REC/timecode on the camera window; blackout + reboot as the set piece of the failure-to-recovery turn; liquid distortion only in short set pieces. |
| `tribunal` | organic | IBM Plex Mono, `#000000` on `#ffd84d` | record / record / page | Chapters as exhibits; the speaker as expert witness in side layout; the verdict is the set piece of the conclusion. |
| `gravidade` | organic | Anton, `#000000` on `#ffd84d` | slate / plate / flash | Physics set pieces (physkit, baked) at the key beats: problems fall into a heap on their words, the turn lands as a heavy block, the answer stacks as a straight tower; clean pip/side layout in between (render cost ~1 s/frame inside the room). |
| `circuito` | didactic | JetBrains Mono, `#03100b` on `#7dffb0` | terminal / terminal / wipe | The screen share becomes the main chip; chapter cards are new boards; concept maps are components drawn on their words (DrawSVG), copper traces on the verbs, pulses (MotionPath) for data that travels, LEDs and flags for the verdict per part. |
| `planta-de-acesso` | didactic | Geist, `#000000` on `#ffd84d` | terminal / tag / page | Permissions, roles and multi-department systems: each chapter is a new sheet of the plan with a PRELIMINARY STUDY stamp; rooms with doors drawn on their words, role badges that open or lock them, a legend box as the chapter recap. |
| `lousa-de-aula` | didactic | Caveat, `#1d2f27` on `#f4dc72` | board / chalk / chalk | Natural for classes: slate world framing the screen (oak border), syllabus chapters whose ? turns into a check, concept maps drawn on trigger words, a SUMMARY checklist per chapter. |
| `nativo` | native | Inter, `#000000` on `#ffd84d` | editorial / tag / cut | Cuts and animated captions only: EDL removes pauses, false starts and repetitions; camera or screen full frame with hard cuts between layouts; no set pieces, callouts, lower thirds, SFX or music unless asked; chapters only in the description. |
| `aduana-de-dados` | authority | Bebas Neue, `#ffffff` on `#a50e24` | record / record / fade | Chapters as declarations; X-ray set piece on what leaves the machine. |
| `arquivo-cofre` | authority | IBM Plex Mono, `#ffffff` on `#2343d6` | record / record / fade | Chapters as archive records; microfilm-rewind set piece for 'go back to the good version'. |
| `cassino-de-precisao` | authority | Bebas Neue, `#000000` on `#ffd970` | record / record / fade | Noir frame with a brass accent; the flip to the precision bench is the set piece of the turn. |
| `laudo-de-sinistro` | authority | Bebas Neue, `#000000` on `#ffd84d` | record / record / fade | Chapters as report sections; TOTAL LOSS to RECOVERABLE stamp as the closing set piece. |
| `mesa-de-risco` | authority | IBM Plex Mono, `#ffffff` on `#c4122f` | record / record / fade | Resource ticker as the chapter bar; circuit-breaker set piece at the crash, green strategy at the close. |
| `turno-da-madrugada` | authority | Bebas Neue, `#000000` on `#ffcf4a` | record / record / fade | Long processes and lives: a shift clock advances with the video; chapters as log entries. |
| `album` | ad | Anton, `#000000` on `#ffd84d` | app / tag / slide | Tool lists become stickers collected across the video; the full page in the recap. |
| `auditorio` | ad | Anton, `#000000` on `#ffd84d` | broadcast / tag / slide | Q&A and lives: each audience question is a round (chapter); green-light answer set piece. |
| `bilheteria` | ad | Anton, `#ffffff` on `#9c1c12` | app / tag / slide | Numbered tickets as chapter cards; golden-ticket set piece only if the speech has an offer. |
| `carrinho` | ad | Anton, `#000000` on `#ffd84d` | app / tag / slide | Items falling into a cart as the chapter recap (checklist set piece). |
| `entrega` | ad | Anton, `#000000` on `#d8f44a` | app / tag / slide | Tracking timeline as the chapter bar; each chapter a delivery stage. |
| `keynote` | ad | Geist, `#000000` on `#ffd84d` | slate / plate / slide | Stage world only in intro, cards and close; the screen share becomes the LED screen in side layout. |
| `manual-de-montagem` | ad | Anton, `#000000` on `#ffd84d` | terminal / tag / slide | Step-by-step classes: each chapter is an assembly step with numbered parts; blueprint grid frames the screen. |
| `porta-de-aco` | ad | Anton, `#000000` on `#bff9ff` | neon / tag / slide | Shutter as the chapter transition; neon signs for chapter titles. |
| `lapidacao` | ad | Geist, `#000000` on `#f3d79b` | slate / plate / flash | Chapters as objects under a spotlight on black velvet: raw material as a rough stone, the explanation as the cut, the result as the named gem; a loupe over screen recordings; case/tag/rope only for the offer chapter. |
| `predio-24h` | ad | Fredoka, `#000000` on `#ffd84d` | app / tag / slide | Each chapter lights a floor; day-to-night across the video in the frame background. |
| `stories` | ad | Geist, `#000000` on `#d7ff3a` | app / tag / slide | Story progress bar as the chapter bar; stickers as callouts; body in a clean pip. |
| `camadas` | layers | Geist, `#ff7a59` text | editorial / tag / fade | Layered moments (text behind the speaker) only in speaker-layout set pieces with a good matte. |
| `raio-x` | layers | Geist, `#c9a8ff` text | terminal / terminal / fade | Pipeline HUD as the chapter bar; depth scan / point cloud only in speaker set pieces. |
| `bancada` | creator | Geist, `#ffffff` text | editorial / tag / cut | Demos: whip pan from face to screen at each proof; callout set pieces (zoom + label) on the screen share. |
| `duelo` | creator | Geist, `#000000` on `#ffd84d` | editorial / tag / cut | A/B comparison chapters in side layout; vote CTA. |
| `manchete` | creator | Geist, `#ffffff` text | broadcast / tag / cut | Reactions: subject on the screen share, speaker beside/below; headline banner per chapter. |
| `reacao` | layers | Geist, `#ffd84d` active word | app / tag / slide | Reviews and reactions: the subject full-bleed with the speaker cut out in front at the bottom corner; callouts drawn on the subject; each chapter swipes to its source with a credit chip. |
| `revista` | creator | Geist, `#c6ff3d` text | editorial / tag / cut | Structured classes: each chapter a spread (keyword + italic serif), icon chips, full-frame breathers. |

Notes on the most used packs:
- **cinema**: keep the gold card border and Anton; the "world change per beat" becomes a palette shift per
  chapter (`style_overrides` per variant, or a custom chapter card); one object-with-action set piece per key
  beat, never more than one per minute in a class.
- **ruptura**: needs a real cold-open line; put a `title` set piece over it at 0:00 (or before the intro card)
  and a typographic finale on the last sentence before the CTA.
- **impacto**: side layout with argument cards (custom set piece) in the free column; bursts = `title` set
  piece + punch-in callout on the key line.
- **documentario**: the most natural long form; use `music_bed` sparingly (filtered piano under reflective
  stretches), letterbox only in speaker layout and cards so screen content is never hidden.
- **documentario-narrado**: chapters are dated cards; keep the globe and the paintings in `custom` set pieces at
  the chapter openings and the turns, the body in speaker/side layout with the film-graded plate; one hard
  music silence per card, not per sentence; recipe in `styles/documentario-narrado.md`.
- **lousa-de-aula**: the slate frames the screen share; concept maps are drawn on the trigger words (±0.15 s,
  recipe in `troubleshooting.md`); a `checklist` SUMMARY closes each chapter.
- **circuito**: reuse the Reel board engine (`templates/styles/circuito/build.py`, `board()`) inside a `custom`
  set piece per chapter; the chip frames the screen share; keep the plugins list (`SplitText`, `DrawSVG`,
  `MorphSVG`, `MotionPath`) in the segment pages.
- **gravidade**: one physics room per chapter at most, baked per segment (`physkit.bake` with the segment's
  duration); the rest of the chapter in pip/side layout.
- **ide**: circular camera, code-comment captions; chapters open like files; callouts zoom into the code.
- **podcast**: speaker layout most of the time for lives; segment colours per chapter; ON AIR card as intro.
- **game**: VT323 captions at 1.5× scale need short lines; STAGE cards; CONTINUE? as the closing card.

## Creative mode in long form

Same research and concept process as `creative-mode.md`, applied to the *frame, cards and set pieces*. Set
pieces available in `build.py` (`SET_PIECES`, out times):

| Kind | What it does | Use for |
|---|---|---|
| `title` | the words spoken in [start, end] appear one by one as giant type over a dimmed frame (`emphasis` words in the accent) | the hook, the thesis, a turn |
| `concept_map` | nodes (`label`, `t`, `x`, `y` in the safe area) pop on their trigger words, arrows (`from`, `to`, `t`, `label`) are drawn; an arrow never finishes before its target node appears | central concepts, timelines, architectures |
| `checklist` | a list whose items light up on their words | chapter recap / SUMMARY |
| `callout` | the layout switches to `screen` zoomed into `region` with a frame and a label, then returns | showing a detail on the screen share |
| `custom` | your own `html`/`css`/`js` (GSAP on the global timeline `tl`, absolute seconds) | anything the world needs |

Every set piece gets the pack's `sfx.set_piece`; layouts/captions keep running underneath. Truth rules hold:
on-screen words come from the speech (titles and labels summarise only what is said).

### Cadence (retention without fatigue)

| Kind | Retention device (keyword chip, punch-in, layout switch) | Creative set pieces | Chapters |
|---|---|---|---|
| `aula` (class) | every 75-120 s | hook + one per central concept, ≥ 6 min apart, + a chapter recap | 4-10 min |
| `live` | every 90-150 s | hook + the 2-3 strongest moments of the live | 6-15 min |
| `youtube` | every 25-45 s | hook + every ~2.5 min + the payoff | 1.5-4 min |

`CALLOUTS = None` builds the automatic plan (`longform.retention_plan`): a keyword chip on the longest content
word inside each cadence window, every second one with a 3.5 % punch-in, never within 1 s of a set piece or a
chapter card. Stop words for chips go to `long.json` `callout_stopwords`. Heavy continuous graphics (particles,
SVG filters, 3D) are allowed only inside set pieces.

## Captions, subtitles, lower thirds, intro and CTA

- Burned captions (`captions.burn`, default on): phrase groups of ≤ 2 lines that break on sentence ends, pauses
  > 0.6 s and ≤ 5.5 s; active word in the pack's colours; size fitted with the real font (PIL) to the caption
  zone. `plan["captions"]` equals what is shown (tested).
- SRT/VTT: `heditor long subs <work> [name]` (also written by finalize): ≤ 42 characters × 2 lines, ≤ 7 s,
  shifted by the intro card. Upload them to YouTube even when captions are burned (search, translation).
- Lower thirds: `LOWER_THIRDS = [{"start", "duration", "title", "role"}]` at the profile's lower-third box.
  Real public information only.
- Intro card: `long.json` `intro` (`title`, `subtitle`, `kicker`, `duration`): a full-frame card before the voice
  (the voice and all timings shift by `voice_offset`). Leave `title` empty for no intro.
- CTA (`cta.kind`): `follow` (logo, handle, Follow → Following tap; the Reel standard, ≥ 5 s) or `youtube`
  (handle, Subscribe → Subscribed with a bell, two "Watch next" slots where YouTube's end-screen elements go,
  10 s by default; YouTube end screens need 5-20 s). Words come from `brand.json` (`subscribe`, `subscribed`,
  `watch_next`; defaults per `lang`).

## Segmented render

`heditor long produce` plans segments (`longform.plan_segments`): chapter starts and the CTA are preferred
boundaries; longer pieces are split evenly into ≤ `render.segment_max_s` (default 60 s); boundaries move out of
set pieces and chapter cards and snap to whole frames, so segment frames add up exactly to the timeline. Each
segment is a self-contained HyperFrames composition (`segments/seg-NNN/index.html` + its own frame-accurate cut
of `screen.mp4`/`camera.mp4`, shared fonts hard-linked) whose timeline plays the **global** GSAP timeline from
its start (`tl.tweenFromTo(start, end)`), so a frame is identical whether rendered in the segment or in the
whole page.

`heditor long render <work> [workers]` (≤ 2 workers on a shared 4-CPU machine):
- skips segments whose page hash and frame count match the previous run (`render/progress.json`), so an
  interrupted render resumes; changing one chapter re-renders only its segments;
- logs every segment with seconds per frame and an updated ETA in `render/render.log`;
- `heditor long estimate <work>` prints the estimate from the measured history (default 0.42 s/frame with
  2 workers until something was measured).

`heditor long finalize` concatenates the segments with the concat demuxer (`-c copy`; all segments are encoded
with the same HyperFrames settings), checks the frame count, then muxes **one continuous `master.wav`** (AAC
256 kbps) over the whole video: there is never an audio seam between segments. The master is guarded for true
peak after AAC.

### Measured cost

Reference run (shared 4-CPU / 7 GB VPS with another production running, 2 render workers): a 4 min 24 s
16:9 edit (7913 frames, 7 segments, documentario pack, 5 set pieces) rendered in 31-33 min of render time,
about **0.24-0.25 s per frame ≈ 7-7.5 min per minute of video** (the CTA-only segment: 0.12-0.15 s/frame); an
unchanged re-render is skipped in about a second. ASR with `small` ran at
0.6-1.1× real time on 3 threads; `apply` cut 4.7 min of source in 2 min; `produce` took 40-75 s (6 min on the
first run: graded camera and segment media). Plan ~8 h of render per hour of 1080p video on such a machine, or
render overnight in segments; `heditor long estimate` uses your own measurements.

## QA (`heditor long qa <work>`, run by finalize)

| Gate | Pass |
|---|---|
| duration | final = plan duration (± 1 frame + 50 ms), canvas = profile, 30 fps, one AAC stream |
| decode | full decode without errors |
| loudness | integrated within ±1 LU of `loudness.lufs` (default −14), true peak ≤ `loudness.true_peak` (−1 dBTP) |
| audio | final audio vs `master.wav`, correlation ≥ 0.98 on sampled windows |
| sync | camera, screen and voice vs the source through the EDL: picture offset ≤ 1 frame, voice lag ≤ 10 ms on ≥ 80 % of the samples (static screens are reported as ambiguous) |
| asr | sampled 20 s windows (3-12) of the final audio vs the reviewed words: mean ≥ 0.85, min ≥ 0.6 |
| chapters | YouTube rules + each chapter starts on a word |
| seams | segment frame counts, total frames, no black frame, duplicated frame or sudden dark frame right after any boundary (`qa/seams.jpg`: 3 frames each side) |
| sheets | `qa/long-sheet-NN.jpg` (24 frames each, ≤ 1400 px wide) reviewed with vision |

Plus, before render: `heditor test <work>` (captions = words, ordered, CTA words, numbers only from speech,
balance, no dead air > 0.6 s, voice files match the timeline) and the previews.

## Pitfalls

- **Meeting tiles are small.** A 420×236 webcam tile is soft at 1440 px wide; prefer `pip`/`side` and use
  `speaker` briefly or with a grade that hides the softness.
- **Static screen shares** look frozen for minutes: use the retention cadence and `screen` zooms on the region
  being discussed; never fake activity with continuous graphics.
- **Names on screen.** Meeting recordings show participant names and chat; crop the screen above them, blur or
  cut those passages (`exclude`).
- **Profanity.** Mask it in captions with `long.json` `censor` (`{"word": "w*rd"}`); the audio stays.
- **Re-applying the EDL** regenerates `words-reviewed.json` (fixes are carried by source time) and the assets;
  run `produce` again before rendering; old segment renders are invalidated by their hash.
- **Letterbox** hides screen content: packs with `letterbox` only show it in speaker layout, intro and cards.
- **4K** multiplies render time by ~4; render 1080p first and only master 4K when the edit is approved.
- **End of the voice.** Screen/camera clips end with the voice; the end card fades in over the last 0.45 s of
  speech so their empty boxes are never seen (an empty box reads as a black flash at the CTA).
- **Low-memory machines**: HyperFrames switches to its low-memory profile (one worker) at ≤ 8 GB RAM; segments
  keep each render short so a failure costs one segment, not the video.
