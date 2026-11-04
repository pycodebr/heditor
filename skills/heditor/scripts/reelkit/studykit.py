#!/usr/bin/env python3
"""studykit: measure a reference video's edit with HyperFrames' local tools and turn it into style targets.

`heditor study` is the first step of deriving a style from reference videos (Reels, ads, explainers someone wants to
emulate). It runs the pinned HyperFrames CLI on this machine only:

  measure probe        size, frame rate, duration, VFR/HDR warnings
  measure cuts         hard cuts from the frame-to-frame difference (jump cuts and punch-ins included) and the shots
  measure events --map what changes on screen and when (appear, disappear, change, hold) with the sound's strong onsets
  measure look         brightness, contrast, saturation, black-and-white share, warmth
  measure face         how big the speaker's face is and where
  audio --quality local  kind, loudness, silences, onsets, tempo and sections of the soundtrack
  measure frames       an overview contact sheet (one frame every N seconds)

and writes the raw JSON plus `study.json` (the numbers a style needs) and `study.md` (a table to paste into the
analysis). `heditor study compare <ref>/study.json <ours>/study.json` puts a pilot's rhythm next to the reference's.

Nothing here signs in, uploads or spends credits: `audio` always runs with `--quality local` (the `best` quality uploads
to HeyGen's audio services and may bill the account). Paid HyperFrames features (reverse-any-video, cloud render,
generated media) are never called from this tool; see references/reference-study.md.

CLI (through `heditor`):
  heditor study <video> [--out DIR] [--every 2] [--no-audio] [--no-face] [--no-frames]
  heditor study compare <reference_study.json> <yours_study.json>
"""
import argparse
import json
import os
import shlex
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_HF = "npx --yes hyperframes@0.9.13"
AUDIO_CAPABILITIES = "kind,moments,onsets,loudness,silence,bpm,sections"
COMPARE_KEYS = (
    ("shot_mean_s", "mean shot length (s)"),
    ("shot_median_s", "median shot length (s)"),
    ("cuts_per_10s", "cuts per 10 s"),
    ("screen_events_per_10s", "on-screen events per 10 s (appear + disappear + change)"),
    ("holds_share", "share of time in holds"),
    ("strong_onsets_per_10s", "strong sound onsets per 10 s"),
    ("lufs_integrated", "integrated loudness (LUFS)"),
    ("silence_share", "share of time in silence"),
    ("luma", "brightness (luma)"),
    ("contrast", "contrast"),
    ("saturation", "saturation"),
    ("bw_share", "black-and-white share"),
    ("warmth", "warmth"),
    ("face_height", "face height / frame height"),
)


def hf_command():
    """The HyperFrames command heditor is pinned to (env.sh may override it)."""
    return shlex.split(os.environ.get("HEDITOR_HYPERFRAMES", DEFAULT_HF))


def parse_json_output(text):
    """HyperFrames prints JSON on stdout, sometimes after a progress line: read from the first brace."""
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON in the output")
    return json.loads(text[start:])


def run_hf(args, out_path, timeout=900):
    """Run one HyperFrames command, keep its JSON in out_path and return it (None when it failed)."""
    env = dict(os.environ, HYPERFRAMES_NO_UPDATE_CHECK="1")
    cmd = hf_command() + list(args)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        print(f"  ! timed out: {' '.join(args[:2])}", file=sys.stderr)
        return None
    try:
        data = parse_json_output(proc.stdout)
    except ValueError:
        tail = (proc.stderr or proc.stdout)[-300:].strip()
        print(f"  ! {' '.join(args[:2])} failed (exit {proc.returncode}): {tail}", file=sys.stderr)
        return None
    Path(out_path).write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    return data


def _per_10s(count, duration):
    return round(count * 10.0 / duration, 2) if duration else None


def _round(value, digits=2):
    return round(value, digits) if isinstance(value, (int, float)) else None


