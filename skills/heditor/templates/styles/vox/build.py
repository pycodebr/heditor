"""Style `vox`: an explainer documentary in monochrome. Runs as-is once beats.json exists; make it yours by rewriting
beats.json from the speech (format below) and generating the stills for the story.

The speaker's voice narrates a short documentary. The picture is a sequence of black-and-white "reconstructed archive"
stills (people only from behind, film grain, vignette) and paper collages (cut-out objects with contact shadows,
pencil sketches, a torn paper card), joined by blur dissolves that grow on the meaning ("silence", "barely") and
held by a slow push-in. The captions are the typography: an italic serif revealed word by word on the subject's dark
coat, and the key word of each line set huge in the same serif, entering with a blur. White chalk line art is drawn on
its words over the stills (icons, arrows, a network, rays), a hand-drawn ellipse closes around the phrase that
matters, the speaker appears once as a black-and-white photograph taped to the paper, and the CTA is a museum label
under a gilded frame. Recipe and rules: references/styles/vox.md.

    heditor new <work> <video> --style vox             # scaffolds this file and DESIGN.md
    # prepare.py (BLOCKS, CROP; ("PAUSE", 0.5, "key") adds a breath between chapters); heditor prepare; heditor words
    # generate the stills into <work>/gen/ (one constant style sentence, see the style file), write beats.json, then:
    heditor produce <work> vox 0                       # music: beats.json "music" or the style default

beats.json = {"scenes": [...], "big": [...], "doodles": [...], "marks": [...], "focus": [...], "cta": {...},
              "music": {...}, "allowed_numbers": [...], "max_duration": 75}
  times   every "at"/"until" is [spoken token, after_seconds] (token without punctuation, accents must match) or a
          number of seconds of the cut; a scene lasts until the next one
  scenes  [{"at": T, "kind": "photo", "src": "gen/x.png", "kb": [1.04, 1.12], "focus": [0.5, 0.55],
            "drift": [0, -30], "enter": "blur|cut|white", "cap": {"y": 1180, "ink": "light", "align": "center",
            "scrim": true}},
           {"at": T, "kind": "paper", "src": "gen/paper.png", "enter": "blur|cut|white",
            "cap": {"y": 420, "ink": "dark"},
            "items": [{"at": T, "img": "gen/obj.png", "x": 540, "y": 900, "w": 640, "rot": -2, "enter": "drop"},
                      {"at": T, "card": ["30", "de abril"], "x": 780, "y": 600, "w": 300, "rot": 4},
                      {"at": T, "plate": true, "x": 540, "y": 900, "w": 600, "rot": -2.5}]}]
          photo = a still in cover, slow push-in (kb = scale from/to, focus = transform origin, drift = px from/to);
          paper = a paper background with items: "img" = an object shot on off-white paper (blended with multiply,
          so its paper disappears), "card" = torn paper card with serif lines (spoken words only), "plate" = the
          speaker as a black-and-white photograph taped to the paper (the only time the camera is seen)
          cap = where the captions of this scene sit (block centre y, light ink on stills, dark ink on paper)
  big     [[token, after], ...]   words set huge in the caption block (the key word of the line), blur-in
  doodles [{"at": T, "until": T, "kind": "icon", "name": "message-square", "x": 300, "y": 700, "size": 150,
            "rot": -6} | {"kind": "arrow", "from": [x, y], "to": [x, y], "bend": 0.3}
           | {"kind": "network", "rect": [x, y, w, h], "n": 60, "until_full": T} | {"kind": "rays", "x":, "y":, "r": 160, "arc": [200, 340]}]
          white chalk line art on stills (ink on paper), drawn on its word
  marks   [{"at": T, "until": T, "kind": "circle|underline", "words": [[token, after], [token, after]]}]
          a hand-drawn ellipse (or underline) around the caption words from the first to the last token
  keep    [[[token, after], [token, after]], ...]  phrases kept in one caption group (e.g. the one a mark circles)
  focus   [{"at": T, "blur": 12, "dur": 0.5}]   rack defocus of the current still (meaning: "barely", "silence")
  cta     {"frame": "gen/frame.png", "photo": "gen/x.png", "paper": "gen/paper.png", "opening": "auto" | [x, y, w, h],
           "label": "Subject", "sub": "(dates as spoken or allowed)", "hold": 5.0}
  music   {"main": "music:955" | "path/to/track.mp3", "drop": 0.0, "gain_db": -1}
Every number on screen must be spoken (or listed in allowed_numbers with the reason in DESIGN.md).
"""
import html
import json
import math
import os
import random
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.environ.get("HEDITOR_KIT", str(Path.home() / ".heditor/kit")))
import reelkit as rk  # noqa: E402

WORK = Path(__file__).resolve().parent
SEED = 20261102
CTA_HOLD = 5.0
DEFAULT_MUSIC = "music:955"          # emotional piano and strings; a soft reflective piano fits the style best
CAP_W = 900
SMALL_PX = 66
BIG_MAX, BIG_MIN, BIG_W = 230, 120, 860
INK = {"light": "#f4f1ea", "dark": "#171512"}
FONT_IT = Path.home() / ".heditor/assets/fonts/InstrumentSerif-Italic.ttf"
CAM_VF = ("format=gray,eq=contrast=1.18:brightness=0.03:gamma=0.95,format=rgb24,"
          "colorchannelmixer=rr=1.0:gg=0.96:bb=0.88,noise=alls=9:allf=t,format=yuv420p")


# ---------------------------------------------------------------- data

def load():
    words_file = WORK / "words-reviewed.json" if (WORK / "words-reviewed.json").exists() else WORK / "words.json"
    words = rk.load_words(words_file)
    edl = json.loads((WORK / "edl.json").read_text())
    return words, round(edl["voice_duration"], 3), edl.get("pauses", [])


def load_beats(words, voice_end):
    path = WORK / "beats.json"
    if path.exists():
        return json.loads(path.read_text())
    # runnable baseline (never a delivery): the paper background, the longest words set big, no stills
    longest = sorted((w for w in words if len(rk.plain(w["word"])) >= 7), key=lambda w: -len(rk.plain(w["word"])))
    big = [[rk.plain(w["word"]), round(w["start"] - 0.05, 2)] for w in longest[:4]]
    return {"scenes": [{"at": 0, "kind": "paper", "src": "", "cap": {"y": 900, "ink": "dark"}, "items": []}],
            "big": big}


