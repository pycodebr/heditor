---
name: heditor
description: 'Use when the user wants to edit a talking-head, class, live or podcast video into a vertical Reel/Short/TikTok (1080x1920), or a long-form video (vídeo longo, aula, live, video for YouTube, minutes to hours) in 16:9, 1:1, 4:5 or 9:16 with pauses removed, chapters, captions/SRT, lower thirds, intro/end cards and a segmented render — with motion graphics, captions, sound design and music — in a named style (cinema, ruptura, impacto, gravidade (the speech has weight: labelled blocks land on their words with baked rigid-body physics, a heavy turn scatters the heap, the answer stacks as a tower), game, thriller, trailer (suspense/launch trailer: dramatic pauses inserted in the speech, silence before hits, words on the wall behind the speaker, letter-by-letter titles, layered score), ide, aeroporto, chat, documentario, documentario-narrado, podcast, missao, tribunal; paid-ad formats keynote, stories, predio-24h, bilheteria, porta-de-aco, lapidacao (luxury jewellery commercial: the raw idea is a rough stone, refining it is the cut, the result is the gem, the offer a case that slams shut), manual-de-montagem, carrinho, entrega, auditorio, album; authority formats cassino-de-precisao, mesa-de-risco, turno-da-madrugada, arquivo-cofre, aduana-de-dados, laudo-de-sinistro; didactic formats lousa-de-aula and circuito (the explanation as a circuit board: components drawn on their words with DrawSVG, copper traces, data pulses with MotionPath, morphing icons, LEDs and flags) and planta-de-acesso (who may use what as an architect floor plan drawn live behind the speaker: rooms with doors, role badges that open or lock them on their words, a sheet turn for the proposal); native format nativo (clean edit: cuts + animated captions only); creator formats camadas, raio-x, duelo, bancada, manchete, reacao (the speaker cut out in front of the post/news he reacts to: the subject full-bleed behind him, pushed in, scrolled and marked on his words), revista), in "creative mode" (maximum originality, built for that specific video) or "creative mode + reference" (e.g. "in the style of GTA 6"). Also free stock B-roll from Mixkit, with no account or key (`heditor stock search|get`, licence checked, provenance recorded), and hook tests on videos that already perform (new openings spliced onto the delivered file with the body untouched: `heditor splice`) and triage of raw takes (reading pauses, retakes, false starts, stumbles, self-corrections, recording failures and the speaker breaking the fourth wall to talk to the editor: `heditor triage`). Covers setup of all tools, cut selection from transcripts, HyperFrames compositions, layered 2.5D/3D effects (text behind the speaker, captions on the set, 3D objects, depth scans, hand-anchored objects), GSAP plugins offline (SplitText, DrawSVG, MorphSVG, MotionPath), SVG clean-up with SVGO, baked rigid-body physics with bloom, voice-first mixing, render and QA. Optional: AI avatar source videos (the digital twin of the user speaking an approved script) from a connected HeyGen account, by OAuth with subscription credits or by API key (`heditor heygen connect|status`, `heditor avatar`).'
license: MIT
metadata:
  author: PycodeBR (Felipe Azambuja)
  version: 2.16.0
  homepage: https://github.com/pycodebr/heditor
---

# heditor — creative video editing (Reels and long form)

