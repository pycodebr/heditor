"""Style `teletransporte`: the speaker travels the story. Runs as-is once beats.json and the place clips exist.

Every sentence happens in another place: a still of the real person in that place (`heditor gen persona`) speaks
the exact words of the sentence with lip-sync from his own recorded voice (`heditor gen talk --audio`). Between
places a teleport (white flash, cyan scan wipe, RGB split, whoosh) moves him and a place card stamps where and when
he is. The voice is the master; the clips are muted. Recipe and rules: references/styles/teletransporte.md and
references/generation.md.

    heditor new <work> <video> --style teletransporte
    # prepare.py (BLOCKS; optional ("PAUSE", 0.5, "key") breaths), heditor prepare, heditor words
    # per sentence: a reference still, heditor gen persona, cut gen/audio/sN.wav from voice-master.wav with the
    # sentence times, heditor gen talk --audio; then write beats.json and:
    heditor produce <work> teletransporte 0

beats.json = {"places": [{"at": T, "clip": "gen/s1-talk.mp4", "card": ["APARTAMENTO", "AGORA"],
                          "face_h": 430, "eye_y": 800}, ...],
              "cta": {"question": "line 1|line 2|line 3", "hold": 4.5},   ("|" breaks the question line by line)
              "music": {"main": "music:187", "drop": 0.0, "gain_db": -2}, "map": true, "allowed_numbers": [...]}
  at     [spoken token, after] or seconds of the cut: the place starts there and lasts until the next one; the
         clip must have been generated from the voice cut at that same time (lip-sync frame for frame)
  card   place name and time, from the speech or the scene (spoken numbers only, or allowed_numbers)
  face_h target face height on the 1920 canvas (the build measures the face in every clip and scales and moves
         the clip so all places have the same head size and eye line: the jump reads as the same person)
"""
import html
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.environ.get("HEDITOR_KIT", str(Path.home() / ".heditor/kit")))
import reelkit as rk  # noqa: E402

WORK = Path(__file__).resolve().parent
SEED = 20261103
CYAN = "#7dd3fc"
DEFAULT_MUSIC = "music:187"


def load():
    words_file = WORK / "words-reviewed.json" if (WORK / "words-reviewed.json").exists() else WORK / "words.json"
    words = rk.load_words(words_file)
    edl = json.loads((WORK / "edl.json").read_text())
    return words, round(edl["voice_duration"], 3), edl.get("pauses", [])


def timer(words):
    find = rk.finder(words)

    def at(spec, default=None):
        if spec is None:
            return default
        if isinstance(spec, (int, float)):
            return float(spec)
        try:
            return float(find(rk.plain(str(spec[0])), float(spec[1]) if len(spec) > 1 else 0.0))
        except KeyError:
            raise AssertionError(f"token not found in the speech: {spec}") from None
    return at


def _size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout
    return tuple(map(int, out.strip().split(",")[:2]))


def face_box(path, at_s=1.0):
    """Face box (fractions) on one frame of a clip, MediaPipe; None when no face."""
    import mediapipe as mp
    import numpy as np
    from mediapipe.tasks.python import BaseOptions, vision
    w, h = _size(path)
    sw, sh = 540, max(2, round(h * 540 / w / 2) * 2)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{at_s:.2f}", "-i", str(path), "-frames:v", "1", "-vf",
                          f"scale={sw}:{sh}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    frame = np.frombuffer(raw, np.uint8).reshape(sh, sw, 3)
    det = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=str(rk.MODELS / "blaze_face_short_range.tflite")),
        min_detection_confidence=0.4))
    r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(frame)))
    det.close()
    if not r.detections:
        return None
    b = max(r.detections, key=lambda d: d.categories[0].score).bounding_box
    return {"cx": (b.origin_x + b.width / 2) / sw, "cy": (b.origin_y + b.height / 2) / sh, "h": b.height / sh,
            "eye": (b.origin_y + b.height * 0.38) / sh}


def prepare_clip(src, name):
    """Place clip as a 30 fps CFR 1080x1920 H.264 without audio (the voice is the master)."""
    out = WORK / "composition/assets/tp" / f"{name}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    srcp = (WORK / src).resolve()
    if not out.exists() or out.stat().st_mtime < srcp.stat().st_mtime:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(srcp), "-vf",
                        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
                        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17", str(out)], check=True,
                       timeout=900)
    return out


def last_frame(clip, name):
    out = WORK / "composition/assets/tp" / f"{name}-last.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i", str(clip), "-frames:v", "1", "-q:v", "2",
                    str(out)], check=True, timeout=120)
    return out


