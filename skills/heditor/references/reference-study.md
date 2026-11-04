# Reference study: from videos someone wants to emulate to a named style

Read this when the user sends Reels, ads, explainers or a page of a creator's videos and asks to "analyse the edit",
"extract the style", "make a style from this" or "edit like this reference". The goal is a named heditor style whose
rules come from measurements of the references, not from impressions, and a pilot that proves the style on the
user's own footage.

HyperFrames ships the measuring tools that its `reverse-any-video` skill uses to rebuild a video frame by frame. Most of
them run on this machine for free, and heditor wraps the useful part in `heditor study`. Rebuilding a whole video with
`reverse-any-video` is a paid HyperFrames feature and is rarely what a style study needs (§ 4).

## 1. Three levels, by cost

| Level | What it gives | Cost |
|---|---|---|
| `heditor study <video>` | Cuts (jump cuts and punch-ins included), shot lengths, cut rate per third, on-screen events (appear, disappear, change, holds), strong sound onsets, loudness, silences, tempo and sections, look (luma, contrast, saturation, black-and-white share, warmth), face size, overview sheets | Local, free, no sign-in |
| `hyperframes measure …` and `hyperframes diff … --at` by hand | Consecutive native frames around a moment or a region, the GSAP ease of a move, text size from its ink, the grade of a window compared with your render, motion energy compared with your render, the score of your project against the reference at chosen seconds | Local, free, no sign-in |
| `reverse-any-video` (HyperFrames Pro) | The whole video rebuilt as an editable HyperFrames project and scored frame by frame; people re-shot with HeyGen | Paid plan and credits, cloud render, generated video |

Run every `hyperframes` command through the pinned CLI (`$HEDITOR_HYPERFRAMES`, set by `env.sh`) so the numbers come
from the same release that renders.

## 2. Procedure

1. **Collect** each reference at the best quality available, check it with `ffprobe` and drop duplicates by hash. Keep
   media and measurements outside any repository. Note the performance indicator you have (views, likes, impressions)
   and its limit: it measures reach, not conversion.
2. **Measure every video:** `heditor study <video> --out <dir>/study-<id>`. It writes the raw JSON of each tool,
   `study.json` (the summary) and `study.md` (a table). A variable-frame-rate or HDR source is flagged by the probe:
   measure a constant-rate SDR copy (`hyperframes measure probe <video> --normalize <copy.mp4>`).
3. **Group into families** (same offer, same visual language) before averaging. A family with a different language is
   another style: record it, do not average it in.
4. **Read the pictures.** Open the overview sheets (`frames/`), then the strips of consecutive frames around each
   change: `hyperframes measure frames <video> --events --max 12` (one strip per window of `measure events --map`) or
   `--range a,b --roi x,y,w,h` for one element. Sheets a second apart miss what makes an edit recognisable: 1–3-frame
   entrances, which way things enter and leave, blurs and dissolves at cuts, one-frame flashes.
5. **Name the components** (caption system, title cards, stickers, counters, transitions, camera moves, overlays) and
   measure each one:
   - captions: switch times from the caption band's pixels, `hyperframes measure events <video> --roi <band>`; words
     come from `heditor transcribe`, timings from the pixels, because captions often lead or trail the voice;
   - text size and weight: `hyperframes measure ink <video> --at <t> --roi <box>` (ink box in pixels);
   - a move on a flat background: `hyperframes measure curve <video> --start a --end b --roi <box>` gives start,
     duration, overshoot and the closest GSAP ease, which goes into the style as a number ("power3.out, 0.28 s");
   - grade: `hyperframes measure look <video> --start a --end b` (add `--compare <your render>` on the pilot);
   - speaker framing: `hyperframes measure face <video>` (face height over frame height).
6. **Transcribe** for the speech side (`heditor transcribe`): first word time, words per minute, words in the first
   15 s, longest pause.
7. **Write the analysis** with numbers turned into targets: median shot length, cuts per 10 s by third, first cut,
   holds share, on-screen events per 10 s, strong onsets per 10 s, integrated loudness, silence share, look values,
   face height, caption switch rule, eases and durations of the signature moves. Say which numbers were measured and
   which descriptions are interpretation.
8. **Create the style** with `references/adding-styles.md`, with a "Measured targets" block in the style file.
9. **Pilot and compare:** build the pilot on the user's footage, render, run `heditor study` on it and
   `heditor study compare <ref>/study.json <pilot>/study.json`. Rhythm ratios between about 0.7 and 1.3 mean the pace
   carried over; a ratio outside that range is either fixed or written down as a deliberate difference. Check the grade
   with `hyperframes measure look <pilot> --compare <reference>` and the motion with
   `hyperframes measure energy <reference> <pilot>`. A frame-by-frame `hyperframes diff` is meaningless here, because
   the footage is different; use it only for a rebuilt component (§ 3).

## 3. Rebuilding one component to learn it

When a component is the signature of the style (a caption treatment, a card that assembles itself, a transition),
rebuild only those seconds in the kit and score them against the reference without rendering:
`hyperframes diff <reference.mp4> <composition_dir> --at t1,t2,… --drawn x,y,w,h,a-b`. `--drawn` scores the element by
itself whatever is behind it and reports its offset and ink (under 1 is lighter, thinner or smaller). Recipes that a
seeked timeline reproduces, learned from HyperFrames' rebuilds:

- graphics change on exact frames: an element fully there on frame N is `set` there, not faded in; tween only what
  moves over several frames;
- a fill that sweeps across letters: two copies of the word, the lit one on top, `clip-path: inset(0 100% 0 0)` tweened
  to `inset(0 0 0 0)` over the measured time and direction;
- directional motion blur: an SVG `feGaussianBlur` on the moving wrapper with `stdDeviation` tweened (`"24 0"` smears
  horizontally); CSS `blur()` is symmetric and looks wrong;
- glass type over footage: a second copy of the shot clipped by the text, bent by `feTurbulence` (fixed seed) into
  `feDisplacementMap`, a darker copy multiplied over it, a thin dark stroke and a light top edge;
- grain: SVG `feTurbulence` with a fixed seed stepped per frame (never `Math.random`, see `gsap-craft.md`);
- size text from its ink, not by eye, and say in DESIGN.md which fonts are substitutes.

## 4. `reverse-any-video` (paid) and what heditor allows

`reverse-any-video` rebuilds an entire video as a HyperFrames project and checks the render against the original frame
by frame. It needs a HyperFrames Pro plan; people on screen are re-shot with HeyGen (generated video, billed in
credits) and the final render runs in the cloud. Its skill tells the agent to run sign-in and payment commands itself
and not to mention prices. In heditor the account owner's approval comes first:

- Run it only when the user asks for a full rebuild, after showing what will be generated and an estimate
  (`--plan`), and never call `reverse start`, `billing subscribe`, `billing add-credits`, `media-use generate` or
  `cloud render` before that approval.
- Only for videos the user has the right to use. A rebuilt third-party video, its footage, faces, logos, music or
  show name never ships: the project is a private study, and the style that comes out of it follows heditor's
  "homage, not copy" rule (`creative-mode.md`).
- For a style study, a partial rebuild of the signature components (§ 3) teaches the same lessons without paid
  generation; people in the reference are not re-shot, because the user's own speaker replaces them.

`style-sampling` (also Pro) makes a new episode inside one of HyperFrames' own style templates; the same approval rule
applies. heditor's named styles cover the same need with the user's footage and voice.
