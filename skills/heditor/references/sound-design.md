# Sound design

Sound is half of the edit, and the voice is always the protagonist.

## Voice
`rk.prepare_voice` chain: `adeclip` → high-pass 85 Hz → adaptive `afftdn` → -2.5 dB @ 250 Hz (mud) → +2.5 dB @ 3.2 kHz (presence) → de-esser → compressor 3:1 → limiter. Never time-stretch or pitch the speech.

## Mix profiles (`plan["mix"]`, read by `rk.mix` and the tests)

Pick the profile by the kind of delivery, not by taste:

| Profile | When | Music vs voice (median) | Background p95 | Filtered make-up | Presence floor | asr-check |
|---|---|---|---|---|---|---|
| `voice` (default) | organic Reels, class excerpts, dense explanations, `nativo` with music | −21.5 dB | −12 dB | 0 dB | bed may not vanish > 8 s | recommended |
| `presence` | paid ads, creative mode, trailer | −15 dB | −7 dB | +4 dB on `muffled`/`lowpass` | bed may not vanish > 2 s | **required** |

- `plan["mix"] = "presence"` or `{"profile": "presence", <overrides>}`; a dict without `"profile"` overrides the voice
  profile (plans made before 2.6.0 keep working). `rk.mix_targets(plan)` returns the resolved values.
- Why two profiles: a 21.5 dB bed under a dense class explanation is right (louder beds there were rejected for
  covering the speech), but the same level under a paid ad or a creative edit reads as "there is no music" — twice in
  production (a trailer and a creative-mode ad), both fixed only by the presence values.
- **Presence floor** (`test_music_presence`): the bed's presence band (500 Hz–6 kHz, after ducking: what the ear
  hears as "the track" over a voice) is measured in 400 ms windows inside the speech, outside sections declared as
  `silence`. Runs under voice median + floor (−48 dB voice, −38 dB presence) are merged across peeks shorter than
  1.2 s and listed in `balance.music_gaps`; a run longer than the profile's limit fails the test. A quiet intro and a
  16 s muffled underwater section measured −44 to −58 dB (read as "no music"); a bed that read as present sat at
  −28 to −36 dB.
- `balance.long_filtered_sections` lists `muffled`/`lowpass` sections longer than 3 s: a filtered bed loses the band
  the ear tracks over speech; keep them short in ads (a dive, a breath) or the floor fails.

## Mix targets (`rk.mix`, reported in `qa/balance.json`)
- Music ≈ 21.5 dB under the voice in the `voice` profile, ≈ 15 dB in `presence` (median of 400 ms windows with speech).
- Background (music + SFX) ≥ 12 dB under the voice at p95; < 5 % of windows within 10 dB.
- Ducking anticipates speech by ~120 ms and holds ~650 ms, so the bed does not pump between words.
- Multiband ducking: bands above 200 Hz duck fully, bass ducks less (keeps the music present without masking).
- Master: two-pass loudnorm to -14 LUFS; finalize re-limits if the AAC true peak exceeds -1.5 dBTP (bright SFX can overshoot the WAV peak by 3 dB after AAC).
- In the CTA (after the voice) music may rise (`cta_boost_db`, ~5 dB).

## SFX rules
- Every visual action gets a sound: appear (pop, swipe), impact (stamp, bass_impact, trailer_hit, sub_drop), reveal (whoosh, magic_transition, reverse_impact), UI (click, mouse_click, data_beep, notify, message_sent/received), error/success (error_ding, wrong_buzzer, success_chime, level_up), texture (heartbeat, clock_tick, typing_fast, crowd_murmur, water_splash, tape_stop, glitch).
- Place strong impacts in gaps between words or 50–120 ms before the word they emphasise. SFX over words: -20 dB or lower.
- Variety: do not repeat the same sample more than ~3 times in a row; use `variant` and `rate` (0.92–1.1) for variation.
- Typical gains (before the automatic calibration): impacts -11 to -14 dB, whooshes -14 to -18, UI ticks -18 to -30, textures -22 to -30.
- Licensed sounds only: the catalog (Mixkit) or files the user provides with a licence. Synthesised sounds (noise bursts, sine beeps, radio crackle made with numpy) are fine; add them through a `sfx_lib()` function in build.py.
- Optional project-local Earshot synthesis and Openverse search/import are described in `sfx-sources.md`; the existing mixer loads their manifests in `heditor produce` and keeps its voice-first rules. Verify the original licence and attribution for each Openverse file.

## Music
**Profile the track before choosing `src`:** `heditor music <music:ID|file> [out.json]` prints the tempo, energy per
second, a kick/bass bar, breakdowns (≥ 4 s without kick), kick entries and lifts. Put the track's own turns on the
speech turns: section `src = event_s − word_s` (kick entry on the first beat of a montage, a breakdown under a
suspense line with the kick returning on the reveal word, phase kept across a short silence by adding the gap to
`src`). Measured, not listened: say so.

Catalog (`assets/catalog.json`, `music:<id>`; Mixkit Free License):

| id | Title | Mood |
|---|---|---|
| 31 | Dreaming Big | inspiring piano/strings, triumph |
| 33 | Motivating Mornings | motivational, bass/drums/brass |
| 82 | Keeping Fit | chiptune / quirky game groove |
| 126 | Trap Electro Vibes | aggressive drum & bass |
| 167 | Brainiac | mechanical, futuristic electronic |
| 187 | Mountains | uplifting electronic, hopeful build |
| 282 | Sweet September | lo-fi hip hop, calm |
| 293 | Lord Knows | serious trap, focus |
| 369 | Need for Speed | determined trap |
| 568 | Focus on Yourself | tense electronic, technology |
| 597 | Vertigo | tense, stealthy investigation |
| 623 | Deep Urban | hypnotic tech house |
| 677 | Epical Drums 02 | dramatic trailer, escalation |
| 680 | Epical Drums 05 | restless cinematic percussion |
| 686 | Epical Drums 06 | epic trailer, reveal |
| 871 | Fright Night | dramatic suspense, mystery |
| 955 | I Believe 2 | emotional piano/strings, hope |
| 1117 | Proud of You | confident uplifting rock |

The catalog has `drop_s` (first energy jump) and `lift_s` (biggest sustained rise) per track; listen-free choices are approximations, so pick the drop by the energy profile and tell the user nobody listened.

Section design (the emotional arc):
- Hook: full or filtered track, sometimes a hit on frame 0.
- Development: `radio`/`lowpass`/`muffled` versions keep energy without competing with the explanation.
- Before the turn: 0.2–0.4 s of `silence` (with a riser or tape stop), then the drop on the key word.
- Payoff and CTA: full track, crescendo, fade out 1 s.
- In `presence` edits a filtered section is a short colour (a dive, a phone speaker), not a long state; the rhythm
  should keep running under the whole speech.

## Masking check (`heditor asr-check`)
ASR of the final mix against the clean voice: master similarity ≥ 0.90 and not more than 0.03 below the voice, exit 1
otherwise. It lists `MASKED` spans (words the clean voice had and the mix lost, with times): dip the bed only there
(split the music section and give the middle part a lower `gain_db`, keeping `src` continuous) or move the SFX to a
gap. Required in the `presence` profile (finalize reminds you).
- A second track can take over at a mood change (tension → hope), with a 0.5–1 s fade.
