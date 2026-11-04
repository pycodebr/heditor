"""Unit tests for studykit (heditor study): JSON parsing, summary numbers, Markdown and compare. No HyperFrames run."""
import json

import pytest

import studykit as sk

PROBE = {"ok": True, "width": 720, "height": 1280, "fps": 30, "duration": 60.0, "vfr": False, "hdr": False}
CUTS = {
    "ok": True, "fps": 30, "end": 60.0,
    "cuts": [{"t": 3.0, "frame": 90}, {"t": 9.0, "frame": 270, "frames": 3}, {"t": 30.0, "frame": 900},
             {"t": 45.0, "frame": 1350}, {"t": 50.0, "frame": 1500}],
    "not_cuts": [{"t": 12.0}],
    "shots": [{"start": 0, "end": 3.0, "seconds": 3.0}, {"start": 3.0, "end": 9.0, "seconds": 6.0},
              {"start": 9.0, "end": 30.0, "seconds": 21.0}, {"start": 30.0, "end": 45.0, "seconds": 15.0},
              {"start": 45.0, "end": 50.0, "seconds": 5.0}, {"start": 50.0, "end": 60.0, "seconds": 10.0}],
}
EVENTS = {
    "counts": {"cut": 5, "flash": 1, "appear": 12, "disappear": 6, "change": 12, "hold": 3},
    "holds": [{"t": 1.0, "seconds": 2.0}, {"t": 20.0, "seconds": 3.0}, {"t": 40.0, "seconds": 1.0}],
    "sound": {"bpm": None, "strong_onsets": [1.0, 2.0, 5.0, 7.0, 9.0, 11.0]},
}
LOOK = {"luma": 53.2, "contrast": 51.5, "saturation": 0.252, "bw_share": 0.36, "warmth": 6.9}
FACE = {"frames_sampled": 10, "frames_with_face": 8, "face_height": 0.21}
AUDIO = {"version": 1, "items": [{
    "kind": {"value": "speech", "features": {"voiced": 0.61}},
    "loudness": {"lufsIntegrated": -14.1, "truePeakDb": -1.6},
    "silence": [{"start": 8.0, "end": 9.0}, {"start": 30.0, "end": 31.5}],
    "bpm": {"value": 120},
    "sections": {"spans": [{"start": 0, "end": 30, "label": "A"}, {"start": 30, "end": 60, "label": "B"}]},
}]}


def test_parse_json_output_skips_progress_lines():
    assert sk.parse_json_output('Installing…\n{"ok": true, "n": 2}') == {"ok": True, "n": 2}
    with pytest.raises(ValueError):
        sk.parse_json_output("no json here")


def test_summary_rhythm():
    s = sk.summarize(probe=PROBE, cuts=CUTS, events=EVENTS)
    assert s["duration_s"] == 60.0 and s["shots"] == 6 and s["cuts"] == 5
    assert s["shot_mean_s"] == 10.0 and s["shot_median_s"] == 8.0
    assert s["shot_min_s"] == 3.0 and s["shot_max_s"] == 21.0
    assert s["first_cut_s"] == 3.0
    assert s["cuts_per_10s"] == pytest.approx(0.83, abs=0.01)
    # thirds of 20 s: cuts at 3 and 9 | 30 | 45 and 50
    assert s["cuts_per_10s_by_third"] == [1.0, 0.5, 1.0]
    assert s["transition_cuts"] == 1 and s["not_cuts"] == 1
    assert s["screen_events_per_10s"] == 5.0 and s["appear_per_10s"] == 2.0
    assert s["holds"] == 3 and s["holds_share"] == pytest.approx(0.1)
    assert s["strong_onsets_per_10s"] == 1.0 and s["flashes"] == 1


def test_summary_sound_look_face():
    s = sk.summarize(probe=PROBE, cuts=CUTS, events=EVENTS, look=LOOK, face=FACE, audio=AUDIO)
    assert s["audio_kind"] == "speech" and s["audio_voiced"] == 0.61
    assert s["lufs_integrated"] == -14.1 and s["true_peak_db"] == -1.6
    assert s["silences"] == 2 and s["silence_share"] == pytest.approx(0.04, abs=0.001)
    assert s["bpm"] == 120 and len(s["music_sections"]) == 2
    assert s["luma"] == 53.2 and s["bw_share"] == 0.36
    assert s["face_height"] == 0.21 and s["face_share_of_samples"] == 0.8


def test_summary_tolerates_missing_measurements():
    s = sk.summarize(probe=PROBE)
    assert s["shots"] == 0 and s["shot_mean_s"] is None and s["cuts_per_10s"] == 0.0
    assert s["silence_share"] is None and s["face_share_of_samples"] is None
    assert sk.summarize()["duration_s"] == 0.0


def test_markdown_lists_every_measure():
    md = sk.render_md(sk.summarize(probe=PROBE, cuts=CUTS, events=EVENTS, look=LOOK, face=FACE, audio=AUDIO), "a.mp4")
    assert md.startswith("| Measure | Value |")
    for label in ("Shots (cuts)", "Cuts per 10 s", "Strong sound onsets", "Loudness", "Look:", "Face height"):
        assert label in md


def test_compare_ratios(tmp_path):
    ref = sk.summarize(probe=PROBE, cuts=CUTS, events=EVENTS, look=LOOK)
    ours = dict(ref, shot_mean_s=5.0, luma=None)
    rows = {label: (a, b, r) for label, a, b, r in sk.compare(ref, ours)}
    assert rows["mean shot length (s)"] == (10.0, 5.0, 0.5)
    assert rows["brightness (luma)"][2] is None
    path = tmp_path / "study.json"
    path.write_text(json.dumps({"summary": ref}))
    assert sk._load_summary(path) == ref
    assert sk.cmd_compare(type("A", (), {"reference": str(path), "yours": str(path)})()) == 0


def test_audio_never_uploads(monkeypatch, tmp_path):
    """heditor study must run `audio` with --quality local (best uploads to HeyGen and may bill)."""
    calls = []

    def fake_run(args, out_path, timeout=900):
        calls.append(args)
        return {"ok": True, "duration": 10.0} if args[:2] == ["measure", "probe"] else None

    monkeypatch.setattr(sk, "run_hf", fake_run)
    video = tmp_path / "v.mp4"
    video.write_bytes(b"x")
    sk.main([str(video), "--out", str(tmp_path / "s"), "--no-frames"])
    audio = [c for c in calls if c[0] == "audio"]
    assert audio and audio[0][audio[0].index("--quality") + 1] == "local"
    assert not any("cloud" in c or "reverse" in c or "generate" in c for c in calls)
    assert (tmp_path / "s" / "study.json").exists() and (tmp_path / "s" / "study.md").exists()


def test_probe_failure_stops_before_writing(monkeypatch, tmp_path, capsys):
    """An old HyperFrames without `measure` must not leave a study full of empty numbers."""
    monkeypatch.setattr(sk, "run_hf", lambda args, out_path, timeout=900: None)
    video = tmp_path / "v.mp4"
    video.write_bytes(b"x")
    assert sk.main([str(video), "--out", str(tmp_path / "s")]) == 1
    assert not (tmp_path / "s" / "study.json").exists()
    assert "hyperframes 0.9" in capsys.readouterr().err


def test_markdown_flags_missing_measurements():
    md = sk.render_md(sk.summarize(probe=PROBE, cuts=CUTS), "a.mp4", ["audio", "face"])
    assert "Missing measurements:** audio, face" in md
