"""`heditor long ...`: long-form pipeline for classes, lives and YouTube videos (any format profile).

    heditor long new <work> <video> [--format 16:9] [--style cinema|creative] [--kind aula|live|youtube] [--range a,b]
    heditor long transcribe <work> [--model small] [--chunk 300]      chunked, resumable ASR -> transcript.json
    heditor long edl <work> [--force]                                  proposed cuts -> edl-proposal.json + qa/edl-proposal.md
    heditor long apply <work>                                          cut screen/camera/voice -> edl.json, words.json
    heditor long chapters <work> [--suggest]                           suggest / validate chapters, export chapters.txt
    heditor long layouts <work>                                        suggested layout switches -> layouts.suggested.json
    heditor long produce <work> [music:ID|file]                        build.py -> plan, composition, segments, mix
    heditor long preview <work> <t1,t2,..> [sheet.jpg] [--format 4:5]  frame previews (any profile) + contact sheet
    heditor long lint <work>                                           HyperFrames lint of the page and every segment
    heditor long render <work> [workers]                               segmented, resumable render with ETA log
    heditor long finalize <work> <name.mp4>                            concat + one continuous master audio + QA
    heditor long qa <work> [name.mp4]                                  QA report only (qa/long-report.{json,md})
    heditor long subs <work> [name]                                    SRT + VTT of the edited timeline
    heditor long sync <work>                                           camera/screen/voice vs source through the EDL
    heditor long estimate <work>                                       render time estimate
    heditor long styles | formats                                      style packs / format profiles
"""

import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))
import formats as fm  # noqa: E402
import longform as lf  # noqa: E402
import stylepacks as sp  # noqa: E402

SKILL = KIT.parents[1]
SR = 48000


def _args(argv, flags=()):
    """Positional args + --flag value pairs (flags listed in `flags` take no value)."""
    pos, opt, i = [], {}, 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            key = a[2:]
            if key in flags:
                opt[key] = True
            else:
                opt[key] = argv[i + 1]
                i += 1
        else:
            pos.append(a)
        i += 1
    return pos, opt


def _cfg(work):
    return json.loads((Path(work) / "long.json").read_text())


def _save(path, data):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    tmp.replace(path)


def _probe(path):
    out = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                     "format=duration:stream=codec_type,width,height,r_frame_rate,nb_frames",
                                     "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout)
    v = next((s for s in out["streams"] if s["codec_type"] == "video"), {})
    num, den = (v.get("r_frame_rate") or "30/1").split("/")
    return {"duration": float(out["format"]["duration"]), "width": v.get("width"), "height": v.get("height"),
            "fps": float(num) / float(den or 1), "frames": int(v["nb_frames"]) if v.get("nb_frames", "N/A") != "N/A" else None}


def _log(work, name, line):
    p = Path(work) / name
    p.parent.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%H:%M:%S")
    with open(p, "a") as fh:
        fh.write(f"{stamp} {line}\n")
    print(f"{stamp} {line}", flush=True)


# ---------------------------------------------------------------- new

def cmd_new(argv):
    pos, opt = _args(argv)
    work, src = Path(pos[0]).resolve(), Path(pos[1]).resolve()
    work.mkdir(parents=True, exist_ok=True)
    (work / "qa").mkdir(exist_ok=True)
    pr = _probe(src)
    fmt = fm.get(opt.get("format", "16:9"))
    style = opt.get("style", "creative")
    sp.get(style)
    rng = [float(x) for x in opt["range"].split(",")] if opt.get("range") else [0.0, round(pr["duration"], 3)]
    cfg = json.loads((SKILL / "templates/long/long.json").read_text())
    cfg.update({"format": fmt.key, "style": style, "kind": opt.get("kind", "aula"), "source": str(src), "range": rng,
                "source_fps": round(pr["fps"], 3), "source_size": [pr["width"], pr["height"]]})
    if not (work / "long.json").exists():
        _save(work / "long.json", cfg)
    for name in ("build.py", "DESIGN.md", "chapters.json"):
        if not (work / name).exists():
            shutil.copy2(SKILL / "templates/long" / name, work / name)
    (work / "composition").mkdir(exist_ok=True)
    print(f"created {work}: edit long.json (layout_source crops, range, intro, cta), then: heditor long transcribe {work}")


