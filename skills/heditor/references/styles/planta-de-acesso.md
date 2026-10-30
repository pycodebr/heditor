---
style: planta-de-acesso
name: Planta de acesso (access floor plan, blueprint drawn live)
family: fixed-style
best_for: explanations about who may use what — permissions, roles, access levels, modules per team, data a department must not see, multi-tenant or multi-department systems, a proposal for how a tool should be distributed inside a company; the company becomes a floor plan drawn live behind the speaker, every area a room with a door, badges per role open or lock the doors
reference: produced by the PycodeBR team with heditor, Oct 2026 (organic Reel from a class excerpt, speaker full-frame on a webcam)
---
# Planta de acesso (access floor plan)

The Reel is an architect's sheet on blue paper. The speaker, cut out with the matte, stands in front of a floor plan that is drawn live on his words: the system (or the company) is a building, every module or department is a room with a door, and the people are ID badges per area. When he says who should use a module the route is drawn and the door swings open with a green check; when he says who must not see something the door slams, a red padlock lands and the room is cross-hatched in red, its contents shown only as masked values (`R$ •••`). A proposal turns the sheet (sheet B), and the closing pulls back to the whole company (sheet C), every sector lighting up and dots of people walking only into the rooms they are allowed into, one of them bounced at a locked door. The language of a project (title block, "preliminary study" stamp, dashed lines "to be built", no scale) tells the viewer this is a plan, not a shipped product, without any "illustrative" label. The core metaphor: **access is space; designing permissions is drawing who walks through which door**.

## When to use / when not to

Use it when the speech:
- says that not everybody should use everything ("depending on the area", "only these people should see the numbers");
- names areas, departments, roles or modules and what each one may do;
- proposes an interface, a gateway or a permission layer between people and a tool or an AI agent;
- closes on distribution: "every sector, every collaborator, each with its own permissions".

Avoid it when:
- the speech has no spatial idea (nobody "enters" anything): use `circuito` for data that travels or `lousa-de-aula` for a concept map;
- the batch already has a blue technical sheet (`manual-de-montagem`) or another engineering world (`circuito`, `raio-x`);
- the source camera is a small tile from a meeting: the style leans on a large, clean cutout of the speaker (use a card-based format instead);
- it would expose real names of colleagues, real figures or a real admin screen: badges are silhouettes with area tabs, values are masked.

## Signature moves

1. **Word behind the head at frame 0**: the hook's key words ("NOT ALWAYS") in giant Bebas Neue behind the cutout (matte layer), the sheet title and its subtitle already on the paper, a slight punch-in that settles.
2. **Preliminary study stamp**: a gold rectangle stamp ("PRELIMINARY STUDY", later "· B", "· C") lands in the first pause; it is the honest proposal label of the whole video.
3. **Walls drawn on the verb**: the rooms of sheet A are drawn with DrawSVG on the word that introduces them, doors drawn as leaf + dashed swing arc, room labels in B612 Mono.
4. **Badges on lanyards**: two or three role badges (silhouette photo, coloured area tab, never a name) drop in with a swing on "employees"/"team"; the tabs pulse on "area".
5. **Doors as the verdict**: allowed module = dashed yellow route drawn from the badge, door swings open (`back.out`), green hatch fill and a green check chip; forbidden module = red dashed route, door slams (`power4.in`), red padlock chip, red cross-hatch, contents masked; a punch-in plus a 7 px shake on the forbidden word.
6. **The right people unlock it**: small badges of the authorised role appear one per spoken person ("me and two more"), a handwritten Caveat note, padlock → open padlock, hatch turns green.
7. **Sheet turn for the proposal**: on "we could build", the whole sheet slides away horizontally with a light sweep, the camera moves down and shrinks, and sheet B is all dashed: people → INTERFACE (drawn dashed while he says it) ⇄ AGENT, the framework name typed letter by letter, a data pulse travelling back and forth on "talks to", chat balloons.
8. **Plan legend**: a legend box ("LEGEND · <FRAMEWORK>") with one checkbox per spoken native feature (registration, user management, permissions per module), each ticked on its word; a round gold stamp ("NATIVE") lands in the gap after the sentence.
9. **Pull back to the company**: sheet C is the whole floor (two rows of three rooms around an "AI INFRASTRUCTURE" corridor drawn from the centre); rooms light in sequence on "multiple sectors", dots of people pop on "collaborators" and walk into their rooms on "accessing", one dot is stopped at a locked door with a buzzer.
10. **Payoff behind the head**: the last key word ("ALLOWED") giant in green behind the cutout, the plan fades to 5 %, a scanline lifts the speaker out of the drawing.

