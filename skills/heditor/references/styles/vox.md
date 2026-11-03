---
style: vox
name: Vox (explainer documentary in monochrome)
family: fixed-style
best_for: a short story with a reveal or a fact that sounds surprising (a date, an origin, "it all runs on the same thing"); history of a technology or an idea told in 25–60 s; explanations where the speaker narrates and the picture illustrates every sentence
reference: reverse-engineered from a vertical "Vox-style" documentary Reel (a 28 s story about a composer, generated period stills animated with code, Nov 2026); pilot built from a class recording about the web in 1993
---
# Vox (explainer documentary in monochrome)

The speaker's voice narrates a **short editorial documentary**. The picture is a sequence of **black-and-white "reconstructed archive" stills** (people only from behind, film grain, vignette, slow push-in) and **paper collages** (objects cut out with their contact shadow, a torn paper card, faint pencil sketches), joined by **blur dissolves** that read as meaning (focus is lost as the scene changes). The captions *are* the typography: an **italic serif revealed word by word on the subject's dark coat**, with the key word of the line set **huge in the same serif, entering with a blur**. White line art is **drawn on its word** over the stills (icons, arrows, a network, rays), a **hand-drawn ellipse** closes around the phrase that matters, the speaker appears **once as a black-and-white photograph taped to the paper**, and the CTA is a **museum label under a gilded frame** (the only colour in the video).

The core metaphor: **the speaker is the narrator of a documentary about the subject**; the viewer is in an archive, not in front of a webcam.

**Status:** created at the channel owner's request from a reference video (Nov 2026); visual approval of the style is pending. Reuse the language and rebuild the stills, the collage and the marks for each new story.

## How it differs from the other documentary styles

| `documentario` | `documentario-narrado` (atlas) | `vox` |
|---|---|---|
| letterboxed cinema band, the camera always on screen | night globe, oil paintings in parallax, dated cards with impacts | monochrome stills + paper collage, no map unless the story needs one |
| Playfair/Fraunces captions on a band | Barlow Condensed on a dark band, gold pill | **Instrument Serif Italic** in the picture, no band, no pill; key word huge |
| the speaker is the subject | narrator in three states (plate, medallion, voice-over) | voice-over ~90 %; the speaker once, as a taped photograph |
| music bed, soft fades | music tree with hard silences and one trailer hit | one soft reflective piano, breathing pauses between chapters, no hits |

## When to use / when not to

Use it when the speech:
- tells something that happened (a date, a first time, an origin) or explains why things are the way they are;
- has 3–6 sentences that each can become one picture (a room, an object, a gesture, a place);
- has one phrase worth circling (the date, the number, the claim) and a few words worth setting big;
- sustains a calm, curious tone: the style persuades by atmosphere, not by energy.

Avoid it when the speech is a fast list, a tutorial with screens, a heated opinion or a hard sell (`impacto`, `reacao`, `bancada`, `keynote`), or when the story needs dates and a world-scale arc of 90 s (`documentario-narrado`).

## Signature moves

1. **Frame 0 is already a still in push-in** (a person from behind in a dark room, an object), the first caption word on the coat; no title card.
2. **Captions revealed word by word**, accumulating in place (the words take their final positions; the line fills left to right), small italic serif; the **key word huge** in the same block, blur 16 px → 0 and scale 1.07 → 1 in 0.42 s.
3. **Blur dissolve between scenes**: the old scene blurs to 22 px and fades in 0.55 s while the new one comes into focus from 24 px in 0.6 s. Optional **fade through white** for a chapter turn (high-key paper), and **rack defocus** of the current still on a word of loss ("barely", "silence").
4. **White line art drawn on its word** over the stills: hand-drawn icons (resampled into a jittered polyline at build time), arrows, rays, a network of points that grows with acceleration and lands on the spoken word.
5. **The hand-drawn ellipse**: an open loop of ~1.05 turns that closes around the key phrase (a date, a number) as the phrase completes, 0.65 s, `power2.out`.
6. **Paper collage**: off-white paper with faint pencil sketches, objects shot on plain paper blended with `multiply` (their paper disappears, the contact shadow stays), a torn paper card with the spoken date in serif, items that drop in with `back.out` and drift.
7. **The speaker as a taped photograph**: black-and-white plate, cream border, two strips of tape, slight rotation, on the sentence that is his own opinion or thesis.
8. **Museum label CTA**: a gilded frame (the only colour) holding the hero still, the subject's name in italic serif and a spoken date under it, the handle and a Follow pill that a touch fills.

## Frame and layout

Canvas 1080×1920, 30 fps. Stills are generated at 1024×1536 and placed in cover (1280×1920, 100 px cropped on each side).

```
y 0–270      atmosphere only (dark sky of a still, paper margin)
y 300–700    captions on paper scenes and on stills whose subject is low (key word ≤ 860 px wide)
y 650–1500   the subject: a back, a desk, an object, the collage, the taped photograph
y 1100–1450  captions on stills whose subject's dark coat is there (block centre; never on a face)
y > 1570     atmosphere only (the UI covers it)
```

