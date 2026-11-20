"""Optional remote compute on Google Colab for heditor: renders and transcription.

heditor runs everything on the local machine by default. With HEDITOR_COMPUTE=colab (put it in
~/.heditor/compute.env, which setup never overwrites), `heditor render`, `heditor transcribe`,
`heditor long transcribe` and `heditor long render` rent a Colab runtime through the official Colab CLI
(`uv tool install google-colab-cli`), using the compute units of the user's Colab or Google AI plan, run the job
there, bring the result back and stop the runtime. When Colab is not available the command does not fall back on
its own: nothing runs, it exits 75 and prints the reason, so the agent can tell the user before re-running the
same command with --local.

Usage (normally through `heditor colab ...`):
  colabkit.py status                                   CLI, login, balance, sessions; exit 75 when unavailable
  colabkit.py render <composition_dir> <out.mp4> [hyperframes render flags]
  colabkit.py transcribe <media> <out.json> [--start S] [--dur D] [--prompt TEXT] [--model M] [--lang pt]
                                                       [--segments seg.json]   words (and segments) with absolute times
  colabkit.py asr-window <media> <start_s> <duration_s> <out.json> [prompt] [model]   (heditor transcribe)
  colabkit.py stop-all                                 stop every runtime this kit created (names heditor-*)

Env (all optional):
  HEDITOR_COMPUTE          local (default) | colab
  HEDITOR_COLAB            path of the Colab CLI (default: `colab` on PATH)
  HEDITOR_COLAB_AUTH       adc | oauth2, passed as `colab --auth` (default: the CLI's own default)
  HEDITOR_COLAB_RENDER     machine order for renders (default "L4,cpu-hm"): a GPU name (T4, L4, G4, A100, H100),
                           `cpu`, or any of them with `-hm` for the high-RAM shape
  HEDITOR_COLAB_ASR        machine order for transcription (default "T4,L4")
  HEDITOR_COLAB_ASR_MODEL  Whisper model on Colab (default large-v3)
  HEDITOR_COLAB_MIN_UNITS  minimum balance before renting (default 5)
  HEDITOR_COLAB_KEY        SSH public key sent to the runtime (default ~/.ssh/id_ed25519.pub or id_ecdsa.pub)
"""
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

UNAVAILABLE = 75
HF_DEFAULT = "npx --yes hyperframes@0.9.13"
CHROME_LIBS = "libatk1.0-0t64 libatk-bridge2.0-0t64 libxcomposite1 libatspi2.0-0t64"
REMOTE = "/content/hjob"


class Unavailable(RuntimeError):
    """Colab cannot take the job right now (no CLI, no login, low balance, no machine). Nothing ran."""


def home():
    return Path(os.environ.get("HEDITOR_HOME", Path.home() / ".heditor"))


def enabled():
    return os.environ.get("HEDITOR_COMPUTE", "local").strip().lower() == "colab"


def notice(reason):
    """The message every caller prints before exiting 75."""
    return (f"heditor: Colab unavailable: {reason}\n"
            "heditor: nothing ran. Tell the user before falling back to this machine, then re-run with --local.")


def _env():
    env = dict(os.environ)
    for k in ("PYTHONPATH", "PYTHONHOME"):  # the CLI is its own uv tool: a foreign PYTHONPATH breaks its imports
        env.pop(k, None)
    return env


def _cli():
    exe = os.environ.get("HEDITOR_COLAB", "colab")
    path = shutil.which(exe) or (exe if Path(exe).is_file() else None)
    if not path:
        raise Unavailable(f"Colab CLI not found ({exe}); install it with `uv tool install google-colab-cli`")
    auth = os.environ.get("HEDITOR_COLAB_AUTH", "").strip()
    return [path] + (["--auth", auth] if auth else [])


def colab(*args, timeout=180):
    return subprocess.run(_cli() + [str(a) for a in args], capture_output=True, text=True, timeout=timeout,
                          env=_env(), stdin=subprocess.DEVNULL)


