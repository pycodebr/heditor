"""Unit tests for genkit (no HeyGen account needed): cost estimates and the blur-frame remover."""
import json
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import genkit as gk  # noqa: E402


def _home(tmp_path, monkeypatch, hist=None):
    monkeypatch.setenv("HEDITOR_HOME", str(tmp_path))
    if hist is not None:
        (tmp_path / "heygen-usage.json").write_text(json.dumps(hist))


def test_default_rates_and_estimate(tmp_path, monkeypatch):
    _home(tmp_path, monkeypatch)
    c = gk.estimate("persona", "identity_remix", None, 3, "subscription")
    assert c["unit"] == "credits" and c["amount"] == 18.0
    v = gk.estimate("clip", "image_to_video", "480p", 5, "wallet")
    assert v["unit"] == "usd" and v["amount"] == 0.1
    assert "unknown" in gk.fmt_cost(gk.estimate("clip", "image_to_video", "2k", 5, "subscription"))


def test_measured_history_wins(tmp_path, monkeypatch):
    _home(tmp_path, monkeypatch, [{"kind": "talk", "mode": "avatar_iv_image", "res": "-", "units": 10,
                                   "credits_spent": 5}])
    r = gk.rate("talk", "avatar_iv_image", None)
    assert abs(r["credits"] - 0.5) < 1e-9 and r["measured_jobs"] == 1


def _textured(h, w, seed=1):
    rng = np.random.default_rng(seed)
    return (rng.integers(0, 255, (h, w, 3))).astype(np.uint8)


def test_unframe_removes_a_blur_fill_frame(tmp_path):
    import cv2
    h, w = 768, 432
    inner = _textured(int(h * 0.8), int(w * 0.8))
    bg = cv2.GaussianBlur(cv2.resize(inner, (w, h)), (0, 0), 25)
    y0, x0 = int(h * 0.1), int(w * 0.1)
    bg[y0:y0 + inner.shape[0], x0:x0 + inner.shape[1]] = inner
    p = tmp_path / "s.png"
    cv2.imwrite(str(p), bg)
    m = gk.unframe(p)
    assert m and min(m.values()) > 0.05
    out = cv2.imread(str(p))
    assert out.shape[:2] == (h, w) and (tmp_path / "s.framed.png").exists()


def test_unframe_keeps_a_photo_with_one_soft_side(tmp_path):
    import cv2
    h, w = 768, 432
    img = _textured(h, w)
    img[: int(h * 0.15)] = cv2.GaussianBlur(img[: int(h * 0.15)], (0, 0), 20)   # a plain sky on top only
    p = tmp_path / "s.png"
    cv2.imwrite(str(p), img)
    assert gk.unframe(p) is None and not (tmp_path / "s.framed.png").exists()


def test_upload_passes_urls_and_asset_ids():
    assert gk.upload("https://example.com/a.jpg") == {"type": "url", "url": "https://example.com/a.jpg"}
    aid = "0123456789abcdef0123456789abcdef"
    if not os.path.exists(aid):
        assert gk.upload(aid) == {"type": "asset_id", "asset_id": aid}
