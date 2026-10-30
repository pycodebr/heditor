# Creative mode

Creative mode is heditor at full power: the edit is invented for this one video. It is what you do when the user says "creative mode", "modo criativo", "surprise me", or gives a reference direction ("creative mode using GTA 6 style").

The reference standard came from a real batch: seven class excerpts, each rebuilt as a different world — a retro RPG, a security-camera disaster tape, a code editor screencast, an airport control tower, a light messaging app, a mini-documentary and a talk show. The creator's reaction: every video surprised him. That is the bar. A competent edit with nice captions is a failure in this mode.

## What "creative" means here (operational definition)

1. **A world, not decorations.** The viewer enters a format with its own rules (an app, a game, a broadcast, a film genre, a machine). Layout, camera, captions, palette, typography, transitions, sound and CTA all obey that world.
2. **The speech drives the world.** Every beat of the argument becomes an event in the world (an error pops, a level is unlocked, a plane is cleared for take-off). Pick the world because the speech already contains it as a latent metaphor.
3. **The camera is a character.** Never just a rectangle: it lives inside the world (a monitor in a tower, a webcam bubble, a game character window, a CCTV feed, a video call) and reacts (zoom on jump cuts, colour shifts, glitches, shrinking to PiP, switching off).
4. **Captions belong to the world** (dialog box, code comment, radio transmission, chat bubble, film subtitle, karaoke) and stay perfectly readable.
5. **Sound is half of the edit.** Every visual action has a sound; music has an arc (tension → release, filtered → full, silence before the drop) chosen for emotion, always under the voice. Creative edits and paid ads use the `presence` mix profile (`plan["mix"] = "presence"`): a rhythmic bed felt the whole time, the track's turns (`heditor music`) on the speech turns, filtered sections kept short, `heditor asr-check` passing.
6. **Surprise every 1.5–2 seconds** without noise: a state change, a reveal, a camera move, a sound gesture. Pattern interrupts at each turn of the argument.
7. **A payoff.** The last spoken line lands with the biggest moment (typographic finale, take-off, level up, credits), then a CTA designed inside the world.

## Process

1. **Analyse the video.** Read the transcript of the chosen cut twice. Write in DESIGN.md: the thesis, the turn, the emotional arc, the audience, the strongest line, and a list of nouns/verbs/images the speaker uses (they are your metaphor seeds). Look at the speaker frames: energy, gestures, setting, camera size.
2. **Generate concepts.** Write 6–8 one-line formats that could carry this speech, as different from each other as possible (an interface, a genre, a broadcast, a physical machine, a game, a document, a place). For each: why it fits, the signature moment, the risk. Discard anything resembling the last edits in this project (check previous DESIGN.md files/contact sheets if available).
3. **Pick and justify.** Choose the concept with the best mix of fit, surprise, legibility on a phone and feasibility in HTML/GSAP. If the user is reachable and the choice is ambiguous, offer the top two in one line each; otherwise decide.
4. **Research.** Use web search/extract (and images if your agent can see them) to study how the real thing looks and sounds: UI conventions, typography, colours, motion, transitions, sound textures, music genre. Write a short "reference brief" in DESIGN.md with concrete specs (hex colours, font mood, element list, motion vocabulary, sound list). Map everything to licensed equivalents (google/fonts, Lucide, the catalog, CSS/SVG drawings, ffmpeg-graded camera variants).
5. **Design the beat sheet.** Time-stamped table: spoken beat → world event → motion/transition → sound. Plan the hook in frame 0, an open loop resolved near the end, a pattern interrupt at every turn, the payoff and the CTA. Plan the music sections and the drop on the most important word.
6. **Build ambitiously.** Write custom HTML/CSS/JS when the world needs it (most creative edits do). Tools that work well: CSS grid/flex UIs, SVG drawings with stroke-dashoffset, SVG filters (feTurbulence/feDisplacementMap for liquid or heat), seeded particles, split-flap/typewriter effects, clip-path wipes, ffmpeg camera variants (`rk.styled_camera`: grade, CCTV, VHS, monochrome, posterize, pixelate), voice-reactive elements from the real amplitude of `voice-master.wav`, typographic choreography.
7. **Critique with vision.** After each preview sheet ask: Is it surprising? Is every beat illustrated? Is anything generic, placeholder-looking or decorative without meaning? Is the face covered? Are captions readable with high contrast? Does it look like any previous edit? Fix and repeat (2–4 rounds is normal).
8. **Pass every gate** (`quality-gates.md`), render, finalize, review the final sheet.
9. **Offer to save the style.** If the user likes the result, name it and add it to `references/styles/` (`adding-styles.md`).

## Creative mode + reference direction

When the user names a reference ("use GTA 6 style", "like a Netflix true-crime opener", "anime opening", "Apple keynote", "90s VHS sitcom"):

1. Research the reference (official trailers/screens, articles, fan analyses). Extract what makes it recognisable in five layers: **palette and light**, **typography and graphic design**, **UI/HUD conventions**, **camera and transitions**, **sound and music**.
2. Write a reference brief with concrete equivalents you are allowed to use:
   - colours, gradients and grading recipes (CSS + ffmpeg filters),
   - OFL fonts with a similar voice (e.g. condensed sans for action titles, script for neon signage),
   - HUD/UI elements redrawn generically in CSS/SVG (stars, minimaps, phone UIs, banners, title cards),
   - motion signatures (freeze-frame character intros, wipes, zoom slams, slow pans),
   - sound textures from the catalog plus a music mood (no copyrighted songs).
