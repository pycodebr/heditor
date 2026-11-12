import json
import wave
from pathlib import Path
from unittest import mock

import pytest

import earshot_sfx
import openverse_sfx
import sfx_sources


def wav(path):
    with wave.open(str(path), "wb") as audio:
        audio.setparams((1, 2, 48000, 4800, "NONE", "not compressed"))
        audio.writeframes(b"\x00\x00" * 4800)


def sample():
    return {"id": "190ad6b8-fcca-4925-a74c-e4886f108fee", "title": "Test", "creator": "Author",
            "license": "cc0", "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "foreign_landing_url": "https://example.org/source", "url": "https://example.org/preview.mp3"}


def test_openverse_defaults_and_licence_filter():
    with mock.patch.object(openverse_sfx, "request", return_value={"results": [sample()]}) as req:
        assert openverse_sfx.search("click")[0]["license"] == "cc0"
        assert req.call_args.kwargs["params"]["license"] == "cc0"
    with pytest.raises(ValueError):
        openverse_sfx.search("click", limit=100)


def test_register_requires_verification_and_preserves_provenance(tmp_path):
    source = tmp_path / "original.wav"
    wav(source)
    item = sample()
    with mock.patch.object(openverse_sfx, "request", return_value=item):
        with pytest.raises(ValueError):
            openverse_sfx.register(tmp_path, item["id"], source, "click", False)
        record = openverse_sfx.register(tmp_path, item["id"], source, "click", True)
        assert record["file_is_original_unverified"] is True
        assert record["creator"] == "Author"
        library = sfx_sources.load(tmp_path, {})
        assert Path(library["openverse_click"]["files"][0]).exists()
        with pytest.raises(FileExistsError):
            openverse_sfx.register(tmp_path, item["id"], source, "click", True)
        Path(library["openverse_click"]["files"][0]).write_bytes(b"tampered")
        with pytest.raises(ValueError, match="changed"):
            sfx_sources.load(tmp_path, {})


def test_reject_unsupported_licenses(tmp_path):
    source = tmp_path / "audio.wav"
    wav(source)
    item = sample()
    item["license"] = "by-nc"
    with mock.patch.object(openverse_sfx, "request", return_value=item), pytest.raises(ValueError):
        openverse_sfx.register(tmp_path, item["id"], source, "click", True)


def test_earshot_render_and_no_overwrite(tmp_path):
    def fake_run(args):
        wav(Path(args[args.index("-o") + 1]))
    with mock.patch.object(earshot_sfx, "run_earshot", fake_run):
        earshot_sfx.render(tmp_path, "whoosh_fast/crisp", "swipe", .8, .32, 4)
        record = json.loads((tmp_path / "earshot-sfx.json").read_text())[0]
        assert record["id"] == "whoosh_fast/crisp"
        assert sfx_sources.load(tmp_path, {})["earshot_swipe"]["trim"] == ("head", 30.0)
        with pytest.raises(FileExistsError):
            earshot_sfx.render(tmp_path, "whoosh_fast/crisp", "swipe", .8, .32, 4)
        with pytest.raises(ValueError):
            earshot_sfx.render(tmp_path, "../bad", "swipe", .8, .32, 4)


def test_manifest_rejects_path_outside_assets(tmp_path):
    external = tmp_path / "secret.wav"
    wav(external)
    (tmp_path / "earshot-sfx.json").write_text(json.dumps([{"category": "x", "file": "secret.wav", "sha256": "x"}]))
    with pytest.raises(ValueError, match="outside"):
        sfx_sources.load(tmp_path, {})