## Frame and layout

Canvas 1080×1920, 30 fps, organic safe area (`../captions-and-layout.md`).

```
y 0–270      paper and grid only
y 300–390    sheet title (B612 Mono 40 px) + subtitle (B612 Mono 24 px, light blue); stamp at the top right (x ≥ 740)
y 410–830    the plan (rooms, doors, routes, legend); labels ≥ 24 px, prefer 30 px
y 560–1500   camera box (cutout over a plate), face around y 1000; plan elements never cross the face
y 1336–1486  caption "dimension line" block
y 1630–1780  technical title block (PROJECT / AUTHOR @handle / SCALE · NOT TO SCALE), 32 % opacity
```

Camera: a 1240×1080 crop of a 1920×1080 webcam frame (the label of the meeting software outside the crop) scaled to 1080×940 without colour filters, mask-faded at the bottom (80 → 99 %) and at the sides (4 %). Two layers: the cutout (`camera-alpha.webm` from `heditor matte`) on top, the giant words between the paper and the cutout. States: `hero` (y 590, scale 1.0) for sheet A, `low` (x 97, y 720, scale 0.82) from the sheet turn on. Punch-ins 1.06–1.10 on the hook, the forbidden word, the native stamp and the payoff; jump cuts alternate 1.0/1.05 per EDL segment.

## Palette and typography

| Role | Hex |
|---|---|
| Paper | radial `#123a72` → `#0a2a55` → `#061a38` |
| Grid | `rgba(140,190,255,.075)` every 180 px, `.035` every 36 px |
| Walls, doors, line work | `#e8f3ff` (7 px walls, 6 px leaves) |
| Swing arcs, thin lines | `rgba(200,225,255,.55)` dashed 8/8 |
| "To be built" (proposal) | `#bfe0ff` dashed 22/12 |
| Allowed (route, check, hatch) | `#7dffb0` / route `#ffd84d` dashed |
| Forbidden (route, padlock, hatch) | `#ff5468` |
| Stamps | gold `#edc580` |
| Highlighter (active word) | `#ffd84d` |

Fonts (OFL, in the kit): **B612 Mono** for every plan label, stamp and annotation, **Geist** 800 for captions and the CTA question, **Bebas Neue** for the giant words behind the head, **Caveat** 700 for the handwritten notes. Icons: Lucide (`palette`, `scan-search`, `wallet`, `briefcase`, `headset`, `package`, `lock`, `lock-open`, `check`, `user-round`, `bot`, `message-circle`, `message-square`, `pointer`).

## Caption system

"Dimension line": one line of Geist 800 uppercase, white with a 9 px `#061a38` stroke (`paint-order: stroke fill`) and a soft shadow, 1–3 words, font size fitted per group so the line is ≤ 880 px (max 66 px); under it an architectural dimension line (3 px light-blue line between two 4 px end ticks) that grows from the centre (`scaleX 0 → 1`, 0.16 s) when the group appears. Active word: **black on `#ffd84d`** (≈ 13:1), the stroke switched to the same yellow so the pill stays clean. A group is held until the next one when the gap is < 0.7 s, so the line does not blink.

