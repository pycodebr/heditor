---
style: revelacao-ia
name: Revelação IA (the fantasy and the reveal)
family: fixed-style
best_for: showing what AI video tools can do with the speaker himself: an opening that looks real (a luxury car, a stage, a famous place, people around him) and then the reveal of the real recording and how it was made; creator and AI-education content; 20–45 s
reference: technique study of a Brazilian creator's Reel (a "my new supercar" opening generated from a selfie in his own car, people and a luxury watch added, then the reveal "it's my car, made with AI"), Nov 2026
---
# Revelação IA (the fantasy and the reveal)

Two acts. **The fantasy**: the speaker talks to the camera in a place or situation he is not in (a supercar, a stage
in a stadium, a penthouse, a rocket launch), with things and people added around him, and says the lines of a
believable flex or a dramatic claim. **The reveal**: a hard cut (or a glitch that peels the fantasy off) to the real
recording in the same framing ("it's my car… this was made with AI"), a before/after split of the same moment, and
the method in one sentence, ending with a keyword CTA. The fun is the contrast; the value is showing the tool honestly.

**Status:** documented from the reference (Nov 2026); pilot pending.

## Two ways to build the fantasy

1. **From the real recording** (closest to the reference): the speaker records the whole thing in his real place;
   key frames of the fantasy act become reference stills where the image generator turns the place into the fantasy
   and adds objects and people; `heditor gen persona` keeps his identity in those stills; `heditor gen talk --audio`
   makes each still speak his own recorded line (lip-sync), so the voice is real and identical in both acts.
2. **From the clone only**: a script the speaker approved, `heditor gen talk --text` on fantasy stills, the reveal
   on his real look or a real recording.

Added people are generic generated people (never a real third person, never sexualised), added objects have no real
brand logos (the reference used a real carmaker's badge; we do not).

## Signature moves

1. **Frame 0 in the fantasy**, selfie framing, natural vlog light; casual captions (white caps, active word on a
   yellow box) so it feels native.
2. **Escalation**: every line adds one thing (the car → the people → the watch → the price), 1–2 s each, with jump
   cuts and a slight handheld drift.
3. **The tell**: a beat where the speaker almost laughs ("cara…") or a micro-glitch on the fantasy.
4. **The reveal**: hard cut to the real place, same framing; then a **split** (top fantasy / bottom real, or a wipe
   that the speaker's hand "pushes") on the same sentence; a small label "FEITO COM IA" on the fantasy half.
5. **The method in one sentence** with 2–3 tool chips; keyword CTA.

## Rules

- The reveal is mandatory and comes in the same video (no deception left standing); the post is labelled AI.
- No fake claims of wealth, results or endorsements left unrevealed; no real brands, celebrities or third parties.
- The speaker approves every line the clone says (`--text`); with `--audio` his own words are used as recorded.

## Layout, palette, sound

Native vlog look in the fantasy (no graphics except captions), clean editorial in the reveal (split line `#ffffff`
3 px, labels in Geist 800 caps on dark pills). Sound: the fantasy has its world ambience (generated clips' own sound,
low) and a confident beat; a `record_scratch` or `tape_stop` on the reveal, then voice only with a soft bed.

## Variations

- **Three fantasies** (car, stage, space) before one reveal.
- **Reverse**: the real recording first, "watch me turn this into…", then the transformation as a wipe.
- **Viewer's choice**: "comment where you want to see me next" (feeds the next video).
