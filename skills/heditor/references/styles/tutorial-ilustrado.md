---
style: tutorial-ilustrado
name: Tutorial ilustrado (white-canvas narrated tutorial with a line-art host)
family: fixed-style
best_for: step-by-step tutorials and "how I do X" explainers narrated by the speaker (setting up a tool, a workflow, a folder, a prompt), where the steps can be drawn as simple UI and diagrams; 45–90 s; no screen recording needed
reference: technique study of a Brazilian creator's narrated tutorial Reel (editing videos with an AI assistant: open the app, create a folder, paste a file, five "powers", send references, the result), Nov 2026
---
# Tutorial ilustrado (white-canvas narrated tutorial with a line-art host)

A **white canvas with a faint grid**, a **line-art portrait of the speaker** as the host (drawn from his photo: black
strokes, round glasses, beard), and every step of the tutorial **drawn as simple vector UI** while he narrates: a
monitor that draws itself, a blue button, a folder that pops in and gets its name on the word, a toggle that turns
from outline to filled blue, a prompt field that types itself, a timeline whose gaps close, a radial diagram of
"five tools" whose nodes light on their words. Each section opens with a **header** (black square + tiny caps label +
rule) and a **two-part headline**: a neutral line in black sans and the emotional complement in **blue italic serif**
("Começa no / *seu computador.*"). The host moves between the centre (hook, key rule) and a corner (while the UI works)
and acts as the pointer, peeking next to the button that matters. Captions are small, black, karaoke with the active
word in blue and underlined. The CTA is a keyword in big blue, a document icon and "Saiba mais" pill.

The core metaphor: **the tutorial is a clean notebook page that the speaker fills while he talks**.

**Status:** documented from the reference (Nov 2026); build the first one in creative mode with this file as the
brief, then save the reference build.

## When to use / when not to

Use it for procedures with 3–7 steps and a clear result, contrarian "you don't need a course for this" hooks, and
tool explanations for beginners. Avoid it when the real interface must be shown exactly (use `ide`, `bancada` or a
screen recording) or when the speech is a story (`vox`, `teletransporte`).

## Signature moves

1. **Hook**: host big in the centre, the headline in two parts, a contrarian object struck through on its word
   ("vendido num *curso*" with a blue strike).
2. **Section header** on every step: numbered square + label caps (`PASSO 1 · SEU COMPUTADOR`) + a rule; update it on
   every step (progress is visible).
3. **UI drawn on the word**: stroke-draw (DrawSVG) of the device, then fill; state changes outline → filled blue on the
   verb ("escolhe *Local*"); a success pill "✓ Pasta conectada" at the end of the step.
4. **The host as pointer**: small line-art bust that slides to the element being explained (never a mouse cursor).
5. **Diagrams**: radial "N tools" with icon nodes lit on their words; film strips cut by scissors (pauses removed); a
   waveform with a playhead writing the caption; three reference cards fanned (LETRA, MOVIMENTO, RITMO).
6. **The rule**: once per video, the host big again with the key rule in huge blue italic ("*se inspirar.*").
7. **Result**: a phone/video card with "✓ Vídeo editado" and the prompt bar with the file attached.

## Frame and layout

White `#fbfbfa` with a 40 px grid at 4 % black. Header y 300–340; headline y 360–520 (sans 64 px + italic serif 76 px,
centred); stage y 600–1200 (UI, diagrams); host 220–420 px tall, centre (hook) or bottom-left corner (x 80–300,
y 1180–1400; never bottom-right, where the Reels buttons are); captions y 1430–1500, black 44 px Geist 600, active
word blue `#2f5be0` underlined 4 px.

## Palette and typography

Black `#111111`, greys `#8a8a8a`/`#d9d9d9`, one royal blue `#2f5be0` for everything that matters (active word, italic
complement, buttons, folder, success pill). Fonts: Geist (sans), Instrument Serif Italic (blue complement; heditor
2.17.0+), JetBrains Mono for tiny labels.

## The line-art host

Generate once per speaker with the image generator from his real photo: "clean black line-art portrait, single weight
strokes, white background, bust, round glasses, beard, no shading" → vectorise (`potrace` or trace in the browser) or
use the PNG with `multiply`; three poses (neutral, pointing, thumbs up). It is an illustration of the speaker, not a
generated photo: no disclosure needed beyond the usual.

## Sound design

`voice` profile; a light, rhythmic bed (`music:282`, `music:167`); `pen_write` on stroke draws, `pop` on pop-ins,
`click` on state changes, `typewriter`/`typing_fast` on the prompt field, `success_chime` on success pills, `swipe`
on section changes.

## Variations

- **Dark notebook** (black canvas, chalk-white strokes, yellow accent) for night-themed content.
- **Real screenshots inside the drawn monitor** when one exact screen matters.
- **The clone instead of line art** (`heditor gen talk --alpha`) for a host who speaks on camera in a corner.
