"""Build the composition and the mix of a cut: produce.py <folder_with_build.py> <track.mp3|music:ID> <drop_s>."""
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import reelkit as rk  # noqa: E402
import sfx_sources  # noqa: E402

folder, track, drop = Path(sys.argv[1]), sys.argv[2], float(sys.argv[3])
if track.startswith("music:"):
    track = rk.music_path(track)
spec = importlib.util.spec_from_file_location("build", folder / "build.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
plan = mod.build(track, drop)
lib = mod.sfx_lib() if hasattr(mod, "sfx_lib") else rk.sfx_library()
lib = sfx_sources.load(mod.WORK, lib)
balance = rk.mix(mod.WORK, plan, lib)
print(json.dumps({"duration": plan["duration"], "captions": len(plan["captions"]), "sound_events": len(plan["sound_events"]), "balance": balance}, indent=1))
