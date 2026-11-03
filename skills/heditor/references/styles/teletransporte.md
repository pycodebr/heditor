---
style: teletransporte
name: Teletransporte (the clone travels the story)
family: fixed-style
best_for: a speech whose sentences visit different places, eras or situations (history of a technology, "from the lab to your phone", a day in the life of a system, before/after); the speaker is the guide who appears in each place; 25–60 s
reference: created at the channel owner's request (Nov 2026) to play with his HeyGen clone in other scenarios, situations and positions; pilot from a class excerpt about the web in 1993
---
# Teletransporte (the clone travels the story)

The voice is the speaker's real recording. The picture is **the speaker himself in a different place on every
sentence**: a 1993 lab in a flannel shirt, a server closet, a data center at night, a rooftop over the city, a
construction site in a hard hat, and back home. Each place is a still of the real person generated from a reference
scene (`heditor gen persona`) and **made to speak the exact words of that sentence with lip-sync** from his own audio
(`heditor gen talk --audio`). Between places a **teleport** (white flash, horizontal RGB split, scan wipe, whoosh)
moves him; a **place card** like a boarding stamp names where and when he is (`LAB · 1993`, `DATA CENTER · AGORA`).
The captions run under the chest; the end card returns him home with the CTA.

The core metaphor: **the speaker can go anywhere the speech goes**.

**Status:** created and piloted (Nov 2026); visual approval pending.

## When to use / when not to

Use it when every sentence has a place (an era, a room, a situation) and the speaker's presence there adds meaning
(a guide, a time traveller, "I'm in the data center now"). Avoid it for abstract opinions with no places, for very
fast speech (each place needs ≥ 1.8 s), and whenever the generated likeness is not good enough to be the person.

## Signature moves

1. Frame 0 already in the first place, the speaker talking; the place card stamps in on the first word.
2. One place per sentence (1.8–6 s each). The **teleport** sits on the junction: the cut happens under a white
   flash (peak 0.95, 0.22 s), the new place arrives overexposed and settles (brightness 1.8 → 1 in 0.35 s), a cyan
   scan line and an RGB split run over it, a short shake, a whoosh, a glitch and a sub tick. Never wipe one place
   into the other across the face: two half heads read as a defect.
3. **Place cards**: monospace capitals in a dark pill with a thin accent border, ±3° rotation, stamped in
   (`scale 1.25 → 1`, 0.18 s), the name and the time (`1993`, `03H`, `AGORA`) from the speech or the scene.
4. **Continuity of the body**: all places are chest-up, eyes in the lens, the head at the same height (y ≈ 620) so
   the jump reads as the same person teleporting, not as a new video.
5. **The clothes change with the era** (flannel in 1993, hard hat on site): costume is part of the story.
6. **Home**: the last place is the speaker's real set (his own look or recording); the CTA lands there.
7. Optional: a mini map of the journey (dots per place, the current one lit) in the top band; a counter of places.

## Frame and layout

1080×1920, 30 fps. Each place clip (1080×1920 from `heditor gen talk --res 1080p`) is scaled and moved so that every
place has the same face height (430 px) and eye line (y 760): the build measures the face in every clip (MediaPipe)
with a scale of at least 1.15 to leave room for the move, at most 1.7. Slow push-in +4 % over the shot. Place card
at y 290–400 (left, x 70), journey map at y 310 on the right, both above the hair at that eye line. Captions in the
kit band (y 1222–1472) over the chest, with a dark gradient behind them; nothing on the face. CTA text below the face
(question y 1060, handle y 1360).

## Palette and typography

Neutral, the places carry the colour. Accent cyan `#7dd3fc` for the teleport (scan line, RGB split edges) and the
place card border; card fill `rgba(8,12,20,.78)`, text `#f4f8fb`. Fonts: JetBrains Mono 700 (place cards), Geist
800 (captions), kit fonts only. Captions: Geist 800 64 px, white with a 10 px dark stroke, active word black on
`#7dd3fc`.

## Sound design

Voice first (`voice` profile). Teleport: `whoosh` −24 + `glitch` −30 + `bass_impact` −28 at each junction; place
card: `stamp` −28; journey map tick: `data_beep` −32; end card: `success_chime` −26. Music: an adventurous bed
(`music:187`, `music:31`), +3 dB on the end card. The generated clips' own sound is muted (the voice is the
recording).

## Production (see `../generation.md`)

1. Cut the speech as usual (`prepare`, `words`). Mark the sentence boundaries; they are the place cuts.
2. For each sentence: a reference still of a stand-in in the place (chest-up, eyes in the lens), then
   `heditor gen persona <work> sN-name --ref gen/refs/rN.png --yes` (6 credits each).
3. Cut the clean voice (`composition/assets/voice-master.wav`) per sentence into `gen/audio/sN.wav` and make each
   still speak it: `heditor gen talk <work> sN-name-talk --image gen/sN-name-1.png --audio gen/audio/sN.wav
   --res 1080p --yes` (~0.55–0.6 credit per second). The clip starts at the sentence start, so the lip-sync matches the
   master voice frame for frame.
4. `beats.json` (reference build `templates/styles/teletransporte/build.py`): places with their clip, card text and
   time; `heditor produce <work> teletransporte 0`.
5. QA: likeness on every place (vision against the real look), mouth in sync at 3 points per clip (start, middle,
   end), no frozen frames at the joins, captions off the face.

Cost of the pilot (30 s, 7 places): 5 persona images (30 credits) + 30 s of talk (~10 credits).

## CTA

Back home (the real set): the place card says `CASA · @handle`, the question of the video, Follow → Following on a
touch, 4–5 s after the last word.

## Pitfalls

- `identity_remix` sometimes returns the scene reduced inside a blurred copy of itself; `heditor gen persona` detects
  that frame (sharp inner rectangle on 3–4 sides) and saves the inner picture at full size, keeping `.framed.png`.
  Avatar IV with `fit: contain` can add the same frame: `heditor gen talk` asks for `cover`.
- A selfie look as "home" makes the face 2× larger than in the generated places; use a non-selfie look or
  recording for the last place.
- A stand-in that differs a lot from the person (no beard, other glasses) gives a weaker likeness; keep the stand-in
  close and use 3+ identity images.
- `identity_remix` beautifies; check moles, beard density and glasses frame against the real look.
- Profile poses or hands near the mouth break the lip-sync; keep chest-up and eyes in the lens.
- Each talk clip must start exactly on its sentence (slice the clean voice with the same times as the cut).
- Disclose AI use: the places are generated (the post caption and the platform's AI label).

## Variations

- **Time machine**: the places are only eras of the same room; the card shows the year rolling.
- **Ubiquity**: the same sentence split into 3–4 places in quick succession (0.6 s each) for a punchline.
- **Transparent speaker** (`--alpha`) over moving generated scenes (`heditor gen clip`) instead of stills.
- **Split home/away**: the real speaker at home in the bottom half, the clone in the place on top.