def _last(res):
    """The most telling line of a CLI failure: the last error-looking line, else the last line."""
    lines = [ln.strip() for ln in ((res.stdout or "") + "\n" + (res.stderr or "")).splitlines() if ln.strip()]
    for line in reversed(lines):
        if re.search(r"error|unavailable|denied|quota|limit|forbidden|unauthori|invalid|expired", line, re.I):
            return line[-300:]
    return lines[-1][-300:] if lines else f"exit {res.returncode}"


def parse_usage(text):
    def num(pat):
        m = re.search(pat, text)
        return float(m.group(1).replace(",", "")) if m else None
    active = re.search(r"Active assignments:\s*(\d+)", text)
    return {"balance": num(r"Current balance:\s*([\d.,]+)"), "rate": num(r"Usage rate:\s*([\d.,]+)"),
            "active": int(active.group(1)) if active else None}


def parse_sessions(text):
    return [m.group(1) for m in re.finditer(r"^\[([^\]]+)\]\s", text, re.M) if m.group(1) != "colab"]


def parse_shapes(spec):
    """"L4,cpu-hm" -> [("L4", ["--gpu", "L4"]), ("cpu-hm", ["--high-mem"])]."""
    out = []
    for item in (spec or "").split(","):
        item = item.strip()
        if not item:
            continue
        base, hm = (item[:-3], True) if item.lower().endswith("-hm") else (item, False)
        args = [] if base.lower() == "cpu" else ["--gpu", base.upper()]
        out.append((item, args + (["--high-mem"] if hm else [])))
    return out


def usage():
    res = colab("usage", timeout=90)
    info = parse_usage(res.stdout or "")
    if res.returncode != 0 or info["balance"] is None:
        raise Unavailable(f"`colab usage` failed (login missing or expired?): {_last(res)}")
    return info


def sessions():
    res = colab("sessions", timeout=90)
    return parse_sessions(res.stdout or "")


def _key():
    env_key = os.environ.get("HEDITOR_COLAB_KEY")
    cands = [Path(env_key).expanduser()] if env_key else [Path.home() / ".ssh/id_ed25519.pub", Path.home() / ".ssh/id_ecdsa.pub"]
    for c in cands:
        if c.is_file():
            return c
    raise Unavailable("no SSH public key for the runtime (ssh-keygen -t ed25519, or set HEDITOR_COLAB_KEY)")


def check(min_units=None):
    """Raise Unavailable unless the CLI, the login, the balance, ssh, rsync and a key are all there."""
    for tool in ("ssh", "rsync"):
        if not shutil.which(tool):
            raise Unavailable(f"`{tool}` not installed on this machine")
    _key()
    info = usage()
    need = float(os.environ.get("HEDITOR_COLAB_MIN_UNITS", 5) if min_units is None else min_units)
    if info["balance"] < need:
        raise Unavailable(f"balance {info['balance']:.2f} compute units, below the minimum {need:g}")
    return info


def _log_usage(entry):
    path = home() / "colab-usage.json"
    try:
        data = json.loads(path.read_text()) if path.exists() else []
    except ValueError:
        data = []
    data.append(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data[-500:], ensure_ascii=False, indent=1))


def _on_signal(signum, _frame):
    raise SystemExit(128 + signum)  # run the finally blocks: the runtime must be stopped


SSH_CONFIG = """Host {name}
  User root
  ProxyCommand {proxy}
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
  LogLevel ERROR
  ControlMaster auto
  ControlPath {tmp}/cm
  ControlPersist 900
  ServerAliveInterval 15
  ServerAliveCountMax 8
"""


