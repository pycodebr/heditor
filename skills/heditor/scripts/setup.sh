#!/usr/bin/env bash
# heditor setup: installs/validates every tool the skill needs and downloads the asset library.
# Usage: bash setup.sh [--no-audio] [--whisper small,medium] [--depth] [--yes]
# Safe to re-run (idempotent). Everything lives in $HEDITOR_HOME (default ~/.heditor).
set -euo pipefail

HYPERFRAMES_VERSION="0.9.13"
HEDITOR_HOME="${HEDITOR_HOME:-$HOME/.heditor}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WHISPER="small"
FETCH_ARGS=()
ASSUME_YES=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-audio) FETCH_ARGS+=(--no-audio); shift ;;
    --whisper) WHISPER="$2"; shift 2 ;;
    --depth) FETCH_ARGS+=(--depth); shift ;;
    --yes|-y) ASSUME_YES=1; shift ;;
    *) echo "unknown option: $1"; exit 2 ;;
  esac
done

say() { printf '\033[1;33m[heditor]\033[0m %s\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }
SUDO=""
if [[ $(id -u) -ne 0 ]] && have sudo; then SUDO="sudo"; fi

install_pkgs() {
  # $@: generic names; mapped per package manager
  if have brew; then brew install "$@"
  elif have apt-get; then $SUDO apt-get update -y && $SUDO apt-get install -y "$@"
  elif have dnf; then $SUDO dnf install -y "$@"
  elif have pacman; then $SUDO pacman -Sy --noconfirm "$@"
  else return 1; fi
}

mkdir -p "$HEDITOR_HOME"
say "HEDITOR_HOME=$HEDITOR_HOME"

# 1) system tools ------------------------------------------------------------
for tool in curl git; do
  have "$tool" || { say "installing $tool"; install_pkgs "$tool" || { say "please install $tool manually"; exit 1; }; }
done
if ! have ffmpeg || ! have ffprobe; then
  say "installing ffmpeg"; install_pkgs ffmpeg || { say "please install ffmpeg (https://ffmpeg.org/download.html)"; exit 1; }
fi
# HyperFrames (hyperframes@0.9.x) declares engines.node >= 22; an older Node passes npx but can fail at render.
if ! have node || [[ $(node -p 'process.versions.node.split(".")[0]') -lt 22 ]]; then
  say "installing Node.js >= 22"
  if have brew; then brew install node
  elif have apt-get; then curl -fsSL https://deb.nodesource.com/setup_22.x | $SUDO bash - && $SUDO apt-get install -y nodejs
  else install_pkgs nodejs npm || { say "please install Node.js >= 22 (https://nodejs.org)"; exit 1; }; fi
fi
PY=""
for cand in python3.13 python3.12 python3.11 python3.10 python3; do
  if have "$cand" && "$cand" -c 'import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] <= (3,13) else 1)' 2>/dev/null; then PY="$cand"; break; fi
done
if [[ -z "$PY" ]]; then
  say "installing Python 3.12"; install_pkgs python3.12 python3.12-venv || install_pkgs python3 python3-venv || true
  for cand in python3.12 python3; do have "$cand" && PY="$cand" && break; done
fi
[[ -n "$PY" ]] || { say "Python 3.10-3.13 is required (mediapipe has no wheels for newer versions yet)"; exit 1; }
"$PY" -c 'import venv' 2>/dev/null || install_pkgs python3-venv || true

# 2) python venv --------------------------------------------------------------
VENV="$HEDITOR_HOME/venv"
if [[ ! -x "$VENV/bin/python" ]]; then say "creating venv with $PY"; "$PY" -m venv "$VENV"; fi
"$VENV/bin/python" -m pip install --upgrade pip wheel >/dev/null
say "installing python packages"
"$VENV/bin/python" -m pip install -r "$SKILL_DIR/scripts/requirements.txt"

# 3) HyperFrames + Chrome for rendering and previews ------------------------
say "warming up hyperframes@$HYPERFRAMES_VERSION and its Chrome"
npx --yes "hyperframes@$HYPERFRAMES_VERSION" browser ensure >/dev/null
CHROME_PATH="$(npx --yes "hyperframes@$HYPERFRAMES_VERSION" browser path 2>/dev/null | tail -1)"

# 3b) node tools: SVGO (SVG clean-up before animation) and Rapier (physics baking for 3D scenes) ---------------
say "installing node tools (svgo, rapier) in $HEDITOR_HOME/node"
mkdir -p "$HEDITOR_HOME/node"
[[ -f "$HEDITOR_HOME/node/package.json" ]] || echo '{"name":"heditor-node-tools","private":true}' > "$HEDITOR_HOME/node/package.json"
npm install --prefix "$HEDITOR_HOME/node" --no-audit --no-fund --silent svgo@4.1.0 @dimforge/rapier3d-compat@0.21.0 || \
  say "node tools failed; 'heditor svg' and 'heditor physics' will not work until setup is re-run"

# 4) assets -------------------------------------------------------------------
say "downloading fonts, GSAP, face/person/hand models, music and SFX (first run takes a few minutes)"
HEDITOR_HOME="$HEDITOR_HOME" "$VENV/bin/python" "$SKILL_DIR/scripts/fetch_assets.py" --whisper "$WHISPER" ${FETCH_ARGS[@]+"${FETCH_ARGS[@]}"} || \
  say "some assets failed; re-run setup to retry (see $HEDITOR_HOME/assets-status.json)"

# 5) env file -----------------------------------------------------------------
cat > "$HEDITOR_HOME/env.sh" <<EOF
# source this file before using heditor: . "$HEDITOR_HOME/env.sh"
export HEDITOR_HOME="$HEDITOR_HOME"
export HEDITOR_SKILL="$SKILL_DIR"
export HEDITOR_KIT="$SKILL_DIR/scripts/reelkit"
export HEDITOR_PY="$VENV/bin/python"
export HEDITOR_CHROME="$CHROME_PATH"
export HEDITOR_HYPERFRAMES="npx --yes hyperframes@$HYPERFRAMES_VERSION"
EOF
ln -sfn "$SKILL_DIR/scripts/reelkit" "$HEDITOR_HOME/kit"
chmod +x "$SKILL_DIR/scripts/heditor"
mkdir -p "$HOME/.local/bin" && ln -sfn "$SKILL_DIR/scripts/heditor" "$HOME/.local/bin/heditor"
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) say "add ~/.local/bin to PATH to use the 'heditor' command (or call $SKILL_DIR/scripts/heditor)";; esac
if [[ ! -f "$HEDITOR_HOME/brand.json" ]]; then
  cp "$SKILL_DIR/templates/brand.example.json" "$HEDITOR_HOME/brand.json"
  say "created $HEDITOR_HOME/brand.json - edit name, handle, colours and logo"
fi

say "running doctor"
. "$HEDITOR_HOME/env.sh"
"$HEDITOR_PY" "$SKILL_DIR/scripts/doctor.py"
