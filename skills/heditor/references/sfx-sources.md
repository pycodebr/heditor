# Optional sound sources

The Mixkit catalog remains the default. These commands add project-local sounds without replacing the mixer.
They are currently wired into `heditor produce` for short-form projects, not the long-form pipeline. Audition the
sounds and inspect the final mix; objective measurements do not establish taste or licence.

## Earshot, procedural sounds

Run `heditor earshot setup` once. It installs the MIT Earshot code pinned to a commit in an isolated venv under
`~/.heditor/earshot` with the small dependencies needed for the sound bank. Installation requires network and disk;
rendering does not call a paid service, download models or require network. This is not the full analysis suite.

```
heditor earshot list
heditor earshot render /path/to/work whoosh_fast/crisp --category sweep --duration 0.8 --apex 0.32 --seed 27
```

The WAV goes into `composition/assets/sfx-earshot`, with seed, parameters and hash in `earshot-sfx.json`.
In the build's `plan["sound_events"]`, use category `earshot_sweep`, with time, gain and optional length/rate as
usual. Multiple seeds under the same category become variants. Files with the same category and seed are never
overwritten. `--apex` is a target within the generated sound, so place the event at visual_time - apex. Confirm timing
and audition: the seed changes onset and the generator's measurement is not a human review.

## Openverse, recordings

```
heditor openverse search "keyboard click" --license cc0 --limit 10
heditor openverse import /path/to/work OPENVERSE_UUID /path/to/downloaded.wav --category keyboard --verified-origin
```

Search uses the anonymous public API; `cc0` is default, and `--license by` selects CC BY. Open the
`foreign_landing_url`, verify the licence and creator there, acquire the correct file through the original provider,
and inspect terms and quality before importing. Pass `--verified-origin` only after this check. Openverse's `url`
can be a lossy preview; metadata and an imported file are not proof it is the original. Import is intentionally local
and does not download media. It records the source, licence, author, SHA-256 and the fact that file identity is not
independently established in `openverse-sfx.json`. CC BY needs attribution in the delivered work as required by the
source; record the credit in `DESIGN.md` and include it in the publication where necessary. Check commercial rights,
including third-party or personality rights, separately.

Use the category `openverse_keyboard` in the project's sound events. `heditor produce` loads both manifests and
refuses files modified after registration or located outside project assets. Files remain with the project; no bulk
scraping, account or key is required. A search result is not permission to use a recording.