def timer(words):
    find = rk.finder(words)

    def at(spec, default=None):
        if spec is None:
            return default
        if isinstance(spec, (int, float)):
            return float(spec)
        token, after = rk.plain(str(spec[0])), float(spec[1]) if len(spec) > 1 else 0.0
        try:
            return float(find(token, after))
        except KeyError:
            raise AssertionError(f"token not found in the speech: {spec}") from None
    return at


def word_index(words, at, spec):
    t = at(spec)
    for i, w in enumerate(words):
        if abs(w["start"] - t) < 1e-6:
            return i
    raise AssertionError(f"no word at {spec}")


# ---------------------------------------------------------------- captions

def _font(size):
    from PIL import ImageFont
    return ImageFont.truetype(str(FONT_IT), size)


def text_w(text, size):
    return _font(size).getlength(text)


def big_size(text):
    size = BIG_MAX
    while size > BIG_MIN and text_w(text, size) > BIG_W:
        size -= 4
    return size


def cap_box(c, words, big_idx, y, align="center"):
    """Estimated box of a caption group on the stage (flex wrap simulated with the real TTF), for marks."""
    lines, cur, cur_w = [], [], 0.0
    gap = 2 * 0.12 * SMALL_PX
    for i in c["idx"]:
        if i in big_idx:
            if cur:
                lines.append(("s", cur_w))
            lines.append(("b", text_w(words[i]["shown"].strip(".,;:"), big_size(words[i]["shown"])) + gap,
                          big_size(words[i]["shown"])))
            cur, cur_w = [], 0.0
            continue
        w = text_w(words[i]["shown"], SMALL_PX) + gap
        if cur and cur_w + w > CAP_W:
            lines.append(("s", cur_w))
            cur, cur_w = [], 0.0
        cur.append(i)
        cur_w += w
    if cur:
        lines.append(("s", cur_w))
    h = sum(SMALL_PX * 1.08 if ln[0] == "s" else ln[2] * 0.98 for ln in lines)
    w = max(ln[1] for ln in lines)
    x0 = 90 + {"center": (CAP_W - w) / 2, "left": 0, "right": CAP_W - w}[align]
    return x0, y - h / 2, x0 + w, y + h / 2


FUNCTION_WORDS = {"a", "o", "as", "os", "e", "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas", "um",
                  "uma", "que", "com", "pra", "para", "por", "se", "é", "está", "foi", "ser", "the", "of", "to", "and", "in", "on", "at", "for"}


CLAUSE_START = {"que", "e", "mas", "porque", "quando", "com", "da", "do", "de", "no", "na", "pelo", "pela", "pra",
                "para", "em", "that", "and", "but", "with", "when"}


def _phrases(words, big_idx, keep):
    """Split the speech into phrases: punctuation, gaps > 0.7 s, kept spans."""
    starts = {a for a, _ in keep}
    inside = {i for a, b in keep for i in range(a, b)}
    out, cur = [], []
    for i, w in enumerate(words):
        if cur and (w["start"] - words[cur[-1]]["end"] > 0.7 or i in starts):
            out.append(cur)
            cur = []
        cur.append(i)
        if i in inside:
            continue
        if w["shown"].strip()[-1:] in ".?!;:,":
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out, inside


def _split(idx, words, big_idx, inside, max_words, max_chars):
    """Split a long phrase in balanced chunks; never end a chunk on a function word, never split a kept span."""
    def size(ch):
        return sum(len(words[j]["shown"]) + 1 for j in ch if j not in big_idx)
    if (len(idx) <= max_words and size(idx) <= max_chars) or all(i in inside for i in idx[:-1]):
        return [idx]
    best = None
    for k in range(1, len(idx)):
        left, right = idx[:k], idx[k:]
        if idx[k - 1] in inside or rk.plain(words[idx[k - 1]]["word"]) in FUNCTION_WORDS:
            continue
        cost = abs(size(left) - size(right)) + (0 if len(left) <= max_words else 50)
        if rk.plain(words[idx[k]]["word"]) in CLAUSE_START:
            cost -= 10
        if best is None or cost < best[0]:
            best = (cost, k)
    if best is None:
        k = len(idx) // 2
    else:
        k = best[1]
    return (_split(idx[:k], words, big_idx, inside, max_words, max_chars)
            + _split(idx[k:], words, big_idx, inside, max_words, max_chars))


def caption_groups(words, big_idx, voice_end, keep=(), max_words=6, max_chars=34, cuts=(), big_hold=1.3):
    """Caption groups = phrases of the speech (punctuation, gaps, big words), long ones split in balanced chunks.
    keep = [(first_index, last_index), ...] spans that stay in one group (a phrase that gets a hand-drawn mark)."""
    phrases, inside = _phrases(words, big_idx, keep)
    groups = []
    for ph in phrases:
        groups += _split(ph, words, big_idx, inside, max_words, max_chars)
    # a big word must stay on screen long enough to be read: when its group ends less than big_hold seconds after
    # it, the next phrase joins the same block (never across a scene cut, never into a kept span)
    starts_keep = {a for a, _ in keep}
    merged, g = [], 0
    while g < len(groups):
        cur = list(groups[g])
        while g + 1 < len(groups):
            bigs = [i for i in cur if i in big_idx]
            nxt = groups[g + 1]
            if not bigs or nxt[0] in starts_keep or any(i in big_idx for i in nxt):
                break
            if words[nxt[0]]["start"] - words[bigs[-1]]["start"] >= big_hold:
                break
            if any(words[cur[-1]]["end"] <= c <= words[nxt[0]]["start"] + 1e-6 for c in cuts):
                break
            small = sum(len(words[j]["shown"]) + 1 for j in cur + nxt if j not in big_idx)
            if small > 64:
                break
            cur += nxt
            g += 1
        merged.append(cur)
        g += 1
    groups = merged
    caps = []
    for g, idx in enumerate(groups):
        ws = [words[i] for i in idx]
        start = ws[0]["start"]
        nxt = words[groups[g + 1][0]]["start"] if g + 1 < len(groups) else voice_end
        end = max(ws[-1]["end"] + 0.12, min(nxt, ws[-1]["end"] + 1.4))
        end = min(end, nxt, voice_end)
        caps.append({"id": f"cap-{g}", "start": round(start, 3), "end": round(end, 3),
                     "text": " ".join(w["shown"] for w in ws), "idx": idx,
                     "words": [{"word": w["word"], "shown": w["shown"], "start": w["start"], "end": w["end"]}
                               for w in ws]})
    return caps


# ---------------------------------------------------------------- hand-drawn geometry (seeded)

