#!/usr/bin/env python3
"""Download and prepare everything heditor needs into HEDITOR_HOME (default ~/.heditor).

Usage: fetch_assets.py [--no-audio] [--whisper small,medium]
Idempotent: files that already exist with the right size are skipped.
- Fonts (OFL) from github.com/google/fonts, GSAP from jsDelivr, Lucide licence, MediaPipe face model.
- Music and SFX from Mixkit's official CDN as listed in assets/catalog.json (Mixkit Free License).
  They are downloaded to the user's machine and never redistributed by this repository.
- A procedural film-grain texture and a neutral logo placeholder.
- Optional: pre-download faster-whisper models.
"""
import argparse
import concurrent.futures
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

HOME = Path(os.environ.get("HEDITOR_HOME", "~/.heditor")).expanduser()
ASSETS = HOME / "assets"
SKILL = Path(__file__).resolve().parents[1]
CATALOG = json.loads((SKILL / "assets/catalog.json").read_text())
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
FONTS = {
    "Anton-Regular.ttf": GF + "anton/Anton-Regular.ttf",
    "VT323-Regular.ttf": GF + "vt323/VT323-Regular.ttf",
    "Geist-VF.ttf": GF + "geist/Geist%5Bwght%5D.ttf",
    "Inter-VF.ttf": GF + "inter/Inter%5Bopsz,wght%5D.ttf",
    "JetBrainsMono-VF.ttf": GF + "jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
    "IBMPlexMono-Regular.ttf": GF + "ibmplexmono/IBMPlexMono-Regular.ttf",
    "IBMPlexMono-Bold.ttf": GF + "ibmplexmono/IBMPlexMono-Bold.ttf",
    "PressStart2P-Regular.ttf": GF + "pressstart2p/PressStart2P-Regular.ttf",
    "PlayfairDisplay-VF.ttf": GF + "playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",
    "PlayfairDisplay-Italic-VF.ttf": GF + "playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf",
    "Fraunces-VF.ttf": GF + "fraunces/Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf",
    "BebasNeue-Regular.ttf": GF + "bebasneue/BebasNeue-Regular.ttf",
    "DMSerifDisplay-Regular.ttf": GF + "dmserifdisplay/DMSerifDisplay-Regular.ttf",
    "Caveat-VF.ttf": GF + "caveat/Caveat%5Bwght%5D.ttf",
    "B612Mono-Regular.ttf": GF + "b612mono/B612Mono-Regular.ttf",
    "B612Mono-Bold.ttf": GF + "b612mono/B612Mono-Bold.ttf",
    "Fredoka-VF.ttf": GF + "fredoka/Fredoka%5Bwdth,wght%5D.ttf",
    "InstrumentSerif-Regular.ttf": GF + "instrumentserif/InstrumentSerif-Regular.ttf",
    "InstrumentSerif-Italic.ttf": GF + "instrumentserif/InstrumentSerif-Italic.ttf",
}
FONT_LICENSE_DIRS = ["anton", "vt323", "geist", "inter", "jetbrainsmono", "ibmplexmono", "pressstart2p", "playfairdisplay",
                     "fraunces", "bebasneue", "dmserifdisplay", "caveat", "b612mono", "fredoka", "instrumentserif"]
OTHER = {
    "js/gsap.min.js": "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js",
    "licenses/Lucide-LICENSE.txt": "https://raw.githubusercontent.com/lucide-icons/lucide/main/LICENSE",
    "models/blaze_face_short_range.tflite":
        "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite",
    # three.js r181 (MIT) for real 3D objects in layered edits; three.module imports ./three.core
    "js/three.module.min.js": "https://cdn.jsdelivr.net/npm/three@0.181.2/build/three.module.min.js",
    "js/three.core.min.js": "https://cdn.jsdelivr.net/npm/three@0.181.2/build/three.core.min.js",
    "licenses/three-LICENSE.txt": "https://raw.githubusercontent.com/mrdoob/three.js/r181/LICENSE",
    **{f"js/three-addons/{rel}": f"https://cdn.jsdelivr.net/npm/three@0.181.2/examples/jsm/{rel}" for rel in (
        # post-processing (bloom, depth of field, output) for physkit and other 3D layers; they import "three",
        # resolved by the importmap that physkit writes into the page
        "postprocessing/EffectComposer.js", "postprocessing/Pass.js", "postprocessing/RenderPass.js",
        "postprocessing/ShaderPass.js", "postprocessing/MaskPass.js", "postprocessing/UnrealBloomPass.js",
        "postprocessing/OutputPass.js", "postprocessing/BokehPass.js", "shaders/CopyShader.js",
        "shaders/LuminosityHighPassShader.js", "shaders/OutputShader.js", "shaders/BokehShader.js",
        "geometries/RoundedBoxGeometry.js")},
    # GSAP plugins (all free since 3.13, same standard licence as the core); loaded offline by rk.page(plugins=...)
    **{f"js/gsap/{p}.min.js": f"https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/{p}.min.js" for p in (
        "SplitText", "DrawSVGPlugin", "MorphSVGPlugin", "MotionPathPlugin", "CustomEase", "CustomWiggle",
        "CustomBounce", "TextPlugin", "Physics2DPlugin", "PhysicsPropsPlugin", "ScrambleTextPlugin", "EasePack")},
    # depthkit (layered edits): person matte and hand landmarks
    "models/selfie_multiclass_256x256.tflite":
        "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/"
        "selfie_multiclass_256x256.tflite",
    "models/hand_landmarker.task":
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task",
}
# Depth Anything V2 Small (Apache-2.0, ~99 MB): only with --depth; otherwise depthkit downloads it on first use.
DEPTH = {"models/depth_anything_v2_small.onnx":
         "https://huggingface.co/onnx-community/depth-anything-v2-small/resolve/main/onnx/model.onnx"}
