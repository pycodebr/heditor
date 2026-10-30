# Changelog

## 2.16.0 — 2026-10-30
- **New didactic style `planta-de-acesso`** (access floor plan): who may use what, drawn as an architect's blue sheet
  behind the cutout speaker. Every module or department is a room with a door drawn on its word, role badges open
  (route, door swing, green check) or lock (door slam, padlock, red hatch, masked values) the doors, a sheet turn
  carries the proposal in dashed "to be built" line work with a PRELIMINARY STUDY stamp, a legend box ticks the
  features said, the closing pulls back to the whole company with people walking only into their rooms, giant words
  behind the head on the hook and the payoff, captions over an architectural dimension line and a badge-reader CTA.
  Style file, INDEX, SKILL.md, README (43 styles), creative-mode idea bank, long-form row and style pack
  (`STYLES["planta-de-acesso"]`, family didactic).
- `references/troubleshooting.md`: voice 30–70 ms off the picture in some blocks of a re-exported preview MP4 (seeked
  AAC decode vs full decode; prepare from a `-c:v copy -c:a pcm_s16le` mezzanine), `camera_sync_check` false OUT OF SYNC
  on crops of the same source, an `<img>` beside the `<video>` in a circle-clipped container leaking in the render, and
  icons read at import time before `ensure_icons`.

## 2.15.1 — 2026-10-27
- `references/gsap-craft.md` § Sequential seeks vs a single seek: the render seeks frame after frame (forward), so a
  tween still running when a later `set` on the same property fires wins in the MP4 while `heditor preview` shows the
  `set` (corner brackets that stayed on screen until the end card). Overlapping tweens on the same property are
  forbidden, the end of one is computed from the keys of the next, `FT` with `immediateRender: false` needs an explicit
  initial `set`, and transitions are checked on frames of the MP4.
- `references/quality-gates.md` § Leftover elements: check them on frames of the rendered MP4 too, and end the exits of
  outgoing cards before a scene cut so they never land on the cut-out speaker's new position.

## 2.15.0 — 2026-10-27
- **Pause cuts on scene seams.** `prepare_cut(..., seams=[...])` takes the source times of the first frame of each new
  scene (pose resets of a HeyGen studio video, splices of joined takes) and moves every pause trim that contains a seam
  so the cut lands exactly on it, removing the same number of frames (the timeline does not change). A seam in a kept
  edge of a pause used to give two jumps a few frames apart; the first avatar Reel hid the speaker between them and it
  read as a vanish. The trim records `seam` and `cut_source` in `edl.json`. Trim frame bounds are now computed with a
  small epsilon, so a pause edge that falls exactly on a frame is no longer shifted by one frame by float error.
- **Matte without background haze.** `depthkit.person_matte(..., floor=0.09)` clears the faint alpha a segmenter
  leaves over the whole background (4-6 % on a synthetic plate: the office shelf showed through as a ghost over a
  graphic wall) and stretches the soft edge back to 0..1 (`alpha_floor`); `qa/matte-stats.json` reports
  `background_haze` measured before the floor. `floor=0` keeps the previous behaviour.
- `references/heygen-avatar.md` § Editing an avatar video: scene seams and the prepare, clicks at splices of joined
  renders (mute the burst before the prepare), head dip at the start of a regenerated scene, matte haze.
  `references/gsap-craft.md`: `svgOrigin` for rotating SVG elements (gauges, dials). `references/troubleshooting.md`:
  lint `gsap_animates_clip_element`, a speaker vanishing at a seam, ghost behind a cut-out. `SKILL.md` points to them.
- `test_prepare_cut.py` (in CI): trim window moved onto the seam with the same width, a synthetic two-scene source
  where the colour changes exactly on the cut, and the alpha floor.

## 2.14.3 — 2026-10-26
- `references/heygen-avatar.md`: corrected gaze guidance. Prompted side glances made an avatar talk turned away (8 s at
  30° of head yaw), which is as unnatural as a fixed stare; every scene now keeps eye contact with the camera with
  natural head motion, each scene is measured (eye-look blendshapes and head yaw) and only a scene that leaves the
  camera is regenerated; silent scene starts with a head dip and warped glasses are trimmed.

## 2.14.2 — 2026-10-26
- `references/heygen-avatar.md`: natural gaze for avatar scenes. A fixed stare is the clearest sign of an avatar
  (9 % of frames away from the central point against 36 % in a real recording); every motion prompt gets a varied gaze
  cue (eye contact plus short thinking glances), and `more_blinking` is flagged because it pulled the gaze down for
  most of a line.

## 2.14.1 — 2026-10-26
- `references/heygen-avatar.md`: the per-sentence recipe now generates with the person's voice selected (`script` +
  `voice_id` per studio scene, the engine saved on the voice, glossary at the top level) and explains why uploading
  audio synthesized elsewhere or forcing an engine is wrong for a person's own avatar: no voice selected in HeyGen,
  no glossary, possibly another engine that sounds unlike the trained voice, and engine-specific tags read aloud.
  Risky terms are tested first in a 10–15 s video on the cheapest engine with the same voice. `SKILL.md` follows.

## 2.14.0 — 2026-10-26
- **The person's official voice in every avatar video.** `heditor avatar` takes the voice from `--voice`, else from
  `~/.heditor/brand.json` `"heygen": {"voice_id": ...}` (or `HEDITOR_HEYGEN_VOICE`), else from the look's default
  only when that voice is one of the account's cloned voices; otherwise it stops and asks for `--voice`. HeyGen can
  return a stock voice as the default of a photo look, which would have put another voice in the person's mouth. The
  plan printed before a generation shows where the voice came from. `templates/brand.example.json` gains the key.
- Avatar V on photo looks now has an estimate: 48 credits/min, as in HeyGen's credit table (it printed "no public
  rate" before). A real 77 s generation cost 63 credits.
- `references/heygen-avatar.md`: "The person's official voice" and "Audio first and one motion prompt per sentence"
  (speech per block with delivery tags, ASR check, master audio sliced into 3–10 s scenes, one `studio` request with an
  Avatar V scene and a motion prompt per slice, gestures in the opening scenes, verification against the master,
  regenerating only the defective scene). `SKILL.md` and `README.md` point to them.
- `test_heygen.py`: refusal of a stock default voice, brand voice in the request, Avatar V photo-look estimate.

