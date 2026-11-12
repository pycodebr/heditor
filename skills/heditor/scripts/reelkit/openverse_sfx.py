"""Search Openverse and register independently verified local audio for a cut."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.openverse.org/v1/audio/"
USER_AGENT = "heditor-sfx/1.0 (+https://github.com/pycodebr/heditor)"


def request(path="", params=None):
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)


def search(query, license_name="cc0", limit=10):
    if not 1 <= limit <= 20:
        raise ValueError("limit must be between 1 and 20")
    result = request(params={"q": query, "license": license_name, "page_size": limit})
    fields = ("id", "title", "creator", "license", "license_version", "license_url", "foreign_landing_url", "url", "filesize", "duration")
    return [{key: item.get(key) for key in fields} for item in result.get("results", [])]


def register(work, item_id, file_path, category, verified):
    if not verified:
        raise ValueError("inspect the original page and pass --verified-origin")
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", category):
        raise ValueError("category must contain only letters, digits, underscore and hyphen")
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", item_id):
        raise ValueError("invalid Openverse UUID")
    source = Path(file_path).resolve(strict=True)
    if not source.is_file():
        raise ValueError("audio must be a file")
    item = request(item_id + "/")
    license_name = str(item.get("license", "")).lower()
    if license_name not in {"cc0", "by"}:
        raise ValueError("only CC0 and CC BY are supported")
    if not item.get("foreign_landing_url") or not item.get("license_url"):
        raise ValueError("source URL and license URL are required")
    if license_name == "by" and not item.get("creator"):
        raise ValueError("CC BY requires creator attribution")
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name", "-of", "json", str(source)], capture_output=True, text=True, check=True)
    if not json.loads(probe.stdout).get("streams"):
        raise ValueError("file has no audio stream")
    work = Path(work).resolve()
    if not work.is_dir():
        raise ValueError("work directory does not exist")
    destdir = work / "composition" / "assets" / "sfx-openverse"
    destdir.mkdir(parents=True, exist_ok=True)
    suffix = source.suffix.lower()
    if not re.fullmatch(r"\.[a-z0-9]{1,5}", suffix):
        raise ValueError("unsupported file extension")
    dest = destdir / (category + "-" + item_id + suffix)
    if dest.exists():
        raise FileExistsError(str(dest))
    manifest = work / "openverse-sfx.json"
    data = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
    record = {key: item.get(key) for key in ("id", "title", "creator", "license", "license_version", "license_url", "foreign_landing_url", "url")}
    with source.open("rb") as audio:
        digest = hashlib.sha256()
        for chunk in iter(lambda: audio.read(1024 * 1024), b""):
            digest.update(chunk)
    record.update({"category": category, "file": str(dest.relative_to(work)), "origin_verified": True,
                   "file_is_original_unverified": True, "sha256": digest.hexdigest()})
    shutil.copyfile(source, dest)
    data.append(record)
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--license", choices=["cc0", "by"], default="cc0")
    p.add_argument("--limit", type=int, default=10)
    p = sub.add_parser("import")
    p.add_argument("work")
    p.add_argument("id")
    p.add_argument("file")
    p.add_argument("--category", required=True)
    p.add_argument("--verified-origin", action="store_true")
    args = parser.parse_args()
    try:
        result = search(args.query, args.license, args.limit) if args.command == "search" else register(args.work, args.id, args.file, args.category, args.verified_origin)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"openverse: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
