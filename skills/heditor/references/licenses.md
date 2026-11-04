# Third-party components and licences

| Component | Use | Licence | How it reaches the user |
|---|---|---|---|
| HyperFrames (`hyperframes@0.9.13`, HeyGen) | HTML → MP4 rendering, lint, local reference measurements (`heditor study`) | Apache-2.0 | `npx` at runtime |
| Chrome headless shell | rendering and previews | Chrome terms | downloaded by `hyperframes browser ensure` |
| GSAP 3.14.2 (GreenSock/Webflow) | animation timeline | GSAP standard "no charge" licence (https://gsap.com/standard-license) | downloaded from jsDelivr by setup |
| faster-whisper + CTranslate2 Whisper models | ASR with word timestamps | MIT (models: MIT) | pip + Hugging Face download |
| MediaPipe + BlazeFace short range | face tracking | Apache-2.0 | pip + Google storage download |
| MediaPipe selfie multiclass segmenter, selfie segmenter, Hand Landmarker | speaker matte, hand landmarks (depthkit) | Apache-2.0 | downloaded by setup / on first use from Google storage |
| Depth Anything V2 Small (ONNX export) | relative depth map (depthkit) | Apache-2.0 (the Small model only; Base/Large are non-commercial) | downloaded on first use or by `setup.sh --depth` from Hugging Face |
| ONNX Runtime | depth inference | MIT | pip |
| OpenCV (contrib) | guided filter, optical flow, drawing | Apache-2.0 | pip |
| three.js r181 | 3D objects in layered edits | MIT | downloaded by setup from jsDelivr (with LICENSE) |
| three.js addons r181 (EffectComposer, UnrealBloomPass, BokehPass, OutputPass, RoundedBoxGeometry and their shaders) | bloom, depth of field, rounded bodies (physkit) | MIT | downloaded by setup from jsDelivr |
| GSAP 3.14.2 plugins (SplitText, DrawSVG, MorphSVG, MotionPath, CustomEase, CustomWiggle, CustomBounce, Text, Physics2D, PhysicsProps, ScrambleText, EasePack) | text, SVG and easing effects | GSAP standard "no charge" licence (same as the core) | downloaded by setup from jsDelivr |
| SVGO 4.1.0 | SVG clean-up before animation (`heditor svg`) | MIT | npm, installed by setup in `~/.heditor/node` |
| Rapier 3D (`@dimforge/rapier3d-compat` 0.21.0) | rigid-body physics baked before render (`heditor physics`) | Apache-2.0 | npm, installed by setup in `~/.heditor/node` |
| FFmpeg | cutting, grading, audio, encoding | LGPL/GPL (system build) | system package |
| Playwright (Python) | deterministic frame previews | Apache-2.0 | pip |
| NumPy, Pillow, pytest | processing, images, tests | BSD/MIT-CMU/MIT | pip |
| Fonts from github.com/google/fonts | typography | SIL Open Font License 1.1 | downloaded by setup with OFL.txt files |
| Lucide icons | inline SVG icons | ISC | downloaded on demand |
| Mixkit music and sound effects | soundtrack and SFX | Mixkit Stock Music Free License / Mixkit Sound Effects Free License (https://mixkit.co/license/) | downloaded by setup from Mixkit's CDN to the user's machine; never redistributed in this repository |
| Mixkit stock video | B-roll (`heditor stock`) | Mixkit Stock Video Free License (https://mixkit.co/license/#videoFree), subject to the Mixkit User Terms (no mass download, no redistribution as stock) | one clip per `heditor stock get`, on demand, from Mixkit's CDN into the work dir after the licence is confirmed on the clip page; provenance in `<work>/stock.json` |
| HeyGen CLI (`heygen`, optional) | AI avatar source videos (`heditor heygen`, `heditor avatar`) | HeyGen terms of service; generated videos are billed to and governed by the user's HeyGen account | never installed by setup; installed only when the user accepts it in `heditor heygen connect` (official installer from static.heygen.ai, checksum verified, `~/.local/bin`) |

Optional external tools referenced by some styles (not installed by setup; check the licence before using them in your project and record it in DESIGN.md):

| Tool | Use in styles | Licence |
|---|---|---|
| Robust Video Matting (MobileNetV3, ONNX) | presenter cutout as WebM with alpha | GPL-3.0 |
| Apple Vision person segmentation | presenter cutout on macOS | Apple SDK terms (macOS only) |
| Extra google/fonts families (Bungee, Alfa Slab One, Tilt Neon, Barlow Condensed, IBM Plex Sans Condensed, Pacifico) | style typography | SIL OFL 1.1 (ship the OFL.txt next to the font) |

Your own videos, logos and any extra music/SFX you add are your responsibility. Do not use third-party logos, trademarks, characters or copyrighted music/footage in homage styles.
