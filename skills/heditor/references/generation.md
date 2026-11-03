# Generated media: the person in new scenarios, new scenes, the clone speaking

Optional. Needs the user's own HeyGen account connected (`heditor heygen status`, see `heygen-avatar.md`); the
stills that do not need the person's identity come from the image generator available to the agent. Nothing in
heditor requires any of this: the named styles that use it (`teletransporte`, `revelacao-ia`, `reconstituicao`,
`tutorial-ilustrado`) say what to do without it.

## What each tool gives

| Need | Tool | Output | Cost (measured, Pro subscription, Nov 2026) |
|---|---|---|---|
| A still of a scene, an object, a reference pose (no real identity) | the agent's image generator | PNG 1024×1536 | subscription of the image model |
| **The person inside that scene** (same pose, clothes, framing, light) | `heditor gen persona` (HeyGen `heygen-image-1`, `identity_remix`) | PNG **2160×3840** | **6 credits per image** |
| A moving shot with its own sound (ambience, effects, generic dialogue) | `heditor gen clip` (HeyGen `heygen-video-1`): `text_to_video`, `image_to_video` (first frame), `reference_to_video` (up to 9 images, 3 videos, 3 audio) | MP4 480p–2K, 5–15 s (30 s for text/image) | ~2 credits for 5 s at 480p (image_to_video); references and 1080p cost more |
| **That still of the person speaking** with lip-sync | `heditor gen talk` (HeyGen Avatar IV, `type: image`) with the cloned voice (`--text`/`--script`) or the person's own recording (`--audio`) | MP4 720p/1080p, or **transparent WebM** with `--alpha` | ~0.55–0.6 credit per second at 1080p, measured (about 35 per minute) |
| The studio digital twin speaking a script | `heditor avatar` (see `heygen-avatar.md`) | MP4 | 31–48 credits per minute |

`heditor gen status` prints the credits left and what each kind of job really cost in this account so far
(`~/.heditor/heygen-usage.json`, before/after credits of every job). Estimates use that history first. HeyGen bills
the real job; a failed or cancelled job is not billed.

## Workflow

1. **Plan on paper**: one scene per sentence (or per turn), what the person does there, what is added (objects,
   people, light), and the shot type. Count the jobs and their cost with the table above; show the user.
2. **Reference stills** with the image generator: the scene with a *stand-in* of the same build and style (beard,
   glasses, shirt) in the pose and framing you want, looking into the lens, chest-up for talking shots. Keep the
   stand-in close to the real person (hair, beard, glasses) so the identity swap has little to change.
3. **Identity**: 3–5 identity images give a better likeness than one selfie (a wide-angle selfie widens the face).
   Set them once in `~/.heditor/brand.json`: `"heygen": {"identity": ["<look id or image path>", ...]}`. Look ids
   are downloaded once as their preview images.
4. **One cheap test** before a batch: one `persona` image, or one `clip` at 480p and 5 s. Look at it with vision
   (likeness: moles, beard density, glasses; light on the face vs the room; hands; text or logos).
5. **Batch**: `heditor gen persona <work> s1-office --ref gen/refs/r1.png --yes` (one per scene; run them in
   parallel only after the test), then `heditor gen talk <work> s1-office-talk --image gen/s1-office-1.png --audio
   gen/audio/s1.wav --yes` for the speaking shots, or `heditor gen clip ... --image gen/s1-office-1.png` for a
   silent moving shot.
6. **Edit** in a named style: the generated files are media like any other (`composition/assets/`), the voice is
   the master; provenance stays in `<work>/gen/gen.json` and goes into DESIGN.md.

## Prompts that work

- **identity_remix** follows the reference image's pose, clothes, background and framing; it beautifies (slimmer
  face, fuller beard, smoother skin). Use 3+ identity images and a reference stand-in that already has the person's
  build. It does not take a text prompt: everything comes from the reference still.
- **image_to_video** tends to over-move the head (90° turns with a frozen torso). Ask for small motion: "stays in
  place, breathes, keeps eye contact, one small nod, slow push-in, no speech, ambient only". Use the first and last
  second only as B-roll if the middle drifts.
- **Avatar IV talk**: `expressiveness: medium` and a `motion_prompt` with one gesture tied to a word read natural;
  `high` exaggerates eyes and smiles. Lip-sync is good from a chest-up still looking into the lens; a profile or a
  hand over the mouth breaks it.
- **Adding things and people to a scene**: put them in the reference still (the image generator), then swap only the
  person's identity; for motion, `reference_to_video` with the scene still and object/person stills as references
  keeps them consistent across shots. Never add a real third person's face without consent.
- **Transparent speaker** (`--alpha`): composite the speaking person over any generated scene, a 3D layer or a
  screen recording, with a soft contact shadow and a light wrap of the scene colour on the edges.

## Truth, consent and disclosure

- Only the account owner's identity (or people who consented, recorded in DESIGN.md).
- The clone says only approved words: a script is shown to the user and approved before `--yes`; with `--audio`, the
  person's own recording is lip-synced as it is (no words added).
- Generated scenes of real events carry a visible "illustrative reconstruction" label (style `reconstituicao`);
  fantasy scenes of the person are revealed as AI in the same video (style `revelacao-ia`).
- Mark the post as AI-generated where the platform or the law asks for it (Instagram "AI info" label).
- Never a real brand, logo or identifiable third party in a generated still; review every image with vision.