3. **Homage, not copy.** Never use the reference's logos, names on screen, characters, screenshots, game/film assets, fonts you have no licence for, or music. Do not claim affiliation. Evoke the feel; the world must still serve the speech.
4. Keep heditor's rules: voice first, readable captions, safe zones, truth, licences.

Example — "creative mode with GTA 6 references" for a talk about career risk:
- Palette: sunset magenta→orange gradients, neon cyan accents, saturated sky; ffmpeg grade on the camera (warm highlights, teal shadows, soft bloom).
- Graphic language: freeze-frame "character intro" with the speaker's name in a bold condensed sans + script nickname; mission briefing cards; a generic five-star "wanted level" that fills when the risk rises; a mini-map route for the career path; phone UI for messages; big "MISSION PASSED"-style banner rewritten in the user's language with original wording (e.g. "MISSÃO CUMPRIDA").
- Motion: zoom slam into freeze-frames, diagonal wipes, radio-station name card when the music changes.
- Sound: whooshes, cash/coins, phone notification, sub drops; a trap or synth-heavy track from the catalog.
- Avoid: the game's logo, title, map, characters, real screenshots or soundtrack.

## Idea bank (formats proven or ready to try)

Proven (named styles): nativo (the clean baseline: cuts + animated captions, useful to compare against a creative version), cinema, ruptura, impacto, game, thriller, ide, aeroporto, chat, documentario, documentario-narrado (alias atlas: large-scale narrated documentary on a living night globe, born from "creative mode + a narrated history documentary as the reference"; use it as the starting point for history-documentary references), podcast, missao (born from "creative mode + GTA 6 reference"; use it as the starting point for open-world game references), tribunal (courtroom sketch), gravidade (the speech has weight: labelled blocks land on their words with baked physics). Paid-ad formats with a "Learn more" CTA: keynote (launch stage), stories (behind the scenes), predio-24h (isometric company, day and night), bilheteria (retro box office), porta-de-aco (steel shutter at midnight), lapidacao (luxury jewellery commercial: raw stone → cut → gem, a loupe over the machine's work, the offer case that slams shut; reference build), manual-de-montagem (assembly blueprint), carrinho (forgotten cart), entrega (order tracking), auditorio (TV quiz show), album (sticker album). Authority formats (serious, the speaker as the expert): cassino-de-precisao (noir casino → precision bench), mesa-de-risco (trading desk on a crash day), turno-da-madrugada (night-shift control room), arquivo-cofre (archive reading table with a microfilm reel), aduana-de-dados (night border checkpoint for your data), laudo-de-sinistro (insurance claim forensic report). Didactic formats: lousa-de-aula (interactive chalkboard lesson drawn live on the words), circuito (the explanation as a circuit board: components, copper traces, data pulses, morphing icons), planta-de-acesso (who may use what as an architect's floor plan: rooms with doors, role badges that open or lock them, a sheet turn for the proposal). Creator formats from a technique study of high-retention tech-creator Reels: camadas (concepts drawn behind the speaker), raio-x (the machine's view, stage by stage), duelo (A/B comparison page), bancada (proof on a filmed screen), manchete (headline inset on top), revista (editorial spreads with the speaker inset).

Layered effects available to any world (`depth-and-3d.md`): title behind the speaker, captions painted on a wall, objects orbiting behind the head, a 3D object passing between the speaker and the room, depth fog, contour scan, point cloud, exploded layers, virtual stage orbit, labels pinned to objects, objects floating over the palms. One "impossible" layered moment per video is often the strongest surprise; do not stack them all in one cut.

Motion tools available to any world: real rigid-body physics baked before render (`physics-3d.md`: things that fall, pile up, collapse, get knocked over, stack; `physkit.land_on` makes each one land on its word), and the GSAP plugins (`gsap-craft.md`): strokes drawn on the word (DrawSVG), one shape becoming another (MorphSVG on `svgkit.single_path` icons), objects riding a route (MotionPath), per-character titles (SplitText), custom bounces and wiggles. Clean every external SVG with `heditor svg` first.

Ready to try: breaking-news broadcast with lower thirds and ticker · weather forecast map · sports commentary with replays and telestrator · cooking show recipe cards · heist movie planning board · nature documentary narration · space mission control countdown · horror found-footage · anime opening with speed lines · comic book panels and onomatopoeia · museum exhibit labels · fitness app rings and streaks · GPS navigation with turn-by-turn · escape-room puzzles · music video with beat-synced cuts · hacker terminal / CRT · spreadsheet that comes alive · slide deck gone wild · receipt printer · polaroid scrapbook · subway map · retro TV channel surfing · dating-app swipes · video-game boss fight · tarot reading cards · K-pop lyric video · elevator floor indicator · arcade high-score table.

## Creative mode in long form

In a long video (class, live, YouTube) the same process designs the *frame, cards and set pieces*, not every
second: `"style": "creative"` + `style_overrides` in `long.json` (palette, fonts, card kind, transition) and the
set pieces (`title`, `concept_map`, `checklist`, `callout`, `custom`) at the hook, central concepts, turns and
chapter closes, with retention devices at the cadence of the kind. See `long-form.md` (Creative mode in long form).

## Escalation ladder (when an edit feels safe, climb)

1. Change the camera's role (from card to character inside the world).
2. Replace generic panels with world-native UI.
3. Give the captions the world's voice.
4. Add a structural surprise (blackout, reboot, rewind, channel switch, level change).
5. Make one element react to the real voice amplitude.
6. Build a payoff that resolves the loop opened in the hook.
7. Design the CTA as the world's ending (credits, continue screen, next flight, next episode).