class Runtime:
    """One Colab runtime for one job: created on enter, always stopped on exit (also on errors and SIGTERM).

    Files move with rsync over SSH (the CLI's ProxyCommand bridge). The runtime takes one SSH connection at a time
    and needs ~15-25 s to release a closed one (HTTP 429 otherwise), so everything goes through one ControlMaster.
    """

    def __init__(self, kind, shapes, quiet=False):
        self.kind, self.shapes, self.quiet = kind, shapes, quiet
        self.name = f"heditor-{kind}-{time.strftime('%m%d-%H%M%S')}-{os.getpid() % 10000:04d}"
        self.tmp = Path(tempfile.mkdtemp(prefix="hcolab-"))
        self.cfg = self.tmp / "ssh_config"
        self.shape, self.t0, self.balance0, self.created = None, None, None, False

    def say(self, msg):
        if not self.quiet:
            print(f"[colab] {msg}", flush=True)

    # -- lifecycle -------------------------------------------------------------------------------------------
    def __enter__(self):
        for sig in (signal.SIGTERM, signal.SIGHUP):
            signal.signal(sig, _on_signal)
        try:
            self.start()
        except BaseException:
            self.stop()
            raise
        return self

    def __exit__(self, *exc):
        self.stop()
        return False

    def start(self):
        info = check()
        self.balance0 = info["balance"]
        errors = []
        for label, args in self.shapes:
            res = colab("new", "-s", self.name, *args, timeout=300)
            if self.name in sessions():
                self.created, self.shape = True, label
                break
            errors.append(f"{label}: {_last(res)}")
        if not self.shape:
            raise Unavailable("no Colab machine available (" + "; ".join(errors) + ")")
        self.t0 = time.time()
        proxy = " ".join(shlex.quote(x) for x in _cli()) + f" ssh --proxy-mode -s {self.name} -i {shlex.quote(str(_key()))}"
        self.cfg.write_text(SSH_CONFIG.format(name=self.name, proxy=proxy, tmp=self.tmp))
        self._master()
        mach = self.ssh("echo nproc=$(nproc) mem=$(free -g | awk 'NR==2{print $2}')GB "
                        "gpu=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)").stdout.strip()
        self.say(f"runtime {self.name} ({self.shape}) ready: {mach}; balance {self.balance0:.2f}")

    def _master(self):
        err = self.tmp / "master.err"
        for attempt in range(5):
            with open(err, "w") as fh:  # -f forks: never hand it a pipe, or this call waits for the daemon
                subprocess.run(["ssh", "-F", str(self.cfg), "-fN", self.name], env=_env(), stdout=subprocess.DEVNULL,
                               stderr=fh, stdin=subprocess.DEVNULL, timeout=180)
            ok = subprocess.run(["ssh", "-F", str(self.cfg), "-O", "check", self.name], env=_env(),
                                capture_output=True, text=True, timeout=30).returncode == 0
            if ok:
                return
            time.sleep(20 if "429" in err.read_text() or attempt else 8)
        raise RuntimeError(f"could not open the SSH connection to {self.name}: {err.read_text()[-400:]}")

    def stop(self):
        try:
            if self.cfg.exists():
                subprocess.run(["ssh", "-F", str(self.cfg), "-O", "exit", self.name], env=_env(), capture_output=True, timeout=30)
        except Exception:  # noqa: BLE001 - best effort, the runtime stop below is what matters
            pass
        if self.created or self.name in _safe_sessions():
            stopped = False
            for _ in range(3):
                try:
                    colab("stop", "-s", self.name, timeout=120)
                except Exception:  # noqa: BLE001
                    pass
                if self.name not in _safe_sessions():
                    stopped = True
                    break
                time.sleep(5)
            after = None
            try:
                after = usage()["balance"]
            except Exception:  # noqa: BLE001
                pass
            spent = round(self.balance0 - after, 3) if (after is not None and self.balance0 is not None) else None
            _log_usage({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": self.kind, "session": self.name, "shape": self.shape,
                        "seconds": round(time.time() - self.t0, 1) if self.t0 else None, "balance_before": self.balance0,
                        "balance_after": after, "units": spent, "stopped": stopped})
            if stopped:
                self.say(f"runtime stopped; balance {after if after is not None else '?'} (spent {spent if spent is not None else '?'})")
            else:
                print(f"[colab] WARNING: {self.name} is still listed after stop; run `heditor colab stop-all`", file=sys.stderr)
            self.created = False
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- commands and files ----------------------------------------------------------------------------------
    def ssh(self, cmd, timeout=600, check=False):
        for attempt in range(4):
            res = subprocess.run(["ssh", "-F", str(self.cfg), self.name, cmd], env=_env(), capture_output=True, text=True,
                                 timeout=timeout, stdin=subprocess.DEVNULL)
            if res.returncode != 255:
                break
            time.sleep(20)
            self._master()
        if check and res.returncode != 0:
            raise RuntimeError(f"remote command failed ({res.returncode}): {cmd[:120]}\n{(res.stderr or res.stdout)[-800:]}")
        return res

    def _rsync(self, src, dst, timeout):
        cmd = ["rsync", "-a", "--partial", "--copy-links", "--exclude", "node_modules", "--exclude", ".cache",
               "-e", f"ssh -F {self.cfg}", str(src), str(dst)]
        for attempt in range(3):
            res = subprocess.run(cmd, env=_env(), capture_output=True, text=True, timeout=timeout)
            if res.returncode == 0:
                return
            time.sleep(20)
            self._master()
        raise RuntimeError(f"rsync failed: {src} -> {dst}: {(res.stderr or res.stdout)[-600:]}")

    def put(self, local, remote, timeout=3600):
        local = Path(local)
        parent = remote.rstrip("/") if local.is_dir() else str(Path(remote).parent)
        self.ssh(f"mkdir -p {shlex.quote(parent)}", check=True)
        t = time.time()
        self._rsync(f"{local}/" if local.is_dir() else local, f"{self.name}:{remote.rstrip('/')}{'/' if local.is_dir() else ''}", timeout)
        return time.time() - t

    def get(self, remote, local, timeout=3600):
        Path(local).parent.mkdir(parents=True, exist_ok=True)
        t = time.time()
        self._rsync(f"{self.name}:{remote}", local, timeout)
        return time.time() - t

    def detach(self, command, log, done):
        """Start `command` in the runtime, detached from the SSH session; `done` appears when it ends."""
        inner = f"{command} > {log} 2>&1; echo $? > {done}"
        self.ssh(f"rm -f {done}; setsid nohup bash -c {shlex.quote(inner)} > /dev/null 2>&1 < /dev/null &", check=True)

    def wait(self, log, done, pattern=None, poll=15, timeout=6 * 3600):
        seen, t0, sep = 0, time.time(), "@@heditor-colab@@"
        while True:
            res = self.ssh(f"cat {done} 2>/dev/null; echo {sep}; tail -n +{seen + 1} {log} 2>/dev/null | head -200")
            head, found, body = (res.stdout or "").partition(sep + "\n")
            if found:
                new = body.splitlines()
                for line in new:
                    if pattern is None or re.search(pattern, line):
                        self.say(line[-300:])
                seen += len(new)
                if head.strip() and len(new) < 200:
                    return int(head.strip())
            if time.time() - t0 > timeout:
                raise RuntimeError(f"remote job exceeded {timeout / 3600:.1f} h")
            time.sleep(poll)


