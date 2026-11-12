"""Optional local Earshot sound bank, without model downloads."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import wave
from pathlib import Path

REVISION = "4ac3d2ac2b151e1c23376f9ce7f3047a17050013"
HOME = Path(os.environ.get("HEDITOR_HOME", str(Path.home() / ".heditor")))
BINARY = HOME / "earshot" / "bin" / "earshot"


def setup():
    subprocess.run([sys.executable, "-m", "venv", str(HOME / "earshot")], check=True)
    pip = str(HOME / "earshot" / "bin" / "python")
    subprocess.run([pip, "-m", "pip", "install", "numpy>=1.26", "scipy>=1.11", "soundfile>=0.12", "pyloudnorm>=0.1"], check=True)
    subprocess.run([pip, "-m", "pip", "install", "--no-deps", f"git+https://github.com/Leonxlnx/earshot.git@{REVISION}"], check=True)


def run_earshot(args):
    executable = os.environ.get("HEDITOR_EARSHOT", str(BINARY))
    try:
        subprocess.run([executable, *args], check=True)
    except FileNotFoundError as exc:
        raise ValueError("Earshot not installed; run heditor earshot setup") from exc


def render(work, sound_id, category, duration, apex, seed):
    work = Path(work).resolve(strict=True)
    if not work.is_dir():
        raise ValueError("work directory does not exist")
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", category):
        raise ValueError("invalid category")
    if not re.fullmatch(r"[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+", sound_id):
        raise ValueError("sound id must be family/variant")
    if not 0 < duration <= 30 or not 0 <= apex <= duration:
        raise ValueError("invalid duration or apex")
    assets = work / "composition" / "assets" / "sfx-earshot"
    assets.mkdir(parents=True, exist_ok=True)
    out = assets / f"{category}-{seed}.wav"
    if out.exists():
        raise FileExistsError(str(out))
    try:
        run_earshot(["sfx", "render", sound_id, "-o", str(out), "--dur", str(duration), "--apex", str(apex), "--seed", str(seed)])
        with wave.open(str(out), "rb") as audio:
            if audio.getnframes() < 1:
                raise ValueError("empty generated audio")
        digest = hashlib.sha256(out.read_bytes()).hexdigest()
        manifest = work / "earshot-sfx.json"
        records = json.loads(manifest.read_text()) if manifest.exists() else []
        records.append({"category": category, "id": sound_id, "duration": duration, "apex": apex, "seed": seed,
                        "file": str(out.relative_to(work)), "sha256": digest,
                        "source": "https://github.com/Leonxlnx/earshot", "setup_revision": REVISION,
                        "binary_override": bool(os.environ.get("HEDITOR_EARSHOT")), "license": "MIT"})
        manifest.write_text(json.dumps(records, indent=2) + "\n")
    except Exception:
        out.unlink(missing_ok=True)
        raise
    print(f"{out}\ncategory: earshot_{category}; provenance: {manifest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("setup")
    sub.add_parser("list")
    p = sub.add_parser("render")
    p.add_argument("work")
    p.add_argument("id")
    p.add_argument("--category", required=True)
    p.add_argument("--duration", type=float, required=True)
    p.add_argument("--apex", type=float, required=True)
    p.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    try:
        if args.command == "setup":
            setup()
        elif args.command == "list":
            run_earshot(["sfx", "list"])
        else:
            render(args.work, args.id, args.category, args.duration, args.apex, args.seed)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"earshot: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