def _thirds(cut_times, duration):
    """Cuts per 10 s in the first, middle and last third of the video."""
    if not duration:
        return [None, None, None]
    third = duration / 3.0
    counts = [0, 0, 0]
    for t in cut_times:
        counts[min(int(t // third), 2)] += 1
    return [_per_10s(c, third) for c in counts]


def summarize(probe=None, cuts=None, events=None, look=None, face=None, audio=None):
    """The numbers that describe an edit, from the raw HyperFrames measurements (any of them may be missing)."""
    probe, cuts, events = probe or {}, cuts or {}, events or {}
    look, face, audio = look or {}, face or {}, audio or {}
    duration = probe.get("duration") or cuts.get("end") or events.get("duration") or 0.0
    out = {
        "duration_s": _round(duration),
        "width": probe.get("width"),
        "height": probe.get("height"),
        "fps": probe.get("fps") or cuts.get("fps"),
        "vfr": probe.get("vfr"),
        "hdr": probe.get("hdr"),
    }

    shots = [s.get("seconds", s.get("end", 0) - s.get("start", 0)) for s in cuts.get("shots", [])]
    cut_list = cuts.get("cuts", [])
    cut_times = [c["t"] for c in cut_list if "t" in c]
    out.update({
        "shots": len(shots),
        "shot_mean_s": _round(statistics.mean(shots)) if shots else None,
        "shot_median_s": _round(statistics.median(shots)) if shots else None,
        "shot_min_s": _round(min(shots)) if shots else None,
        "shot_max_s": _round(max(shots)) if shots else None,
        "first_cut_s": _round(min(cut_times)) if cut_times else None,
        "cuts": len(cut_times),
        "cuts_per_10s": _per_10s(len(cut_times), duration),
        "cuts_per_10s_by_third": _thirds(cut_times, duration),
        "transition_cuts": sum(1 for c in cut_list if c.get("frames", 1) > 1),
        "not_cuts": len(cuts.get("not_cuts", [])),
    })

    counts = events.get("counts", {})
    holds = events.get("holds", [])
    hold_total = sum(h.get("seconds", 0) for h in holds)
    screen_events = sum(counts.get(k, 0) for k in ("appear", "disappear", "change"))
    strong = (events.get("sound") or {}).get("strong_onsets") or []
    out.update({
        "event_counts": counts,
        "screen_events_per_10s": _per_10s(screen_events, duration),
        "appear_per_10s": _per_10s(counts.get("appear", 0), duration),
        "flashes": counts.get("flash", 0),
        "holds": len(holds),
        "holds_share": _round(hold_total / duration) if duration else None,
        "strong_onsets_per_10s": _per_10s(len(strong), duration),
    })

    item = (audio.get("items") or [{}])[0]
    loud = item.get("loudness") or {}
    silences = item.get("silence") or []
    silence_total = sum(max(0.0, s.get("end", 0) - s.get("start", 0)) for s in silences)
    kind = item.get("kind") or {}
    out.update({
        "audio_kind": kind.get("value"),
        "audio_voiced": _round((kind.get("features") or {}).get("voiced")),
        "lufs_integrated": loud.get("lufsIntegrated"),
        "true_peak_db": loud.get("truePeakDb"),
        "silences": len(silences),
        "silence_share": _round(silence_total / duration) if duration and audio else None,
        "bpm": (item.get("bpm") or {}).get("value"),
        "music_sections": [(s.get("start"), s.get("end"), s.get("label"))
                           for s in (item.get("sections") or {}).get("spans", [])],
    })

    out.update({k: look.get(k) for k in ("luma", "contrast", "saturation", "bw_share", "warmth")})
    sampled = face.get("frames_sampled") or 0
    out.update({
        "face_height": face.get("face_height"),
        "face_share_of_samples": _round(face.get("frames_with_face", 0) / sampled) if sampled else None,
    })
    return out


def render_md(summary, video, missing=()):
    """A Markdown table of the study, ready to paste into a reference analysis."""
    s = summary
    thirds = s.get("cuts_per_10s_by_third") or [None, None, None]
    rows = [
        ("Video", f"`{video}`"),
        ("Size / fps / duration", f"{s.get('width')}x{s.get('height')} / {s.get('fps')} / {s.get('duration_s')} s"),
        ("Shots (cuts)", f"{s.get('shots')} ({s.get('cuts')}, {s.get('transition_cuts')} over several frames)"),
        ("Shot length mean / median / min / max", f"{s.get('shot_mean_s')} / {s.get('shot_median_s')} / "
                                                  f"{s.get('shot_min_s')} / {s.get('shot_max_s')} s"),
        ("First cut", f"{s.get('first_cut_s')} s"),
        ("Cuts per 10 s (whole; thirds)", f"{s.get('cuts_per_10s')}; {thirds[0]} / {thirds[1]} / {thirds[2]}"),
        ("On-screen events per 10 s (appear)", f"{s.get('screen_events_per_10s')} ({s.get('appear_per_10s')})"),
        ("Holds (share of time), flashes", f"{s.get('holds')} ({s.get('holds_share')}), {s.get('flashes')}"),
        ("Strong sound onsets per 10 s", f"{s.get('strong_onsets_per_10s')}"),
        ("Sound kind (voiced share), BPM", f"{s.get('audio_kind')} ({s.get('audio_voiced')}), {s.get('bpm')}"),
        ("Loudness / true peak", f"{s.get('lufs_integrated')} LUFS / {s.get('true_peak_db')} dBTP"),
        ("Silences (share of time)", f"{s.get('silences')} ({s.get('silence_share')})"),
        ("Look: luma / contrast / saturation / B&W / warmth", f"{s.get('luma')} / {s.get('contrast')} / "
                                                              f"{s.get('saturation')} / {s.get('bw_share')} / "
                                                              f"{s.get('warmth')}"),
        ("Face height (share of samples with a face)", f"{s.get('face_height')} ({s.get('face_share_of_samples')})"),
    ]
    lines = ["| Measure | Value |", "|---|---|"] + [f"| {k} | {v} |" for k, v in rows]
    if missing:
        lines += ["", f"**Missing measurements:** {', '.join(missing)}. Their rows are empty, not zero."]
    lines += ["", "Measured locally with HyperFrames (`heditor study`); numbers describe rhythm and look, not quality.",
              "Read the overview sheets and the event strips before turning a number into a rule."]
    return "\n".join(lines) + "\n"


def compare(ref, yours):
    """Rows of (label, reference, yours, ratio) for the keys both studies have."""
    rows = []
    for key, label in COMPARE_KEYS:
        a, b = ref.get(key), yours.get(key)
        ratio = round(b / a, 2) if isinstance(a, (int, float)) and isinstance(b, (int, float)) and a else None
        rows.append((label, a, b, ratio))
    return rows


def cmd_study(args):
    video = Path(args.video).resolve()
    if not video.exists():
        print(f"no such video: {video}", file=sys.stderr)
        return 2
    out = Path(args.out or f"study-{video.stem}").resolve()
    out.mkdir(parents=True, exist_ok=True)
    print(f"studying {video.name} -> {out}")
    raw = {}
    steps = [
        ("probe", ["measure", "probe", str(video)]),
        ("cuts", ["measure", "cuts", str(video)]),
        ("events", ["measure", "events", str(video), "--map"]),
        ("look", ["measure", "look", str(video)]),
    ]
    if not args.no_face:
        steps.append(("face", ["measure", "face", str(video), "--samples", "12"]))
    if not args.no_audio:
        steps.append(("audio", ["audio", str(video), "--only", AUDIO_CAPABILITIES, "--quality", "local", "--json"]))
    for name, hf_args in steps:
        print(f"  {name}...")
        raw[name] = run_hf(hf_args, out / f"{name}.json")
        if name == "probe" and raw[name] is None:
            print("HyperFrames could not probe the video. heditor study needs hyperframes 0.9 or newer: run "
                  "`heditor setup` (or check HEDITOR_HYPERFRAMES in ~/.heditor/env.sh).", file=sys.stderr)
            return 1
    if not args.no_frames:
        print("  frames...")
        run_hf(["measure", "frames", str(video), "--every", str(args.every), "--out", str(out / "frames")],
               out / "frames.json")
    summary = summarize(**{k: raw.get(k) for k in ("probe", "cuts", "events", "look", "face", "audio")})
    record = {
        "video": str(video),
        "measured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "hyperframes": " ".join(hf_command()),
        "missing": sorted(k for k, v in raw.items() if v is None),
        "summary": summary,
    }
    (out / "study.json").write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
    markdown = render_md(summary, video.name, record["missing"])
    (out / "study.md").write_text(markdown, encoding="utf-8")
    print(markdown)
    if record["missing"]:
        print(f"missing measurements: {', '.join(record['missing'])}", file=sys.stderr)
    print(f"wrote {out / 'study.json'} and {out / 'study.md'}")
    return 0 if raw.get("cuts") and raw.get("probe") else 1


def _load_summary(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data.get("summary", data)


def cmd_compare(args):
    rows = compare(_load_summary(args.reference), _load_summary(args.yours))
    print("| Measure | Reference | Yours | Yours / reference |")
    print("|---|---|---|---|")
    for label, a, b, ratio in rows:
        print(f"| {label} | {a} | {b} | {ratio} |")
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["compare"]:
        ap = argparse.ArgumentParser(prog="heditor study compare")
        ap.add_argument("reference")
        ap.add_argument("yours")
        return cmd_compare(ap.parse_args(argv[1:]))
    ap = argparse.ArgumentParser(prog="heditor study", description=__doc__.split("\n\n")[0])
    ap.add_argument("video")
    ap.add_argument("--out", help="folder for the measurements (default: ./study-<video name>)")
    ap.add_argument("--every", type=float, default=2.0, help="seconds between frames of the overview sheet")
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--no-face", action="store_true")
    ap.add_argument("--no-frames", action="store_true")
    return cmd_study(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