Captions sit **on a dark, plain area of the picture** (a coat, a night sky, a shadow); a soft radial scrim (black 0.52 at the centre) helps on stills. On paper the ink is dark and there is no scrim.

## Palette and typography

| Role | Hex |
|---|---|
| Light ink (captions and line art on stills) | `#f4f1ea` with `0 2px 16px rgba(0,0,0,.75)` |
| Dark ink (captions and line art on paper) | `#171512` |
| Paper | `#e8e5df` (generated texture), card `#f3efe6`, photo border `#f1ebdf` |
| Warm tone over stills | `#efe4d0`, `multiply`, opacity 0.5 (bridges grey stills and cream paper) |
| The only colour | the gilded frame of the CTA (`saturate(.7)`) |

Fonts (OFL): **Instrument Serif Italic** (captions and key words; regular for the card numbers and the label date), installed by `setup.sh`; Geist 600 for the Follow pill only. Small words 66 px, key word 120–230 px fitted to 860 px with the real TTF.

## Caption system

- Groups follow the speech: phrases split at punctuation and gaps > 0.7 s, long phrases split in balanced chunks of ≤ 6 words / 34 characters that never end on a function word and prefer breaking before a clause word; a phrase that will be circled stays in one group (`keep`).
- **A key word must be readable**: when its group ends less than 1.3 s after it, the next phrase joins the same block (not across a scene cut, not into a kept span).
- Every word appears at its start (opacity, blur 7 → 0, y 8 → 0 in 0.2 s); the group leaves with a 0.18 s blur-out before the next.
- Active-word contrast: the revealed word is the active one, white on a dark area with a shadow (≥ 7:1) or ink on paper (≥ 12:1). Nothing is shown before it is spoken.

## Scene grammar

Generic example (a class excerpt about the web in 1993): hook "every innovation today runs on the same thing deployed on 30 April 1993" over a modern night still (icons for "AI", "API", "system" drawn on their words); blur to a 1990s office still, the key word "same" big, the ellipse around "on 30 April 93"; a breath; a paper collage with a period computer cut out and a torn card "30 / April", "WWW" big, rays drawn on "available"; blur to a desk globe at night, "500" big, a network that grows over the globe and lands on "the world"; fade through white to the paper with the speaker's taped photograph on his thesis ("the foundation is always the same", underline); a collage of the old computer and a phone with arrows "goes there / comes back"; museum label CTA.

| Beat | World | What happens |
|---|---|---|
| Hook | still, push-in | captions on the coat from frame 0; line art drawn on the nouns |
| Thesis / reveal | still (blur dissolve) | key word big; the ellipse closes on the phrase; optional rack defocus |
| Breath (0.5–0.7 s, `PAUSE` block) | same still | music only; the push-in continues |
| Context | paper collage | objects drop in on their words; torn card with the spoken date; key word big in ink |
| Scale / number | still | the number big; a network or marks that land on the spoken number |
| Opinion | paper + taped photograph (fade through white) | the speaker's thesis; underline under the phrase |
| Payoff | collage | arrows or a before/after pair acting out the verbs |
| CTA (5 s) | museum label | the hero still in the gilded frame, the subject's name, a spoken date, handle, Follow → Following on a touch |

Rules: no faces in generated stills (backs only, or out of focus), no real people, no logos, brands or readable screens; text, numbers and dates on screen come from the speech (a full year spoken as "93" goes to `allowed_numbers` with the reason); one constant style sentence for every still.

## Generating the stills

```
Black-and-white documentary still, reconstructed archival photograph, 35 mm film grain, soft halation on
highlights, shallow depth of field, strong vignette, high contrast with rich mid-tones, natural cinematic light.
Vertical portrait 2:3, 1024x1536. Scene: <a person seen strictly from behind at ... / an object in a room>.
<Where the dark calm area is (for the captions)>. No text, no letters, no numbers, no logos, no brands, no
readable screens, no visible faces.
```

- **Objects for the collage**: "studio product photograph in black and white, film grain, <object>, isolated on plain flat off-white paper (#ECE9E3) with only a soft contact shadow, the object occupies ~40–60 % of the width". The build divides each object by a smooth fit of its own paper (paper → white) and blends it with `multiply`, so no box and no halo remain; blacks are lifted to 28 so a glossy modern object prints like the old ones.
- **Paper**: "flat top-down scan of warm off-white sketchbook paper, faint almost erased pencil sketches near the edges, empty centre".
- **Frame**: "ornate antique gilded frame on a plain off-white wall, the opening EMPTY and flat white". The build finds the opening by flood fill from the centre, punches it, feathers the crop and lays it with `darken`.
- Review every still with vision for pseudo-text, faces and where the dark calm area is; place the captions there.

## beats.json (reference build)