heditor turns a recording of someone speaking into a short vertical video that holds attention second by second: a strong opening, a visual world built for what is being said, captions synced word by word, sound effects tied to every action, music with an emotional arc and a call to action. Compositions are HTML + GSAP rendered to MP4 by [HyperFrames](https://github.com/heygen-com/hyperframes). Everything runs locally.

The standard is high: **every video gets an edit designed for it.** A style is a proven visual language, never a template to stamp. If two videos in the same batch look like the same mould, the work is not done.

## 0. Setup (once per machine)

```bash
bash <skill_dir>/scripts/setup.sh          # installs ffmpeg/node/python deps if missing, venv, Chrome, fonts, music, SFX, models
. ~/.heditor/env.sh && heditor doctor       # must end with "heditor is ready."
```

- Re-running setup is safe. `--no-audio` skips the Mixkit library; `--whisper small,medium` pre-downloads ASR models.
- Edit `~/.heditor/brand.json` (name, `@handle`, colours, logo path, Follow/Following words, language). Ask the user for these the first time; never invent a handle.
- If a tool cannot be installed automatically (no sudo/package manager), tell the user the exact command to run and stop.
- All commands below assume `. ~/.heditor/env.sh` was sourced. The CLI is `heditor` (also at `<skill_dir>/scripts/heditor`).

## 1. Choose the mode

| User says | Mode | Read |
|---|---|---|
| "edit in style X", "igual ao estilo X" | Fixed style | `references/styles/<slug>.md` |
| "nativo", "edição simples/limpa", "só corta e legenda" | Style `nativo` (the one exception to "different every time": the edit stays invisible) | `references/styles/nativo.md` |
| "creative mode", "modo criativo", "surprise me" | Creative mode | `references/creative-mode.md` |
| "creative mode with/using X" (GTA 6, Wes Anderson, anime, news broadcast…) | Creative mode + reference | `references/creative-mode.md` (§ Reference direction) |
| Nothing specified | Ask once which mode; if the user wants you to decide, use creative mode | |
| "vídeo longo", "aula", "live", "YouTube", "16:9", "editar a aula inteira", chapters, SRT | Long-form mode (any style or creative) | `references/long-form.md` |
| "plano de gravação", "analise os roteiros", "pré-produção", plan before recording | Pre-production: recording plan, teleprompter and edit plan; nothing is edited yet | `references/pre-production.md` |
| "novas aberturas", "teste de gancho", "troca só o começo", new hooks for an ad that already converts | Hook variants: render only the opening and splice it onto the delivered file, body identical (`heditor splice`) | `references/hook-variants.md` |
| "vídeo com meu avatar/clone", "HeyGen", "gêmeo digital", no camera recording, only a script | Optional AI avatar: the source comes from the user's HeyGen twin (`heditor heygen status`, `heditor avatar`), then any mode | `references/heygen-avatar.md` |
| Raw recording read from a teleprompter or a batch of scripted takes ("pausas para ler", "falei com o editor", "quebrei a quarta parede", retakes, erros de gravação) | Triage first (`heditor triage`): asides to the editor are notes to follow, never content; then any mode | `references/raw-takes.md` |

Named styles (`heditor styles`): see `references/styles/INDEX.md` for when each fits.

| Style | Identity |
|---|---|
| `cinema` | One visual metaphor per speech beat, world changes on each turn, live camera card, kinetic captions |
| `ruptura` | Cold open with the strongest line, the camera itself becomes the metaphor, typographic finale |
| `impacto` | Organised layout with coordinated emphasis bursts (type, sound, zoom) on the key lines |
| `gravidade` | The speech has weight: every key noun is a labelled block that lands on its word (baked Rapier physics, `physkit.land_on`); problems pile up, the turn lands as a heavy block that throws the heap, the answer stacks as a straight tower. Reference build: `heditor new <work> <video> --style gravidade` + `beats.json` |
| `game` | The screen is a retro RPG: HUD, dialog-box captions, skills unlocked, inventory, CONTINUE? CTA |
| `thriller` | Security-camera disaster tape: REC overlay, heartbeat, liquid distortion, blackout, system reboot |
| `trailer` | Suspense/launch trailer: hard cuts between the speaker (cool-steel grade, letterbox) and black, dramatic pauses inserted in the speech with silence before every hit, words on the wall behind the speaker (matte), titles spelled by light, a real object of the set as the date device, layered score with a smash to silence before the climax, poster end card. Beats measured on real trailers |
| `ide` | Code-editor screencast: circular webcam bubble, captions typed as code comments, terminal CTA |
| `aeroporto` | Control tower: radar, split-flap departures board, flight strips, radio-transmission captions |
| `chat` | Light messaging app: the speaker's sentences arrive as messages, the bot replies, video-call PiP |
| `documentario` | Mini-documentary: letterbox, film grain, serif chapter cards, documentary subtitles, rolling credits |
| `documentario-narrado` | Large-scale narrated documentary (alias atlas): the speaker narrates history on a living night globe (lights and routes on the words), generated period paintings in 2.5D parallax, dated cards with hard silence → impact → reveal, narrator as film-treated plate / gold medallion / voice-over, "next chapter" loop |
| `podcast` | Talk show / podcast: saturated set, ON AIR sign, voice-reactive waveform, giant karaoke captions |
| `missao` | Open-world game homage: sunset neon world, in-world social clip, character intro freeze-frame, mission card, GPS route, stats screen, mission-complete banner, phone-chat CTA |
| `tribunal` | Courtroom sketch: the speaker as expert witness on the court monitor, typed testimony captions, exhibits and stamps, a verdict, the jury is the viewer |
| `keynote` | Ad · launch stage: presenter cutout in front of a giant LED screen, slides and stage objects per sentence, deadline close-up, "Learn more" slide |
| `stories` | Ad · behind the scenes as a sequence of stories: progress bars, tap and cube swipe, hand-made stickers, "Learn more" link sticker |
| `predio-24h` | Ad · isometric company model with a day/night cycle: floors light per department, server cutaway, 24 h orbit, second tower for the offer |
| `bilheteria` | Ad · retro box office: numbered tickets, the clerk's arched window, a ticket ruler that gains golden extras, golden ticket, turnstile that lets the viewer in |
| `porta-de-aco` | Ad · shop front at night: steel shutter descending at each turn, neon signs, "you take" window, closed shutter as the CTA |
| `lapidacao` | Ad · luxury jewellery commercial: the tool is closed and the room goes dark, the raw material drops as a rough stone, the cut (laser, facets, flash) reveals the gem with its parts named, a loupe reviews the machine's work, a tray locks the unsaid steps, the offer case slams shut on the warning, sealed date tag, velvet rope CTA, louder score. Reference build: `heditor new <work> <video> --style lapidacao` + `beats.json` |
| `manual-de-montagem` | Ad · assembly manual on a blueprint: numbered parts that snap in, same parts in every project, assembly at the turn, kit box |
| `carrinho` | Ad · forgotten cart in a shopping app: push notification, items fall into the cart, bonuses as gifts, checkout CTA |
| `entrega` | Ad · order tracking: the timeline jumps to "delivered now", a box opens and items fly into the checklist |
| `auditorio` | Ad · TV quiz show: each question is a round, A/B answers light green, scoreboard, velvet doors open for the CTA |
| `album` | Ad · sticker album: every named item becomes a sticker on its word, collection tray, "missing one" CTA slot |
| `cassino-de-precisao` | Authority · noir casino that flips into a precision bench at the turn; the expert as the croupier; engraved rule |
| `mesa-de-risco` | Authority · trading desk on a crash day: the resource is an asset, replay, false-safety seal, circuit breaker, green strategy |
| `turno-da-madrugada` | Authority · night-shift control room: main monitor, annunciator windows, process line, time-lapse to dawn, shift handover CTA |
| `arquivo-cofre` | Authority · archive reading table at night: the expert as a record in a passe-partout, steel drawer, time-stamp clock, microfilm reel that rewinds to the good day, RESTORED stamp |
| `aduana-de-dados` | Authority · night border checkpoint between your computer and the internet: exit declaration, X-ray monitor, barrier, regulations underlined, READ THE TERMS stamp |
| `laudo-de-sinistro` | Authority · forensic claim report: the expert in the technical photograph, forensic flash, coverage clause filled as said, pen marks TOTAL LOSS → RECOVERABLE |
| `circuito` | Didactic · circuit board: the speaker is the main chip, components drawn on their words (DrawSVG outline + icon, decoded silkscreen), copper traces on the verbs, data pulses (MotionPath), icon morphs (MorphSVG), LEDs and flags, silkscreen titles (SplitText), push-button CTA. Reference build: `--style circuito` + `beats.json` |
| `planta-de-acesso` | Didactic · access floor plan: the company or system as a blue architect's sheet drawn live behind the cutout speaker, every module a room with a door, role badges that open or lock the doors on their words, forbidden data masked behind a padlock, a sheet turn for the proposal (dashed "to be built"), the whole company lit at the close, badge-reader CTA |
| `lousa-de-aula` | Didactic · interactive chalkboard lesson: every stroke drawn live on its word, syllabus whose "?" turns into ✓, arrows labelled with the spoken verb, eraser, SUMMARY chain, homework CTA |
| `nativo` | Native · clean edit: only cuts at clean word boundaries, jump cuts that alternate the framing, and animated word-by-word captions; no music, SFX, graphics or end card. Reference build: `heditor new <work> <video> --style nativo`, `heditor produce <work> none 0` |
| `camadas` | Layers · every concept drawn between the speaker and the wall: giant words and "?" behind the head, guide lines on the set, glass slab, floating cards, comment-to-DM CTA |
| `raio-x` | Layers · the machine's view: live pipeline HUD, depth scan, exploded layers, point cloud, face/hand tracking, transcript becoming the prompt, timeline assembly |
| `duelo` | Creator · A/B comparison page: the same take in two synchronised panels edited two ways, VS badge, checklist verdict, vote CTA |
| `bancada` | Creator · proof on the workbench: label sticker hook, whip pan to a filmed/simulated monitor, finger and punch-ins on the screen, result inserts |
| `manchete` | Creator · headline inset on top: subject clip/post above, banner across the seam, the speaker reacting below, full-bleed peak, band splits |
| `reacao` | Layers · the speaker in front of the post: raw talking head cut out at the bottom, the news/post/page/screen recording full-bleed behind him, pushed in, scrolled and panned on his words, boxes, highlighter, underline and circles on the exact word, lime highlighter headline, title cards, credit chip, profile CTA. Backdrops: screenshot, `heditor capture <url>`, `heditor region` (the post inside the raw recording) or a clip. Reference build: `heditor new <work> <video> --style reacao` + `beats.json` |
| `revista` | Creator · editorial spreads: condensed keyword + italic serif line, rounded portrait window, icon chips per item, date pages, full-frame breathers |

### Long-form mode (classes, lives, YouTube; any format)

For minutes to hours of video in 16:9 (also 16:9 4K, 1:1, 4:5, 9:16), follow `references/long-form.md`:
`heditor new --long <work> <video> --format 16:9 --style <slug|creative> --kind aula|live|youtube` →
`heditor long transcribe` (chunked, resumable ASR) → `long edl` (proposed cuts of dead pauses, false starts,
repetitions and fillers, reviewed before applying) → `long apply` → `long chapters` → `long layouts` (screen +
camera layouts: pip, screen with zoom, speaker, side) → `long produce` (style pack, set pieces, captions, lower
thirds, intro/CTA, mix) → `long preview` → `heditor test` → `long render` (segmented, resumable) → `long finalize`
(one continuous master audio, SRT/VTT, YouTube chapters, QA report). Every named style is available as a *style
pack* (`heditor long styles`); creative mode lives in set pieces at key moments. Format profiles: `heditor formats`.

### Layered effects (any mode)

Text and objects *behind* the speaker, captions painted on a wall, 3D objects passing between the speaker and the room, depth fog, contour scans, point clouds and objects that follow the hands come from depthkit: `heditor matte|depth|look|hands|plane <work>` (models download on first use). Read `references/depth-and-3d.md` before using them in any style or in creative mode; layouts, illustrations, hooks and CTAs borrowed from creator Reels are in `references/technique-catalogue.md`.

### Motion tools (any mode)

- **GSAP plugins offline:** SplitText, DrawSVG, MorphSVG, MotionPath, CustomEase/Bounce/Wiggle, Text, Physics2D/Props and EasePack ship with setup; load them with `rk.page(..., plugins=("SplitText", "DrawSVG"))`. Read `references/gsap-craft.md` first: some GSAP features call `Math.random` (ScrambleText, `stagger from: "random"`, `gsap.utils.random`) and break the render; the kit has seeded replacements (`rnd()`, `scramble()`).
- **SVG preparation:** `heditor svg <in.svg> [out.svg] [static|draw|morph]` cleans exported SVGs with SVGO for the animation they will get and proves, pixel by pixel in the render Chrome, that they still look the same.
- **Real physics:** `heditor physics` / `physkit` bakes a Rapier rigid-body simulation (falling piles, impacts, blasts) into per-frame transforms that a three.js layer with bloom and depth of field reads at any time. Recipe, framing and look values in `references/physics-3d.md`; working pilot in `templates/physics/pilot_build.py`.
- **Styles built on these tools:** `gravidade` (physics: blocks land on their words, `physkit.land_on`) and `circuito` (DrawSVG, MorphSVG, MotionPath, SplitText on a circuit board). Both ship a reference build: `heditor new <work> <video> --style gravidade|circuito`, write `<work>/beats.json` from the speech (format in the style file and at the top of the build), then `heditor produce`. In creative mode, borrow their engines (`board()`, `physics()`) for a single set piece.

### Stock video / B-roll (any mode)

`heditor stock search "<english words>" [--orientation portrait]` lists free Mixkit clips (no account, no API key) and `heditor stock get <work> '#N'` downloads one into `<work>/composition/assets/stock/`, after confirming the Mixkit Stock Video Free License on the clip page, and records its provenance in `<work>/stock.json` (paste the printed line into DESIGN.md). Use B-roll only where it illustrates a word of the speech, muted, 1.5–3 s per idea, without recognisable faces next to claims in ads, logos or brands; one clip per `get`, never bulk downloads (Mixkit's terms forbid scraping the library). Read `references/stock-media.md`.

### AI avatar source (optional, HeyGen)

When there is no recording, only a script, the source can be the user's own HeyGen digital twin. Read
`references/heygen-avatar.md` first. In short:

- `heditor heygen status` (exit 0 connected, 3 not connected). Not connected: the **user** runs `heditor heygen
  connect` in their own terminal (HeyGen account by OAuth with subscription credits, or API key with the API wallet;
  on servers the assistant prints a link and asks for the return address). Never run it for them and never ask for a
  key in chat.
- `heditor heygen avatars|voices` → `heditor avatar <work> --look ID --script roteiro.txt --dry-run` shows the cost
  estimate (credits or USD). Show it to the user; only after approval run it again with `--yes`. The file lands in
  `<work>/source/` with provenance in `<work>/avatar.json` (`synthetic: true`), then the normal workflow from
  `heditor new <work> <file>`.
- The person's own cloned voice, always: set it once in `~/.heditor/brand.json` (`"heygen": {"voice_id": "..."}`);
  `heditor avatar` refuses a look default that is not one of the account's cloned voices (HeyGen can return a stock
  voice for photo looks). Generate with `script` + that `voice_id` (the engine saved on the voice), never with
  uploaded audio synthesized elsewhere; per-sentence gestures: § One motion prompt per sentence in the reference.
- Prepare the speech before spending: the approved `roteiro.txt` (caption spelling) and a spoken
  `roteiro-fala.txt` with numbers as said, abbreviations expanded, a few `<break time="0.4s"/>` pauses and connected
  sentences; recurring foreign terms, acronyms and names go into a HeyGen pronunciation glossary
  (`heditor heygen glossaries`, `--glossary ID`), respelled the way the person really says them. After generating,
  compare the transcript with the approved script word by word and regenerate any mispronounced line
  (`references/heygen-avatar.md` § Writing the script for the voice).
- Editing a studio avatar video (one scene per sentence): pass the scene seams to the prepare
  (`prepare_cut(..., seams=[...])`) so every pause cut lands on a pose reset instead of a few frames from it, check
  each splice of joined renders for clicks and each scene start for a head dip, and never blank the speaker to hide
  a jump (`references/heygen-avatar.md` § Editing an avatar video).
- The user approves every script; no claims, numbers or promises they did not approve; disclose AI use where a
  platform or law requires it.

## 2. Workflow (all modes)

Follow `references/workflow.md` step by step. Summary:

1. **Probe the source.** `heditor probe <video> 5 60 300` and look at the frames: where is the speaker (full frame, webcam tile in a meeting, screen share)? Note resolution, the speaker crop, what else is on screen.
2. **Transcribe and choose the cut.** `heditor transcribe <video> 0 <duration> qa/asr-full.json` (or a window). Pick a self-contained argument of 30–70 s: hook → thesis → explanation → conclusion. Long-form stories (e.g. a narrated documentary of ~90 s, style `documentario-narrado`) are allowed when requested: declare `max_duration` in the plan (≤ 180 s) so `heditor test` accepts them, and keep a retention device every few seconds. The hook must exist in the speech. Never invent, reorder words inside a sentence, speed up or splice half-sentences into a new claim. Remove repetitions, false starts and tangents only at clean word boundaries. Scripted or teleprompter takes go through `heditor triage <video...>` first: chunks between silences transcribed alone and labelled keep / retake / false_start / editor / noise, so reading pauses, repeated sentences and asides to the editor never reach the cut. An aside is a note from the speaker to you (`cut`, `redo`, `marker`, `note`): follow it and report what you did (`references/raw-takes.md`).
3. **Scaffold and prepare.** `heditor new <work> <video>`, fill `BLOCKS`/`CROP` in `<work>/prepare.py`, `heditor prepare <work>`, `heditor gaps <work>` (no pause > 0.45 s), then `heditor words <work>` and fix spelling/brand names in `words-reviewed.json` (timings untouched; profanity can be masked on screen only).
4. **Design first.** Fill `<work>/DESIGN.md`: video analysis, mode/style, frame map, palette, captions, beat sheet with timestamps, music, CTA, risks. In creative mode, research before designing.
5. **Build.** Rewrite `<work>/build.py` (the template is only a runnable baseline) to implement DESIGN.md. Use the kit (`references/kit-api.md`) or write your own HTML when the format needs it.
6. **Produce.** Pick the mix profile (`voice` or `presence`), profile the track with `heditor music <music:ID|file>` and place its turns on the speech turns; `heditor produce <work> music:<id> <drop_s>` → composition + mix; read the `balance` it prints (targets, `music_gaps`).
7. **QA before render.** `heditor lint <work>` (0 errors) → `heditor preview <work> <18–24 times>` → inspect the contact sheet with vision and fix every defect → `heditor test <work>`. Gates in `references/quality-gates.md`.
8. **Render and finalize.** `heditor render <work>` → `heditor finalize <work> <name>.mp4` → review `qa/final-contact-sheet.jpg` and `qa/final-verification.json` → `heditor asr-check <work>`.
9. **Deliver** the MP4 path with a short summary (format, music, what was verified, what nobody has checked: nobody has *listened* to it — say so). Never publish to social networks unless the user explicitly asks.
10. **Learn.** If you created a new style that the user liked, add it as a named style (`references/adding-styles.md`).

## 3. Non-negotiables

- **No dead air.** Inspect pauses inside blocks and across every junction, using the assembled clean voice, not the music mix. Run `heditor gaps` after prepare and check the surrounding words. The default 0.45 s threshold flags candidates for revision; it does not authorize clipping consonants, removing every breath or flattening deliberate rhetorical pauses. Preserve speech at 1× and shorten unwanted dead air with small safety margins. Document any intentional longer pause and verify the exception explicitly before rendering. For a pause-only revision of an approved edit, preserve its visual language and previous version, remap captions, media and SFX to the new timeline, then verify the exported MP4.
- **Voice first, music present.** Mix profile by delivery (`plan["mix"]`): `voice` (default; organic Reels, class excerpts) music ≈ 21.5 dB under the voice (median), background ≥ 12 dB under at p95; `presence` (paid ads, creative mode, trailer) music ≈ 15 dB under, background p95 ≥ 7 dB under, filtered sections with make-up gain and `heditor asr-check` required. In both the bed may not vanish inside the speech (`test_music_presence`). Impacts in the gaps, ducking held across the whole phrase. -14 LUFS, true peak ≤ -1.5 dBTP after AAC.
- **Readable captions.** Every spoken word, synced; active word with high contrast (black on light yellow, white on saturated dark — never dark-on-mid or dark outline on dark text). Check enlarged crops.
- **Safe zones.** (9:16; every format profile has its own safe area, see `long-form.md`.) Nothing important above y = 270 (top 14%; titles with accents start ≥ 300), keep the bottom ~350 px and the right edge (~120 px, y 1000–1700) free of critical info, never cover the face.
- **Truth.** Numbers, names and claims exactly as spoken; no invented stats, testimonials, promises or private data; no third-party logos or copyrighted assets (homage through type, colour, motion, sound).
- **Licences.** Fonts OFL (google/fonts), icons Lucide, music/SFX from the catalog (Mixkit Free License), stock video through `heditor stock` (Mixkit Stock Video Free License, `stock.json`) or user-provided licensed files. Record provenance in DESIGN.md.
- **Different every time.** In a batch, give each video its own format (layout, camera treatment, captions, palette, transitions, music, CTA). Ask vision to compare contact sheets: "do these look like the same template?" If yes, change more.
- **Verify before claiming.** A video is done only after lint, previews, tests, render, finalize gates and contact-sheet review pass. Report what failed honestly.
- **The fourth wall stays closed.** Nothing the speaker says to the editor or the crew ("cut that", "again", "corta aí, editor", "vamos editar essa parte") appears in the cut, in picture, sound or captions. Each aside is a note to you: follow it (discard, use the retake, apply the edit) and report what you did; run `heditor triage` on raw scripted takes before choosing anything.
- **Paid-ad hooks.** Frame 0 shows something concrete and readable plus a title of up to 6 words; the first spoken word is the object, the pain or the question; keep voice ≥ 90 % and ≥ 38 words in the first 15 s (`first_15s` in `qa/final-verification.json`) and put dramatic pauses, blacks and slow cards after that. A hook test changes only the opening: the body keeps the frames and audio of the running version (encoded once more, never re-edited) (`references/hook-variants.md`).

## 4. References

- `references/workflow.md` — the full procedure with commands, cut selection and EDL rules.
- `references/raw-takes.md` — raw takes: asides to the editor (the fourth wall) and their intents, choosing takes, stutters and self-corrections, recording failures (clipping, knocks, duplicated frames, the set moving, mirrored or HDR sources) and what goes in the delivery.
- `references/hook-variants.md` — new openings for a video that already performs: body identical, routes A (splice onto the delivered file with `heditor splice`), B (project copy) and C (rebuild and reproduce), continuous music, loudness and seal at the splice, what to report.
- `references/pre-production.md` — before recording: measure the scripts, inventory the set, reuse existing screen recordings, fact-check cited studies, recording plan (setups, gestures on words, screens, inserts), teleprompter generated from the source and a per-video style map for a batch.
- `references/long-form.md` — long-form mode: format profiles, layouts, EDL proposal, chapters, style packs for all styles, creative set pieces and cadence, segmented render, QA.
- `references/creative-mode.md` — creative mode, reference-directed creative mode, research method, idea bank.
- `references/kit-api.md` — reelkit functions, page skeleton, GSAP helpers, plan/sound/music formats.
- `references/depth-and-3d.md` — depthkit: speaker matte, depth map, scans, planes, tracking, three.js, layered recipes and QA.
- `references/gsap-craft.md` — GSAP plugins available offline, seek-safety rules (determinism hazards inside GSAP), SplitText/DrawSVG/MorphSVG in a render, SVG preparation with `heditor svg`.
- `references/physics-3d.md` — physkit: baked Rapier physics, scene format, three.js page with bloom/depth of field, look values and framing that passed QA.
- `references/technique-catalogue.md` — creator layouts (A/B page, morphs, insets, bands), illustrations, camera moves, caption systems, hooks and CTAs.
- `references/heygen-avatar.md` — optional AI avatar source from the user's HeyGen account: `heditor heygen connect` (OAuth with subscription credits, `--remote` for servers, or API key), status, looks and voices, `heditor avatar` (estimate, approval, idempotent request, download, `avatar.json`), writing the script for the voice (pronunciation glossary, spoken script, pauses, natural flow, word-by-word check), editing synthetic footage, consent and disclosure.
- `references/stock-media.md` — free Mixkit B-roll: search in English, orientation, quality, licence check, `stock.json` provenance, using clips in the page, what to avoid, Mixkit terms (no mass download) and why Pexels/Pixabay/Unsplash/Adobe Stock/Videezy are not built in.
- `references/sound-design.md` — voice chain, mix targets, SFX vocabulary, music catalog and section design.
- `references/captions-and-layout.md` — caption systems, contrast rules, safe zones, camera treatments.
- `references/quality-gates.md` — every gate, how to read false positives, final checklist.
- `references/adding-styles.md` — how to turn a successful edit into a new named style.
- `references/troubleshooting.md` — known failures and fixes.
- `references/licenses.md` — third-party components and asset licences.
- `references/styles/` — one file per named style.

## 5. Changing heditor itself

Every change pushed to `main` ships as a version, never as a loose commit:

1. Bump `metadata.version` in this file (semver: patch for fixes and docs, minor for styles, commands and features, major for breaking changes).
2. Add a `## X.Y.Z — YYYY-MM-DD` section at the top of `CHANGELOG.md`.
3. Commit as `heditor X.Y.Z: <summary>`, push to `main` and wait for CI to pass on that commit.
4. Create the annotated tag and the GitHub release with that CHANGELOG section as notes:
   `git tag -a vX.Y.Z -m "heditor X.Y.Z: <summary>" && git push origin vX.Y.Z`
   `gh release create vX.Y.Z --verify-tag --title "heditor X.Y.Z: <summary>" --notes-file <notes.md> --latest`
5. Read it back: `gh release view vX.Y.Z` shows the release as Latest and `git ls-remote --tags origin` lists the tag.

Full procedure in the repository's `CONTRIBUTING.md`.
