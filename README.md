# Traditional Chinese Snacks — Cantonese Salted Egg Yolk Mooncake (40s Reel)

A 40-second vertical short-form video (TikTok / Reels / Shorts) about the Cantonese mooncake.
This repo contains the **script, shot list, burned-in subtitles, source stills and the complete
ffmpeg build pipeline** — everything needed to regenerate the master file from scratch.

## Quick look

Open `index.html` (via any static server) for an interactive shot timeline with a playable preview.
The page needs a local server because it fetches the `.srt` file:

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

## Deliverables

| File | What it is |
|---|---|
| `index.html` | Interactive shot-timeline page with embedded 720p preview |
| `build.py` | Full build pipeline — motion, grade, captions, score, concat |
| `fetch_assets.py` | Pulls CC-licensed source stills from Wikimedia Commons |
| `output/mooncake_reel_720p.mp4` | Web preview, 720×1280, 8.5 MB |
| `output/Cantonese_SaltedEggYolk_Mooncake_40s.srt` | 11 subtitle cues |
| `output/CREDITS.md` | Attribution for every source still |
| `output/waveform_before_after.png` | Audio fix verification (before/after envelope) |
| `assets/shot0*.jpg` | 7 source stills, one per shot |

## Rebuild the master (1080×1920)

```bash
python3 fetch_assets.py   # download source stills (skip if assets/ is populated)
python3 build.py          # ≈40 s → output/Cantonese_SaltedEggYolk_Mooncake_40s.mp4
```

Requires Python 3 with `numpy`, plus `ffmpeg` (H.264 via `libopenh264`, ASS subtitle support).

Two ffmpeg gotchas already solved in `build.py`, worth knowing if you edit it:

1. `libopenh264` defaults to `rc_mode=quality`, which **ignores** `-b:v` and produces huge files.
   The script passes `-rc_mode 1` plus `-frames:v` to force bitrate mode and a hard frame cap.
2. `enable='between(t,a,b)'` inside a `-vf` string gets split on the comma. All time gates use the
   comma-free form `gte(t,a)*lte(t,b)` instead.

## Shot list

| # | Time | Visual | Audio |
|---|---|---|---|
| 1 | 0:00–0:03 | Mooncake broken open, golden yolk revealed | "Ever seen a snack that tastes like the full moon?" |
| 2 | 0:03–0:10 | Slow pan over carved pastry patterns | "Look at these stunning handcrafted patterns…" |
| 3 | 0:10–0:18 | Cross-section, lotus paste around the yolk | "Inside, silky sweet lotus paste hugs a rich salted egg yolk…" |
| 4 | 0:18–0:27 | Family sharing mooncakes at night | "…Mid-Autumn Festival, a holiday about family reunion." |
| 5 | 0:27–0:34 | Small bite, then hot tea | "Pro tip: sip hot tea alongside to balance the sweetness." |
| 6 | 0:34–0:40 | Final beauty shot + series title | "Sweet, savory, and full of meaning…" |

## Before you publish

Two placeholders must be swapped — everything else is final:

1. **Still images → real footage.** The 7 stills are previz stand-ins, not final art. Replace each
   entry in the `SHOTS` list in `build.py` with a real clip or an AI-generated video segment.
   Timings, captions and grade carry over unchanged.
2. **Placeholder score → licensed music.** The soundtrack is a synthesised pentatonic loop. Try
   Pixabay Music (CC0) searching *guzheng soft* / *traditional chinese instrumental*, or a
   subscription library.

## Working in Bolt.new

This repo is a static site — no install step, no build step. Import it and open `index.html`.
Good next prompts:

- "Add a share/export button that downloads the 1080p master"
- "Turn the shot list into an editable table that writes back to the timeline"
- "Darken the grade and increase subtitle size for mobile readability"

## Licensing

Source stills are CC-licensed from Wikimedia Commons — see `output/CREDITS.md` for per-image
author and license. The synthesised score and all code in this repo are free to use.