def rough_path(points, rng, jitter=3.0):
    pts = [(x + rng.uniform(-jitter, jitter), y + rng.uniform(-jitter, jitter)) for x, y in points]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts) - 1, 2):
        c, e = pts[i], pts[i + 1] if i + 1 < len(pts) else pts[i]
        d += f" Q{c[0]:.1f},{c[1]:.1f} {e[0]:.1f},{e[1]:.1f}"
    return d


def arrow_paths(a, b, bend, rng):
    (x0, y0), (x1, y1) = a, b
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    cx, cy = mx - dy * bend, my + dx * bend
    body = (f"M{x0:.1f},{y0:.1f} Q{cx + rng.uniform(-6, 6):.1f},{cy + rng.uniform(-6, 6):.1f} "
            f"{x1:.1f},{y1:.1f}")
    ang = math.atan2(y1 - cy, x1 - cx)
    head = []
    for s in (-1, 1):
        a2 = ang + math.pi - s * 0.5
        head.append(f"M{x1:.1f},{y1:.1f} L{x1 + 38 * math.cos(a2):.1f},{y1 + 38 * math.sin(a2):.1f}")
    return [body] + head


def network(rect, n, rng):
    x, y, w, h = rect
    pts = []
    tries = 0
    while len(pts) < n and tries < n * 60:
        tries += 1
        p = (x + rng.uniform(0, w), y + rng.uniform(0, h))
        ex, ey = (p[0] - (x + w / 2)) / (w / 2), (p[1] - (y + h / 2)) / (h / 2)
        if ex * ex + ey * ey <= 1 and all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > 34 ** 2 for q in pts):
            pts.append(p)
    cx, cy = x + w / 2, y + h / 2
    pts.sort(key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2 + rng.uniform(0, 900))
    links = []
    for i, p in enumerate(pts[1:], 1):
        j = min(range(i), key=lambda k: (p[0] - pts[k][0]) ** 2 + (p[1] - pts[k][1]) ** 2)
        links.append((j, i))
    return pts, links


def rays(x, y, r, rng, n=12, arc=(0, 360)):
    out = []
    a0, a1 = math.radians(arc[0]), math.radians(arc[1])
    full = abs(arc[1] - arc[0]) >= 359
    for k in range(n):
        f = k / n if full else k / max(1, n - 1)
        a = a0 + (a1 - a0) * f + rng.uniform(-0.06, 0.06)
        r0, r1 = r * rng.uniform(0.62, 0.72), r * rng.uniform(0.95, 1.12)
        out.append(f"M{x + r0 * math.cos(a):.1f},{y + r0 * math.sin(a):.1f} "
                   f"L{x + r1 * math.cos(a):.1f},{y + r1 * math.sin(a):.1f}")
    return out


def torn_clip(rng, n=14):
    pts = []
    for k in range(n):
        pts.append(f"{k * 100 / (n - 1):.1f}% {rng.uniform(0, 3.5):.1f}%")
    for k in range(n):
        pts.append(f"{100 - rng.uniform(0, 3.5):.1f}% {k * 100 / (n - 1):.1f}%")
    for k in range(n):
        pts.append(f"{100 - k * 100 / (n - 1):.1f}% {100 - rng.uniform(0, 3.5):.1f}%")
    for k in range(n):
        pts.append(f"{rng.uniform(0, 3.5):.1f}% {100 - k * 100 / (n - 1):.1f}%")
    return "polygon(" + ",".join(pts) + ")"


# ---------------------------------------------------------------- media