def _safe_sessions():
    try:
        return sessions()
    except Exception:  # noqa: BLE001
        return []


# ---------------------------------------------------------------- render

RENDER_SH = r"""#!/usr/bin/env bash
# heditor colab render job: renders each "<composition_dir>\t<output.mp4>" line of jobs.tsv with the same flags.
set -uo pipefail
export PATH=/tools/node/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export FFMPEG_ENCODE_TIMEOUT_MS=3600000
HF="$1"; shift
cd /content
if [ ! -f /content/.hf-ready ]; then
  t=$(date +%s)
  $HF browser ensure 2>&1 | tail -2
  CH="$($HF browser path 2>/dev/null | tail -1)"
  if [ -n "$CH" ] && ldd "$CH" 2>/dev/null | grep -q "not found"; then
    # IPv6 hangs apt on Colab; the image's package index is enough (no apt-get update)
    DEBIAN_FRONTEND=noninteractive timeout 300 apt-get -o Acquire::ForceIPv4=true -o Acquire::http::Timeout=20 \
      install -y --no-install-recommends __LIBS__ > /dev/null 2>&1
  fi
  echo "SETUP chrome_missing_libs=$(ldd "$CH" 2>/dev/null | grep -c 'not found') seconds=$(( $(date +%s) - t ))"
  touch /content/.hf-ready
fi
rc_all=0
while IFS=$'\t' read -r comp out; do
  [ -n "$comp" ] || continue
  t=$(date +%s)
  (cd "$comp" && $HF render "$@" --output "$out") 2>&1 | tr '\r' '\n' | grep -v "Capturing frame\|@hf-progress" | tail -25
  rc=${PIPESTATUS[0]}
  echo "RESULT $out rc=$rc seconds=$(( $(date +%s) - t ))"
  if [ "$rc" != 0 ]; then rc_all=$rc; break; fi
done < __REMOTE__/jobs.tsv
exit $rc_all
""".replace("__LIBS__", CHROME_LIBS).replace("__REMOTE__", REMOTE)