# ---------------------------------------------------------------- energy + transcription

def _energy(work, rng, src):
    qa = Path(work) / "qa"
    path = qa / f"energy-{rng[0]:.3f}-{rng[1]:.3f}.npy"
    if path.exists():
        return np.load(path)
    db = lf.energy_profile(src, rng[0], rng[1])
    np.save(path, db)
    return db


def transcribe_media(work, media, rng, chunk_dir, model_name="small", chunk=300.0, prompt=None, lang=None, log="qa/asr/progress.log"):
    """Chunked ASR of [rng] of `media`: one JSON per chunk (skipped when present), merged word list returned."""
    from faster_whisper import WhisperModel

    import reelkit as rk
    chunk_dir = Path(chunk_dir)
    chunk_dir.mkdir(parents=True, exist_ok=True)
    db = _energy(work, rng, media) if Path(media).suffix != ".wav" else lf.energy_profile(media, rng[0], rng[1])
    thr, _ = lf.silence_threshold(db)
    quiet = lf.quiet_runs(db, thr, rng[0], 0.25)
    chunks = lf.plan_chunks(rng[0], rng[1], chunk, quiet)
    model, results, t_start, done_audio = None, [], time.time(), 0.0
    for k, (a, b) in enumerate(chunks):
        path = chunk_dir / f"chunk-{a:010.3f}-{b:010.3f}.json"
        if path.exists():
            results.append(json.loads(path.read_text()))
            continue
        if model is None:
            model = WhisperModel(model_name, device="cpu", compute_type="int8",
                                 cpu_threads=int(os.environ.get("HEDITOR_ASR_THREADS", 3)))
        t0 = time.time()
        audio = rk.load_audio_16k(media, a, b - a)
        segs, _ = model.transcribe(audio, language=lang or os.environ.get("HEDITOR_LANG", "pt"), beam_size=5,
                                   word_timestamps=True, vad_filter=False, condition_on_previous_text=False, initial_prompt=prompt)
        words = [{"word": w.word.strip(), "start": round(a + w.start, 3), "end": round(a + w.end, 3), "p": round(w.probability, 3)}
                 for s in segs for w in s.words if w.word.strip()]
        _save(path, words)
        results.append(words)
        done_audio += b - a
        el = time.time() - t_start
        left = sum(bb - aa for aa, bb in chunks[k + 1:])
        rtf = (time.time() - t0) / max(1e-3, b - a)
        _log(work, log, f"chunk {k + 1}/{len(chunks)} {a:.1f}-{b:.1f}s: {len(words)} words, RTF {rtf:.2f}, "
                        f"elapsed {el / 60:.1f} min, ETA {left * el / max(1e-3, done_audio) / 60:.1f} min")
    return lf.merge_chunk_words(results), chunks


def cmd_transcribe(argv):
    pos, opt = _args(argv)
    work = Path(pos[0])
    cfg = _cfg(work)
    asr = cfg.get("asr", {})
    words, chunks = transcribe_media(work, cfg["source"], cfg["range"], work / "qa/asr", opt.get("model", asr.get("model", "small")),
                                     float(opt.get("chunk", asr.get("chunk_s", 300))), asr.get("prompt") or None, asr.get("lang"))
    _save(work / "transcript.json", words)
    print(json.dumps({"words": len(words), "chunks": len(chunks), "transcript": str(work / "transcript.json")}))


# ---------------------------------------------------------------- EDL