`heditor new <work> <video> --style vox` scaffolds `build.py` and `DESIGN.md`; write `beats.json` from the speech (format at the top of the build and in `templates/styles/vox/beats.example.json`), then `heditor produce <work> vox 0`. Keys: `scenes` (photo / paper with items: `img`, `card`, `plate`), `big`, `keep`, `marks` (circle / underline over caption words), `doodles` (icon / arrow / rays with `arc` / network with `until_full`), `focus`, `cta` (frame, photo, paper, label, sub), `music`, `allowed_numbers`. Item and doodle coordinates are stage pixels; check them against the object's bounding box written next to it (`composition/assets/vox/*.json`) so arrows and rays keep 20–40 px of air.

## Transitions and motion vocabulary

- Blur dissolve (default between scenes), fade through white (chapter turn, paper scene), hard cut (rare).
- Slow push-in on every still (scale 1.03–1.05 → 1.11–1.16 over the scene + 0.9 s), optional drift/lift in px.
- Collage items: drop in (`y −60`, `rotation +5` → final, 0.5 s `back.out(1.5)`), then drift 12 px up.
- Line art: stroke draw with `pathLength="1"` and `stroke-dasharray: 1 2` (a 1/1 pattern leaves round-cap dots at the path end), hidden until its word.

## Sound design

| Action | Category | gain_db | length |
|---|---|---|---|
| Blur dissolve / fade through white | `whoosh` (variants alternated) | −32 / −33 | 0.8 / 0.7 |
| Collage item, torn card | `page_turn` | −27 / −26 | — |
| Taped photograph | `camera_shutter` | −27 | — |
| Line art, icons | `pen_write` | −30…−29 | 0.6 |
| Ellipse / underline | `pen_write` | −27 | 0.7 |
| Network starts | `data_beep` | −33 | 0.3 |
| Museum card / touch / following | `page_turn` / `mouse_click` / `success_chime` | −24 / −20 / −27 | — / — / 0.9 |

Music: one soft reflective piano under the whole voice (`voice` mix profile, music ≈ 21.5 dB under the voice), +3 dB on the CTA with a 1.4 s fade. Reference: Mixkit "Classical 7" (id 714, Mixkit Free License, downloaded per `mixkit-stock-audio`); catalog alternatives `music:955` (emotional piano and strings, the default in the build) and `music:871` for a darker mystery. Breaths between chapters are `("PAUSE", 0.5–0.7, "key")` blocks in `prepare.py`, listed in `plan["duck_open"]`; no impacts, no risers.

## CTA design inside the style

5 s after the last word: blur-in of the museum (0.7 s), the frame group settles from 1.05 → 1.0 over the hold, the label (Instrument Serif Italic 84 px) fades up, the date (Regular 56 px), a 260 px rule draws, then the handle and the Follow pill (330 px, ink border); a touch ripple at the centre of the pill, the ink fill sweeps from the left and "✓ Following" appears. The placard must end above y 1580 (the build asserts it; lower `frame_w` or `frame_top`).

## Pitfalls found in production

- **Blending inside a stacking context does nothing**: `mix-blend-mode: multiply` on an `<img>` inside an element with a transform or opacity blends with that element's transparent backdrop and shows the object's paper as a grey box. Put the blend on the wrapper that is the direct child of the scene.
- **Cut-outs with masks look pasted**: flood-fill or edge masks left a light halo and a hard-edged shadow plate. Dividing by the object's own paper and multiplying keeps the shadow and the paper texture with no edge.
- **Measuring caption boxes in a timeline callback is seek-order dependent** (lint `gsap_callback_dom_measurement`): the ellipse and underline are computed in Python from the real TTF (simulated flex wrap) and drawn in stage coordinates.
- **`vector-effect: non-scaling-stroke` breaks `pathLength`** (the dash pattern falls back to user units and the mark shows as a dotted line from frame 0).
- **Short groups hide the key word**: at a normal speaking rate a group lives ~0.6 s; the big word vanished after 0.3 s until short groups were merged with the next phrase (1.3 s rule).
- **The frame opening found by a column scan was wrong** (a highlight on the crest): find it by connected components from the centre and punch it.
- **Captions jump in the CTA area**: keep the placard above 1580 and the frame top near 250.
- **Line icons from a library read as UI**: resample them into a jittered polyline at build time (seeded) and add a ghost stroke at 35 %.
- **Lint is clean when every draw uses `TO` on dashoffset after a `set` of opacity at the same time**; `fromTo` on a selector list triggers the baseline warning.
- **Nobody listens in QA**: the breaths and the junctions must be heard before delivery.

## Variations

- **Engraving** instead of photographs (copperplate lines, sepia ink) for older centuries.
- **Map collage**: a paper map with pins and string instead of the globe still when the story has places.
- **Archive desk**: hands, magnifier and index cards as the opening montage (0.6 s per shot).
- **Accent colour**: one spot colour (red pencil or yellow highlighter) for the ellipse only, when the brand needs it; keep the rest monochrome.
- **Long form**: chapters as fades through white to a new sheet of paper; stills at 6–9 s each with the same push-in; the taped photograph as the chapter's lower third.