def _hf():
    hf = os.environ.get("HEDITOR_HYPERFRAMES", HF_DEFAULT).strip()
    return hf if hf.startswith("npx ") else HF_DEFAULT  # a local binary path does not exist in the runtime


def render_many(jobs, flags, shapes=None, quiet=False):
    """Render [(composition_dir, out.mp4), ...] in one runtime. Returns [{out, seconds}] in order."""
    jobs = [(Path(c).resolve(), Path(o).resolve()) for c, o in jobs]
    shapes = shapes or parse_shapes(os.environ.get("HEDITOR_COLAB_RENDER", "L4,cpu-hm"))
    t_all = time.time()
    with Runtime("render", shapes, quiet=quiet) as rt:
        up = 0.0
        lines = []
        for i, (comp, _out) in enumerate(jobs):
            up += rt.put(comp, f"{REMOTE}/in/{i:03d}")
            lines.append(f"{REMOTE}/in/{i:03d}\t{REMOTE}/out/{i:03d}.mp4")
        rt.say(f"uploaded {len(jobs)} composition(s) in {up:.0f} s")
        local_tsv, local_sh = rt.tmp / "jobs.tsv", rt.tmp / "render.sh"
        local_tsv.write_text("\n".join(lines) + "\n")
        local_sh.write_text(RENDER_SH)
        rt.put(local_tsv, f"{REMOTE}/jobs.tsv")
        rt.put(local_sh, f"{REMOTE}/render.sh")
        rt.ssh(f"mkdir -p {REMOTE}/out", check=True)
        rt.detach(f"bash {REMOTE}/render.sh {shlex.quote(_hf())} " + " ".join(shlex.quote(f) for f in flags),
                  f"{REMOTE}/render.log", f"{REMOTE}/render.done")
        rc = rt.wait(f"{REMOTE}/render.log", f"{REMOTE}/render.done", pattern=r"^(SETUP|RESULT)|rror")
        log = rt.ssh(f"cat {REMOTE}/render.log").stdout
        results = {m.group(1): int(m.group(2)) for m in re.finditer(r"^RESULT (\S+) rc=0 seconds=(\d+)", log, re.M)}
        if rc != 0:
            raise RuntimeError(f"remote render failed (exit {rc}):\n{log[-2500:]}")
        out = []
        for i, (_comp, dest) in enumerate(jobs):
            remote = f"{REMOTE}/out/{i:03d}.mp4"
            rt.get(remote, dest)
            if not dest.exists() or dest.stat().st_size == 0:
                raise RuntimeError(f"render output missing after download: {dest}")
            out.append({"out": str(dest), "seconds": results.get(remote)})
        rt.say(f"{len(jobs)} render(s) done in {(time.time() - t_all) / 60:.1f} min on {rt.shape}")
    return out


# ---------------------------------------------------------------- transcription