def cmd_edl(argv):
    pos, opt = _args(argv, flags=("force",))
    work = Path(pos[0])
    cfg = _cfg(work)
    words = json.loads((work / "transcript.json").read_text())
    rng = cfg["range"]
    db = _energy(work, rng, cfg["source"])
    prop = lf.propose_edl(words, db, rng[0], rng, dict({"lang": cfg.get("asr", {}).get("lang", "pt"), "exclude": cfg.get("exclude", [])}, **cfg.get("edl", {})))
    prop["source"] = cfg["source"]
    target = work / "edl-proposal.json"
    if target.exists() and not opt.get("force"):
        target = work / "edl-proposal.new.json"
        print(f"edl-proposal.json exists (reviewed?): wrote {target.name}; use --force to overwrite")
    _save(target, prop)
    md = ["# EDL proposal", "", f"Range {rng[0]:.2f}-{rng[1]:.2f} s · threshold {prop['threshold_dbfs']} dBFS · "
          f"{json.dumps(prop['stats'], ensure_ascii=False)}", "",
          "Flip `apply` in edl-proposal.json to accept/refuse a cut; add manual removals to long.json `exclude` "
          "([start, end] in source seconds, cut in word gaps). Then `heditor long apply <work>`.", "",
          "| id | kind | source | removed | apply | conf | text / context |", "|---|---|---|---|---|---|---|"]
    for c in prop["cuts"]:
        md.append(f"| {c['id']} | {c['kind']} | {c['start']:.2f}-{c['end']:.2f} | {c['removed_s']:.2f} | "
                  f"{'yes' if c['apply'] else '**review**'} | {c['confidence']} | {c['context'] or c['text']} {c.get('note', '')} |")
    (work / "qa/edl-proposal.md").write_text("\n".join(md) + "\n")
    print(json.dumps(prop["stats"], ensure_ascii=False))


def _crop_filter(crop, scale_w=None, sharpen=False):
    parts = [crop] if crop else []
    if scale_w:
        parts.append(f"scale={scale_w}:-2:flags=lanczos")
    if sharpen:
        parts.append("unsharp=5:5:0.5:5:5:0,eq=contrast=1.03:saturation=1.05")
    parts.append("format=yuv420p")
    return ",".join(parts)


def _ffmpeg_major():
    out = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.split()
    try:
        ver = out[2].lstrip("n")
        return int(ver.split(".")[0]) if ver[0].isdigit() else 99
    except (IndexError, ValueError):
        return 99


def filter_script_args(path):
    """Filter graph read from a file: `-/filter_complex <file>` (ffmpeg >= 7) or `-filter_complex_script` (older)."""
    return ["-/filter_complex", str(path)] if _ffmpeg_major() >= 7 else ["-filter_complex_script", str(path)]


def assemble_video(src, rng0, keeps, fps, outputs):
    """One ffmpeg pass: select the kept frames of [rng0, ...] and write each (crop, path, scale_w) output."""
    expr = "+".join(f"between(t,{a - rng0 - 0.5 / fps:.5f},{b - rng0 - 0.5 / fps:.5f})" for a, b in keeps)
    total = keeps[-1][1] - rng0
    graph = [f"[0:v]select='{expr}',setpts=N/({fps}*TB),split={len(outputs)}" + "".join(f"[s{i}]" for i in range(len(outputs)))]
    maps = []
    for i, (crop, path, scale_w, sharpen) in enumerate(outputs):
        graph.append(f"[s{i}]{_crop_filter(crop, scale_w, sharpen)}[o{i}]")
        maps += ["-map", f"[o{i}]", "-r", f"{fps}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-an", str(path)]
    script = Path(outputs[0][1]).with_suffix(".filter")
    script.write_text(";".join(graph))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{rng0:.4f}", "-t", f"{total + 0.5:.4f}", "-i", str(src),
                    *filter_script_args(script), *maps], check=True)
    script.unlink()


