# Adding a named style

When an edit made in creative mode (or a variation) is approved by the user, turn it into a reusable named style so it can be requested by name later ("edit this in style X"). A style derived from reference videos starts with `references/reference-study.md`: its measured numbers go into the style file as a "Measured targets" block (median shot length, cuts per 10 s by third, on-screen events and strong sound onsets per 10 s, loudness, look values, eases and durations of the signature moves), and a pilot is accepted only after `heditor study compare` puts its rhythm next to the reference's.

1. **Name it** with a short, memorable slug in the user's vocabulary (e.g. `aeroporto`, `game`, `podcast`). Ask the user if they want a specific name; otherwise propose one.
2. **Write `references/styles/<slug>.md`** with the same structure as the existing styles:
   - frontmatter: `style`, `name`, `family: fixed-style`, `best_for`, `reference` (who produced it and when),
   - identity, when to use / not, signature moves, frame and layout (px), palette and typography, caption system with active-word contrast spec, scene grammar, transitions and motion, sound design (SFX map + `music:<id>` options + section plan), CTA design, implementation notes and snippets, pitfalls found in production, variations (so it does not become a template).
   - Generic wording only: no private names, quotes, paths or screenshots of private material.
3. **Add a row** to `references/styles/INDEX.md`, to the style table and the `description` list in `SKILL.md`, and to the README style tables (Portuguese and English sections; update the style count).
4. **Add its long-form style pack** to `scripts/reelkit/stylepacks.py` (`STYLES[<slug>]`: family, palette, fonts from the kit, caption tokens with an active word ≥ 4.5:1, frame, transition, chapter card, lower third, camera grade, SFX, music, `long_notes`) and a row to the style table in `references/long-form.md`. `test_formats.py` fails when a style file has no pack.
5. **Keep the reference implementation** (DESIGN.md + build.py) in the user's own project archive; if it can be shared publicly, strip private content and put it under `templates/styles/<slug>/`.
6. **Record lessons** in `references/troubleshooting.md` when the production revealed a new pitfall.

A style is a language, not a template: when reusing it, rebuild the scenes from the new speech, choose music for the new emotional arc and vary at least two of camera treatment, palette accents and transitions.