ASR_PY = r'''# heditor colab ASR job: python asr.py request.json result.json
import glob, json, os, site, subprocess, sys, time
req_path, out_path = sys.argv[1], sys.argv[2]
if not os.path.exists("/content/.asr-ready"):
    t = time.time()
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "faster-whisper", "nvidia-cublas-cu12", "nvidia-cudnn-cu12==9.*"],
                       capture_output=True, text=True)
    print("SETUP pip rc=%d seconds=%.0f" % (r.returncode, time.time() - t), flush=True)
    if r.returncode:
        print(r.stderr[-2000:]); sys.exit(3)
    open("/content/.asr-ready", "w").close()
if os.environ.get("HEDITOR_ASR_CHILD") != "1":
    # ctranslate2 needs the CUDA 12 libraries from pip; the loader reads LD_LIBRARY_PATH only at process start
    libs = [p for sp in site.getsitepackages() for p in glob.glob(os.path.join(sp, "nvidia", "*", "lib"))]
    env = dict(os.environ, HEDITOR_ASR_CHILD="1", LD_LIBRARY_PATH=":".join(libs + [os.environ.get("LD_LIBRARY_PATH", "")]))
    sys.exit(subprocess.run([sys.executable] + sys.argv, env=env).returncode)
import numpy as np
import ctranslate2
from faster_whisper import BatchedInferencePipeline, WhisperModel
req = json.load(open(req_path))
cuda = ctranslate2.get_cuda_device_count() > 0
t = time.time()
model = WhisperModel(req["model"], device="cuda" if cuda else "cpu", compute_type="float16" if cuda else "int8")
print("MODEL %s device=%s seconds=%.0f" % (req["model"], "cuda" if cuda else "cpu", time.time() - t), flush=True)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", req["audio"], "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(raw, dtype=np.float32)
pipe = BatchedInferencePipeline(model=model)
out, t_all = {}, time.time()
for k, job in enumerate(req["jobs"]):
    a, b = float(job["start"]), float(job["end"])
    t = time.time()
    segs, _ = pipe.transcribe(audio[int(a * 16000):int(b * 16000)], language=req["lang"], batch_size=req["batch"],
                              word_timestamps=True, initial_prompt=req.get("prompt"))
    base = float(req["offset"]) + a
    words, segments = [], []
    for s in segs:
        segments.append({"start": round(base + s.start, 3), "end": round(base + s.end, 3), "text": s.text.strip()})
        words += [{"word": w.word.strip(), "start": round(base + w.start, 3), "end": round(base + w.end, 3),
                   "p": round(w.probability, 3)} for w in (s.words or []) if w.word.strip()]
    out[job["id"]] = {"words": words, "segments": segments}
    print("JOB %d/%d %s %.0f s of audio: %d words in %.0f s" % (k + 1, len(req["jobs"]), job["id"], b - a, len(words), time.time() - t), flush=True)
json.dump(out, open(out_path, "w"), ensure_ascii=False)
print("ASR done in %.0f s" % (time.time() - t_all), flush=True)
'''


def _duration(media):
    res = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(media)],
                         capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def transcribe_jobs(media, jobs, model=None, lang=None, prompt=None, shapes=None, batch=16, quiet=False):
    """Word-timed ASR of several windows of one media file in one runtime.

    jobs: [(job_id, start_s, end_s), ...] in source seconds. Returns {job_id: {"words": [{word, start, end, p}, ...],
    "segments": [{start, end, text}, ...]}} with absolute source times; the words have the format of heditor's local ASR.
    """
    if not jobs:
        return {}
    lo, hi = min(a for _, a, _ in jobs), max(b for _, _, b in jobs)
    shapes = shapes or parse_shapes(os.environ.get("HEDITOR_COLAB_ASR", "T4,L4"))
    model = model or os.environ.get("HEDITOR_COLAB_ASR_MODEL", "large-v3")
    t_all = time.time()
    with Runtime("asr", shapes, quiet=quiet) as rt:
        audio = rt.tmp / "audio.flac"  # only the needed audio travels: 16 kHz mono FLAC (lossless for the ASR)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{lo:.3f}", "-t", f"{hi - lo:.3f}", "-i", str(media), "-vn",
                        "-ac", "1", "-ar", "16000", "-c:a", "flac", str(audio)], check=True)
        req = {"audio": f"{REMOTE}/audio.flac", "offset": lo, "model": model, "batch": batch,
               "lang": lang or os.environ.get("HEDITOR_LANG", "pt"), "prompt": prompt or None,
               "jobs": [{"id": str(j), "start": round(a - lo, 3), "end": round(b - lo, 3)} for j, a, b in jobs]}
        (rt.tmp / "request.json").write_text(json.dumps(req, ensure_ascii=False))
        (rt.tmp / "asr.py").write_text(ASR_PY)
        up = sum(rt.put(rt.tmp / f, f"{REMOTE}/{f}") for f in ("audio.flac", "request.json", "asr.py"))
        rt.say(f"uploaded {audio.stat().st_size / 1e6:.0f} MB of audio ({hi - lo:.0f} s) in {up:.0f} s")
        rt.detach(f"python3 {REMOTE}/asr.py {REMOTE}/request.json {REMOTE}/result.json", f"{REMOTE}/asr.log", f"{REMOTE}/asr.done")
        rc = rt.wait(f"{REMOTE}/asr.log", f"{REMOTE}/asr.done", pattern=r"^(SETUP|MODEL|JOB|ASR)|rror")
        if rc != 0:
            raise RuntimeError(f"remote ASR failed (exit {rc}):\n{rt.ssh(f'tail -n 40 {REMOTE}/asr.log').stdout}")
        rt.get(f"{REMOTE}/result.json", rt.tmp / "result.json")
        result = json.loads((rt.tmp / "result.json").read_text())
        rt.say(f"ASR of {hi - lo:.0f} s done in {(time.time() - t_all) / 60:.1f} min on {rt.shape} ({model})")
    return result