def assemble_audio(src, rng0, keeps, out_wav, fade=0.004, block_s=30.0):
    """Stream [rng0, last keep] once and write the kept samples (4 ms fades at every junction) to a mono WAV."""
    end = keeps[-1][1]
    spans = [(round((a - rng0) * SR), round((b - rng0) * SR)) for a, b in keeps]
    r = round(fade * SR)
    args = ["ffmpeg", "-v", "error", "-ss", f"{rng0:.4f}", "-t", f"{end - rng0 + 0.2:.4f}", "-i", str(src), "-vn", "-ac", "1",
            "-ar", str(SR), "-f", "f32le", "pipe:1"]
    pos, written, peak = 0, 0, 0.0
    tmp = Path(out_wav).with_suffix(".f32")
    with subprocess.Popen(args, stdout=subprocess.PIPE) as proc, open(tmp, "wb") as fh:
        while True:
            buf = proc.stdout.read(int(SR * block_s) * 4)
            if not buf:
                break
            x = np.frombuffer(buf, np.float32)
            b0, b1 = pos, pos + len(x)
            for s0, s1 in spans:
                lo, hi = max(s0, b0), min(s1, b1)
                if hi <= lo:
                    continue
                seg = x[lo - b0:hi - b0].copy()
                idx = np.arange(lo, hi)
                g = np.minimum(1.0, np.minimum((idx - s0 + 1) / r, (s1 - idx) / r)).astype(np.float32)
                seg *= g
                peak = max(peak, float(np.max(np.abs(seg))) if len(seg) else 0.0)
                fh.write(seg.astype("<f4").tobytes())
                written += len(seg)
            pos = b1
    expected = sum(s1 - s0 for s0, s1 in spans)
    if written < expected:  # source ended early: pad with silence so voice and picture keep the same length
        with open(tmp, "ab") as fh:
            fh.write(np.zeros(expected - written, "<f4").tobytes())
    scale = min(1.0, 0.98 / peak) if peak > 0 else 1.0
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", str(tmp), "-af",
                    f"volume={scale:.6f}", "-c:a", "pcm_s16le", str(out_wav)], check=True)
    tmp.unlink()
    return expected / SR


def _carry_review(new_words, reviewed_path):
    """Keep spelling fixes from an older words-reviewed.json (matched by source time) after a new apply."""
    if not reviewed_path.exists():
        return new_words, 0
    old = json.loads(reviewed_path.read_text())
    by_src, seen = {}, {}
    for w in old:
        if "source_start" in w:
            k = round(w["source_start"], 3)
            seen[k] = seen.get(k, -1) + 1
            by_src[(k, seen[k])] = w["word"]
    out, fixed, seen = [], 0, {}
    for w in new_words:
        k = round(w["source_start"], 3)
        seen[k] = seen.get(k, -1) + 1
        txt = by_src.get((k, seen[k]))
        if txt is not None and txt != w["word"]:
            fixed += 1
            w = dict(w, word=txt)
        out.append(w)
    return out, fixed


def _remap_and_review(work, cfg, prop, chunks):
    words = json.loads((work / "transcript.json").read_text())
    mapped = lf.remap_words(words, chunks, drop=lf.word_drop_ranges(prop["cuts"], cfg.get("exclude", [])))
    _save(work / "words.json", mapped)
    reviewed = work / "words-reviewed.json"
    if reviewed.exists():
        shutil.copy2(reviewed, work / "qa/words-reviewed.prev.json")
    carried, fixed = _carry_review(mapped, work / "qa/words-reviewed.prev.json")
    _save(reviewed, carried)
    return mapped, fixed