CSS = r"""
@font-face{font-family:JBM;src:url('assets/JetBrainsMono-VF.ttf');font-weight:100 900;font-display:block}
#bg{background:#05070b}
.glow,.floor,#horizon,.speed,.conf,#rig,#rig-aura,#border{display:none}
#grain{opacity:.08}
.pl{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;opacity:0}
.pl video,.pl img{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;transform-origin:0 0}
.pl .shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.40) 0%,rgba(0,0,0,0) 22%,
  rgba(0,0,0,0) 54%,rgba(0,0,0,.55) 66%,rgba(0,0,0,.62) 80%,rgba(0,0,0,.35) 100%)}
.scan{position:absolute;left:0;width:1080px;height:8px;top:-20px;background:#fff;opacity:0;z-index:20;
  box-shadow:0 0 18px 6px var(--tp),0 0 60px 18px rgba(125,211,252,.45)}
.card{position:absolute;left:60px;top:276px;z-index:22;opacity:0;padding:12px 22px 12px;border-radius:14px;
  background:rgba(8,12,20,.88);border:2px solid var(--tp);font-family:JBM;color:#f4f8fb;
  box-shadow:0 12px 30px rgba(0,0,0,.45)}
.card b{display:block;font-weight:800;font-size:32px;letter-spacing:.06em}
.card i{display:block;font-style:normal;font-weight:700;font-size:27px;letter-spacing:.1em;color:#bfe9ff;margin-top:2px}
#map{display:flex;gap:9px;align-items:center;margin-top:9px}
#map .d{width:13px;height:13px;border-radius:50%;border:2px solid rgba(255,255,255,.7);background:transparent}
#map .ln{width:14px;height:2px;background:rgba(255,255,255,.4)}
#rgb{position:absolute;inset:0;z-index:19;opacity:0;pointer-events:none;mix-blend-mode:screen;
  background:linear-gradient(90deg,rgba(255,0,80,.35),rgba(0,0,0,0) 30%,rgba(0,0,0,0) 70%,rgba(0,200,255,.35))}
#cta{position:absolute;inset:0;z-index:30;opacity:0}
#cta .q{position:absolute;left:110px;width:860px;top:300px;text-align:center;font:800 64px/1.14 Geist;color:#fff;
  text-wrap:balance;padding:22px 28px;border-radius:26px;background:rgba(5,7,11,.72);border:2px solid var(--tp);
  text-shadow:0 2px 10px rgba(0,0,0,.6)}
#cta .hd{position:absolute;left:0;width:1080px;top:1300px;display:flex;justify-content:center;align-items:center;
  gap:24px;font:800 56px Geist;color:#fff;text-shadow:0 3px 14px rgba(0,0,0,.8)}
.fbtn{position:relative;font:800 40px/1 Geist;color:#05070b;background:#fff;border-radius:40px;padding:18px 0;
  width:300px;text-align:center;overflow:hidden;white-space:nowrap}
.fbtn .fill{position:absolute;inset:0;background:var(--tp);transform:scaleX(0);transform-origin:0 50%}
.fbtn .t{position:relative}.fbtn .t2{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  opacity:0;color:#05070b}
#tap{position:absolute;width:90px;height:90px;margin:-45px 0 0 -45px;border-radius:50%;border:5px solid #fff;background:rgba(255,255,255,.25);
  opacity:0;z-index:31}
"""