## 2.13.0 — 2026-10-26
- **Pronunciation and natural speech for HeyGen avatar scripts.**
  - `heditor avatar --glossary ID` passes a HeyGen brand glossary (`brand_glossary_id`): written terms are spoken
    with the respelling you registered, while HeyGen's captions keep the written spelling. Only for synthesized speech
    (`--script`/`--text`); with `--audio` it is refused, because an audio file is lip-synced as it is.
  - `heditor avatar --speed 0.5-1.5` sets `voice_settings.speed` (omitted at 1.0, the voice's natural pace).
  - `heditor heygen glossaries [--json]` lists the account's pronunciation glossaries with every term and respelling.
  - Pause tags are checked before anything is sent: `<break time="0.4s"/>` in seconds; millisecond values, which
    HeyGen rejects, stop the command. The duration estimate counts words without the tags, adds the pauses and
    divides by the speed.
  - The plan printed before a generation shows the glossary (or warns that terms will be read as written) and the
    speed; `avatar.json` records `glossary_id` and `speed`.
- `references/heygen-avatar.md` gains "Writing the script for the voice": approved script and spoken script, risky
  words to mark (foreign terms, acronyms, names, numbers, handles, symbols, homographs), the glossary as the source of
  truth (respelled the way the person speaks; `update` replaces the whole term list), what goes inline, punctuation
  and sentence length for continuous speech, pauses, speed, an audio-only test of risky terms and a word-by-word check
  of the generated video. `SKILL.md` and `README.md` point to it.
- `test_heygen.py`: glossary and speed in the request and in `avatar.json`, refusal with `--audio` and with invalid
  values, pause tags in seconds, duration with pauses and speed, glossary listing.

## 2.12.0 — 2026-10-26
- **Optional AI avatar source from HeyGen: `heditor heygen` and `heditor avatar`.** Nothing is installed or required
  by default; `setup.sh` is unchanged and `heditor doctor` reports HeyGen as an optional warning only.
  - `heditor heygen connect` is an interactive assistant (Portuguese or English, from `brand.json` `lang` or
    `HEDITOR_LANG`) run by the account owner. It installs the official HeyGen CLI when the user accepts (official
    installer, checksum verified) and offers two ways to connect: the HeyGen account by OAuth, billed to the premium
    credits of the subscription, or an API key, billed to the prepaid API wallet and typed into the HeyGen CLI's hidden
    prompt. On a desktop OAuth opens the browser; on a server or over SSH (`--remote`) the HeyGen CLI waits on a
    loopback port inside a pseudo-terminal, heditor prints the authorize link, the user approves on any computer and
    pastes the return address, which heditor validates (port, path, `state`) and delivers locally. `--device` keeps
    HeyGen's device-code login available for when HeyGen enables it (it answered `invalid_request` at release).
    Without a terminal the command refuses and prints the commands the user should run.
  - `heditor heygen status [--json]` shows the connection type, account, plan, premium credits or wallet balance and
    warns when `HEYGEN_API_KEY` overrides a stored OAuth login; `disconnect`, `avatars` (look ids, type,
    orientation, supported engines, default voice) and `voices` (cloned voices).
  - `heditor avatar <work> --look ID (--script FILE | --text "..." | --audio FILE)` checks the engine against the
    look (`v` by default when supported, `iv`, `iii`), estimates duration and cost in the unit of the connection
    (credits on OAuth, USD on the API wallet, published rates of October 2026), asks for confirmation (`--yes` only
    after approval; `--dry-run` spends nothing), uploads the audio, requests the video with an idempotency key,
    polls with backoff, downloads it with HeyGen's sidecar captions into `<work>/source/` and records provenance in
    `<work>/avatar.json` (look, engine, voice, input hash, billing, estimate, SHA-256, size, `synthetic: true`).
    `--resume VIDEO_ID` finishes a render that outlived `--timeout`.
  - heditor never reads, prints, stores or passes a HeyGen key on a command line; the credential stays with the
    HeyGen CLI (`~/.heygen/credentials`) or `HEYGEN_API_KEY`.
- New reference `references/heygen-avatar.md`: connecting, billing modes, the remote OAuth flow, rules for agents
  (never connect for the user, approval before `--yes`), editing synthetic footage, consent and disclosure.
- `SKILL.md`, `README.md` and `references/licenses.md` document the optional feature; CI runs `test_heygen.py` (fake
  HeyGen CLI: status in both billing modes, connect menu and remote OAuth callback, approval gate, request body,
  idempotency, download and provenance, resume after timeout; no network).

## 2.11.0 — 2026-10-24
- **Free stock B-roll from Mixkit: `heditor stock search` and `heditor stock get`.** No account, no API key, nothing
  to configure.
  - `heditor stock search "<english words>" [--orientation portrait|landscape|square] [--page N] [--limit N]
    [--json]` lists numbered clips with orientation (from the listing thumbnail) and page URL. Paginates on the
    canonical URL (discover pages that redirect to a tag page), caches listings for 24 h and explains empty results
    (Mixkit searches in English) or pages with no clip in the requested orientation.
  - `heditor stock get <work> <#N|mixkit:video:ID|clip page URL> [--quality 1080|4k|best|720] [--as name]` confirms
    the Mixkit Stock Video Free License on the clip page, downloads from the official CDN with size fallback into
    `<work>/composition/assets/stock/`, probes size and duration, records provenance in `<work>/stock.json` (licence,
    page, download URL, SHA-256, size) and prints the DESIGN.md line.
- New reference `references/stock-media.md`: commands, using clips in the page (unique `id`, muted,
  `data-media-start`), choosing B-roll that serves the speech, the Mixkit User Terms that bind the tool (one clip per
  `get`, never mass downloads or redistribution) and why Pexels, Pixabay, Unsplash, Adobe Stock and Videezy are not
  built in (per-user API keys, hotlinking/attribution rules, enterprise-only API, mandatory attribution).
- `SKILL.md`, `README.md` and `references/licenses.md` document the new source; CI runs `test_stock.py` (parsing,
  references, cache, orientation filter, provenance, licence refusal; no network).

## 2.10.1 — 2026-10-24
- **Fix: `npx skills add` and `npx skills update` find the skill again** ([#1](https://github.com/pycodebr/heditor/issues/1)).
  Since 2.1.0 the unquoted `description:` in the `SKILL.md` frontmatter contained `: ` (`nativo (clean edit: …)`,
  `trailer (suspense/launch trailer: …)`, `gravidade (…: …)`, `circuito (…: …)`), which YAML reads as a nested
  mapping, so strict parsers (`yaml` 2.x in `skills`, PyYAML) rejected the whole frontmatter and the skill was
  skipped. The value is now single-quoted; the parsed description is identical to the previous text.
- CI reads the frontmatter with PyYAML instead of a regex (name, description, `metadata.version` and its CHANGELOG
  section), so a new style in the description cannot break installation again.
- `CONTRIBUTING.md`: keep the description single-quoted when adding a style to it.
- Thanks to @GabrielCesar48 for the report, the root-cause analysis and the suggested fix.

## 2.10.0 — 2026-10-24
- **Recording errors and the fourth wall in `heditor triage`**, plus the new reference `references/raw-takes.md`.
  - **Asides to the editor as instructions.** When the speaker breaks the fourth wall ("corta aí, editor", "vamos de
    novo", "vamos editar essa parte, essa última frase", "cut that", "again"), each aside is listed with the chunk
    before and after, an intent and the action it asks for. Intents:
    - `cut`: discard the take before;
    - `redo`: use the next take of the same sentence;
    - `marker`: slate, attention or thanks;
    - `note`: an editing instruction in the speaker's words, to follow or report.

    New section "Asides to the editor (fourth wall)" in `<stem>.triage.md` and `instructions` in the JSON.
  - **Issues inside usable chunks**, with word times:
    - `stutter` and `repeat` ("com com", the same two words twice);
    - `aside_inside`: an aside in the middle of a sentence;
    - `self_correction`: "conectada por trás, não, conectada ao sistema", "quer dizer", "ou melhor", "I mean";
    - `unclear`: low ASR confidence;
    - `forbidden`: phrases the campaign forbids, passed with `--forbid "a,b"`.
  - **Recording failures** (`tech`, skip with `--no-tech`):
    - clipped samples;
    - loud sounds outside the speech (knocks, claps, notifications);
    - duplicated frames: about 50 % means the camera captured half the frame rate, which is not a render freeze;
    - jumps of the set between consecutive kept takes (camera moved, light changed, something entered). Only the top
      and the sides of the frame are measured, so the speaker's gestures do not count. On real takes the set
      differs by 0.7–4 between takes, against 15–21 when the camera moves 2–3 px.
  - `raw-takes.md` covers:
    - what to do with each intent, label and issue;
    - how to choose one whole take per sentence: eyes back on the lens, no hand on the chin in a hook;
    - which failures can be worked around and which need a re-record (clipping, mirrored and HDR sources, the set
      moving);
    - what goes in the delivery.

  SKILL.md gains the non-negotiable "the fourth wall stays closed": no aside reaches the cut in picture, sound or
  captions, and every aside is followed and reported.
- Unit tests for intents and instructions, issues and false-positive guards, and a synthetic recording with
  clipping, a knock and a light change.

## 2.9.0 — 2026-10-24
- **Hook tests on videos that already perform: `heditor splice`** (`scripts/reelkit/splice.py`) and the new reference
  `references/hook-variants.md`. A new opening is rendered as its own work and joined to the delivered MP4 from a cut
  frame, so the body that is running stays identical and the test measures only the hook.
  - `heditor splice find-cut <video> <a> <b>` finds the splice frame: first black frame after a lit one (per-frame
    luma), biggest picture jumps and the audio level at each.
  - `heditor splice <opening_work> <body.mp4> <out.mp4> --cut-frame K` uses `round(D·fps)` frames of the opening
    (HyperFrames renders one extra frame), decodes the body audio whole without `-ss` (`-ss 0` on AAC drops 1024
    samples and the body comes 21 ms early), cuts by sample with an equal-power crossfade ending on the cut, matches
    the opening loudness to the body's 3 s before the cut (±4 dB cap), limits only the opening (oversampled limiter
    with latency compensation), draws an optional full-canvas overlay (campaign seal) over the body with fades, and
    encodes once.
  - `<out>.splice.json` proves the result: frame count, body audio correlation ≥ 0.999 with lag 0 against the
    delivered file, opening audio lag 0, short-term loudness at the splice versus the original cut, frame differences
    on sampled body frames, true peak, decode errors, `ok`.
  - `hook-variants.md` (from a batch of nine openings on three running ads and a rebuilt fourth): the three routes
    (A splice onto the delivered file, B project copy for a splice inside a phrase, C rebuild and reproduce when the
    media are gone), ending the opening in the state of the body's frame 0, colour and music continuity, loudness at
    the splice, seals, frame 0 visibility, route B stems and matte reuse, route C reproduction criteria and task
    sizing for agent runs.
- **Triage of scripted raw takes: `heditor triage`** (`scripts/reelkit/triage.py`). It splits a recording at silence
  and transcribes each chunk alone (large-v3, no context, no prompt), because a whole-file ASR glues reading pauses
  into words and invents repetitions. Each chunk is labelled:
  - `keep`;
  - `retake`: superseded by a later take, or the take right before an aside;
  - `false_start`;
  - `editor`: asides to the editor or crew, with strong cues anywhere and weak cues at the start of a short chunk,
    in PT and EN;
  - `noise`: breaths and clicks, including stock Whisper hallucinations such as subtitle credits and impossible
    speaking rates.

  Writes `<stem>.triage.json` and `.md`. The workflow and pre-production references now start scripted recordings
  with it.
- **asr-check folds notation** (`scripts/reelkit/textnorm.py`): "pra"/"para (a)", "7h30"/"sete e meia", "5"/"cinco",
  "Fast API"/"FastAPI" no longer count as masking. Similarity and the gate use the folded words; the raw values
  are reported (`similarity_raw`, `delta_raw`), notation-only differences are listed as `NOTATION` apart from `MASKED`,
  and `HEDITOR_ASR_CHECK_STRICT=1` keeps the old raw gate. On a real trailer the raw master score was 0.951 against the
  clean voice's 0.988 (fail) with no masked word; folded, it is 0.982 against 0.994.
- **finalize keeps −14 LUFS when the AAC peaks:** the true-peak guard now limits only the peaks first (4× oversampled
  limiter with latency compensation, gain re-trimmed to −14 LUFS) and only falls back to a lower loudnorm TP; before,
  a single stacked impact made the whole file end at −15 LUFS. `tp_guard.method` records which ran; a stale
  `master-pre-tp.wav` from an older produce is replaced.
- **Hook metrics in `qa/final-verification.json`:** `first_15s` = voice share (10 ms RMS of the cut's voice, short gaps
  bridged) and words started in the first 15 s. Paid ads that hold keep ≥ 0.90 and ≥ 38 words; new advisory gate
  in `quality-gates.md`, a paid-ad hook rule in SKILL.md and a "keep the first 15 s talking" note in the `trailer`
  style, measured on running ads.
- `heditor preview` accepts the times as separate arguments too (`heditor preview <work> 0 0.5 2 sheet.jpg`); before,
  the second time was taken as the sheet name and the run failed with "unknown file extension".
- Troubleshooting:
  - whole-file ASR repetitions and noise hallucinations;
  - a card exit crossing the speaker's face;
  - `alimiter` latency, `-ss 0` AAC priming, HyperFrames' extra frame;
  - phone sources with half of the frames duplicated;
  - a white flash lifting the blacks of a dark world;
  - character-by-character code reveals that look like a staircase;
  - the old −15 LUFS finalize.
- Unit tests `test_triage.py` (chunking, labels, notation folding) and `test_splice.py` (synthetic clips: cut frame,
  frame count, untouched body audio, opening before the whole body) in CI.

## 2.8.0 — 2026-10-22
- **New named style `reacao` (the speaker in front of the post) with a runnable reference build**
  (`heditor new <work> <video> --style reacao` + `beats.json`, example in `templates/styles/reacao/`): from a raw take
  where the speaker only talks about a news item or a post, the speaker is cut out (matte) and placed at the bottom of
  the frame in front of the subject, which fills the frame behind him as a virtual green screen. The subject is a
  screenshot, a captured page, a screen recording or a region of the same recording, static or moving: each shot sets
  a focus that is pushed in, scrolled and panned on the spoken words (with a slow drift on holds); boxes, highlighter,
  underline and hand-drawn circles appear on the exact word with labels from the speech; a lime highlighter headline
  opens on frame 0, white title cards name the subject, a credit chip names the source, source switches swipe or
  flash, the speaker jumps between seven states (center, right, left, small, low, hero, punch) and the CTA freezes his
  last frame under a profile card with Follow → Following.
- `scripts/reelkit/reacaokit.py`: `speaker_cutout` (matte at 720 px merged with the camera at ≤ 1080 px, class 5
  kept so glasses stay opaque, each stage cached with its parameters; a 1440 px alpha crashed the render Chrome on a
  4-core/8 GB host), `region_clip` (another region of the source cut with the cut's EDL, frame for frame),
  `external_clip`, `image_backdrop`, `fill_layer` (blurred cover copy), `last_frame` (held under a video backdrop
  for the CTA), `capture` (Playwright page screenshot, mobile or desktop, full page, lazy images, cookie walls
  dismissed), `view` (focus → transform that covers the width and the top and reaches `min_bottom`, with `max_top`),
  `speaker_states` (the median face placed per state, body never above y 1600), `speaker_top`, `freeze_alpha`.
- The build writes `qa/marks.json` and warns about marks at the frame sides, above y 200 or behind the head.
- CLI: `heditor capture <url> <out.png>` and `heditor region <work> <name> <crop>`.
- Unit tests `test_reacao.py` (geometry, EDL-synced region) in CI; style file, style pack (long form), INDEX, SKILL,
  README (PT/EN), long-form row, troubleshooting (glasses in class 5, 24 fps default of the base prepare template,
  bands behind landscape recordings, caption word spacing under a heavy stroke, videos without id, render Chrome
  crash with a large alpha video).

## 2.7.0 — 2026-10-21
- **New named style `lapidacao` (luxury jewellery commercial) with a runnable reference build**
  (`heditor new <work> <video> --style lapidacao` + `beats.json`, example in `templates/styles/lapidacao/`): the tool
  everyone starts with is closed and the room goes dark on a declared pause; under a cool spotlight on a black void the
  raw material is typed live and sucked into a rough stone, refining it is the cut (laser, facets, sparks, flash), the
  result is the gem with its parts named; the machine comes in only then and a jeweller's loupe reviews its work; a
  display tray locks the unsaid steps, a certificate grades the result, the offer case opens and slams shut on the
  warning, a sealed tag carries the spoken date, a velvet rope opens on the "Learn more" button. Mixed with the `presence` profile
  (2.6.0) plus the style's own targets; default score `music:126` with its kick entry on the gem flash and Mixkit m179
  for the CTA (presence-band share ≥ 0.24; a bass-only bed failed the presence floor in the reference edit).
- `scripts/reelkit/lapidacao_kit.py`: neutral-cool grade, presenter matte at 720 px with clamped levels and a static
  garbage mask from the median face (merged with the full-resolution RGB), rig states from the face, soft-edged object
  photos (+ a dull "raw" stone), synthesised SFX and the Mixkit tracks/SFX downloaded once into
  `~/.heditor/assets/lapidacao` with provenance. Object photos are generated per cut (prompts in `OBJECT_PROMPTS`);
  none ship with heditor.
- Style file with pitfalls from production (matte background not zero, accessories class keeps the glasses, hard source
  edges, floor glow edges, raw stone that already looked cut, joining two takes of the same phrase, a bed too low),
  style pack (long form), INDEX, SKILL, README (PT/EN), long-form row, idea bank.

## 2.6.0 — 2026-10-21
- **Mix profiles** (`plan["mix"]`, `rk.MIX_PROFILES`, `rk.mix_targets`): `voice` (default; organic Reels, class
  excerpts: music ~21.5 dB under the voice) and `presence` (paid ads, creative mode, trailer: music ~15 dB under,
  background p95 −7 dB, ducks .62/.35/.6, SFX offset −4, +4 dB make-up on `muffled`/`lowpass` sections,
  `asr-check` required). `"presence"`, `{"profile": "presence", ...}` or `plan["mix_profile"]`; legacy dicts
  without `"profile"` keep overriding the voice profile. Born from a creative-mode ad whose bed (quiet intro,
  16 s muffled underwater, −21.5 dB) read as "no music" while every gate passed.
- **Presence floor:** `rk.mix` measures the bed's presence band (500 Hz–6 kHz, after ducking, `rk.presence_levels`)
  in 400 ms windows inside the speech, outside `silence` sections; runs under voice median + floor (−48 dB voice,
  −38 dB presence), merged across peeks < 1.2 s (`rk.music_gaps`), go to `balance.music_gaps`; new test
  `test_music_presence` fails a run longer than 8 s (voice) or 2 s (presence). `balance` also reports
  `mix_profile`, `music_presence_pct`, `long_filtered_sections` and `asr_check_required`. Thresholds calibrated on
  the real case (vanished bed −44 to −58 dB, present bed −28 to −36 dB).
- **asr-check:** word-timed comparison lists `MASKED` spans (words the clean voice had and the mix lost) with times,
  writes `pass`, exits 1 when master similarity < 0.90 or more than 0.03 below the voice. `finalize` prints the
  required next step for the presence profile. `test_voice_first_balance` reads the profile targets.
- **`heditor music <music:ID|file> [out.json]`** (`music_profile.py`): tempo, energy per second, kick/bass bar,
  breakdowns, kick entries and lifts, to place each section's `src` so the track's turns land on the speech turns.
- Docs: sound-design (profiles, floor, track profiling, masking check), quality-gates, kit-api, workflow, creative
  mode, paid-ad variant, trailer style, SKILL non-negotiables; template `build.py` exposes `MIX`.
- CI runs the new unit tests (`test_mix.py`).

## 2.5.3 — 2026-10-21
- setup.sh: requires Node.js 22 or newer (HyperFrames 0.8.x declares `engines.node >= 22`); before, a Node 18 or 20
  install passed the check and could fail later at preview or render. On apt it installs Node 22 from NodeSource.
- doctor: new required check `node >= 22 (HyperFrames)` with the current major version in the hint.
- README: installation section says Node.js ≥ 22.

## 2.5.2 — 2026-10-20
- SKILL.md: new section "Changing heditor itself" — every change pushed to `main` ships as a version with
  CHANGELOG section, passing CI, annotated tag and GitHub release, read back before it counts as published.

## 2.5.1 — 2026-10-20
- troubleshooting.md: a shot set at t = 0 that shows in the preview but is blank in the rendered MP4 (set the
  opening state outside the timeline, start timeline calls at 0.001, `decoding="sync" loading="eager"` on images);
  Python tuples written into page JS read as the comma operator (emit lists or `json.dumps`).
- CONTRIBUTING.md: release procedure (version in SKILL.md, CHANGELOG section, CI, annotated tag, GitHub release).
- Every version since 1.0.0 is now tagged and published as a GitHub release.

## 2.5.0 — 2026-10-20
- **Two new named styles built on the motion tools, each with a runnable reference build** driven by a
  `beats.json` written from the speech (`heditor new <work> <video> --style gravidade|circuito`):
  - `gravidade` (the speech has weight): labelled blocks land on their words with baked Rapier physics; problems
    pile up readable, the turn lands as a heavy block that throws the heap and releases its rotation, the answer
    stacks as a straight tower in the clearest lane of the floor (chosen from the bake, cleared by a shockwave);
    room viewport faded into the page, impact flash in the impact colour, silence before the impact.
  - `circuito` (the explanation is a circuit board): the speaker becomes the main chip; zones, components (outline
    and icon drawn with DrawSVG, silkscreen decoded), copper traces on the verbs, data pulses (MotionPath),
    icon morphs (MorphSVG), LEDs and flags, silkscreen titles (SplitText), push-button CTA.
  - Style files, style packs (long form), INDEX, SKILL, README (PT/EN) and long-form rows; idea bank updated.
- physkit: `land_on()` (bake, measure the first contact of each body, correct its spawn until it lands on its
  word; ≤ 1 frame in 3 passes), `landings()`, body locks `"lock": "rotation"|"vertical"` and `lockRotationAxes`
  (locked components of the initial velocities are zeroed), `blast(..., unlock=...)` to release locked rotations
  at the blast. Lessons in `physics-3d.md` (8 substeps for heavy impacts on locked bodies, weights pin heaps,
  lanes from the bake, labels only on camera faces, tone-mapped background seams).
- svgkit: `single_path()` merges a multi-shape icon (rect with rx, circle, ellipse, line, polyline, polygon) into one
  path for MorphSVG, rewriting each sub-path's leading relative moveto; pixel-identical on Lucide icons.
- reelkit: `rk.page(..., caption_pill=(text, pill))` and `captions_js(..., pill=...)` for the active-word colours
  in pill mode (defaults unchanged).
- gsap-craft.md: SplitText inside a flex container loses the spaces between words (split an inner span).
- Tests: single_path (structure and pixel check), pill colours, locks/unlock/land_on.

## 2.4.0 — 2026-10-20
- **GSAP plugins offline.** Setup downloads SplitText, DrawSVG, MorphSVG, MotionPath, CustomEase, CustomWiggle,
  CustomBounce, Text, Physics2D, PhysicsProps, ScrambleText and EasePack (free since GSAP 3.13); `rk.setup_assets`
  copies them and `rk.page(..., plugins=(...))` / `rk.gsap_plugin_tags()` load and register them.
- New reference `references/gsap-craft.md`: the official GSAP skills (greensock/gsap-skills) audited against the
  HyperFrames seek model. Documents the `Math.random` calls inside GSAP that break renders (ScrambleText,
  `stagger: {from: "random"}`, `gsap.utils.random/shuffle`, CustomWiggle `random`, RoughEase), SplitText in a render
  (split once, lines only after fonts, no autoSplit, masks), DrawSVG/MorphSVG practice, directional rotation,
  `svgOrigin`, grid staggers, CSS variables and what not to use in video (ScrollTrigger, Flip, quickTo, matchMedia).
- BASE_JS: deterministic `scramble(sel, text, t, dur)` (seeded, precomputed, seek-safe).
- **`heditor svg`** (`svgkit`): SVGO 4 clean-up in three modes (`static`, `draw` keeps shapes/separate paths for
  DrawSVG, `morph` converts shapes to paths) with a pixel comparison of original vs result in the render Chrome
  (`ok`, side-by-side check sheet); `svgkit.inline()` for build.py.
- **`heditor physics`** (`physkit`): Rapier rigid bodies baked at a fixed step into per-frame transforms
  (`assets/physics-<name>.js`), played back by `physics_player.js` at any HyperFrames time; helpers for floors,
  trays, seeded rain, mass-scaled radial blasts with exclusions; three.js post-processing addons (bloom, depth of
  field, output) and an importmap for offline 3D. New reference `references/physics-3d.md` with look values and
  framing rules from the pilot QA; working pilot `templates/physics/pilot_build.py`.
- Setup installs svgo and rapier in `~/.heditor/node`; doctor reports plugins, addons and node tools.
- Tests: `scripts/reelkit/test_motion.py` (plugin tags, SVGO modes and visual check, bake determinism, settling,
  spawn visibility and interpolation in the player).

## 2.3.0 — 2026-10-19
- **New style `trailer`** (movie trailer): hard cuts between the graded speaker and black, dramatic pauses inserted in
  the speech, words on the wall behind the speaker (inside the camera rig, under the speaker matte), letter-by-letter
  titles revealed by light, a real object of the set as the date device, "lights on" into the final act, a smash to
  silence before the climax and a score built in layers. Beats measured on real suspense and product-reveal trailers
  (card durations, silence before hits, hit spacing). `references/styles/trailer.md`, style pack and long-form row.
- `prepare_cut`: `("PAUSE", seconds, "key")` blocks insert digital silence + black frames; `edl["pauses"]` lists them.
- `gaps` / `test_no_dead_air`: declared pauses count only for the silence around them (`excess`); an uncut pause next to
  a beat still fails.
- `rk.mix`: `plan["duck_open"]` releases the voice ducking inside pauses (hits land at full level instead of being held
  ~650 ms); `plan["mix"]` overrides the bed targets when the user asks for a louder bed (`test_voice_first_balance`
  reads the same targets).
- `track_faces` / `_probe`-style ffprobe reads take the first two fields (some files print a trailing comma).
- `camera_sync_check`: pause chunks are skipped when sampling the source.

## 2.2.0 — 2026-10-19
- New reference `references/pre-production.md`: recording plan and edit plan from written scripts, before anything is recorded. Covers exporting a shared Google Doc, measuring the scripts by code (edited duration and the position of the first brand/campaign mention), inventorying the set from photos and previous contact sheets with vision, checking existing screen recordings before reusing them, fact-checking cited studies (including later "out of date" notices), recording rules that save editing (two setups, gestures tied to words, locked tripod for mattes and screen projection, narrated demos with a clap and a visible timer), a teleprompter generated and verified from the source, a speech-structure → style table for batches and a quote audit for the plan.
- `SKILL.md`: pre-production row in the mode table and in the references list.

## 2.1.2 — 2026-10-18
- `finalize` no longer muxes with `-shortest`: with `-c:v copy` it dropped the last video packets (2350 of 2354 frames on a 78 s cut) and the contact sheet then failed on a frame past the end. The mux is trimmed to the render's duration instead.

## 2.1.1 — 2026-10-18
- `track_faces` detects on a copy downscaled to at most 640 px wide (positions are fractions, so results are unchanged). Decoding 5 fps of full-HD RGB frames for a 78 s cut used ~2.4 GB and was killed by the OOM killer on a 8 GB VPS.
- Troubleshooting: 4K HEVC phone recordings (e.g. iPhone `.MOV`) can also exhaust memory in `heditor prepare`; make a 1080×1920 proxy and use it as `SOURCE`.
- Validated on a 78 s first-person phone recording in the `nativo` style (`full` mode, no face in frame).

## 2.1.0 — 2026-10-16
- **New style `nativo`** (family *native*): a clean native edit with only cuts at clean word boundaries, jump cuts that alternate the framing (1.0/1.075 on the face of each segment) and animated word-by-word captions (Inter 900, black on a light-yellow pill). No music, SFX, graphics or end card unless asked. Ships a reference build in `templates/styles/nativo/build.py` with two camera modes: `full` (vertical source, or a 9:16 crop around the median face from the full-resolution source, frame for frame) and `fit` (camera fitted to the width over a blurred copy of itself, for small or wide sources).
- `heditor new <work> <video> --style <slug>` seeds `build.py`/`DESIGN.md` from `templates/styles/<slug>/` when the style has a reference build.
- `heditor produce <work> none 0` builds without a music track (the mix stays voice only).
- `heditor test`: a Reel may end with the speech, without a CTA screen, when the plan declares `"end_card": false`.
- Long-form style pack `nativo`; style packs may set an SFX category to `None` to stay silent.
- `camera_sync_check` checks blurred background variants (`*blur*`) by frame count only, instead of reporting noise as a sync failure.
- Validated on a 35 s cut in `fit` mode (lint 0 errors, `heditor test` 10/10, render about 4 min, −14.1 LUFS, final camera within one frame of the source); `full` mode exercised on the same cut (frame-exact 9:16 crop).

## 2.0.0 — 2026-10-16
- Quality gate and troubleshooting row for short labels that stay on screen (overlapping fade-in/fade-out tweens), found in the narrated documentary production.

Long-form and multi-format editing, style packs for every named style, Reels up to 180 s and a new narrated-documentary style. Existing 9:16 projects build and render as before.

### Long-form mode
- **Long-form mode** (classes, lives, YouTube videos; minutes to hours) — `heditor new --long` and `heditor long transcribe | edl | apply | chapters | layouts | produce | preview | render | finalize | qa | subs | sync | estimate | styles`, documented in `references/long-form.md`:
  - chunked, resumable ASR with boundaries in silences and a progress/ETA log;
  - reviewable EDL proposal (`edl-proposal.json` + `qa/edl-proposal.md`): dead pauses shortened by energy (never by ASR timing), immediate repetitions, false starts and per-language fillers removed at the quietest point of word gaps, low-confidence cuts left for review, manual `exclude` ranges with their surrounding silence trimmed; `apply` assembles screen, camera and voice in single passes on the source frame grid (frame counts checked) and remaps the words without a second ASR (spelling fixes carried by source time; `--words-only`);
  - layouts for screen share + camera (`pip`, `screen` with zoom, `speaker`, `side`) switched per passage, with suggestions from screen activity; chapters (suggestion, YouTube rules, cards, current-chapter tag, description timestamps); burned captions fitted with the real fonts and SRT/VTT export; lower thirds; intro card; closing CTA `follow` (Follow → Following) or `youtube` (Subscribe → Subscribed + "Watch next" slots);
  - style packs (`stylepacks.py`) for all 36 named styles (palette, typography, captions with tested active-word contrast, frame, overlays, transition, chapter card, lower third, camera grade, SFX, music) with vertical → horizontal adaptation rules; creative set pieces (`title`, `concept_map`, `checklist`, `callout`, `custom`) and an automatic retention plan at the cadence of each kind (aula, live, youtube);
  - segmented, resumable render: one HyperFrames composition per segment (chapter-aware, ≤ 60 s, frame-exact) that plays the global timeline from its start, skipped when unchanged, render log with seconds per frame and ETA, optional per-segment heavy-job lock (`HEDITOR_LOCK`); concat without re-encoding and one continuous master audio muxed at the end;
  - memory-bounded voice-first mixer for long timelines (`longmix.py`, same balance targets, loudness from `long.json`);
  - long-form QA report (`longqa.py`): duration/canvas, decode, loudness (−14 LUFS default), audio/master correlation, camera/screen/voice sync against the source, sampled-window ASR, chapters, segment seams (black or duplicated frames), contact sheets ≤ 1400 px.
- `heditor test` understands long-form plans (`mode: "long"`): CTA by `cta.kind`, intro offset, optional captions, pauses up to 0.6 s, no 180 s cap.
- `camera_sync_check.py --source` (also `heditor long sync`): camera, screen and voice compared with the original recording through the EDL; module docstring and messages in English.
- `rk.load_brand` fills `subscribe`, `subscribed` and `watch_next` from the brand language when absent.

### Format profiles and style packs
- **Format profiles** (`scripts/reelkit/formats.py`, `heditor formats`): 9:16 (unchanged Reel numbers), 16:9, 16:9 4K, 1:1, 4:5 with canvas, safe area, caption zone, lower third and camera layouts. Used by `preview` (viewport from the composition), `finalize` (safe top row and sheet aspect per profile), `prepare_cut` (`crop="fit:<fmt>"`, `format` in `edl.json`), `rk.page(fmt=...)` and `heditor test`. Existing 9:16 projects behave as before.
- **Style packs** for the 36 named styles: `stylepacks.py` (`sp.get`, `sp.css_vars`, `heditor long styles`), the vertical → horizontal adaptation table in `references/long-form.md`, and `adding-styles.md` now asks every new style for its pack (`test_formats.py` fails when a style file has no pack).

### Longer Reels
- `heditor test` accepts longer Reels (narrated documentaries, stories of ~90 s): `plan["max_duration"]` (or `HEDITOR_MAX_DURATION`) raises the default 70 s limit up to 180 s, the Instagram Reels maximum.

### New style: `documentario-narrado` (alias atlas)
- Large-scale narrated documentary: the speaker's voice is the narration and a living night globe is the spine (Natural Earth, public domain, orthographic canvas with a virtual camera flight, lights that switch on with acceleration and land on the spoken number, great-circle routes fired on each repetition of the verb, world-scale payoff); generated period paintings in one constant style with 2.5D parallax; dated cards with a music-only hard silence → low impact → reveal → amber flash; the narrator as a film-graded testimony plate, a gold medallion on the map or voice-over; documentary notes with verified, sourced facts; a music tree in sections (era radio, filtered, full with the lift on the climax word, synthesized drone, silences, one trailer hit); "next chapter" loop back to the first globe shot. Full recipe, render cost and production pitfalls in `references/styles/documentario-narrado.md`; row in INDEX, SKILL, README, creative-mode, the style pack and the long-form table.
- depthkit: `dk.still_layers(src, out_dir)` splits a still (a generated painting, a photo) into a background and a soft RGBA front layer for 2.5D parallax; `dk.front_alpha` is the tested pure helper.
- troubleshooting.md: generated images in another aspect ratio, pseudo-text in generated paintings, animated `letterSpacing` lint error, vision timeouts on large sheets, music-only dramatic silences, documentary fact notes and the numbers test, canvas worlds that slow the render. quality-gates.md: a gate for unspoken facts on screen; cards listed among expected freeze flags.

### Fixes and tooling
- Long-form set pieces keep the speaker visible: checklists dim only the screen (world-level dim under the camera) and the full-screen concept map uses an opaque background instead of leaving a dark ghost of the camera.
- The `heditor` CLI exports `HEDITOR_KIT`/`HEDITOR_SKILL` pointing at its own checkout, so a second checkout never imports another checkout's kit through `env.sh`.
- New tests: `test_formats.py` (profiles, layouts, style packs) and `test_longform.py` (EDL, chapters, captions, segments, page windows, concatenation, audio/video assembly); CI runs them; `test_depthkit.py` gains a test for `front_alpha`.

## 1.6.1 — 2026-10-15
- `lousa-de-aula` approved after its first production and marked as a reusable style for technical explanations.

## 1.6.0 — 2026-10-15
- New didactic style `lousa-de-aula` (interactive chalkboard lesson): the whole screen is a classroom slate and the explanation is drawn live in chalk, each stroke starting on the word that triggers it (±0.15 s); numbered syllabus whose "?" turns into ✓, arrows labelled with the spoken verb, emphasis circles and double underlines, a felt eraser that wipes by mask, a SUMMARY board that rebuilds the chain, the teacher in a framed picture that shrinks to a corner and grows back, captions written on the board's margin, homework CTA. Full recipe: word-synced keys with `rk.finder`, pure `render(t)` engine, `stroke-dashoffset` drawing, hand jitter and double strokes, SVG chalk filter + grain mask, chalk stick and dust at the tip, handwriting reveal, eraser mask, per-stroke chalk SFX levels, `music:282` with the real drop at 12.45 s.
- troubleshooting.md: recipe "Drawing synced to speech" (sync keys, stroke offsets, consequence strokes, sync-table gate) and new rows for the cost of SVG filters in the render, small chalk labels, arrow-label agreement and an eraser that does not read as erasing.
- INDEX: new **didactic** family.

## 1.5.0 — 2026-10-15
- New `depthkit` module (`scripts/reelkit/depthkit.py`) for layered 2.5D/3D edits, every output frame for frame with `camera-hd.mp4` and rebuilt when stale:
  - `person_matte`: speaker alpha as `camera-alpha.webm` (camera RGB untouched) + `matte-person.mp4`, MediaPipe multiclass segmenter with temporal smoothing and a guided-filter edge, matte sheet and coverage stats for QA;
  - `depth_map` (Depth Anything V2 Small, ONNX, Apache-2.0) and `depth_look` (any ffmpeg grade on the far parts only, e.g. depth fog);
  - `edge_look` (room as glowing iso-depth contours or edge lines) and `dots_look` (background as a point cloud with a real point count), the speaker kept in colour;
  - `plane_matrix3d` / `homography` (pin captions and titles onto walls, desks, screens), `track_points` (Lucas–Kanade), `track_hands` (MediaPipe Hand Landmarker: palm centre and size per hand), `to_stage`, `setup_three` (offline three.js r181).
- CLI: `heditor matte | depth | look | hands | plane`.
- Six new named styles from a technique study of high-retention tech-creator Reels: `camadas` (concepts drawn behind the speaker), `raio-x` (the machine's view, stage by stage), `duelo` (A/B comparison page), `bancada` (proof on a filmed screen), `manchete` (headline inset on top), `revista` (editorial spreads with the speaker inset).
- New references: `depth-and-3d.md` (toolkit, layer stack, 14 layered recipes, QA) and `technique-catalogue.md` (layouts, illustrations, camera moves, caption systems, hooks, CTAs).
- Setup downloads the person and hand models and three.js; `setup.sh --depth` pre-fetches the depth model (otherwise it downloads on first use). `doctor` checks onnxruntime, `cv2.ximgproc` and the models. Requirements gain `opencv-contrib-python` and `onnxruntime`.
- New `test_depthkit.py` (homography, CSS matrix3d, cover mapping). `plane_matrix3d` writes 12 significant digits (8 decimals left a 0.15 px error on strong perspectives).
- troubleshooting.md: layered-shot pitfalls (double edges, semi-transparent hands, accessories kept by the matte, pumping depth, dense point clouds, offline three.js, render time).

## 1.4.0 — 2026-10-15
- Three new authority styles (serious tone, the speaker as the expert; organic Reels with a comment question and Follow), each with the full recipe:
  - `arquivo-cofre`: archive reading table at night; the expert as a record in a passe-partout, steel drawer with hanging tabs, time-stamp clock, microfilm reel that rewinds to the good day, captions printed on continuous copier paper (white on cobalt);
  - `aduana-de-dados`: night border checkpoint between your computer and the internet; exit declaration, X-ray monitor, barrier, regulations underlined item by item, booth-intercom captions (white on stamp red);
  - `laudo-de-sinistro`: insurance claim forensic report; the expert in the technical photograph with a forensic scale, forensic flash + B&W on every record, coverage clause filled as it is said, pen marks TOTAL LOSS → RECOVERABLE, one-line transcript captions (black on evidence yellow).
- troubleshooting.md: Reels over 70 s fail `heditor test`, music dips with `silence` sections, numeric layout values among timeline keys, `rk.finder` landing on a later occurrence, strips over a low face, tiny text in decorative SVG, camera black in the CTA, empty caption during a stretched word, one-line captions that overflow, repeated tracks inside a batch.
- Idea bank: archive, border checkpoint and forensic case-file formats are now named styles.
- Fix: `prepare_camera` and `styled_camera` rebuild `camera-hd.mp4` and every `camera-<name>.mp4` when they are older than their source. Before, a variant made from a previous `camera-src.mp4` was reused after the EDL changed, so picture and voice drifted apart (seconds) from the first removed sentence on.
- New `scripts/reelkit/camera_sync_check.py <work>`: compares every camera variant with `camera-src.mp4` frame by frame and fails when any is offset or has a different frame count. Run it before rendering whenever the EDL changed.

## 1.3.0 — 2026-10-15
- Fourteen new named styles, each with a full recipe (layout in px, palette, typography, caption contrast, scene grammar, motion, SFX map, music sections, CTA, pitfalls, variations):
  - organic: `tribunal` (courtroom sketch);
  - paid-ad formats with a "Learn more" CTA: `keynote`, `stories`, `predio-24h`, `bilheteria`, `porta-de-aco`, `manual-de-montagem`, `carrinho`, `entrega`, `auditorio`, `album`;
  - authority formats (serious tone, the speaker as the expert): `cassino-de-precisao`, `mesa-de-risco`, `turno-da-madrugada`.
- captions-and-layout.md: presenter cutout (alpha-matted speaker) guidance and the paid-ad safe area (captions at y 1046–1150, nothing critical below 1152, "Learn more" end card).
- quality-gates.md: the CTA test fails by design on "Learn more" ads; document it.
- troubleshooting.md: undefined timeline keys, SVG markers drawn early, gradients on zero-height paths, stale `words-reviewed.json`, upper-cased CTA text, background p95 stuck at −12 dB, DOM overflow checks, numeric HTML entities, colloquial captions in `asr-check`.
- licenses.md: optional external tools used by some styles (matting models, extra OFL font families).
- Idea bank updated: courtroom, stock ticker, checkout and blueprint formats are now named styles.

## 1.2.0 — 2026-10-13
- No dead air: `prepare_cut` now trims the silence at the edges of every block (`lead=0.08`, `tail=0.12` s around the first/last voiced window) and shortens internal pauses longer than 0.35 s (`edge=0.12`). Block boundaries snap to the quietest point of their radius, so junctions used to keep silence from both sides (0.8–1.3 s gaps that read as uncut pauses). `lead=None`/`tail=None` restore the old behaviour.
- New `heditor gaps <work> [max_s]`: lists every silence left in the assembled voice (junction or internal, with surrounding words) and fails above 0.45 s. `heditor test` gained `test_no_dead_air`; the gate is in quality-gates.md and workflow.md.

## 1.1.0 — 2026-10-13
- New named style `missao`: open-world game homage (sunset neon world, in-world social clip, character intro freeze-frame, mission card, GPS route, stats screen, mission-complete banner, phone-chat CTA), born from "creative mode + GTA 6 reference".
- Rendering heavy compositions: documented `PRODUCER_ENABLE_CHUNKED_ENCODE=true` and a larger `FFMPEG_ENCODE_TIMEOUT_MS`.

## 1.0.1 — 2026-10-13
- macOS: `install.sh` no longer uses associative arrays (`declare -A`), which the stock bash 3.2 does not support.
- macOS: `install.sh` and `setup.sh` expand optional argument arrays safely under `set -u` (bash 3.2 treated an empty array as unbound).
- `heditor preview` accepts a relative work directory (the path is resolved before building the file URI).

## 1.0.0 — 2026-10-13
- First public release.
- Ten named styles: cinema, ruptura, impacto, game, thriller, ide, aeroporto, chat, documentario, podcast.
- Creative mode and creative mode with a reference direction.
- reelkit: frame-accurate cuts with measured silence threshold, word-timed ASR, captions (text/pill), HyperFrames page skeleton, face tracking with jump-cut zoom, voice-first multiband mix, two-pass loudnorm, AAC true-peak guard, freeze/top-margin checks, integrity tests.
- One-command setup (tools, venv, Chrome, fonts, music and SFX catalog), `heditor` CLI and multi-agent installer.