def cmd_apply(argv):
    pos, opt = _args(argv, flags=("words-only",))
    work = Path(pos[0])
    cfg = _cfg(work)
    prop_path = work / "edl-proposal.json"
    prop = json.loads(prop_path.read_text()) if prop_path.exists() else {"cuts": []}
    if opt.get("words-only"):  # remap words after a transcript/review change without cutting media again
        edl = json.loads((work / "edl.json").read_text())
        mapped, fixed = _remap_and_review(work, cfg, prop, edl["chunks"])
        print(json.dumps({"words": len(mapped), "review_fixes_carried": fixed}))
        return
    fps = float(cfg.get("source_fps") or _probe(cfg["source"])["fps"])
    rng = [round(cfg["range"][0] * fps) / fps, round(cfg["range"][1] * fps) / fps]
    keeps = lf.keep_ranges(rng, prop["cuts"], fps, exclude=cfg.get("exclude", []))
    chunks = lf.edl_chunks(keeps)
    a = work / "composition/assets"
    a.mkdir(parents=True, exist_ok=True)
    ls = cfg.get("layout_source", {})
    outputs = []
    if ls.get("screen"):
        outputs.append((ls["screen"], a / "screen.mp4", None, False))
    cam_w = cfg.get("camera_width", 1280)
    outputs.append((ls.get("camera"), a / "camera.mp4", cam_w, True))
    t0 = time.time()
    assemble_video(cfg["source"], rng[0], keeps, fps, outputs)
    voice_dur = assemble_audio(cfg["source"], rng[0], keeps, a / "voice-raw.wav")
    frames = sum(round((b - a_) * fps) for a_, b in keeps)
    got = {p.name: _probe(p)["frames"] for _, p, _, _ in outputs}
    trims = [c for c in prop["cuts"] if c.get("apply")]
    edl = {"mode": "long", "format": cfg["format"], "source": cfg["source"], "fps": fps, "range": rng,
           "crop": ls.get("camera"), "screen_crop": ls.get("screen"), "speed": 1.0, "voice_duration": voice_dur,
           "silence_threshold_dbfs": prop.get("threshold_dbfs", -45.0), "noise_floor_dbfs": prop.get("noise_floor_dbfs"),
           "chunks": chunks, "silence_trims": [{"source_start": c["start"], "source_end": c["end"], "removed_s": c["removed_s"],
                                                "kind": c["kind"]} for c in trims],
           "excluded": cfg.get("exclude", []), "removed_seconds": round((rng[1] - rng[0]) - voice_dur, 3),
           "expected_frames": frames, "asset_frames": got}
    _save(work / "edl.json", edl)
    mapped, fixed = _remap_and_review(work, cfg, prop, chunks)
    bad = {k: v for k, v in got.items() if v is not None and v != frames}
    print(json.dumps({"keeps": len(keeps), "voice_s": round(voice_dur, 3), "removed_s": edl["removed_seconds"],
                      "frames_expected": frames, "frames": got, "words": len(mapped), "review_fixes_carried": fixed,
                      "seconds": round(time.time() - t0, 1)}, ensure_ascii=False))
    if bad:
        print(f"FRAME COUNT MISMATCH {bad} (expected {frames})")
        sys.exit(1)


# ---------------------------------------------------------------- chapters, layouts, subtitles

def _words(work):
    p = Path(work) / "words-reviewed.json"
    return json.loads((p if p.exists() else Path(work) / "words.json").read_text())


def cmd_chapters(argv):
    pos, opt = _args(argv, flags=("suggest",))
    work = Path(pos[0])
    cfg = _cfg(work)
    words = _words(work)
    edl = json.loads((work / "edl.json").read_text())
    dur = edl["voice_duration"]
    if opt.get("suggest"):
        sug = lf.suggest_chapters(words, dur, cfg.get("kind", "aula"), float(opt["target"]) if opt.get("target") else None)
        _save(work / "chapters.suggested.json", sug)
        for c in sug:
            print(f"{lf.fmt_ts(c['start'])}  {c['excerpt']}")
        print("write titles into chapters.json ([{\"start\": s, \"title\": \"...\"}]); titles summarise what is said")
        return
    chapters = json.loads((work / "chapters.json").read_text())
    probs = lf.validate_chapters(chapters, dur)
    off = 0.0
    if (work / "plan.json").exists():
        off = json.loads((work / "plan.json").read_text()).get("voice_offset", 0.0)
    (work / "chapters.txt").write_text(lf.youtube_timestamps(chapters, off))
    print((work / "chapters.txt").read_text())
    print("problems:", probs or "none")
    sys.exit(1 if probs else 0)


