"""Generated media from the user's HeyGen account: the person in new scenarios, new scenes, the clone speaking.

Optional, like `heditor avatar`: nothing else in heditor needs it. It drives the official `heygen` CLI (the credential
stays with that CLI) and spends the credits of the user's HeyGen subscription (OAuth) or the API wallet (API key).
Every command shows the plan and an estimate first and spends nothing without --yes; every result is recorded with
its provenance (`synthetic: true`) in <work>/gen/gen.json and its measured cost in ~/.heditor/heygen-usage.json.

  heditor gen status                                   credits left + what each kind of job cost so far
  heditor gen persona <work> <name> --ref IMG [--n 1] [--aspect 9:16] [--seed N] [--identity IMG|LOOK ...]
        the person (identity images or look ids, default brand.json heygen.identity) inside the reference
        image's scene, pose, clothing and framing: heygen-image-1 identity_remix -> <work>/gen/<name>-<k>.png
  heditor gen clip <work> <name> --prompt "..." [--image IMG | --ref IMG ...] [--seconds 5] [--res 480p]
        [--aspect 9:16] [--enhance turbo]
        a scene with its own sound from a prompt (text_to_video), a first frame (image_to_video) or references
        (reference_to_video): heygen-video-1 -> <work>/gen/<name>.mp4
  heditor gen talk <work> <name> --image IMG (--text "..." | --script FILE | --audio FILE) [--motion "..."]
        [--expressiveness low|medium|high] [--res 720p] [--aspect 9:16] [--alpha]
        any image of the person speaking with lip-sync (Avatar IV, type image): the brand's cloned voice for a
        script, or the person's own recording; --alpha returns a transparent WebM to composite on any scene
        -> <work>/gen/<name>.mp4|webm
  heditor gen resume <work> <job_id>                   download a job that was still rendering
  heditor gen unframe <image>                          remove a blurred "fill" frame around a generated still

Rules (references/generation.md): only the account owner's own identity, or people who consented; say only what the
person approved (a script is approved before `--yes`); never a real person's face added to a scene without consent;
disclose AI use where the platform or the law asks for it; one cheap test (480p, 5 s, one image) before a batch.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import heygenkit as hk  # noqa: E402

# Measured on a Pro subscription (OAuth premium credits), Nov 2026: identity_remix 6 credits per image (2160x3840);
# a 480p 5 s image_to_video plus a 2.5 s Avatar IV photo video cost 3 credits together. Estimates use the user's own
# measured history first (heygen-usage.json), then these defaults. HeyGen bills the real job, not the estimate.
DEFAULT_RATES = {
    ("persona", "identity_remix", "-"): {"per": "image", "credits": 6.0, "usd": None},
    ("clip", "image_to_video", "480p"): {"per": "second", "credits": 0.4, "usd": 0.02},
    ("clip", "image_to_video", "768p"): {"per": "second", "credits": 0.6, "usd": 0.03},
    ("clip", "image_to_video", "1080p"): {"per": "second", "credits": 1.8, "usd": 0.09},
    ("clip", "text_to_video", "480p"): {"per": "second", "credits": 0.4, "usd": 0.02},
    ("clip", "text_to_video", "768p"): {"per": "second", "credits": 0.6, "usd": 0.03},
    ("clip", "text_to_video", "1080p"): {"per": "second", "credits": 1.8, "usd": 0.18},
    ("clip", "reference_to_video", "480p"): {"per": "second", "credits": 0.8, "usd": 0.04},
    ("clip", "reference_to_video", "768p"): {"per": "second", "credits": 1.2, "usd": 0.06},
    ("clip", "reference_to_video", "1080p"): {"per": "second", "credits": 3.6, "usd": 0.36},
    ("talk", "avatar_iv_image", "-"): {"per": "second", "credits": 16 / 60, "usd": 2.31 / 60},
}
EXIT_USAGE = hk.EXIT_USAGE


def usage_file():
    return hk.heditor_home() / "heygen-usage.json"


def asset_cache_file():
    return hk.heditor_home() / "cache" / "heygen-assets.json"


def _load(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def credits_left():
    status = hk.account_status()
    if not status.get("connected"):
        raise hk.HeyGenError(hk.msg("not_connected"), hk.EXIT_AUTH)
    return status, status.get("premium_credits"), status.get("wallet_balance")


# ---------------------------------------------------------------- cost

def rate(kind, mode, res):
    """Measured average from the usage history, else the shipped default."""
    key = (kind, mode, res or "-")
    hist = [j for j in _load(usage_file(), []) if (j.get("kind"), j.get("mode"), j.get("res") or "-") == key
            and j.get("credits_spent") is not None and j.get("units")]
    base = dict(DEFAULT_RATES.get(key) or {"per": "second", "credits": None, "usd": None})
    if hist:
        spent = sum(j["credits_spent"] for j in hist)
        units = sum(j["units"] for j in hist)
        if units > 0 and spent >= 0:
            base["credits"] = spent / units
            base["measured_jobs"] = len(hist)
    return base


def estimate(kind, mode, res, units, billing):
    r = rate(kind, mode, res)
    if billing == "subscription":
        amount = None if r.get("credits") is None else round(r["credits"] * units, 1)
        return {"unit": "credits", "amount": amount, "rate": r}
    amount = None if r.get("usd") is None else round(r["usd"] * units, 2)
    return {"unit": "usd", "amount": amount, "rate": r}


def fmt_cost(cost):
    if cost["amount"] is None:
        return "unknown (no published or measured rate yet: run one cheap test first)"
    src = f"measured over {cost['rate']['measured_jobs']} job(s)" if cost["rate"].get("measured_jobs") else "default"
    return f"~{cost['amount']} {cost['unit']} ({src} rate)"


def log_usage(entry):
    hist = _load(usage_file(), [])
    hist.append(entry)
    _save(usage_file(), hist)


# ---------------------------------------------------------------- assets and identity

def upload(path):
    """Upload a local file once (cache by content hash); return the asset id. URLs and asset ids pass through."""
    text = str(path)
    if text.startswith(("http://", "https://")):
        return {"type": "url", "url": text}
    if len(text) == 32 and all(c in "0123456789abcdef" for c in text) and not Path(text).exists():
        return {"type": "asset_id", "asset_id": text}
    p = Path(text).expanduser().resolve()
    if not p.exists():
        raise hk.HeyGenError(f"file not found: {p}", EXIT_USAGE)
    digest = sha256_file(p)
    cache = _load(asset_cache_file(), {})
    hit = cache.get(digest)
    if hit and time.time() - hit.get("at", 0) < 6 * 86400:
        return {"type": "asset_id", "asset_id": hit["asset_id"]}
    out = hk.cli_json(["asset", "create", "--file", str(p)], timeout=600).get("data") or {}
    if not out.get("asset_id"):
        raise hk.HeyGenError(f"HeyGen did not return an asset_id for {p.name}")
    cache[digest] = {"asset_id": out["asset_id"], "file": str(p), "at": time.time()}
    _save(asset_cache_file(), cache)
    return {"type": "asset_id", "asset_id": out["asset_id"]}


def brand_identity():
    try:
        data = json.loads((hk.heditor_home() / "brand.json").read_text(encoding="utf-8"))
        return list((data.get("heygen") or {}).get("identity") or [])
    except (OSError, ValueError, AttributeError):
        return []


def identity_image(item):
    """A look id becomes its preview image (cached locally); a path or URL is used as it is."""
    text = str(item)
    if Path(text).expanduser().exists() or text.startswith(("http://", "https://")):
        return text
    cache = hk.heditor_home() / "cache" / "identity" / f"{text}.jpg"
    if not cache.exists():
        look = hk.get_look(text)
        url = look.get("preview_image_url") or look.get("image_url")
        if not url:
            raise hk.HeyGenError(f"look {text} has no preview image to use as identity")
        cache.parent.mkdir(parents=True, exist_ok=True)
        tag = f"{os.getpid()}-{time.time_ns()}"          # parallel jobs must not share temporary files
        tmp, part = cache.with_suffix(f".{tag}.src"), cache.with_suffix(f".{tag}.jpg")
        subprocess.run(["curl", "-sL", "--fail", url, "-o", str(tmp)], check=True, timeout=180)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-q:v", "2", str(part)], check=True,
                       timeout=180)
        tmp.unlink(missing_ok=True)
        os.replace(part, cache)
    return str(cache)


# ---------------------------------------------------------------- provenance

def record(work, entry):
    path = Path(work) / "gen" / "gen.json"
    data = _load(path, [])
    data = [e for e in data if e.get("job_id") != entry.get("job_id")] + [entry]
    _save(path, data)


def _key(req):
    return "heditor-" + hashlib.sha256(json.dumps(req, sort_keys=True).encode()).hexdigest()[:40]


def _confirm(args):
    if args.yes:
        return True
    print("nothing spent: add --yes to run it (after the estimate is approved)")
    return False


def _download(url, dest):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-sL", "--fail", url, "-o", str(dest)], check=True, timeout=900)
    return dest


def _probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, timeout=60).stdout
    try:
        d = json.loads(out)
    except ValueError:
        return {}
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    return {"width": v.get("width"), "height": v.get("height"),
            "duration": round(float(d.get("format", {}).get("duration") or 0), 3),
            "audio": any(s.get("codec_type") == "audio" for s in d.get("streams", []))}


def _poll(getter, job_id, timeout_s, done=("completed",), failed=("failed", "error")):
    deadline = time.monotonic() + timeout_s
    delay = 5.0
    while True:
        info = hk.cli_json(getter + [job_id], timeout=60).get("data") or {}
        status = info.get("status")
        if status in done:
            return info
        if status in failed:
            raise hk.HeyGenError(f"job {job_id} failed: {info.get('failure_code') or ''} "
                                 f"{info.get('failure_message') or info.get('error') or ''}".strip())
        if time.monotonic() + delay > deadline:
            return None
        time.sleep(delay)
        delay = min(delay * 1.4, 20.0)


def _finish(work, entry, before, units):
    """Measured cost = credits before - after. Jobs run in parallel share the delta: run the first job of a kind
    alone (the cheap test) so the ledger learns a clean rate."""
    _, after, _ = credits_left()
    spent = None if before is None or after is None else before - after
    entry["credits_before"], entry["credits_after"], entry["credits_spent"] = before, after, spent
    record(work, entry)
    log_usage({"kind": entry["kind"], "mode": entry["mode"], "res": entry.get("res") or "-", "units": units,
               "credits_spent": spent, "job_id": entry["job_id"], "work": str(work), "at": entry["requested_at"]})
    print(f"spent:    {spent if spent is not None else '?'} credits (left: {after})")
    print("remember: synthetic media of a real person: approved words only, disclose AI where required")


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def unframe(path, min_margin=0.02):
    """identity_remix sometimes returns the scene reduced inside a blurred copy of itself (a "blur fill" frame).
    Find the sharp inner rectangle (Laplacian energy per row/column) and, when the frame is wider than
    min_margin on a side, save the inner picture back at the original size and aspect (cover). Returns the
    margins found (fractions) or None. The original is kept as <name>.framed.png."""
    import cv2
    import numpy as np
    img = cv2.imread(str(path))
    if img is None:
        return None
    h, w = img.shape[:2]
    small = cv2.resize(img, (w // 4, h // 4))
    lap = np.abs(cv2.Laplacian(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), cv2.CV_32F, ksize=3))
    lap = cv2.blur(lap, (9, 9))
    cols, rows = lap.mean(axis=0), lap.mean(axis=1)

    def span(v):
        core = np.median(v[len(v) // 4: 3 * len(v) // 4])
        on = np.nonzero(v > 0.35 * core)[0]
        return (on[0] / len(v), (on[-1] + 1) / len(v)) if len(on) else (0.0, 1.0)
    x0, x1 = span(cols)
    y0, y1 = span(rows)
    margins = {"left": round(x0, 3), "right": round(1 - x1, 3), "top": round(y0, 3), "bottom": round(1 - y1, 3)}
    sides = [k for k, v in margins.items() if v >= min_margin]
    # a blur-fill frame surrounds the picture (3-4 sides, left and right alike); one soft side is just a plain wall,
    # a sky or a window out of focus, and must not be cropped
    if len(sides) < 3 or abs(margins["left"] - margins["right"]) > 0.03:
        return None
    pad = 0.006
    X0, X1 = int((x0 + pad) * w), int((x1 - pad) * w)
    Y0, Y1 = int((y0 + pad) * h), int((y1 - pad) * h)
    inner = img[Y0:Y1, X0:X1]
    ih, iw = inner.shape[:2]
    scale = max(w / iw, h / ih)
    big = cv2.resize(inner, (int(iw * scale + 0.5), int(ih * scale + 0.5)), interpolation=cv2.INTER_LANCZOS4)
    bh, bw = big.shape[:2]
    ox, oy = (bw - w) // 2, (bh - h) // 2
    framed = Path(path).with_suffix(".framed.png")
    Path(path).replace(framed)
    cv2.imwrite(str(path), big[oy:oy + h, ox:ox + w])
    return margins


# ---------------------------------------------------------------- commands

def cmd_status(_args):
    status, credits, wallet = credits_left()
    hk.print_status(status)
    hist = _load(usage_file(), [])
    if hist:
        print("measured costs:")
        seen = {}
        for j in hist:
            seen.setdefault((j["kind"], j["mode"], j.get("res") or "-"), []).append(j)
        for (k, m, r), jobs in sorted(seen.items()):
            rr = rate(k, m, r)
            per = DEFAULT_RATES.get((k, m, r), {}).get("per", "unit")
            c = f"{rr['credits']:.2f}" if rr.get("credits") is not None else "?"
            print(f"  {k:8s} {m:20s} {r:6s} {c} credits per {per}  ({len(jobs)} job(s))")
    return 0


def cmd_persona(args):
    work = Path(args.work)
    status, before, _ = credits_left()
    ids = args.identity or brand_identity()
    if not ids:
        raise hk.HeyGenError("no identity: pass --identity IMG|LOOK_ID (1-5) or set brand.json "
                             '"heygen": {"identity": ["<look id or image>", ...]}', EXIT_USAGE)
    if not 1 <= len(ids) <= 5:
        raise hk.HeyGenError("identity_remix takes 1 to 5 identity images", EXIT_USAGE)
    billing = status.get("billing") or ("subscription" if status.get("auth") == "oauth" else "wallet")
    cost = estimate("persona", "identity_remix", None, args.n, billing)
    print(f"persona:  {args.n} image(s) of the identity ({len(ids)} source image(s)) inside {args.ref}")
    print(f"model:    heygen-image-1 identity_remix   aspect: {args.aspect}")
    print(f"credits:  {before} left   estimate: {fmt_cost(cost)}")
    if not _confirm(args):
        return 0
    req = {"identity_images": [upload(identity_image(i)) for i in ids], "reference_images": [upload(args.ref)]}
    flags = ["--model", "heygen-image-1", "--num-images", str(args.n), "--aspect-ratio", args.aspect]
    if args.seed is not None:
        flags += ["--seed", str(args.seed)]
    key = _key({"req": req, "flags": flags})
    out = hk.cli_json(["model", "images", "create", *flags, "-d", "-", "--idempotency-key", key],
                      stdin=json.dumps(req), timeout=300).get("data") or {}
    gid = out.get("generation_id")
    if not gid:
        raise hk.HeyGenError("HeyGen did not return a generation_id")
    entry = {"kind": "persona", "mode": "identity_remix", "job_id": gid, "model": "heygen-image-1", "name": args.name,
             "identity": [str(i) for i in ids], "reference": str(args.ref), "aspect": args.aspect, "seed": args.seed,
             "requested_at": _now(), "synthetic": True, "status": "rendering"}
    record(work, entry)
    info = _poll(["model", "images", "get"], gid, 900)
    if not info:
        print(f"still rendering: heditor gen resume {work} {gid}")
        return hk.EXIT_TIMEOUT
    files = []
    for k, img in enumerate(info.get("images") or [], 1):
        dest = _download(img["image_url"], work / "gen" / f"{args.name}-{k}.png")
        frame = unframe(dest)
        files.append({"file": str(dest), "width": img.get("width"), "height": img.get("height"),
                      "seed": img.get("seed"), "blur_frame_removed": frame})
        print(f"saved:    {dest}  ({img.get('width')}x{img.get('height')})"
              + (f"  blurred frame removed {frame} (original kept as .framed.png)" if frame else ""))
    entry.update(status="completed", files=files)
    _finish(work, entry, before, len(files))
    return 0


def cmd_clip(args):
    work = Path(args.work)
    status, before, _ = credits_left()
    mode = "reference_to_video" if args.ref else ("image_to_video" if args.image else "text_to_video")
    if mode == "reference_to_video" and args.seconds > 15:
        raise hk.HeyGenError("reference_to_video lasts 5-15 s", EXIT_USAGE)
    billing = status.get("billing") or ("subscription" if status.get("auth") == "oauth" else "wallet")
    cost = estimate("clip", mode, args.res, args.seconds, billing)
    print(f"clip:     {mode}, {args.seconds} s, {args.res}, aspect {args.aspect}, enhancement {args.enhance}")
    print(f"prompt:   {args.prompt[:160]}{'…' if len(args.prompt) > 160 else ''}")
    print(f"credits:  {before} left   estimate: {fmt_cost(cost)}")
    if not _confirm(args):
        return 0
    req = {"model": "heygen-video-1", "mode": mode, "prompt": args.prompt, "duration": args.seconds,
           "resolution": args.res, "prompt_enhancement": args.enhance}
    if mode == "image_to_video":
        req["image"] = upload(args.image)
    else:
        req["aspect_ratio"] = args.aspect
    if mode == "reference_to_video":
        req["reference_images"] = [upload(r) for r in args.ref]
    if args.seed is not None:
        req["seed"] = args.seed
    out = hk.cli_json(["model", "videos", "create", "-d", "-", "--idempotency-key", _key(req)],
                      stdin=json.dumps(req), timeout=300).get("data") or {}
    vid = out.get("video_id")
    if not vid:
        raise hk.HeyGenError("HeyGen did not return a video_id")
    entry = {"kind": "clip", "mode": mode, "res": args.res, "job_id": vid, "model": "heygen-video-1",
             "name": args.name, "prompt": args.prompt, "image": args.image, "refs": args.ref,
             "seconds": args.seconds, "requested_at": _now(), "synthetic": True, "status": "rendering"}
    record(work, entry)
    info = _poll(["model", "videos", "get"], vid, 1800)
    if not info:
        print(f"still rendering: heditor gen resume {work} {vid}")
        return hk.EXIT_TIMEOUT
    dest = _download(info["video_url"], work / "gen" / f"{args.name}.mp4")
    entry.update(status="completed", file=str(dest), **_probe(dest))
    print(f"saved:    {dest}  ({entry.get('width')}x{entry.get('height')}, {entry.get('duration')} s, "
          f"{'with' if entry.get('audio') else 'no'} audio)")
    _finish(work, entry, before, args.seconds)
    return 0


def cmd_talk(args):
    work = Path(args.work)
    status, before, _ = credits_left()
    inputs = [x for x in (args.text, args.script, args.audio) if x]
    if len(inputs) != 1:
        raise hk.HeyGenError("pass exactly one of --text, --script or --audio", EXIT_USAGE)
    script = args.text or (Path(args.script).read_text(encoding="utf-8").strip() if args.script else None)
    if script is not None:
        hk.check_breaks(script)
        seconds = hk.script_seconds(script)
        voice = args.voice or hk.brand_voice()
        if not voice:
            raise hk.HeyGenError("no voice: set brand.json heygen.voice_id (the person's cloned voice) or --voice",
                                 EXIT_USAGE)
    else:
        seconds = round(hk.probe_duration(Path(args.audio)), 1)
        voice = None
    billing = status.get("billing") or ("subscription" if status.get("auth") == "oauth" else "wallet")
    cost = estimate("talk", "avatar_iv_image", None, seconds, billing)
    print(f"talk:     Avatar IV from an image, ~{seconds:.1f} s, {args.res}, aspect {args.aspect}"
          + (", transparent WebM" if args.alpha else ""))
    print(f"input:    {'script (voice ' + voice + ')' if script is not None else 'audio ' + args.audio}")
    if script is not None:
        print(f"script:   {script}")
    print(f"credits:  {before} left   estimate: {fmt_cost(cost)}")
    if not _confirm(args):
        return 0
    req = {"type": "image", "image": upload(args.image), "resolution": args.res, "aspect_ratio": args.aspect,
           "fit": args.fit, "expressiveness": args.expressiveness, "title": f"heditor {work.name} {args.name}"}
    if script is not None:
        req.update(script=script, voice_id=voice)
    else:
        req["audio_asset_id"] = upload(args.audio)["asset_id"]
    if args.motion:
        req["motion_prompt"] = args.motion
    if args.alpha:
        req["output_format"] = "webm"
    out = hk.cli_json(["video", "create", "-d", "-", "--idempotency-key", _key(req)], stdin=json.dumps(req),
                      timeout=300).get("data") or {}
    vid = out.get("video_id")
    if not vid:
        raise hk.HeyGenError("HeyGen did not return a video_id")
    entry = {"kind": "talk", "mode": "avatar_iv_image", "res": None, "job_id": vid, "name": args.name,
             "image": str(args.image), "script": script, "voice_id": voice, "audio": args.audio,
             "motion": args.motion, "alpha": args.alpha, "requested_at": _now(), "synthetic": True,
             "status": "rendering"}
    record(work, entry)
    info = _poll(["video", "get"], vid, 1800)
    if not info:
        print(f"still rendering: heditor gen resume {work} {vid}")
        return hk.EXIT_TIMEOUT
    url = info.get("video_url") or info.get("url")
    dest = _download(url, work / "gen" / f"{args.name}.{'webm' if args.alpha else 'mp4'}")
    entry.update(status="completed", file=str(dest), **_probe(dest))
    print(f"saved:    {dest}  ({entry.get('width')}x{entry.get('height')}, {entry.get('duration')} s)")
    _finish(work, entry, before, entry.get("duration") or seconds)
    return 0


def cmd_resume(args):
    work = Path(args.work)
    entry = next((e for e in _load(work / "gen" / "gen.json", []) if e.get("job_id") == args.job_id), None)
    if not entry:
        raise hk.HeyGenError(f"job {args.job_id} is not in {work}/gen/gen.json", EXIT_USAGE)
    _, before, _ = credits_left()
    if entry["kind"] == "persona":
        info = _poll(["model", "images", "get"], args.job_id, 600)
        if not info:
            return hk.EXIT_TIMEOUT
        entry["files"] = [{"file": str(_download(img["image_url"], work / "gen" / f"{entry['name']}-{k}.png"))}
                          for k, img in enumerate(info.get("images") or [], 1)]
    else:
        getter = ["model", "videos", "get"] if entry["kind"] == "clip" else ["video", "get"]
        info = _poll(getter, args.job_id, 600)
        if not info:
            return hk.EXIT_TIMEOUT
        ext = "webm" if entry.get("alpha") else "mp4"
        dest = _download(info.get("video_url") or info.get("url"), work / "gen" / f"{entry['name']}.{ext}")
        entry.update(file=str(dest), **_probe(dest))
    entry["status"] = "completed"
    record(work, entry)
    print(f"saved:    {entry.get('file') or [f['file'] for f in entry['files']]}  (credits now {before})")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="heditor gen", description="generated media from your HeyGen account")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    pe = sub.add_parser("persona")
    pe.add_argument("work")
    pe.add_argument("name")
    pe.add_argument("--ref", required=True, help="reference image: scene, pose, clothing and framing")
    pe.add_argument("--identity", nargs="+", help="1-5 identity images or look ids (default brand.json)")
    pe.add_argument("--n", type=int, default=1, choices=range(1, 6))
    pe.add_argument("--aspect", default="9:16", choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9"])
    pe.add_argument("--seed", type=int)
    pe.add_argument("--yes", action="store_true")
    cl = sub.add_parser("clip")
    cl.add_argument("work")
    cl.add_argument("name")
    cl.add_argument("--prompt", required=True)
    cl.add_argument("--image", help="first frame (image_to_video)")
    cl.add_argument("--ref", nargs="+", help="reference images (reference_to_video, up to 9)")
    cl.add_argument("--seconds", type=int, default=5)
    cl.add_argument("--res", default="480p", choices=["480p", "768p", "1080p", "2k"])
    cl.add_argument("--aspect", default="9:16", choices=["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"])
    cl.add_argument("--enhance", default="turbo", choices=["turbo", "quality", "ultraquality", "disabled"])
    cl.add_argument("--seed", type=int)
    cl.add_argument("--yes", action="store_true")
    ta = sub.add_parser("talk")
    ta.add_argument("work")
    ta.add_argument("name")
    ta.add_argument("--image", required=True)
    ta.add_argument("--text")
    ta.add_argument("--script")
    ta.add_argument("--audio", help="the person's own recording to lip-sync")
    ta.add_argument("--voice", help="voice id (default brand.json heygen.voice_id)")
    ta.add_argument("--motion", help="body and hand gestures, e.g. 'one open-hand gesture on the last word'")
    ta.add_argument("--expressiveness", default="medium", choices=["low", "medium", "high"])
    ta.add_argument("--res", default="720p", choices=["720p", "1080p"])
    ta.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "4:5", "5:4", "1:1", "auto"])
    ta.add_argument("--alpha", action="store_true", help="transparent WebM for compositing")
    ta.add_argument("--fit", default="cover", choices=["cover", "contain"],
                    help="cover fills the frame (default); contain can add a blurred letterbox inside the clip")
    ta.add_argument("--yes", action="store_true")
    un = sub.add_parser("unframe")
    un.add_argument("image")
    re_ = sub.add_parser("resume")
    re_.add_argument("work")
    re_.add_argument("job_id")
    args = p.parse_args(argv)
    if args.cmd == "unframe":
        print(json.dumps(unframe(args.image)))
        return 0
    return {"status": cmd_status, "persona": cmd_persona, "clip": cmd_clip, "talk": cmd_talk,
            "resume": cmd_resume}[args.cmd](args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except hk.HeyGenError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(exc.code)
