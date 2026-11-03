---
style: reconstituicao
name: Reconstituição (illustrative reconstruction of a real event with live data)
family: fixed-style
best_for: explaining a news event or an incident that happened (a crash, an outage, a launch, a leak, a market move) with public data: timeline, numbers, places, quotes; 45–90 s narrated, no presenter on screen
reference: technique study of a viral Brazilian news Reel (an aircraft accident explained the same day with generated scenes, tracking data, the radio transcript and a "made entirely with AI" reveal; ~250 k likes), Nov 2026
---
# Reconstituição (illustrative reconstruction of a real event with live data)

A narrated explainer of something that **really happened**, built from public data. The picture is a sequence of
**generated cinematic shots of the event** (from stills animated with `heditor gen clip`, or stills with motion),
always under a small **"RECONSTITUIÇÃO ILUSTRATIVA · DADOS PÚBLICOS"** label, over which a **consistent system of data
cards** tells the facts: live counters that climb or fall on their words (altitude, time, money, users), a **dark map**
with the route drawn on the verb and a pulsing target on the place, **quote cards** for what was said (the original
language in small mono under the translation), instrument or gauge screens (a limit bar that passes into red), a
numbered **sequence of causes** over the scene, an **"investigation" checklist panel**, and a closing reveal of the
production itself (a grid of the generated shots, "made entirely with AI") followed by a keyword CTA in a fake
comment box. The voice is the speaker's recording (or his cloned voice on an approved script).

The core metaphor: **a newsroom graphics desk that rebuilt the event with the data**.

**Status:** documented from the reference (Nov 2026); build the first one in creative mode with this file as the
brief, then save the reference build.

## When to use / when not to

Use it for events with checkable facts: times, numbers, places, quotes, a cause under investigation. Avoid it when
the facts are not public or verified, when people involved could be identified or harmed, for tragedies the brand
should not use as a hook, or for opinion pieces (`impacto`, `vox`). Never invent a number, a quote or a cause.

## Signature moves

1. **Hook in 3 s**: the most dramatic generated shot already in motion + a two-line title question (white + yellow,
   heavy sans) + a live counter that is already moving (e.g. altitude falling) + the reconstruction label.
2. **Data cards** (one family everywhere): dark rounded card `rgba(10,14,22,.78)`, label in tiny mono caps
   (`ALTITUDE`, `TEMPO`, `A BORDO`), value in big mono white, unit small; red only when the value becomes critical.
   Counters land on the spoken number on its word (odometer or eased count).
3. **The map**: navy `#0b1730` with faint mono place labels, a header strip with date and time; pins drop on their
   names, the route draws in yellow on the verb, the unreached part dashed white, a red pulsing target where it ended.
4. **Quote cards**: speaker role and channel in the header with a red dot and an audio meter, the translated quote in
   bold white, the original in small grey mono; one card per quote, on the word that introduces it.
5. **Instrument/gauge screens** for technical terms: a limit bar (0 · 0,5 · LIMIT) that fills and crosses into red on
   the word; an attitude indicator that rolls to the spoken angle.
6. **Numbered causes** over the scene (① ② ③) on their words; a vision-friendly **checklist panel** ("what the
   investigators will look at") with ticks on each item and a calendar card for the next report.
7. **Production reveal**: a 3×2 grid of the generated shots, an orange pill "MADE ENTIRELY WITH AI · WITH TODAY'S NEWS",
   then the CTA headline and a fake comment field where the keyword types itself, a send button and a pill "I'll send
   you everything".

## Frame and layout

Title band y 300–420 (hook only). Data cards y 1000–1180 left and right (two per row). Captions y 1380–1460 (one line,
2–4 words). Reconstruction label at y 290 (small mono, `#9fb0c4`). Map and panels full frame. Nothing critical below
1570.

## Palette and typography

Storm greys and navy for the world; yellow `#ffd84d` (active word, route, title line 2), red `#ff4d4f` (critical
values, targets, OVERSPEED), orange `#ff8a3d` (AI pill, CTA button), white text. Fonts (kit): Anton or Bebas Neue for
the title, Geist 800 caps for captions (active word yellow), JetBrains Mono for labels, values and the reconstruction
label.

## Sound design

`presence` profile (music ~15 dB under). A dark pulsing bed (`music:871`, `music:686`), radio static under the quote
cards (`glitch` −34), `data_beep` −30 on counters, `stamp` −28 on cards, `whoosh` on map moves, `heartbeat` −30 in the
critical stretch, a hard music silence before the reveal of the cause, `success_chime` on the CTA.

## Facts and labels (non-negotiable)

- Every number, time, place and quote comes from a cited source; list them in DESIGN.md with URLs and the time of
  the information ("information up to 23:00 on 01/11").
- The reconstruction label stays on every generated shot; the post caption repeats it.
- No faces of real victims, no real airline/company logos, no invented cause ("nobody knows yet" when that is true).
- Respectful framing for tragedies: no jokes, no sales hook on the event; condolences when people died.

## Production

Stills of the event with the image generator (no logos, no faces), animated with `heditor gen clip --image` at 480p
for tests and 768p–1080p for delivery (`../generation.md`); data cards, map, gauges and panels are HTML/SVG (never in
the image); counters are pure functions of time. Narration: the speaker's recording, or his cloned voice on an
approved script (`heditor avatar`, voice only).

## Variations

- **Outage reconstruction** (a service down): a status page, request graphs, a world map of affected regions.
- **Launch reconstruction**: the timeline of a product launch with the real numbers.
- **Market move**: a price chart as the instrument screen, quotes from official statements.