def build(track=None, drop_s=0.0):
    rk.setup_assets(WORK)
    rk.prepare_voice(WORK)
    words, voice_end, pauses = load()
    at = timer(words)
    b = json.loads((WORK / "beats.json").read_text())
    places = b["places"]
    starts = [at(p["at"], 0.0) for p in places]
    assert starts == sorted(starts) and starts[0] <= 0.05, "places in speech order, the first one at 0"
    cta = b.get("cta", {})
    hold = float(cta.get("hold", 4.5))
    duration = round(voice_end + hold, 3)
    brand = rk.load_brand(WORK)

    html_pl, js, sound, qa = [], [], [], []

    def sfx(t, cat, gain, ctx, length=None):
        ev = {"time": round(max(0.0, t), 3), "category": cat, "variant": 0, "gain_db": gain, "context": ctx}
        if length:
            ev["length"] = length
        sound.append(ev)

    last_clip, last_tf = None, (1.0, 0.0, 0.0)
    for i, p in enumerate(places):
        t0 = starts[i]
        t1 = starts[i + 1] if i + 1 < len(starts) else voice_end
        clip = prepare_clip(p["clip"], f"p{i}")
        last_clip = clip
        cw, ch = _size(clip)
        box = face_box(clip, min(1.0, max(0.2, (t1 - t0) / 2)))
        target_h, eye_y = float(p.get("face_h", 430)), float(p.get("eye_y", 800))
        if box:
            s = max(1.15, min(1.7, target_h / (box["h"] * 1920)))   # >= 1.15 leaves room to align the eyes
            # a face high in its clip cannot move down (the clip must cover the frame): zoom a little more to bring
            # the eyes down, up to a face 20 % larger than the target
            s_eye = eye_y / (box["eye"] * 1920)
            if s_eye > s:
                s = min(s_eye, 1.35 * target_h / (box["h"] * 1920), 1.7)
            tx = 540 - box["cx"] * 1080 * s
            ty = eye_y - box["eye"] * 1920 * s
            tx = min(0.0, max(1080 - 1080 * s, tx))
            ty = min(0.0, max(1920 - 1920 * s, ty))
        else:
            s, tx, ty = 1.0, 0.0, 0.0
        last_tf = (s, tx, ty)
        head_top = (box["eye"] * 1920 * s + ty - 0.95 * box["h"] * 1920 * s) if box else 600
        qa.append({"place": i, "clip": p["clip"], "face": box, "scale": round(s, 3), "tx": round(tx), "ty": round(ty),
                   "head_top": round((box["eye"] * 1920 * s + ty - 0.95 * box["h"] * 1920 * s) if box else 600)})
        dur = t1 - t0 + (hold if i == len(places) - 1 else 0.4)
        html_pl.append(
            f'<div class="pl" id="pl{i}"><video id="v{i}" class="clip" data-start="{t0:.4f}" '
            f'data-duration="{max(0.2, min(dur, t1 - t0 + 0.4)):.4f}" data-track-index="{i + 1}" src="assets/tp/{clip.name}" '
            f'muted playsinline style="transform:translate({tx:.1f}px,{ty:.1f}px) scale({s:.4f})"></video>'
            f'<div class="shade"></div></div>')
        js.append(f"FT('#pl{i} video',{{scale:{s:.4f}}},{{scale:{s * 1.04:.4f},duration:{max(0.5, t1 - t0):.3f},"
                  f"ease:'none'}},{t0:.3f});")
        if i == 0:
            js.append(f"S('#pl0',{{opacity:1}},0);")
        else:
            # teleport: the cut happens under a white flash (never a wipe across the face: two heads), then a cyan
            # scan line and an RGB split run over the new place as the arrival
            js.append(f"flash({t0:.3f},.9,.16,'#ffffff');")
            js.append(f"S('#pl{i}',{{opacity:1}},{t0:.3f});")
            js.append(f"S('#pl{i - 1}',{{opacity:0}},{t0 + 0.02:.3f});")
            js.append(f"FT('.scan',{{top:-20,opacity:1}},{{top:1930,duration:.42,ease:'power2.in'}},{t0 + 0.04:.3f});")
            js.append(f"S('.scan',{{opacity:0}},{t0 + 0.47:.3f});")
            js.append(f"FT('#rgb',{{opacity:.55,x:-14}},{{opacity:0,x:0,duration:.3,ease:'power2.out'}},{t0:.3f});")
            js.append(f"FT('#pl{i} video',{{filter:'brightness(1.8) saturate(.6)'}},{{filter:'brightness(1) "
                      f"saturate(1)',duration:.35,ease:'power2.out'}},{t0:.3f});")
            js.append(f"shake({t0 + 0.02:.3f},8);")
            sfx(t0 - 0.06, "whoosh", -24, f"teleport to place {i}", 0.6)
            sfx(t0, "glitch", -31, "RGB split", 0.3)
            sfx(t0 + 0.02, "bass_impact", -29, "arrival")
        card = p.get("card")
        if card:
            cid = f"cd{i}"
            dots = ""
            if b.get("map", True):
                dots = '<div id="map">' + "".join(
                    ('<i class="ln"></i>' if k else "") + (
                        f'<i class="d" style="background:{CYAN};border-color:{CYAN};box-shadow:0 0 10px {CYAN}"></i>'
                        if k == i else ('<i class="d" style="background:rgba(255,255,255,.75)"></i>' if k < i
                                        else '<i class="d"></i>'))
                    for k in range(len(places))) + '</div>'
            # the card sits above the head; when the head is too high it moves to the chest, above the captions
            top = 276 if head_top >= 360 else 1060
            html_pl.append(f'<div class="card" id="{cid}" style="top:{top}px;transform:rotate('
                           f'{(-2.5 if i % 2 else 2.0)}deg)">'
                           f'<b>{html.escape(card[0])}</b>' + (f'<i>{html.escape(card[1])}</i>' if len(card) > 1
                                                               else "") + dots + '</div>')
            ct = t0 + (0.32 if i else 0.15)
            js.append(f"FT('#{cid}',{{opacity:0,scale:1.25}},{{opacity:1,scale:1,duration:.18,ease:'power3.out'}},"
                      f"{ct:.3f});")
            js.append(f"TO('#{cid}',{{opacity:0,duration:.2}},{max(ct + 0.6, t1 - 0.25):.3f});")
            sfx(ct, "stamp", -28, f"place card {card[0]}")

    map_html = ""   # the journey map lives inside each place card (no separate element over the head)

    # CTA over the last frame of home
    still = last_frame(last_clip, "home")
    q = cta.get("question", "")
    c0 = voice_end + 0.05
    cta_html = (f'<div id="cta"><img src="assets/tp/{still.name}" style="position:absolute;inset:0;width:1080px;'
                f'height:1920px;object-fit:cover;filter:brightness(.78)"><div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 40%,rgba(0,0,0,.75) 70%,rgba(0,0,0,.6) 100%)"></div>'
                + (f'<div class="q">{"<br>".join(html.escape(x) for x in q.split("|"))}</div>' if q else "")
                + f'<div class="hd"><span>{html.escape(brand["handle"])}</span><div class="fbtn" id="fbtn">'
                  f'<i class="fill"></i><span class="t">{html.escape(brand["follow"])}</span>'
                  f'<span class="t2">✓ {html.escape(brand["following"])}</span></div></div><div id="tap"></div></div>')
    fb = c0 + 1.9
    js += [f"FT('#cta',{{opacity:0}},{{opacity:1,duration:.5}},{c0:.3f});",
           f"FT('#cta .q',{{opacity:0,y:24}},{{opacity:1,y:0,duration:.5}},{c0 + 0.3:.3f});",
           f"FT('#cta .hd',{{opacity:0,y:18}},{{opacity:1,y:0,duration:.45}},{c0 + 0.8:.3f});",
           f"S('#tap',{{left:{540 + 140},top:1340,scale:.3,opacity:0}},0);",
           f"FT('#tap',{{scale:.3,opacity:.9}},{{scale:2.1,opacity:0,duration:.6,ease:'power2.out'}},{fb:.3f});",
           f"TO('#fbtn .fill',{{scaleX:1,duration:.35}},{fb + 0.05:.3f});",
           f"TO('#fbtn .t',{{opacity:0,duration:.15}},{fb + 0.1:.3f});",
           f"TO('#fbtn .t2',{{opacity:1,duration:.2}},{fb + 0.2:.3f});"]
    sfx(c0, "whoosh", -26, "home", 0.6)
    sfx(fb, "mouse_click", -20, "follow tap")
    sfx(fb + 0.25, "success_chime", -26, "following", 0.9)

    caps = rk.captions(words, voice_end, max_words=3, max_chars=18)
    keys = {"voice_end": voice_end, "duration": duration, "seed": SEED,
            "rigStates": {"hero": {"x": 0, "y": 0, "scale": 1}}, "rig": [[0.0, "hero"]]}
    for i, t0 in enumerate(starts):
        keys[f"place_{i}"] = round(t0, 3)
    scenes = "".join(html_pl) + '<div class="scan"></div><div id="rgb"></div>' + map_html + cta_html
    markup = rk.page(title=f"{brand['name']} teletransporte", duration=duration, card_w=1080, card_h=1920,
                     face_origin="50% 40%", videos=[], scenes_html=scenes, css=f":root{{--tp:{CYAN}}}" + CSS,
                     js="".join(js), keys=keys, caps=caps, caption_mode="pill", brand_work=WORK,
                     caption_pill=("#000000", CYAN))
    (WORK / "composition/index.html").write_text(markup)

    mus = b.get("music", {})
    main = track if track and track not in ("teletransporte", "none") else mus.get("main", DEFAULT_MUSIC)
    if isinstance(main, str) and main.startswith("music:"):
        main = rk.music_path(main)
    elif isinstance(main, str) and not os.path.isabs(main):
        main = str((WORK / main).resolve())
    drop = float(drop_s or mus.get("drop", 0.0))
    g = float(mus.get("gain_db", -2))
    music = [{"start": 0.0, "end": voice_end, "mode": "full", "gain_db": g, "track": main, "src": drop,
              "fade_in": 0.3, "fade_out": 0.05},
             {"start": voice_end, "end": duration, "mode": "full", "gain_db": g + 3, "track": main,
              "src": drop + voice_end, "fade_in": 0.05, "fade_out": 1.2}]
    plan = {"style": "teletransporte", "duration": duration, "voice_end": voice_end, "keys": keys, "captions": caps,
            "sound_events": sorted(sound, key=lambda e: e["time"]), "music": music, "mix": "voice",
            "duck_open": [[p["out_start"], p["out_end"]] for p in pauses],
            "allowed_numbers": b.get("allowed_numbers", []), "synthetic_media": True}
    if b.get("max_duration"):
        plan["max_duration"] = b["max_duration"]
    (WORK / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2))
    (WORK / "captions.json").write_text(json.dumps(caps, ensure_ascii=False, indent=2))
    (WORK / "qa").mkdir(exist_ok=True)
    (WORK / "qa/places.json").write_text(json.dumps(qa, indent=1))
    return plan