def still(src, name):
    """Cover still for the 1080x1920 stage (JPEG at the used size)."""
    from PIL import Image
    out = WORK / "composition/assets/vox" / f"{name}.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    srcp = WORK / src
    if not out.exists() or out.stat().st_mtime < srcp.stat().st_mtime:
        im = Image.open(srcp).convert("RGB")
        s = max(1080 / im.width, 1920 / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        im.save(out, quality=90)
    return f"vox/{out.name}", s_of(srcp)


def s_of(path):
    from PIL import Image
    with Image.open(path) as im:
        return max(1080 / im.width, 1920 / im.height), im.width, im.height


def object_img(src, name, width):
    """Object shot on plain paper, prepared for `mix-blend-mode: multiply` on the paper background: greyscale,
    divided by a smooth fit of its own paper (so that paper becomes pure white and disappears in the blend) while the
    object and its contact shadow keep their tones. No cut-out edge, no halo, the paper texture shows through."""
    import numpy as np
    from PIL import Image
    out = WORK / "composition/assets/vox" / f"{name}.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    srcp = WORK / src
    if not out.exists() or out.stat().st_mtime < srcp.stat().st_mtime:
        im = Image.open(srcp).convert("L")
        s = width / im.width
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        a = np.asarray(im).astype(np.float64)
        h, w = a.shape
        border = np.concatenate([a[:8].ravel(), a[-8:].ravel(), a[:, :8].ravel(), a[:, -8:].ravel()])
        med = float(np.median(border))
        yy, xx = np.mgrid[0:h, 0:w]
        pick = (np.abs(a - med) < 12)
        pick[::3, ::3] &= True
        ys, xs = yy[pick][::7] / h, xx[pick][::7] / w
        A = np.stack([np.ones_like(xs), xs, ys, xs * xs, ys * ys, xs * ys], axis=1)
        coef, *_ = np.linalg.lstsq(A, a[pick][::7], rcond=None)
        X, Y = xx / w, yy / h
        fit = coef[0] + coef[1] * X + coef[2] * Y + coef[3] * X * X + coef[4] * Y * Y + coef[5] * X * Y
        norm = np.clip(a / np.maximum(fit, 1) * 255.0, 0, 255)
        norm[norm > 247] = 255
        norm = 28 + norm * (255 - 28) / 255          # printed blacks: a modern glossy black reads as pasted on
        Image.fromarray(norm.astype(np.uint8)).convert("RGB").save(out, quality=92)
    return f"vox/{out.name}"


def frame_crop(src, opening=None, margin=40):
    """Crop a generated frame photo to the frame (+ its shadow), punch its empty opening and feather the crop, so it
    sits on the paper with `darken` and the photo shows through the opening. The opening is found by flood fill
    from the centre of the frame (the generated opening is flat white); pass [x, y, w, h] to force it.
    Returns (url, (x, y, w, h) of the crop in source px, opening (x, y, w, h) relative to the crop)."""
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
    srcp = WORK / src
    im = Image.open(srcp).convert("RGB")
    rgb = np.asarray(im).astype(np.int32)
    wall = rgb[im.height // 2, 8]
    diff = np.abs(rgb - wall).sum(axis=2)
    ys, xs = np.nonzero(diff[::4, ::4] > 60)
    ys, xs = ys * 4, xs * 4
    x0, y0 = max(0, xs.min() - margin), max(0, ys.min() - margin)
    x1, y1 = min(im.width, xs.max() + margin), min(im.height, ys.max() + margin)
    gray = np.asarray(im.convert("L"))
    white = (gray >= 238).astype(np.uint8)
    if opening is None or opening == "auto":
        cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
        n, lab, stats, _ = cv2.connectedComponentsWithStats(white, connectivity=4)
        k = lab[cy, cx]
        assert k, "frame_crop: the centre of the frame is not white; pass cta.opening"
        ox, oy, ow, oh = (int(v) for v in stats[k][:4])
        hole = lab == k
    else:
        ox, oy, ow, oh = opening
        hole = np.zeros(gray.shape, bool)
        hole[oy:oy + oh, ox:ox + ow] = True
    out = WORK / "composition/assets/vox/frame.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    crop = im.crop((x0, y0, x1, y1)).convert("RGBA")
    mask = Image.new("L", crop.size, 0)
    ImageDraw.Draw(mask).rectangle((margin // 2, margin // 2, crop.width - margin // 2, crop.height - margin // 2),
                                   fill=255)
    mask = np.asarray(mask.filter(ImageFilter.GaussianBlur(margin / 3))).copy()
    hole_c = cv2.dilate(hole[y0:y1, x0:x1].astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    mask[hole_c] = 0
    crop.putalpha(Image.fromarray(mask))
    crop.save(out)
    return "vox/frame.png", (x0, y0, x1 - x0, y1 - y0), (ox - x0, oy - y0, ow, oh)


# ---------------------------------------------------------------- page

CSS = r"""
@font-face{font-family:IS;src:url('assets/InstrumentSerif-Italic.ttf');font-display:block}
@font-face{font-family:ISR;src:url('assets/InstrumentSerif-Regular.ttf');font-display:block}
@font-face{font-family:Geist;src:url('assets/Geist-VF.ttf');font-weight:100 900;font-display:block}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden;background:#0b0b0b}
#stage{position:relative;width:1080px;height:1920px;overflow:hidden;background:#0b0b0b}
#world{position:absolute;inset:0}
.sc{position:absolute;inset:0;opacity:0;overflow:hidden;will-change:opacity,filter}
.sc .ph{position:absolute;left:0;top:0;transform-origin:50% 55%;will-change:transform}
.sc .paper{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover}
.sc .tone{position:absolute;inset:0;pointer-events:none}
.scrim{position:absolute;left:-60px;width:1200px;height:520px;border-radius:50%;
  background:radial-gradient(closest-side,rgba(0,0,0,.52),rgba(0,0,0,.30) 55%,rgba(0,0,0,0));pointer-events:none}
.item{position:absolute;transform-origin:50% 50%;opacity:0}
.item img{display:block;width:100%}
.item.obj{mix-blend-mode:multiply}
.card{background:#f3efe6;color:#171512;padding:30px 26px 46px;text-align:center;
  box-shadow:0 18px 30px rgba(0,0,0,.22),0 2px 4px rgba(0,0,0,.18)}
.card b{display:block;font:400 150px/0.9 ISR;letter-spacing:-2px}
.card i{display:block;font:400 54px/1.1 IS;margin-top:6px}
.plate{background:#f1ebdf;padding:22px 22px 70px;box-shadow:0 22px 40px rgba(0,0,0,.28),0 2px 5px rgba(0,0,0,.2)}
.plate .pp{position:relative;overflow:hidden;background:#222}
.plate video{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover}
.plate .tape{position:absolute;width:150px;height:46px;background:rgba(236,230,214,.78);
  box-shadow:0 1px 2px rgba(0,0,0,.12)}
.plate .t1{left:-40px;top:-14px;transform:rotate(-34deg)}.plate .t2{right:-40px;top:-14px;transform:rotate(32deg)}
.vc{position:absolute;left:90px;width:900px;display:flex;flex-wrap:wrap;justify-content:center;align-items:baseline;
  transform:translateY(-50%);z-index:30}
.vc.al-left{justify-content:flex-start}.vc.al-right{justify-content:flex-end}
.vc .w{font:400 66px/1.08 IS;color:var(--ink);opacity:0;display:inline-block;white-space:nowrap;
  margin:0 .12em;text-shadow:var(--shadow)}
.vc .w.big{flex-basis:100%;text-align:center;line-height:.9;letter-spacing:-.01em;margin:.02em 0 .06em}
.vc.al-left .w.big{text-align:left}.vc.al-right .w.big{text-align:right}
svg.dd{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible;z-index:25;pointer-events:none}
svg.dd path,svg.dd line,svg.dd circle,svg.dd rect,svg.dd polyline,svg.dd ellipse{fill:none;stroke-linecap:round;
  stroke-linejoin:round}
svg [pathLength]{stroke-dasharray:1 2;stroke-dashoffset:1}
svg.dd [pathLength]{opacity:0}
#museum{position:absolute;inset:0;opacity:0;z-index:40}
#museum .paper{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}
#museum .mph{position:absolute;object-fit:cover;filter:grayscale(1) contrast(1.05)}
#museum .frm{position:absolute;left:0;top:0;mix-blend-mode:darken;filter:saturate(.7)}
#placard{position:absolute;left:90px;width:900px;text-align:center;color:#171512}
#placard .lb{font:400 84px/1 IS}
#placard .sb{font:400 56px/1.2 ISR;margin-top:10px;color:#2a2722}
#placard .rule{width:260px;height:2px;background:#171512;opacity:.55;margin:30px auto 30px}
#placard .hd{display:flex;align-items:center;justify-content:center;gap:26px}
#placard .hd span{font:400 60px/1 IS}
.fbtn{position:relative;font:600 38px/1 Geist;color:#171512;border:3px solid #171512;border-radius:44px;
  padding:16px 0;overflow:hidden;width:330px;text-align:center;white-space:nowrap}
.fbtn .fill{position:absolute;inset:0;background:#171512;transform:scaleX(0);transform-origin:0 50%}
.fbtn .t{position:relative}.fbtn .t2{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  color:#f6f3ec;opacity:0}
#tap{position:absolute;width:90px;height:90px;margin:-45px 0 0 -45px;border-radius:50%;border:4px solid #171512;
  opacity:0;z-index:45}
#lines{position:absolute;inset:0;z-index:60;pointer-events:none;opacity:.5;
  background:repeating-linear-gradient(90deg,rgba(255,255,255,.035) 0 1px,rgba(0,0,0,0) 1px 4px)}
#vig{position:absolute;inset:0;z-index:61;pointer-events:none;
  background:radial-gradient(ellipse 78% 62% at 50% 50%,rgba(0,0,0,0) 55%,rgba(0,0,0,.55) 100%)}
#grain{position:absolute;inset:-60px;z-index:62;pointer-events:none;background:url(assets/grain.png);opacity:.16;
  mix-blend-mode:overlay}
#wht{position:absolute;inset:0;background:#f1efea;opacity:0;z-index:58;pointer-events:none}
"""


def page(duration, voice_end, scenes_html, caps_html, museum_html, js, keys):
    return f"""<!doctype html><html lang="pt"><head><meta charset="utf-8"><title>vox</title>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<main id="stage" data-composition-id="main" data-start="0" data-duration="{duration:.4f}" data-width="1080" data-height="1920" data-fps="30">
<div id="world">{scenes_html}</div>
<div id="wht"></div>
{caps_html}
{museum_html}
<div id="lines"></div><div id="vig"></div><div id="grain"></div>
<audio id="master" class="clip" data-start="0" data-duration="{duration:.4f}" data-track-index="100" src="assets/master.wav" data-volume="1"></audio>
</main>
<script>window.K={json.dumps(keys, ensure_ascii=False)};</script>
<script>{rk.BASE_JS}{js}
window.__timelines=window.__timelines||{{}};window.__timelines.main=tl;</script>
</body></html>"""


# ---------------------------------------------------------------- build

def build(track=None, drop_s=0.0):
    rk.setup_assets(WORK)
    a = WORK / "composition/assets"
    for f in ("InstrumentSerif-Italic.ttf", "InstrumentSerif-Regular.ttf"):
        src = Path.home() / ".heditor/assets/fonts" / f
        if src.exists() and not (a / f).exists():
            (a / f).write_bytes(src.read_bytes())
    rk.prepare_voice(WORK)
    words, voice_end, pauses = load()
    at = timer(words)
    b = load_beats(words, voice_end)
    rng = random.Random(SEED)
    cta = b.get("cta", {})
    hold = float(cta.get("hold", CTA_HOLD))
    duration = round(voice_end + hold, 3)

    # scenes ---------------------------------------------------------
    scenes = b["scenes"]
    starts = [at(s["at"], 0.0) for s in scenes]
    assert starts == sorted(starts), "scenes must be in speech order"
    needs_cam = any(it.get("plate") for s in scenes for it in s.get("items", []))
    cam = None
    if needs_cam:
        rk.prepare_camera(WORK, width=720)
        cam = rk.styled_camera(WORK, "vox", CAM_VF)
    sc_html, sc_js, sound = [], [], []

    def sfx(t, cat, gain, ctx, length=None, variant=0):
        ev = {"time": round(max(0.0, t), 3), "category": cat, "variant": variant, "gain_db": gain, "context": ctx}
        if length:
            ev["length"] = length
        sound.append(ev)

    scene_meta = []
    for i, s in enumerate(scenes):
        t0 = starts[i]
        t1 = starts[i + 1] if i + 1 < len(starts) else voice_end + 0.2
        cap = {"y": 1180, "ink": "light", "align": "center", "scrim": s.get("kind") == "photo"}
        cap.update(s.get("cap", {}))
        scene_meta.append({"t0": t0, "t1": t1, "cap": cap, "kind": s["kind"]})
        inner = []
        if s["kind"] == "photo":
            url, (sc, iw, ih) = still(s["src"], f"s{i}")
            w, h = round(iw * sc), round(ih * sc)
            fx, fy = s.get("focus", [0.5, 0.55])
            inner.append(f'<img class="ph" id="ph{i}" src="assets/{url}" style="width:{w}px;height:{h}px;'
                         f'left:{(1080 - w) / 2:.0f}px;top:{(1920 - h) / 2:.0f}px;transform-origin:{fx * 100:.0f}% '
                         f'{fy * 100:.0f}%">')
            inner.append(f'<div class="tone" style="background:#efe4d0;mix-blend-mode:multiply;'
                         f'opacity:{s.get("tone", 0.5)}"></div>')
            if cap.get("scrim"):
                inner.append(f'<div class="scrim" style="top:{cap["y"] - 260}px"></div>')
            k0, k1 = s.get("kb", [1.04, 1.12])
            d0, d1 = s.get("drift", [0, 0])
            l0, l1 = s.get("lift", [0, 0])
            life = t1 - t0 + 0.9
            sc_js.append(f"FT('#ph{i}',{{scale:{k0},x:{d0},y:{l0}}},{{scale:{k1},x:{d1},y:{l1},duration:{life:.3f},"
                         f"ease:'none'}},"
                         f"{max(0.0, t0 - 0.45):.3f});")
        else:
            if s.get("src"):
                url, _ = still(s["src"], f"s{i}")
                inner.append(f'<img class="paper" src="assets/{url}">')
            else:
                inner.append('<div class="paper" style="background:#e8e5df"></div>')
            for j, it in enumerate(s.get("items", [])):
                iid = f"it{i}-{j}"
                ti = at(it.get("at"), t0)
                x, y, w, rot = it.get("x", 540), it.get("y", 900), it.get("w", 600), it.get("rot", 0)
                if it.get("img"):
                    url = object_img(it["img"], iid, w)
                    body = f'<img src="assets/{url}">'
                    cls = "item obj"
                    sfx(ti, "page_turn", -27, f"cut-out lands: {it['img']}")
                elif it.get("card"):
                    lines = it["card"]
                    body = f"<b>{html.escape(lines[0])}</b>" + "".join(f"<i>{html.escape(x)}</i>" for x in lines[1:])
                    cls = "item card"
                    sfx(ti, "page_turn", -26, "paper card")
                elif it.get("plate"):
                    ph = round(w * 1.25)
                    body = (f'<div class="pp" style="height:{ph}px"><video id="cam" class="clip" data-start="0" '
                            f'data-duration="{voice_end:.4f}" data-track-index="0" src="assets/{cam}" muted '
                            f'playsinline></video></div><i class="tape t1"></i><i class="tape t2"></i>')
                    cls = "item plate"
                    sfx(ti, "camera_shutter", -27, "the speaker's photograph")
                else:
                    continue
                style = f"left:{x - w / 2:.0f}px;top:{y:.0f}px;width:{w}px;transform:translateY(-50%) rotate({rot}deg)"
                if it.get("card"):
                    style += f";clip-path:{torn_clip(rng)}"
                inner.append(f'<div class="{cls}" id="{iid}" style="{style}">{body}</div>')
                enter = it.get("enter", "drop")
                if enter == "drop":
                    sc_js.append(f"FT('#{iid}',{{opacity:0,y:-60,rotation:{rot + 5}}},{{opacity:1,y:0,rotation:{rot},"
                                 f"duration:.5,ease:'back.out(1.5)'}},{ti:.3f});")
                else:
                    sc_js.append(f"FT('#{iid}',{{opacity:0}},{{opacity:1,duration:.4}},{ti:.3f});")
                sc_js.append(f"TO('#{iid}',{{y:-12,duration:{max(0.5, t1 - ti):.3f},ease:'none'}},{ti + 0.5:.3f});")
        sc_html.append(f'<div class="sc" id="sc{i}">{"".join(inner)}</div>')
        enter = s.get("enter", "blur" if i else "cut")
        if i == 0 or enter == "cut":
            sc_js.append(f"S('#sc{i}',{{opacity:1}},{t0:.3f});")
            if i:
                sc_js.append(f"S('#sc{i - 1}',{{opacity:0}},{t0:.3f});")
        elif enter == "white":
            sc_js.append(f"FT('#wht',{{opacity:0}},{{opacity:1,duration:.32,ease:'power1.in'}},{t0 - 0.32:.3f});")
            sc_js.append(f"S('#sc{i - 1}',{{opacity:0}},{t0:.3f});S('#sc{i}',{{opacity:1}},{t0:.3f});")
            sc_js.append(f"TO('#wht',{{opacity:0,duration:.6,ease:'power1.out'}},{t0:.3f});")
            sfx(t0 - 0.3, "whoosh", -33, "fade through white", 0.7, variant=i % 3)
        else:  # blur dissolve: the old still loses focus while the new one comes into it
            sc_js.append(f"TO('#sc{i - 1}',{{filter:'blur(22px)',opacity:0,duration:.55,ease:'power1.in'}},"
                         f"{t0 - 0.3:.3f});")
            sc_js.append(f"FT('#sc{i}',{{opacity:0,filter:'blur(24px)'}},{{opacity:1,filter:'blur(0px)',duration:.6,"
                         f"ease:'power2.out'}},{t0 - 0.2:.3f});")
            sfx(t0 - 0.3, "whoosh", -32, "blur dissolve", 0.8, variant=i % 3)

    # rack defocus on meaning
    for f in b.get("focus", []):
        t = at(f["at"])
        i = max(k for k, st in enumerate(starts) if st <= t + 1e-6)
        sc_js.append(f"TO('#sc{i}',{{filter:'blur({f.get('blur', 12)}px)',duration:{f.get('dur', 0.5)},"
                     f"ease:'power1.inOut'}},{t:.3f});")

    # captions ---------------------------------------------------------
    big_idx = {word_index(words, at, spec) for spec in b.get("big", [])}
    keep = [tuple(word_index(words, at, spec) for spec in span) for span in b.get("keep", [])]
    caps = caption_groups(words, big_idx, voice_end, keep, cuts=starts[1:])
    cap_html, cap_js = [], []
    for c in caps:
        sm = next(m for m in reversed(scene_meta) if m["t0"] <= c["start"] + 1e-6) if scene_meta else \
            {"cap": {"y": 1180, "ink": "light", "align": "center"}}
        cp = sm["cap"]
        ink = INK[cp.get("ink", "light")]
        shadow = ("0 2px 16px rgba(0,0,0,.75),0 0 3px rgba(0,0,0,.5)" if cp.get("ink", "light") == "light"
                  else "none")
        spans = []
        for j, i in enumerate(c["idx"]):
            w = words[i]
            if i in big_idx:
                spans.append(f'<span id="{c["id"]}-w{j}" class="w big" style="font-size:{big_size(w["shown"])}px">'
                             f'{html.escape(w["shown"].strip(".,;:"))}</span>')
            else:
                spans.append(f'<span id="{c["id"]}-w{j}" class="w">{html.escape(w["shown"])}</span>')
        cap_html.append(f'<div id="{c["id"]}" class="vc al-{cp.get("align", "center")}" style="top:{cp["y"]}px;'
                        f'--ink:{ink};--shadow:{shadow}">{"".join(spans)}</div>')
        for j, i in enumerate(c["idx"]):
            w = words[i]
            t = max(0.0, w["start"] - 0.03)
            if i in big_idx:
                cap_js.append(f"FT('#{c['id']}-w{j}',{{opacity:0,filter:'blur(16px)',scale:1.07}},{{opacity:1,"
                              f"filter:'blur(0px)',scale:1,duration:.42,ease:'power2.out'}},{t:.3f});")
            else:
                cap_js.append(f"FT('#{c['id']}-w{j}',{{opacity:0,filter:'blur(7px)',y:8}},{{opacity:1,"
                              f"filter:'blur(0px)',y:0,duration:.2,ease:'power1.out'}},{t:.3f});")
        cap_js.append(f"TO('#{c['id']}',{{opacity:0,filter:'blur(8px)',duration:.18}},{max(c['start'], c['end'] - 0.16):.3f});")

    # doodles and marks ------------------------------------------------
    dd_html, dd_js = [], []
    ink_at = []
    for m in scene_meta:
        ink_at.append((m["t0"], INK["dark"] if m["cap"].get("ink") == "dark" else INK["light"]))

    def ink_for(t):
        col = INK["light"]
        for t0, c in ink_at:
            if t0 <= t + 1e-6:
                col = c
        return col

    for n, d in enumerate(b.get("doodles", [])):
        t0 = at(d["at"])
        t1 = at(d.get("until"), t0 + 2.5)
        col = ink_for(t0)
        did = f"dd{n}"
        kind = d["kind"]
        paths = []
        if kind == "icon":
            rk.ensure_icons([d["name"]])
            svg = rk.icon(d["name"], cls="ic")
            size, x, y, rot = d.get("size", 150), d.get("x", 540), d.get("y", 800), d.get("rot", 0)
            inner = svg[svg.index(">") + 1: svg.rindex("</svg>")]
            inner = re.sub(r"<(path|circle|rect|line|polyline|ellipse)\b", r'<\1 pathLength="1"', inner)
            dd_html.append(f'<svg class="dd" id="{did}" viewBox="0 0 1080 1920"><g class="rough" '
                           f'transform="translate({x - size / 2},'
                           f'{y - size / 2}) rotate({rot},{size / 2},{size / 2}) scale({size / 24})" '
                           f'stroke="{col}" stroke-width="1.7">{inner}</g>'
                           f'<g transform="translate({x - size / 2 + 3},{y - size / 2 + 2}) rotate({rot},{size / 2},'
                           f'{size / 2}) scale({size / 24})" stroke="{col}" stroke-width="1.1" opacity=".35" class="rough">{inner}'
                           f'</g></svg>')
            dd_js.append(f"rough('#{did}',.45);draw('#{did}',{t0:.3f},.7);")
            sfx(t0, "pen_write", -30, f"chalk icon {d['name']}", 0.6)
        elif kind in ("arrow", "rays"):
            if kind == "arrow":
                paths = arrow_paths(d["from"], d["to"], d.get("bend", 0.25), rng)
            else:
                paths = rays(d["x"], d["y"], d.get("r", 150), rng, d.get("n", 12), d.get("arc", (0, 360)))
            body = "".join(f'<path pathLength="1" d="{p}" stroke="{col}" stroke-width="7"/>' for p in paths)
            ghost = "".join(f'<path pathLength="1" d="{p}" stroke="{col}" stroke-width="3" opacity=".35" '
                            f'transform="translate(3,2)"/>' for p in paths)
            dd_html.append(f'<svg class="dd" id="{did}" viewBox="0 0 1080 1920">{ghost}{body}</svg>')
            dd_js.append(f"draw('#{did}',{t0:.3f},{d.get('dur', 0.6)});")
            sfx(t0, "pen_write", -29, f"chalk {kind}", 0.6)
        elif kind == "network":
            pts, links = network(d["rect"], d.get("n", 60), rng)
            full = at(d.get("until_full"), t0 + 2.4)
            body = []
            for k, (px, py) in enumerate(pts):
                tk = t0 + (full - t0) * math.sqrt(k / max(1, len(pts) - 1))
                body.append(f'<circle id="{did}-p{k}" cx="{px:.1f}" cy="{py:.1f}" r="6" fill="{col}" '
                            f'style="fill:{col};opacity:0"/>')
                dd_js.append(f"FT('#{did}-p{k}',{{opacity:0,scale:2.4,transformOrigin:'50% 50%'}},{{opacity:1,"
                             f"scale:1,duration:.25}},{tk:.3f});")
            for k, (i0, i1) in enumerate(links):
                (x0, y0), (x1, y1) = pts[i0], pts[i1]
                tk = t0 + (full - t0) * math.sqrt(i1 / max(1, len(pts) - 1))
                body.insert(0, f'<path pathLength="1" id="{did}-l{k}" d="M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}" '
                               f'stroke="{col}" stroke-width="2.6" opacity=".8"/>')
                dd_js.append(f"drawOne('#{did}-l{k}',{tk:.3f},.3);")
            dd_html.append(f'<svg class="dd" id="{did}" viewBox="0 0 1080 1920">{"".join(body)}</svg>')
            sfx(t0, "data_beep", -33, "network starts", 0.3)
        dd_js.append(f"TO('#{did}',{{opacity:0,duration:.3}},{t1:.3f});")

    for n, mk in enumerate(b.get("marks", [])):
        t0, t1 = at(mk["at"]), at(mk.get("until"), voice_end)
        first = word_index(words, at, mk["words"][0])
        cap = next(c for c in caps if first in c["idx"])
        cp = next(m for m in reversed(scene_meta) if m["t0"] <= cap["start"] + 1e-6)["cap"]
        x0, y0, x1, y1 = cap_box(cap, words, big_idx, cp["y"], cp.get("align", "center"))
        kind = mk.get("kind", "circle")
        pts = []
        if kind == "underline":
            for k in range(13):
                pts.append((x0 + (x1 - x0) * k / 12, y1 + 6 + 5 * math.sin(k * 1.7) + rng.uniform(-2, 2)))
        else:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            rx, ry = min(510.0, (x1 - x0) / 2 + 90), (y1 - y0) / 2 + 62
            a0, turn = math.pi * 1.05, math.pi * 2.1
            for k in range(65):
                ang = a0 + turn * k / 64
                j = 1 + rng.uniform(-0.015, 0.015) + 0.04 * math.sin(k / 64 * math.pi)
                pts.append((cx + rx * j * math.cos(ang), cy + ry * j * math.sin(ang) - 14 * k / 64))
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        col = INK[cp.get("ink", "light")]
        dd_html.append(f'<svg class="dd" id="mk{n}" viewBox="0 0 1080 1920"><path class="dr" id="mk{n}-p" '
                       f'pathLength="1" d="{d}" stroke="{col}" stroke-width="{mk.get("width", 8)}"/></svg>')
        dd_js.append(f"S('#mk{n}-p',{{opacity:1}},{t0:.3f});TO('#mk{n}-p',{{strokeDashoffset:0,"
                     f"duration:{mk.get('dur', 0.65)},ease:'power2.out'}},{t0:.3f});")
        dd_js.append(f"TO('#mk{n}',{{opacity:0,duration:.2}},{min(t1, cap['end'] - 0.16):.3f});")
        sfx(t0, "pen_write", -27, f"hand-drawn {kind}", 0.7)

    # CTA: museum label --------------------------------------------------
    museum_html, cta_js = "", []
    if cta.get("frame"):
        furl, (fx0, fy0, fw0, fh0), opening = frame_crop(cta["frame"], cta.get("opening"))
        k = float(cta.get("frame_w", 700)) / fw0
        left, top = (1080 - fw0 * k) / 2, float(cta.get("frame_top", 250))
        ox, oy, ow, oh = opening
        bx, by, bw, bh = left + ox * k - 10, top + oy * k - 10, ow * k + 20, oh * k + 20
        purl, _ = still(cta["photo"], "frame-photo") if cta.get("photo") else (None, None)
        brand = rk.load_brand(WORK)
        lab_y = top + fh0 * k + 34
        museum_html = (
            f'<div id="museum">'
            + (f'<img class="paper" src="assets/{still(cta["paper"], "museum-paper")[0]}">' if cta.get("paper")
               else '<div class="paper" style="background:#e8e5df"></div>')
            + f'<div id="mgrp" style="position:absolute;inset:0;transform-origin:540px {top + fh0 * k / 2:.0f}px">'
            + (f'<img class="mph" src="assets/{purl}" style="left:{bx:.0f}px;top:{by:.0f}px;width:{bw:.0f}px;'
               f'height:{bh:.0f}px">' if purl else "")
            + f'<img class="frm" id="frm" src="assets/{furl}" style="width:{fw0 * k:.0f}px;height:{fh0 * k:.0f}px;'
              f'left:{left:.0f}px;top:{top:.0f}px"></div>'
            + f'<div id="placard" style="top:{lab_y:.0f}px"><div class="lb">{html.escape(cta.get("label", ""))}</div>'
            + (f'<div class="sb">{html.escape(cta["sub"])}</div>' if cta.get("sub") else "")
            + f'<div class="rule"></div><div class="hd"><span>{html.escape(brand["handle"])}</span>'
              f'<div class="fbtn" id="fbtn"><i class="fill"></i><span class="t">{html.escape(brand["follow"])}</span>'
              f'<span class="t2">✓ {html.escape(brand["following"])}</span></div></div></div>'
            + '<div id="tap"></div></div>')
        assert lab_y + 300 < 1580, f"museum placard too low ({lab_y:.0f}): lower frame_w or frame_top"
        c0 = voice_end + 0.05
        cta_js += [
            f"FT('#museum',{{opacity:0,filter:'blur(18px)'}},{{opacity:1,filter:'blur(0px)',duration:.7,"
            f"ease:'power2.out'}},{c0 - 0.25:.3f});",
            f"FT('#mgrp',{{scale:1.05}},{{scale:1.0,duration:{hold:.2f},ease:'power1.out'}},{c0 - 0.25:.3f});",
            f"FT('#placard .lb',{{opacity:0,y:16}},{{opacity:1,y:0,duration:.6}},{c0 + 0.5:.3f});",
            f"FT('#placard .sb',{{opacity:0}},{{opacity:1,duration:.5}},{c0 + 0.9:.3f});",
            f"FT('#placard .rule',{{scaleX:0}},{{scaleX:1,duration:.5}},{c0 + 1.2:.3f});",
            f"FT('#placard .hd',{{opacity:0,y:12}},{{opacity:1,y:0,duration:.5}},{c0 + 1.5:.3f});",
        ]
        fb = c0 + 2.6
        hw = text_w(brand["handle"], 60)
        bx0 = 540 - (hw + 26 + 330) / 2 + hw + 26
        hd_top = lab_y + 84 + (70 if cta.get("sub") else 0) + 62
        tx, ty = bx0 + 165, hd_top + 38            # a touch on the centre of the button (mobile, no cursor)
        cta_js += [
            f"S('#tap',{{left:{tx:.0f},top:{ty:.0f},scale:.3,opacity:0}},0);",
            f"FT('#tap',{{scale:.3,opacity:.85}},{{scale:2.1,opacity:0,duration:.6,ease:'power2.out'}},{fb:.3f});",
            f"TO('#fbtn .fill',{{scaleX:1,duration:.35,ease:'power2.out'}},{fb + 0.05:.3f});",
            f"TO('#fbtn .t',{{opacity:0,duration:.15}},{fb + 0.1:.3f});",
            f"TO('#fbtn .t2',{{opacity:1,duration:.2}},{fb + 0.2:.3f});",
        ]
        sfx(c0 - 0.2, "page_turn", -24, "museum card")
        sfx(fb, "mouse_click", -20, "follow tap")
        sfx(fb + 0.25, "success_chime", -27, "following", 0.9)

    # music -------------------------------------------------------------
    mus = b.get("music", {})
    main = track if track and track not in ("vox", "none") else mus.get("main", DEFAULT_MUSIC)
    if isinstance(main, str) and main.startswith("music:"):
        main = rk.music_path(main)
    elif isinstance(main, str) and not os.path.isabs(main):
        main = str((WORK / main).resolve())
    drop = float(drop_s or mus.get("drop", 0.0))
    g = float(mus.get("gain_db", -1))
    music = [{"start": 0.0, "end": voice_end, "mode": "full", "gain_db": g, "track": main, "src": drop,
              "fade_in": 0.5, "fade_out": 0.05},
             {"start": voice_end, "end": duration, "mode": "full", "gain_db": g + 3, "track": main,
              "src": drop + voice_end, "fade_in": 0.05, "fade_out": 1.4}]

    keys = {"voice_end": voice_end, "duration": duration, "seed": SEED,
            "rigStates": {"hero": {"x": 0, "y": 0, "scale": 1}}, "rig": [[0.0, "hero"]]}
    for k, st in enumerate(starts):
        keys[f"scene_{k}"] = round(st, 3)
    js = JS + "".join(sc_js) + "".join(cap_js) + "".join(dd_js) + "".join(cta_js)
    caps_markup = "".join(cap_html)
    markup = page(duration, voice_end, "".join(sc_html) + "".join(dd_html), caps_markup, museum_html, js, keys)
    (WORK / "composition/index.html").write_text(markup)
    plan = {"style": "vox", "duration": duration, "voice_end": voice_end, "keys": keys,
            "captions": [{k: v for k, v in c.items() if k != "idx"} for c in caps],
            "sound_events": sorted(sound, key=lambda e: e["time"]), "music": music, "mix": "voice",
            "duck_open": [[p["out_start"], p["out_end"]] for p in pauses],
            "allowed_numbers": b.get("allowed_numbers", [])}
    if b.get("max_duration"):
        plan["max_duration"] = b["max_duration"]
    (WORK / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2))
    (WORK / "captions.json").write_text(json.dumps(plan["captions"], ensure_ascii=False, indent=2))
    return plan


JS = r"""
// hand-drawn look for clean line icons: resample every stroke into a jittered polyline (build time, seeded)
function rough(sel,amp){document.querySelectorAll(sel+' .rough [pathLength]').forEach(el=>{
  let L=0;try{L=el.getTotalLength()}catch(e){return}
  const n=Math.max(10,Math.round(L/1.1));let d='';const ns='http://www.w3.org/2000/svg';
  for(let i=0;i<=n;i++){const p=el.getPointAtLength(L*i/n);const j=(rnd()-.5)*2*amp*(0.6+0.4*Math.sin(i*0.7));
    d+=(i?' L':'M')+(p.x+j).toFixed(2)+','+(p.y+j*0.8).toFixed(2);}
  const np=document.createElementNS(ns,'path');np.setAttribute('d',d);np.setAttribute('pathLength','1');
  el.parentNode.replaceChild(np,el);});}
function draw(sel,t,dur){S(sel+' [pathLength]',{opacity:1},t);
  TO(sel+' [pathLength]',{strokeDashoffset:0,duration:dur,ease:'power1.inOut',stagger:0.05},t);}
function drawOne(sel,t,dur){S(sel,{opacity:1},t);TO(sel,{strokeDashoffset:0,duration:dur,ease:'power1.out'},t);}
"""


def sfx_lib():
    return rk.sfx_library()
