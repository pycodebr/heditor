# Remote compute on Google Colab (optional)

heditor runs on the local machine by default. On a small server (a few vCPUs, no GPU) the two heavy steps are slow:
a 35 s Reel takes about 11 minutes to render, and word-timed ASR of a two-hour recording with `medium` on the CPU
takes hours. Users with a Colab or Google AI plan receive Colab compute units every month. With this option heditor
rents a Colab runtime through Google's official Colab CLI, runs the step there, brings the result back and stops
the runtime.

## What runs where

| Command | With `HEDITOR_COMPUTE=colab` | Machine order (env) |
|---|---|---|
| `heditor render <work>` | the composition is rendered on Colab with the same flags (`--workers auto`) | `HEDITOR_COLAB_RENDER`, default `L4,cpu-hm` |
| `heditor transcribe <video> <start> <dur> <out.json> [prompt] [model]` | the window is transcribed on Colab (`large-v3` unless a model is given) | `HEDITOR_COLAB_ASR`, default `T4,L4` |
| `heditor long transcribe <work>` | the missing chunks are transcribed in one runtime and written to the same chunk files | `HEDITOR_COLAB_ASR` |
| `heditor long render <work>` | the pending segments are rendered in one runtime; same progress file and frame checks | `HEDITOR_COLAB_RENDER` |
| `heditor colab render <comp_dir> <out.mp4> [flags]` | any HyperFrames composition (default flags `--quality high --workers auto`) | `HEDITOR_COLAB_RENDER` |
| `heditor colab transcribe <media> <out.json> [--start S] [--dur D] [--prompt T] [--model M] [--lang pt] [--segments seg.json]` | any audio or video file: words with absolute times in `out.json`, sentence segments (`start`, `end`, `text`) in `seg.json` | `HEDITOR_COLAB_ASR` |

Everything else stays local: `words` and `asr-check` (a minute of the assembled cut, where renting a runtime costs
more time than it saves), `triage`, `prepare`, `produce`, `preview`, `finalize` and the QA.

The render gain comes from vCPUs and RAM, not from the GPU: HyperFrames captures frames in software and the Chrome
GPU path was 2.3× slower than software on an L4. That is why renders ask for an L4 runtime (12 vCPUs, 52 GB) and
never pass `--gpu` or `--browser-gpu`. A CPU-only high-RAM runtime would be cheaper, but the plan we tested did not
offer it (`Service Unavailable` on every attempt, also for T4 with high RAM); it stays second in the default order
so it is used when an account has it. The standard CPU runtime has 2 vCPUs and is not worth it for renders.

## Setup (once)

1. Install the CLI: `uv tool install google-colab-cli` (or `pip install google-colab-cli`); `colab version`.
2. Sign in, in **your own interactive terminal** (the CLI shows a link and reads a code; an agent's shell has no
   keyboard and fails with "Malformed auth code"). On a server without a keyring, Application Default Credentials
   avoid a login per command: `gcloud auth application-default login --no-launch-browser --scopes=openid,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/colaboratory`
   and then `HEDITOR_COLAB_AUTH=adc`.
3. An SSH key (`ssh-keygen -t ed25519`): the CLI sends the public key to each runtime.
4. Turn it on in `~/.heditor/compute.env` (heditor sources it after `env.sh`; setup never overwrites it):

```bash
export HEDITOR_COMPUTE="${HEDITOR_COMPUTE:-colab}"
export HEDITOR_COLAB="${HEDITOR_COLAB:-$HOME/.local/bin/colab}"
export HEDITOR_COLAB_AUTH="${HEDITOR_COLAB_AUTH:-adc}"      # only with the gcloud ADC login
```

5. `heditor colab status` prints the balance and the sessions, or exits 75 with the reason.

## When Colab is unavailable

The command runs nothing, exits **75** and prints why (no CLI, login missing or expired, balance below
`HEDITOR_COLAB_MIN_UNITS`, no machine of the listed types). It never falls back on its own, because the user may
prefer to wait than to load the local machine for hours. Tell the user what happened and that the job will run
locally, then re-run the same command with `--local` (or `HEDITOR_COMPUTE=local`). A failure after the runtime was
created (render error, ASR error) exits 1 like a local failure, with the remote log; the runtime is stopped anyway.

## How a job runs