```css
.capw{left:40px;top:1336px;width:1000px;height:150px;z-index:30}
.cl{display:inline-block;font-family:Geist;font-weight:800;font-size:66px;line-height:1.08;text-transform:uppercase;
  color:#fff;-webkit-text-stroke:9px #061a38;paint-order:stroke fill;text-shadow:0 6px 18px rgba(0,0,0,.55)}
.cl .w{display:inline-block;padding:0 .12em;border-radius:.12em}
.cota{position:relative;width:calc(100% - 20px);height:24px;margin:4px auto 0;border-left:4px solid #9cc7ff;border-right:4px solid #9cc7ff}
.cota i{position:absolute;left:0;right:0;top:11px;height:3px;background:#9cc7ff}
```

## Scene grammar

Generic example: a speaker explaining that, inside a company, the content team should use the AI agent only to make art and analyse posts, never the module that analyses the finances, and proposing a web interface with per-module permissions between people and the agent.

| Beat | Sheet | What happens |
|---|---|---|
| Hook | A | Giant hook words behind the cutout from frame 0; title + subtitle; stamp in the first pause. |
| Who | A | Walls and doors drawn on "want"; badges drop on "employees"; tabs pulse on "area"; all doors open on "all the features", the AGENT sign lights. |
| Allowed example | A | Doors close; the content badge's route is drawn; ART and ANALYSIS doors open with green checks on their words. |
| Forbidden | A | Red route to FINANCE; the door slams on the forbidden word, padlock, red hatch, masked values on "the numbers"; punch + shake. |
| The right people | A | One small management badge per spoken person, handwritten note, padlock opens. |
| Proposal | B | Sheet turn on "we could build"; dashed INTERFACE drawn while said; people → interface ⇄ agent; framework name typed; pulses on "talks to"; chat balloons. |
| What already exists | B | Legend box with three checkboxes ticked on their words; round NATIVE stamp in the gap. |
| Distribution | C | Pull back to the company; corridor drawn from the centre; sectors light in sequence; people walk to their rooms; one dot bounced at the locked door. |
| Payoff | C | Giant "ALLOWED" behind the head; plan fades; scanline lifts the speaker out. |
| CTA (4.5 s) | — | Badge reader (see below). |

Rules: room, badge and legend labels are concept text from the speech; badges never carry real names or photos of colleagues; figures inside a forbidden room are always masked; dashed line work and the PRELIMINARY STUDY stamp stay on screen whenever the speech is a proposal; no "illustrative" tags (the project language does that job).

## Transitions and motion vocabulary

- **Draw**: walls and routes with DrawSVG `0% 0% → 0% 100%`, 0.4–0.55 s `power2.inOut`, staggered 0.06 s per wall.
- **Door**: the leaf rotates around its hinge with `svgOrigin` (not `transformOrigin`) — open −90° in 0.35 s `back.out(1.6)`, slam to 0° in 0.18 s `power4.in`.
- **Sheet turn**: sheet A `x → −1080` and sheet B `1080 → 0` in 0.55 s `power3.inOut`, with a light-blue sweep across the frame and the camera moving to `low` with `expo.inOut`.
- **Pull back**: sheet B `scale .8, opacity 0` in 0.24 s, then sheet C `scale 1.12 → 1` in 0.5 s.
- **Pulse**: a yellow dot tweened on `attr:cx` back and forth on the conversation verb.
- **Stamp**: `scale 1.8–2.2 → 1` with a small rotation, 0.16 s `power4.in`, always in a gap.
- **Exit**: a 6 px scanline sweeps up while the camera's `clip-path` closes from the bottom.

## Sound design

| Action | Category | gain_db |
|---|---|---|
| Room turns into a drawing (frame 0) | `scan` | −22 |
| Stamps (gaps) | `stamp` | −20 to −17 |
| Walls, routes, dashed interface | `pen_write` | −27 to −26 |
| Badges drop / tabs | `swipe` / `click` | −22 / −24 |
| Doors open | `door_open`, `success` | −24 to −22 |
| Doors close before the example (gap) | `lock_click` | −18 |
| Forbidden door | `door_slam` + `lock_click` | −20 / −21 |
| Masked numbers | `glitch` | −28 |
| Authorised badges / pulses | `data_beep` | −26 to −25 |
| Padlock opens | `key_turn` | −22 |
| Sheet turn (gap) | `page_turn` + `whoosh` | −15 / −21 |
| Typed framework name | `typewriter` | −24 |
| Chat balloons | `message_received` | −22 |
| Legend checks | `click` (alternate variants and rate) | −23 |
| People walking | `footsteps` | −27 |
| Bounced at the door | `wrong_buzzer` | −27 |
| Payoff word | `success_chime` after the word | −17 |
| CTA: reader, LED, tap, done | `data_beep`, `success`, `click`, `level_up` | −13 / −16 / −11 / −15 |

