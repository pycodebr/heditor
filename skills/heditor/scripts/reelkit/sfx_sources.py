"""Load opt-in project SFX manifests into the existing heditor mixer."""
import hashlib
import json
from pathlib import Path


def load(work, library):
    work = Path(work).resolve()
    for source in ("earshot", "openverse"):
        manifest = work / f"{source}-sfx.json"
        if not manifest.exists():
            continue
        for item in json.loads(manifest.read_text(encoding="utf-8")):
            path = (work / item["file"]).resolve(strict=True)
            if not path.is_relative_to(work / "composition" / "assets"):
                raise ValueError("SFX file is outside the project assets")
            digest = hashlib.sha256()
            with path.open("rb") as audio:
                for chunk in iter(lambda: audio.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != item["sha256"]:
                raise ValueError(f"SFX file changed after registration: {path}")
            key = f"{source}_{item['category']}"
            library.setdefault(key, {"files": [], "trim": ("head", 30.0)})["files"].append(str(path))
    return library