def screen_activity(path, fps=2):
    """Mean absolute frame difference (0-255) per sample of a screen recording (64x36 gray)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"fps={fps},scale=64:36,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, 36, 64).astype(np.float32)
    return np.concatenate([[0.0], np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))])


def suggest_layouts(activity, words, fps=2, kind="aula", static_s=35.0):
    """pip by default; long static stretches of the screen alternate side/speaker; scrolling/typing -> screen."""
    out = [{"start": 0.0, "layout": "pip"}]
    starts = [w["start"] for i, w in enumerate(words) if i == 0 or str(words[i - 1]["word"]).rstrip().endswith((".", "?", "!"))]
    moving = activity > 2.0
    t, n, alt = 0.0, len(activity) / fps, 0
    while t < n:
        i = int(t * fps)
        window = moving[i:i + int(static_s * fps)]
        if len(window) and window.mean() < 0.03:
            s = next((x for x in starts if x >= t), None)
            if s is None or s > n - 8:
                break
            alt += 1
            out.append({"start": round(s, 2), "layout": "side" if alt % 2 else "speaker"})
            e = next((x for x in starts if x >= s + 14), None)
            if e is None or e > n - 4:
                break
            out.append({"start": round(e, 2), "layout": "pip"})
            t = e + static_s / 2
        else:
            t += static_s / 4
    return out


def cmd_layouts(argv):
    pos, _ = _args(argv)
    work = Path(pos[0])
    cfg = _cfg(work)
    scr = work / "composition/assets/screen.mp4"
    if not scr.exists():
        print("no screen.mp4 (camera-only source): layout is always 'speaker'")
        return
    act = screen_activity(scr)
    sug = suggest_layouts(act, _words(work), kind=cfg.get("kind", "aula"))
    _save(work / "layouts.suggested.json", sug)
    print(json.dumps(sug))
    print("review and copy to layouts.json (add \"zoom\": [x, y, w, h] fractions of the screen for focus moments)")


def cmd_subs(argv):
    pos, _ = _args(argv)
    work = Path(pos[0])
    name = pos[1] if len(pos) > 1 else "subtitles"
    plan = json.loads((work / "plan.json").read_text())
    fmt = fm.get(plan["format"])
    cues = lf.cue_groups(_words(work), max_chars=42 if not fmt.vertical else 32, max_lines=2, max_dur=7.0)
    out = work / "render"
    out.mkdir(exist_ok=True)
    (out / f"{name}.srt").write_text(lf.to_srt(cues, plan.get("voice_offset", 0.0)))
    (out / f"{name}.vtt").write_text(lf.to_vtt(cues, plan.get("voice_offset", 0.0)))
    print(f"{len(cues)} cues -> {out / (name + '.srt')}, {out / (name + '.vtt')}")


# ---------------------------------------------------------------- produce / preview

def _run_build(work, track, env=None):
    work = Path(work)
    old = dict(os.environ)
    os.environ.update(env or {})
    try:
        spec = importlib.util.spec_from_file_location(f"build_{abs(hash(str(work)))}", work / "build.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.build(track)
    finally:
        os.environ.clear()
        os.environ.update(old)


def cmd_produce(argv):
    import longmix
    import reelkit as rk
    pos, _ = _args(argv)
    work = Path(pos[0]).resolve()
    track = pos[1] if len(pos) > 1 else None
    rk.ensure_icons(["pointer", "check", "bell-ring", "message-circle"])
    longmix.prepare_voice(work)
    t0 = time.time()
    plan = _run_build(work, track)
    lib = rk.sfx_library()
    balance = longmix.mix(work, plan, lib)
    est = lf.estimate_render(plan["duration"], plan.get("fps", 30), _history(work))
    print(json.dumps({"duration": plan["duration"], "format": plan["format"], "style": plan["style"], "captions": len(plan["captions"]),
                      "chapters": len(plan["chapters"]), "segments": len(plan["segments"]), "sound_events": len(plan["sound_events"]),
                      "balance": balance, "render_estimate": est, "seconds": round(time.time() - t0, 1)}, indent=1))


def cmd_preview(argv):
    pos, opt = _args(argv)
    work = Path(pos[0]).resolve()
    times = pos[1]
    sheet = pos[2] if len(pos) > 2 else "sheet.jpg"
    target = work
    if opt.get("format"):
        fmt = fm.get(opt["format"])
        plan = json.loads((work / "plan.json").read_text()) if (work / "plan.json").exists() else {}
        if fmt.key != plan.get("format"):
            target = work / "variants" / fmt.key.replace(":", "x")
            target.mkdir(parents=True, exist_ok=True)
            (target / "qa").mkdir(exist_ok=True)
            _run_build(work, None, {"HEDITOR_LONG_FORMAT": fmt.key, "HEDITOR_LONG_OUT": str(target)})
    subprocess.run([sys.executable, str(KIT / "preview.py"), sheet, times, str(target)], check=True)


# ---------------------------------------------------------------- render (segmented, resumable)

def _history(work):
    p = Path(work) / "render/progress.json"
    if not p.exists():
        return []
    return [h for h in json.loads(p.read_text()).values() if h.get("seconds")]


def cmd_lint(argv):
    """HyperFrames lint of the whole-timeline page and of every segment page (0 errors required)."""
    pos, _ = _args(argv)
    work = Path(pos[0]).resolve()
    hf = shlex.split(os.environ.get("HEDITOR_HYPERFRAMES", "npx --yes hyperframes@0.9.13"))
    dirs = [work / "composition"] + sorted((work / "segments").glob("seg-*"))
    bad = 0
    for d in dirs:
        res = subprocess.run(hf + ["lint"], cwd=d, capture_output=True, text=True)
        tail = [ln for ln in (res.stdout + res.stderr).splitlines() if "error(s)" in ln]
        line = tail[-1].strip() if tail else (res.stdout + res.stderr).strip()[-200:]
        print(f"{d.relative_to(work)}: {line}")
        bad += res.returncode != 0 or not tail or not line.lstrip("◇ ").startswith("0 error")
    sys.exit(1 if bad else 0)


def cmd_estimate(argv):
    pos, opt = _args(argv)
    work = Path(pos[0])
    plan = json.loads((work / "plan.json").read_text())
    print(json.dumps(lf.estimate_render(plan["duration"], plan.get("fps", 30), _history(work), int(opt.get("workers", 2)))))


def _frames(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                          "stream=nb_read_packets", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()
    return int(out) if out.isdigit() else -1


def _acquire(path):
    """Exclusive lock (flock) on `path` for one heavy step; returns the open file (close it to release) or None."""
    if not path:
        return None
    import fcntl
    fh = open(path, "a")
    fcntl.flock(fh, fcntl.LOCK_EX)
    return fh


def cmd_render(argv):
    pos, opt = _args(argv)
    work = Path(pos[0]).resolve()
    workers = int(pos[1]) if len(pos) > 1 else 2
    cfg = _cfg(work)
    rcfg = cfg.get("render", {})
    segs = json.loads((work / "segments/index.json").read_text())
    out_dir = work / "render/segments"
    out_dir.mkdir(parents=True, exist_ok=True)
    prog_path = work / "render/progress.json"
    prog = json.loads(prog_path.read_text()) if prog_path.exists() else {}
    hf = shlex.split(os.environ.get("HEDITOR_HYPERFRAMES", "npx --yes hyperframes@0.9.13"))
    env = dict(os.environ, FFMPEG_ENCODE_TIMEOUT_MS=os.environ.get("FFMPEG_ENCODE_TIMEOUT_MS", "3600000"))
    total = sum(s["frames"] for s in segs)
    todo = [s for s in segs if not (prog.get(s["dir"], {}).get("hash") == s["hash"] and (out_dir / f"seg-{s['index']:03d}.mp4").exists()
                                    and _frames(out_dir / f"seg-{s['index']:03d}.mp4") == s["frames"])]
    est = lf.estimate_render(sum(s["frames"] for s in todo) / 30, 30, _history(work), workers)
    _log(work, "render/render.log", f"{len(segs)} segments, {len(segs) - len(todo)} ready, {len(todo)} to render "
                                    f"({sum(s['frames'] for s in todo)}/{total} frames); estimate {est['eta_s'] / 60:.1f} min")
    t_all = time.time()
    for k, s in enumerate(todo):
        out = out_dir / f"seg-{s['index']:03d}.mp4"
        lock = _acquire(os.environ.get("HEDITOR_LOCK"))  # shared machine: hold the heavy-job lock per segment
        t0 = time.time()
        cmd = hf + ["render", "--fps", str(cfg.get("fps", 30)), "--quality", "high", "--crf", str(rcfg.get("crf", 17)),
                    "--workers", str(workers), "--strict", "--no-best-effort", "--quiet", "--output", str(out)]
        res = subprocess.run(cmd, cwd=work / s["dir"], env=env, capture_output=True, text=True)
        if lock:
            lock.close()
        if res.returncode != 0:
            _log(work, "render/render.log", f"seg-{s['index']:03d} FAILED: {(res.stderr or res.stdout)[-1500:]}")
            sys.exit(1)
        got = _frames(out)
        dt = time.time() - t0
        prog[s["dir"]] = {"hash": s["hash"], "frames": s["frames"], "seconds": round(dt, 1), "got_frames": got}
        _save(prog_path, prog)
        hist = _history(work)
        left = sum(x["frames"] for x in todo[k + 1:])
        eta = lf.estimate_render(left / 30, 30, hist, workers)["eta_s"]
        _log(work, "render/render.log", f"seg-{s['index']:03d} {s['start']:.2f}-{s['end']:.2f}s {s['frames']} frames in {dt:.0f}s "
                                        f"({dt / max(1, s['frames']):.2f} s/frame) frames ok={got == s['frames']}; "
                                        f"{k + 1}/{len(todo)} done, ETA {eta / 60:.1f} min")
        if got != s["frames"]:
            _log(work, "render/render.log", f"seg-{s['index']:03d} frame count {got} != {s['frames']}")
            sys.exit(1)
    _log(work, "render/render.log", f"render done in {(time.time() - t_all) / 60:.1f} min")


def concat_segments(paths, out):
    """Concatenate equally-encoded segments without re-encoding (concat demuxer, -c copy)."""
    lst = Path(out).with_suffix(".txt")
    lst.write_text("".join(f"file '{Path(p).resolve()}'\n" for p in paths))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-map", "0:v:0", "-c", "copy",
                    "-movflags", "+faststart", str(out)], check=True)
    lst.unlink()
    return out


def mux_master(video, master, out, duration, brand_name, bitrate="256k"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(master), "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", bitrate, "-ar", str(SR), "-t", f"{duration:.4f}",
                    "-movflags", "+faststart", "-metadata", f"artist={brand_name}", str(out)], check=True)
    return out


def cmd_finalize(argv):
    import longqa
    import reelkit as rk
    pos, _ = _args(argv)
    work = Path(pos[0]).resolve()
    name = pos[1]
    plan = json.loads((work / "plan.json").read_text())
    segs = json.loads((work / "segments/index.json").read_text())
    paths = [work / "render/segments" / f"seg-{s['index']:03d}.mp4" for s in segs]
    missing = [p.name for p in paths if not p.exists()]
    if missing:
        print("missing segments:", missing, "-> heditor long render", work)
        sys.exit(1)
    video = concat_segments(paths, work / "render/video.mp4")
    tp = longqa.guard_true_peak(work, plan)
    final = mux_master(video, work / "composition/assets/master.wav", work / "render" / name, plan["duration"], rk.load_brand(work)["name"])
    stem = Path(name).stem
    cmd_subs([str(work), stem])
    chapters = plan["chapters"]
    (work / "render" / f"{stem}-chapters.txt").write_text(lf.youtube_timestamps(chapters, plan.get("voice_offset", 0.0)))
    report = longqa.run(work, final, tp_guard=tp)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=1))


def cmd_qa(argv):
    import longqa
    pos, opt = _args(argv)
    work = Path(pos[0]).resolve()
    name = pos[1] if len(pos) > 1 else None
    final = work / "render" / name if name else max((work / "render").glob("*.mp4"), key=lambda p: p.stat().st_mtime)
    report = longqa.run(work, final, asr=opt.get("asr", "1") != "0")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=1))


def cmd_sync(argv):
    import camera_sync_check as cs
    pos, _ = _args(argv)
    res = cs.sync_against_source(Path(pos[0]))
    print(json.dumps(res, indent=1))
    sys.exit(0 if res["ok"] else 1)


def main(argv):
    if not argv or argv[0] in ("help", "-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "styles":
        print(sp.table())
        return 0
    if cmd == "formats":
        print(fm.describe())
        return 0
    fn = {"new": cmd_new, "transcribe": cmd_transcribe, "edl": cmd_edl, "apply": cmd_apply, "chapters": cmd_chapters,
          "layouts": cmd_layouts, "subs": cmd_subs, "produce": cmd_produce, "preview": cmd_preview, "render": cmd_render,
          "finalize": cmd_finalize, "qa": cmd_qa, "sync": cmd_sync, "estimate": cmd_estimate, "lint": cmd_lint}.get(cmd)
    if not fn:
        print(f"unknown command {cmd!r}\n{__doc__}")
        return 2
    fn(rest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