**Music:** `music:187` (Mountains, hopeful electronic that builds) — reference, mix profile `voice`. One section aligned so the track's kick enters on the proposal ("we could build"): the build-up without drums sits under the problem; ~0.2 s of silence before the closing sentence (same phase on return), CTA +5 dB, 1 s fade. Alternatives: `music:167` (mechanical electronic) for a more technical speech, `music:31` (Dreaming Big, uplifting piano and strings) for a warmer one.

## CTA design inside the style

Badge reader at the end of the plan: the spoken question of the video (from the brief, never put in the speaker's voice) at the top, a large badge with the brand logo and @handle slides in from the left and dips into a reader ("BADGE READER"), the LED turns from red to green, the badge tab reveals "ACCESS GRANTED", then a yellow Follow button is tapped by a pointer and becomes Following. Paid-ad variant: the badge tab reads the product name and the button "LEARN MORE ›".

## Implementation notes

- Grid as stacked `linear-gradient` backgrounds, a double hairline border inset 26 px and a faint title block at the bottom; never an image.
- Each sheet is one absolutely positioned layer with its own inline SVG (`viewBox 0 0 1080 1920`) plus HTML labels positioned on top; walls, doors and routes are separate paths so each can be drawn on its own word. Hatches are SVG `pattern`s (green 45°, red −45°) swapped by setting `fill` on the room rectangle.
- The camera layer is a `<video>` of the cutout (`camera-alpha.webm`) inside `#cam > #cam-punch > #cam-jump`; the giant words are siblings *before* the video inside the same box so the head occludes them. Animate the wrappers, never the video element itself (lint `gsap_animates_clip_element`).
- Initial states (`gsap.set`) outside the timeline: door `svgOrigin`, walls at `drawSVG: '0% 0%'`, sheets B and C at `x: 1080` (see `../gsap-craft.md`).
- All keys come from `rk.finder(words)` and are asserted to be in speech order; sheet turns are placed in the gap before the first word of the new idea (`min(end_of_prev + 0.04, start_next − 0.2)`).

## Pitfalls found in production

- **Real room on frame 0**: starting on the real plate (a hard rectangle edge and a legible wall calendar date) before the "room becomes a drawing" scan looked like a mistake; frame 0 is already the plan with the hook word behind the head.
- **Plan touching the head**: the rooms of sheet A sat too low and touched the hair; walls at y 410–690 and the AGENT sign above the labels.
- **Payoff word clipped by the punch-in**: a giant word placed above the camera box lost the tops of its letters when the box punched in; place it inside the box, behind the cutout.
- **Small labels**: plan labels at 24 px are at the limit of a phone; keep room names ≥ 30 px and handwritten notes ≥ 52 px with a contrast check on the blue.
- **Captions over the shirt print**: the caption block sits on the chest; a printed T-shirt slogan can peek around short groups — acceptable, but never let it read as part of the caption.
- **A dead "E" at the start**: when the first kept word is a conjunction with no silent valley before the next word, keep it; do not amputate it to make the hook "cleaner".

## Variations

- **Building section** instead of a floor plan: floors per access level (public, team, management), an elevator that only stops where the badge allows; for hierarchy rather than departments.
- **Data rooms**: rooms are databases or tables, the doors are API scopes; for engineering audiences talking about tokens, scopes and tenants.
- **White architectural paper**: black ink on warm white with a red pen for the forbidden door; for a lighter, editorial batch next to a dark one.
- **Long form** (`heditor long`): each chapter is a new sheet (A, B, C…), the screen share framed as the sheet's main drawing, the legend box as the chapter recap.