1. `colab usage` (balance) and `colab new -s heditor-<kind>-<time>-<pid>` for the first machine type that answers.
2. One SSH connection through the CLI's ProxyCommand bridge (`colab ssh --proxy-mode`), kept open with OpenSSH
   ControlMaster. The runtime accepts one SSH connection at a time and needs 15–25 s to release a closed one; a second
   connection in that window gets HTTP 429 and scp/rsync break with "Broken pipe". Everything goes through the master.
3. Files move with `rsync` (8 MB/s up and 14 MB/s down in our test; a repeated upload sends only the changes). For
   ASR only the needed window travels, as 16 kHz mono FLAC. Compositions are uploaded with symlinks resolved.
4. The job runs detached in the runtime (`setsid nohup`), with a log the client follows every 15 s, so a dropped
   connection does not kill it.
5. The result comes back, is checked (file present; frame counts for long-form segments), and the runtime is stopped
   in a `finally` (also on Ctrl-C and SIGTERM) and confirmed gone from `colab sessions`.
6. The balance before and after, the machine and the time go to `~/.heditor/colab-usage.json`.

`heditor colab stop-all` stops every runtime whose name starts with `heditor-` (for example after a crash of the
client). It never touches sessions with other names, such as a notebook the user has open.

## Measured on a 4-vCPU server (Colab CLI 0.8.0, heditor 2.22.0)

| Job | Local | Colab, end to end | Units |
|---|---|---|---|
| `heditor render`, 35 s Reel (style `vox`, 1,045 frames) | 11 min 3 s, 2 workers | 3.9 min on L4: 36 s upload, 18 s Chrome setup, 116 s render, download | 0.10 |
| `heditor long render`, 4.4 min class in 16:9 (7 segments, 7,913 frames) | 32.3 min | 14.4 min on L4 (57 s upload, render 18–114 s per segment) | 0.36 |
| `heditor transcribe`, 10 min window with `large-v3` | ~25–30 min with `medium` (extrapolated) | 1.9 min on T4 (25 s of ASR; the rest is renting, pip and the model) | < 0.05 |
| `heditor long transcribe`, 4.7 min in 3 chunks | — | 2 min on T4 | < 0.05 |
| ASR of a 2 h 22 min recording (pilot, batched `large-v3`) | ~7 h extrapolated (`medium`) | 7.5 min on T4 | ~0.16 |

Outputs matched the local ones: same frame count and duration, mean SSIM 0.98 (Reel with film grain) and 0.99
(long-form segment), frames identical on inspection; the 10 min ASR window matched an earlier `large-v3` run at
98.6 % of words with a median timing difference of 10 ms. Every job carries 1.5–2 minutes of fixed cost (renting,
setup), so a one-minute clip is faster locally; that is why `words` and `asr-check` stay local.

Rates seen on one account: T4 1.15/h, L4 1.94/h, CPU 0.08/h. Google changes them without notice and other accounts
report different values; read `colab usage` with a runtime open.

## Limits

- No permanent service: a runtime lasts hours, not days, drops when idle and a GPU is never guaranteed.
- Colab's terms forbid hosting services or files, proxies and deepfakes. Avatar generation, voice cloning and
  anything that is not the user's own render or transcription does not go there.
- Third-party personal data (other people's voice notes, customer recordings) goes to Colab only with the owner's
  permission.
- `colab drivemount` asks for a browser consent on every runtime, so it cannot be used by an unattended job;
  download from Drive locally and let heditor upload.
- The ASR job installs `faster-whisper` and the CUDA 12 libraries (`nvidia-cublas-cu12`, `nvidia-cudnn-cu12==9.*`)
  on each runtime and runs the worker in a subprocess with `LD_LIBRARY_PATH` pointing at them: the Colab image ships
  CUDA 13 and ctranslate2 needs CUDA 12. It decodes with ffmpeg (faster-whisper 1.2.1 breaks with `av` 19).
- The Chrome of HyperFrames needs `libatk1.0-0t64 libatk-bridge2.0-0t64 libxcomposite1 libatspi2.0-0t64`; the job
  installs them with `apt-get -o Acquire::ForceIPv4=true` (IPv6 hangs apt on Colab) and no `apt-get update`.
- The CLI is a separate Python tool: a `PYTHONPATH` from another environment breaks its imports
  (`ImportError: cannot import name 'ArgsKwargs' from 'pydantic_core'`). colabkit removes `PYTHONPATH` and
  `PYTHONHOME` before calling it; do the same when calling `colab` by hand.