def transcribe(media, start=0.0, dur=None, model=None, lang=None, prompt=None, quiet=False):
    """One window -> {"words": [...], "segments": [...]} (absolute times)."""
    if not dur:
        dur = _duration(media) - start
    return transcribe_jobs(media, [("all", start, start + dur)], model=model, lang=lang, prompt=prompt, quiet=quiet)["all"]


# ---------------------------------------------------------------- CLI

def _opts(argv):
    pos, opt, i = [], {}, 0
    while i < len(argv):
        if argv[i].startswith("--") and i + 1 < len(argv):
            opt[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            pos.append(argv[i])
            i += 1
    return pos, opt


def _write_words(words, out):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(words, ensure_ascii=False, indent=1))
    print(" ".join(f"[{w['start']:.2f}]{w['word']}" for w in words))


def main(argv):
    if not argv or argv[0] in ("help", "-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    try:
        if cmd == "status":
            info = check()
            print(json.dumps({"available": True, "compute": "colab" if enabled() else "local", **info,
                              "sessions": sessions()}, indent=1))
            return 0
        if cmd == "stop-all":
            mine = [s for s in sessions() if s.startswith("heditor-")]
            for s in mine:
                colab("stop", "-s", s, timeout=120)
            print(json.dumps({"stopped": mine, "left": [s for s in sessions() if s.startswith("heditor-")]}))
            return 0
        if cmd == "render":
            comp, out, flags = rest[0], rest[1], rest[2:] or ["--quality", "high", "--workers", "auto"]
            if "--workers" not in flags:
                flags += ["--workers", "auto"]
            res = render_many([(comp, out)], flags)
            print(json.dumps(res[0]))
            return 0
        if cmd == "transcribe":
            pos, opt = _opts(rest)
            res = transcribe(pos[0], float(opt.get("start", 0)), float(opt["dur"]) if opt.get("dur") else None,
                             opt.get("model"), opt.get("lang"), opt.get("prompt"))
            if opt.get("segments"):
                seg = Path(opt["segments"])
                seg.parent.mkdir(parents=True, exist_ok=True)
                seg.write_text(json.dumps(res["segments"], ensure_ascii=False, indent=1))
            _write_words(res["words"], pos[1])
            return 0
        if cmd == "asr-window":  # same positional arguments as asr_window.py
            src, start, dur, out = rest[0], float(rest[1]), float(rest[2]), rest[3]
            prompt = rest[4] if len(rest) > 4 and rest[4] else None
            model = rest[5] if len(rest) > 5 else None
            _write_words(transcribe(src, start, dur, model=model, prompt=prompt)["words"], out)
            return 0
    except Unavailable as exc:
        print(notice(exc), file=sys.stderr)
        return UNAVAILABLE
    print(f"unknown command {cmd!r}\n{__doc__}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