UA = {"User-Agent": "heditor-setup/1.0 (+https://github.com/pycodebr/heditor)"}


def get(url, dest, tries=4):
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        return "skip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r, tmp.open("wb") as f:
                while block := r.read(1 << 20):
                    f.write(block)
            if tmp.stat().st_size == 0:
                raise IOError("empty file")
            tmp.replace(dest)
            return "ok"
        except Exception as exc:  # noqa: BLE001
            if attempt == tries - 1:
                tmp.unlink(missing_ok=True)
                return f"fail: {type(exc).__name__}: {exc}"
            time.sleep(2 * (attempt + 1))


def grain():
    path = ASSETS / "grain.png"
    if path.exists():
        return
    import numpy as np
    from PIL import Image
    rng = np.random.default_rng(7)
    noise = rng.normal(128, 42, (512, 512)).clip(0, 255).astype("uint8")
    Image.fromarray(noise, "L").convert("RGB").save(path)


def logo_placeholder():
    path = ASSETS / "logo-placeholder.png"
    if path.exists():
        return
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((16, 16, 496, 496), fill=(237, 197, 128, 255))
    d.ellipse((150, 150, 362, 362), fill=(8, 22, 38, 255))
    im.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-audio", action="store_true", help="skip Mixkit music and SFX")
    ap.add_argument("--whisper", default="", help="comma-separated faster-whisper models to pre-download (e.g. small,medium)")
    ap.add_argument("--depth", action="store_true", help="also pre-download the depth model (~99 MB) used by depthkit")
    args = ap.parse_args()
    ASSETS.mkdir(parents=True, exist_ok=True)
    jobs = [(url, ASSETS / "fonts" / name) for name, url in FONTS.items()]
    jobs += [(GF + d + "/OFL.txt", ASSETS / "licenses" / f"OFL-{d}.txt") for d in FONT_LICENSE_DIRS]
    jobs += [(url, ASSETS / rel) for rel, url in OTHER.items()]
    if args.depth:
        jobs += [(url, ASSETS / rel) for rel, url in DEPTH.items()]
    if not args.no_audio:
        for name, items in CATALOG["sfx"].items():
            for it in items:
                jobs.append((it["url"], ASSETS / "sfx" / f"{name}-{it['id']}{Path(it['url']).suffix}"))
        for m in CATALOG["music"]:
            jobs.append((m["url"], ASSETS / "music" / f"music-{m['id']}.mp3"))
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for (url, dest), res in zip(jobs, pool.map(lambda j: get(*j), jobs)):
            results[str(dest.relative_to(ASSETS))] = res
    grain()
    logo_placeholder()
    (ASSETS / "icons").mkdir(exist_ok=True)
    fails = {k: v for k, v in results.items() if v.startswith("fail")}
    for model in [m for m in args.whisper.split(",") if m]:
        try:
            from faster_whisper import WhisperModel
            WhisperModel(model, device="cpu", compute_type="int8")
            results[f"whisper:{model}"] = "ok"
        except Exception as exc:  # noqa: BLE001
            fails[f"whisper:{model}"] = f"fail: {exc}"
    (HOME / "assets-status.json").write_text(json.dumps({"total": len(results), "failed": fails}, indent=1))
    ok = sum(1 for v in results.values() if v in ("ok", "skip"))
    print(f"assets: {ok}/{len(results)} ready in {ASSETS}")
    for k, v in fails.items():
        print(f"  FAILED {k}: {v}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
