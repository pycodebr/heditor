"""Style packs: the named styles as reusable tokens for long-form and multi-format edits.

A Reel style (references/styles/<slug>.md) is a full scene grammar for 30-70 s. A long video (minutes to hours)
cannot carry that density, so each style is reduced to a *pack*: the tokens that keep its identity on every
frame (palette, typography, caption system, camera frame and grade, transitions, chapter card, lower third,
sound map, music) plus an adaptation note for horizontal and square canvases. Set pieces (creative moments)
then borrow the style's signature moves at key moments only.

    import stylepacks as sp
    pack = sp.get("cinema")          # dict; sp.get("creative") is the neutral base for creative mode
    sp.css_vars(pack)                # ":root{--bg:...}" for the composition
    sp.SLUGS                         # every named style has a pack (test_formats checks it)

Fonts are limited to the kit (Anton, Bebas Neue, Geist, Inter, JetBrains Mono, IBM Plex Mono, VT323,
Press Start 2P, Playfair Display, Fraunces, DM Serif Display, Caveat, B612 Mono, Fredoka). Where a Reel style
uses an extra OFL family, the pack names the closest kit font and `font_note` says which family to download
for full fidelity.
"""

import copy

# Card kinds rendered by longkit (chapter cards, opening and closing cards share them):
CARD_KINDS = ("slate", "serif", "board", "terminal", "hud", "broadcast", "record", "editorial", "neon", "app")
# Lower-third kinds:
LOWER_KINDS = ("bar", "plate", "terminal", "chalk", "hud", "record", "tag")
# Transitions between layouts and into cards:
TRANSITIONS = ("slide", "fade", "wipe", "flash", "glitch", "iris", "cut", "chalk", "page")

BASE = {
    "slug": "creative",
    "name": "Creative base",
    "family": "creative",
    "palette": {"bg": "#050a14", "bg2": "#081626", "surface": "#0e1c2c", "text": "#f4f8fb", "muted": "#9fb3c4",
                "accent": "#edc580", "accent2": "#7dd3fc", "alert": "#ff3d57", "ok": "#7dffb0"},
    "fonts": {"display": "Anton", "body": "Geist", "mono": "JetBrains Mono", "caption": "Geist"},
    "captions": {"weight": 700, "case": "none", "fg": "#ffffff", "active_fg": "#000000", "active_bg": "#ffd84d",
                 "box": "rgba(5,10,20,.72)", "stroke": None, "scale": 1.0},
    "frame": {"screen_radius": 18, "camera_radius": 18, "camera_shape": "rect", "border": "3px solid var(--accent)",
              "shadow": "0 18px 50px rgba(0,0,0,.55)",
              "world": "radial-gradient(ellipse 80% 70% at 50% 40%, var(--bg2) 0%, var(--bg) 75%)"},
    "overlay": {"grain": 0.05, "letterbox": False, "scanlines": False, "vignette": 0.25},
    "transition": {"kind": "slide", "dur": 0.55, "ease": "expo.inOut"},
    "chapter_card": "slate",
    "lower_third": "bar",
    "camera_grade": None,
    "sfx": {"chapter": "whoosh", "callout": "pop", "lower_third": "swipe", "set_piece": "bass_impact",
            "transition": "whoosh", "cta_tap": "click", "cta_done": "level_up", "intro": "bass_impact"},
    "music": {"ids": [], "mood": "", "bed": False},
    "font_note": "",
    "long_notes": "",
}

FAMILY = {
    "organic": {},
    "ad": {"captions": {"weight": 800, "case": "upper"}, "transition": {"kind": "slide", "dur": 0.45},
           "chapter_card": "app", "lower_third": "tag",
           "long_notes": "Ad formats drive to a \"Learn more\" button. In long form keep the world for the opening, "
                         "chapter cards and the closing card only; the body is a clean pip/side layout in the "
                         "palette. The closing CTA follows the platform (follow, YouTube subscribe or a link card); "
                         "never invent prices, deadlines or scarcity."},
    "authority": {"captions": {"weight": 700, "case": "none"}, "transition": {"kind": "fade", "dur": 0.6, "ease": "power2.inOut"},
                  "chapter_card": "record", "lower_third": "record", "overlay": {"grain": 0.04, "vignette": 0.35},
                  "sfx": {"chapter": "stamp", "callout": "click", "transition": "page_turn"},
                  "long_notes": "Sober palette with one accent. The expert stays large (side or speaker layout) and "
                                "each chapter opens as a numbered record of the style's object (claim, protocol, "
                                "declaration). No playful set pieces; one engraved rule per chapter at most."},
    "didactic": {"transition": {"kind": "chalk", "dur": 0.6, "ease": "power2.out"}, "chapter_card": "board",
                 "lower_third": "chalk"},
    "layers": {"transition": {"kind": "fade", "dur": 0.5}, "chapter_card": "editorial", "lower_third": "tag",
               "long_notes": "Layered moments (text behind the speaker, depth scans) need a full-frame camera with a "
                             "good matte: use them only in speaker-layout set pieces, never over a screen share."},
    "creator": {"transition": {"kind": "cut", "dur": 0.25}, "chapter_card": "editorial", "lower_third": "tag"},
    # Clean native edit: cuts and animated captions only (no SFX, no music bed, no set pieces).
    "native": {"transition": {"kind": "cut", "dur": 0.0}, "chapter_card": "editorial", "lower_third": "tag",
               "overlay": {"grain": 0.0, "vignette": 0.0},
               "sfx": {"chapter": None, "callout": None, "lower_third": None, "set_piece": None, "transition": None,
                       "cta_tap": None, "cta_done": None, "intro": None}},
}

# One entry per named style. Only what differs from BASE + FAMILY is written.
STYLES = {
    "cinema": {
        "name": "Cinema", "family": "organic",
        "fonts": {"display": "Anton", "caption": "Anton"},
        "captions": {"weight": 400, "case": "upper", "box": None, "stroke": "6px #050a14", "active_fg": "#f5c66b",
                     "active_bg": None, "scale": 1.1},
        "frame": {"border": "4px solid #edc580", "camera_radius": 28},
        "transition": {"kind": "slide", "dur": 0.5},
        "chapter_card": "slate", "lower_third": "bar",
        "sfx": {"chapter": "whoosh", "set_piece": "trailer_hit"},
        "music": {"ids": [293, 369, 597, 686], "mood": "cinematic pulse, drop on the thesis"},
        "long_notes": "The live camera card with a gold border survives the whole video (pip or side). Each "
                      "chapter is a world change: card in the chapter's palette shift, Anton title with a gold rule. "
                      "Set pieces are the style's 'one metaphor per beat' reduced to the key beats: an object with an "
                      "action (stamp, scanner, rewinding tape) on the hook, each central concept and each turn.",
    },
    "ruptura": {
        "name": "Ruptura", "family": "organic",
        "palette": {"accent": "#edc580", "accent2": "#7dd3fc", "alert": "#ff3d57"},
        "fonts": {"display": "Anton", "caption": "Anton"},
        "captions": {"weight": 400, "case": "upper", "box": None, "stroke": "6px #050a14", "active_fg": "#000000",
                     "active_bg": "#ffd84d", "scale": 1.1},
        "transition": {"kind": "flash", "dur": 0.3, "ease": "power4.out"},
        "chapter_card": "slate",
        "sfx": {"chapter": "reverse_impact", "set_piece": "trailer_hit"},
        "music": {"ids": [369, 568, 597], "mood": "tense, silence before the drop"},
        "long_notes": "Open cold with the strongest line of the whole recording (a real spoken line from later, "
                      "then 'from the start'). The camera-as-metaphor moves (clones, split, freeze) become set pieces "
                      "at each turn; the body stays a clean pip. Typographic finale before the closing CTA.",
    },
    "impacto": {
        "name": "Impacto", "family": "organic",
        "palette": {"bg": "#03090e", "bg2": "#0e283a", "surface": "#0e283a", "accent": "#edc580", "accent2": "#7dd3fc"},
        "captions": {"weight": 700, "box": None, "stroke": None, "active_fg": "#edc580", "active_bg": None},
        "frame": {"border": "2px solid #2a576f", "camera_radius": 22},
        "transition": {"kind": "slide", "dur": 0.5},
        "chapter_card": "slate", "lower_third": "plate",
        "sfx": {"chapter": "whoosh", "callout": "stamp", "set_piece": "bass_impact"},
        "music": {"ids": [167, 568, 623], "mood": "steady, two hard hits"},
        "long_notes": "The calm, organised board of argument cards maps naturally to 16:9: the screen in the main "
                      "box, a column of argument cards on the side layout. Keep the coordinated bursts (type + "
                      "sound + zoom) for two or three lines per chapter, never more.",
    },
    "game": {
        "name": "Game (retro RPG)", "family": "organic",
        "palette": {"bg": "#0b0b23", "bg2": "#1d2b53", "surface": "#1d2b53", "accent": "#ffd84d", "accent2": "#7ee7ff",
                    "alert": "#ff004d", "ok": "#00e436"},
        "fonts": {"display": "Press Start 2P", "caption": "VT323", "body": "VT323"},
        "captions": {"weight": 400, "case": "upper", "box": "#0b0b23", "fg": "#ffffff", "active_fg": "#0b0b23",
                     "active_bg": "#ffd84d", "scale": 1.5},
        "frame": {"screen_radius": 0, "camera_radius": 0, "border": "6px solid #ffffff",
                  "shadow": "8px 8px 0 #000000", "world": "linear-gradient(#1d2b53,#0b0b23)"},
        "overlay": {"grain": 0.0, "scanlines": True},
        "transition": {"kind": "wipe", "dur": 0.4, "ease": "steps(8)"},
        "chapter_card": "hud", "lower_third": "hud",
        "camera_grade": "scale=320:-2:flags=neighbor,scale=960:-2:flags=neighbor",
        "sfx": {"chapter": "level_up", "callout": "game_coin", "set_piece": "power_up", "transition": "retro_computer_beep",
                "lower_third": "retro_computer_beep"},
        "music": {"ids": [1117, 167, 597], "mood": "chiptune-adjacent, playful"},
        "long_notes": "Chapters are STAGES (\"STAGE 2 · <title>\"), set pieces are skills unlocked and inventory "
                      "items on the key concepts, the closing card is CONTINUE? with the CTA. The dialog-box caption "
                      "becomes a bottom box in 16:9 (VT323, 2 lines). Pixelated camera only in set pieces: a whole "
                      "class in pixel art tires the eye.",
    },
    "thriller": {
        "name": "Thriller", "family": "organic",
        "palette": {"bg": "#000000", "bg2": "#07130d", "surface": "#030806", "accent": "#39ff88", "accent2": "#ffd84d",
                    "alert": "#ff3d57"},
        "fonts": {"display": "Bebas Neue", "caption": "Inter", "mono": "IBM Plex Mono"},
        "captions": {"weight": 600, "case": "lower", "box": None, "stroke": None, "active_fg": "#ff3d57", "active_bg": None},
        "frame": {"border": "2px solid #39ff88", "camera_radius": 4, "screen_radius": 4},
        "overlay": {"grain": 0.08, "scanlines": True, "vignette": 0.45},
        "transition": {"kind": "glitch", "dur": 0.35},
        "chapter_card": "terminal", "lower_third": "terminal",
        "camera_grade": "eq=saturation=0.35:contrast=1.15,colorbalance=gs=.06",
        "sfx": {"chapter": "glitch", "callout": "data_beep", "set_piece": "heartbeat", "transition": "glitch"},
        "music": {"ids": [187, 568, 597], "mood": "tense to hopeful"},
        "long_notes": "REC overlay and timecode on the camera window; blackout + reboot as the set piece of the "
                      "turn (failure → recovery). Liquid distortion only on short set pieces: on a long screen share it "
                      "hides the content.",
    },
    "ide": {
        "name": "IDE", "family": "organic",
        "palette": {"bg": "#0d0f17", "bg2": "#1e1e1e", "surface": "#252526", "text": "#d4d4d4", "muted": "#858585",
                    "accent": "#4fc1ff", "accent2": "#c586c0", "ok": "#6a9955", "alert": "#f44747"},
        "fonts": {"display": "JetBrains Mono", "caption": "JetBrains Mono", "body": "Inter"},
        "captions": {"weight": 700, "box": "#1e1e1e", "fg": "#6a9955", "active_fg": "#ffffff", "active_bg": "#264f78",
                     "prefix": "# "},
        "frame": {"camera_shape": "circle", "border": "3px solid #4fc1ff", "screen_radius": 10},
        "transition": {"kind": "cut", "dur": 0.2},
        "chapter_card": "terminal", "lower_third": "terminal",
        "sfx": {"chapter": "keyboard", "callout": "mouse_click", "set_piece": "success_chime", "transition": "click"},
        "music": {"ids": [167, 282, 623], "mood": "focused lo-fi"},
        "long_notes": "The most natural long-form style for programming classes: the real screen share is the "
                      "editor, the webcam is a circular bubble, captions are code comments in the bottom panel, "
                      "chapters open as a new file tab (`02-chapter.md`). Set pieces: a terminal that runs the step "
                      "the speaker describes, a diff highlight, a test going green.",
    },
    "aeroporto": {
        "name": "Aeroporto (control tower)", "family": "organic",
        "palette": {"bg": "#010302", "bg2": "#07170e", "surface": "#06120c", "text": "#cfe9d8", "accent": "#ffb000",
                    "accent2": "#39ff6a", "alert": "#ff2d2d"},
        "fonts": {"display": "Bebas Neue", "caption": "IBM Plex Mono", "mono": "IBM Plex Mono"},
        "captions": {"weight": 700, "box": "#000000", "fg": "#cfe9d8", "active_fg": "#000000", "active_bg": "#ffb000"},
        "frame": {"border": "3px solid #ffb000", "camera_radius": 6, "screen_radius": 6},
        "transition": {"kind": "wipe", "dur": 0.45},
        "chapter_card": "terminal", "lower_third": "terminal",
        "sfx": {"chapter": "data_beep", "callout": "sonar_ping", "set_piece": "riser"},
        "music": {"ids": [187, 597, 677], "mood": "tension to release"},
        "long_notes": "Chapters are flights on a split-flap departures board (title as destination, status "
                      "BOARDING → DEPARTED). Radio-transmission captions in the bottom band. Set piece for each "
                      "approval/deploy moment: clearance for take-off.",
    },
    "chat": {
        "name": "Chat (light messenger)", "family": "organic",
        "palette": {"bg": "#efe6da", "bg2": "#e1d3c0", "surface": "#ffffff", "text": "#111111", "muted": "#5b6a67",
                    "accent": "#1f9d6b", "accent2": "#0f5a49"},
        "fonts": {"display": "Geist", "caption": "Inter"},
        "captions": {"weight": 600, "box": "#d9fdd3", "fg": "#111111", "active_fg": "#111111", "active_bg": "#ffe066"},
        "frame": {"border": "0 solid transparent", "camera_radius": 24, "screen_radius": 16,
                  "shadow": "0 10px 30px rgba(0,0,0,.18)", "world": "#efe6da"},
        "overlay": {"grain": 0.0, "vignette": 0.0},
        "transition": {"kind": "slide", "dur": 0.4, "ease": "power3.out"},
        "chapter_card": "app", "lower_third": "tag",
        "sfx": {"chapter": "message_received", "callout": "message_sent", "set_piece": "notify"},
        "music": {"ids": [187, 282, 33], "mood": "light"},
        "long_notes": "Light theme: check contrast of the screen share against the wallpaper. Captions as sent "
                      "bubbles (one per sentence) at the bottom; chapter cards as a pinned message; the bot replies "
                      "are the set pieces on key concepts.",
    },
    "documentario": {
        "name": "Documentário", "family": "organic",
        "palette": {"bg": "#000000", "bg2": "#0b0906", "surface": "#120f0a", "text": "#f6efe1", "muted": "#cdc6b9",
                    "accent": "#e2b866", "accent2": "#f7d993"},
        "fonts": {"display": "Fraunces", "caption": "Fraunces", "body": "Inter"},
        "captions": {"weight": 500, "box": None, "stroke": None, "fg": "#e8e2d6", "active_fg": "#f6efe1",
                     "active_bg": None, "underline": "#e2b866", "scale": 1.05},
        "frame": {"border": "0 solid transparent", "camera_radius": 0, "screen_radius": 0, "shadow": "none",
                  "world": "#000000"},
        "overlay": {"grain": 0.09, "letterbox": True, "vignette": 0.3},
        "transition": {"kind": "fade", "dur": 0.9, "ease": "sine.inOut"},
        "chapter_card": "serif", "lower_third": "plate",
        "camera_grade": "curves=preset=increase_contrast,colortemperature=temperature=5200,eq=saturation=0.85",
        "sfx": {"chapter": "cymbal_swell", "callout": "page_turn", "set_piece": "sub_drop", "transition": "ocean_wave_whoosh"},
        "music": {"ids": [187, 31, 871, 955], "mood": "emotional piano/strings", "bed": True},
        "long_notes": "Made for long form. 2.39:1 letterbox inside 16:9, serif chapter cards on black "
                      "(\"Capítulo 2\" + title), serif subtitles with an underlined active word, slow push-ins on the "
                      "speaker. Screen shares enter as archive footage (grain, slight vignette). Rolling credits as "
                      "the closing card.",
    },
    "documentario-narrado": {
        "name": "Documentário narrado (atlas)", "family": "organic",
        "palette": {"bg": "#041117", "bg2": "#0c3039", "surface": "#08303b", "text": "#f3ead7", "muted": "#cfc4ad",
                    "accent": "#f2cf60", "accent2": "#ca995c", "alert": "#952e2f", "ok": "#76ba65"},
        "fonts": {"display": "DM Serif Display", "caption": "Inter", "body": "Inter", "serif": "DM Serif Display"},
        "captions": {"weight": 600, "box": None, "stroke": None, "fg": "#f3ead7", "active_fg": "#0b0906",
                     "active_bg": "#f2cf60", "scale": 1.05},
        "frame": {"border": "3px solid #ca995c", "camera_radius": 0, "screen_radius": 4,
                  "shadow": "0 0 0 1px rgba(0,0,0,.6), 0 24px 60px rgba(0,0,0,.7)",
                  "world": "radial-gradient(ellipse 85% 75% at 50% 45%,#0a2129 0%,#041117 62%,#020709 100%)"},
        "overlay": {"grain": 0.1, "letterbox": False, "vignette": 0.35},
        "transition": {"kind": "flash", "dur": 0.45, "ease": "power2.out"},
        "chapter_card": "serif", "lower_third": "plate",
        "camera_grade": "eq=saturation=0.80:contrast=1.08:brightness=0.01,"
                        "colorbalance=rs=.05:gs=.01:bs=-.06:rm=.04:bm=-.05,noise=alls=7:allf=t",
        "sfx": {"chapter": "bass_impact", "callout": "swipe", "lower_third": "page_turn", "set_piece": "sub_drop",
                "transition": "ocean_wave_whoosh", "intro": "bass_impact"},
        "font_note": "Cinzel 700 (years, chapter cards), Cormorant Garamond Italic 600 (card titles, questions) and "
                     "Barlow Condensed 600/800 (captions, map labels, fact notes), all OFL, for full fidelity",
        "music": {"ids": [31, 955, 686], "mood": "cinematic documentary in sections, hard silences before the cards",
                  "bed": True},
        "long_notes": "The reference language is a long-form narrated history documentary, so it fits naturally. "
                      "A night globe (Natural Earth) is the bridge between chapters: fly the virtual camera to the "
                      "chapter's region, lights and routes on the spoken words. Chapter cards are dated (year or "
                      "roman numeral + italic title) after a 0.3-0.5 s music-only silence, with a low impact and an "
                      "amber flash out. The speaker has three states: film-graded testimony plate (speaker/side "
                      "layout) on key lines, a gold-ringed medallion over the map, voice-over over generated period "
                      "paintings in 2.5D parallax. Fast opening, then 6-9 s per shot, slower on grave chapters; "
                      "verified fact notes with a source; the close loops back to the first globe shot with "
                      "\"next chapter\".",
    },
    "podcast": {
        "name": "Podcast (talk show)", "family": "organic",
        "palette": {"bg": "#2a0838", "bg2": "#7a2ff0", "surface": "#ff5b35", "text": "#ffffff", "accent": "#ffe14d",
                    "accent2": "#5ff3ff", "alert": "#e8287f", "ok": "#3dff8f"},
        "fonts": {"display": "Anton", "caption": "Anton"},
        "captions": {"weight": 400, "case": "upper", "box": None, "stroke": "6px #111111", "active_fg": "#ffe14d",
                     "active_bg": None, "scale": 1.2},
        "frame": {"border": "6px solid #111111", "shadow": "14px 14px 0 #111111", "camera_radius": 10},
        "transition": {"kind": "wipe", "dur": 0.35, "ease": "power4.inOut"},
        "chapter_card": "broadcast", "lower_third": "bar",
        "sfx": {"chapter": "tv_news_sting", "callout": "pop", "set_piece": "crowd_cheer_short"},
        "music": {"ids": [1117, 282, 33], "mood": "energetic", "bed": False},
        "long_notes": "Lives and long conversations: ON AIR sign with the chapter, a voice-reactive waveform in "
                      "the side column, segment colours per chapter (coral, purple, magenta, amber). Giant karaoke "
                      "captions only in set pieces; the body uses two-line captions.",
    },
    "missao": {
        "name": "Missão (open-world homage)", "family": "organic",
        "palette": {"bg": "#07031a", "bg2": "#4a1262", "surface": "#1d0a3e", "accent": "#ff2bd6", "accent2": "#ffa24a",
                    "ok": "#2bb7b0"},
        "fonts": {"display": "Anton", "caption": "Inter"},
        "captions": {"weight": 800, "box": "rgba(10,4,30,.80)", "active_fg": "#ffffff", "active_bg": "#9c1f6e"},
        "frame": {"border": "4px solid #ff2bd6", "camera_radius": 18,
                  "world": "linear-gradient(#07031a 0%,#4a1262 45%,#e8365f 75%,#ffa24a 100%)"},
        "transition": {"kind": "wipe", "dur": 0.45},
        "chapter_card": "neon", "lower_third": "tag",
        "camera_grade": "colorbalance=rh=.06:bh=-.04:rs=-.03:bs=.05,eq=saturation=1.15",
        "sfx": {"chapter": "whoosh", "callout": "coins", "set_piece": "sub_drop"},
        "music": {"ids": [1117, 126, 167, 187], "mood": "synth, sunset"},
        "long_notes": "Chapters are missions (MISSION 2 card, GPS route between chapters), character-intro "
                      "freeze-frame for the speaker's lower third, MISSION COMPLETE banner before the CTA.",
    },
    "tribunal": {
        "name": "Tribunal (courtroom sketch)", "family": "organic",
        "palette": {"bg": "#3f1d10", "bg2": "#5b2c1a", "surface": "#e9dcc3", "text": "#2b2522", "accent": "#edc580",
                    "accent2": "#8fb8d6", "alert": "#c0322b"},
        "fonts": {"display": "DM Serif Display", "caption": "IBM Plex Mono"},
        "captions": {"weight": 700, "box": "#fbf7ee", "fg": "#111111", "active_fg": "#000000", "active_bg": "#ffd84d"},
        "frame": {"border": "8px solid #5b2c1a", "camera_radius": 4, "world": "linear-gradient(#5b2c1a,#3f1d10)"},
        "transition": {"kind": "page", "dur": 0.6},
        "chapter_card": "record", "lower_third": "record",
        "sfx": {"chapter": "stamp", "callout": "pen_write", "set_piece": "cage_or_metal_slam"},
        "music": {"ids": [597, 680, 871], "mood": "grave"},
        "long_notes": "Chapters are exhibits (EXHIBIT A, B…), the speaker is the expert witness on the court monitor "
                      "(side layout), the verdict is the set piece of the conclusion.",
    },
    "keynote": {
        "name": "Keynote (launch stage)", "family": "ad",
        "palette": {"bg": "#060403", "bg2": "#120c05", "accent": "#e2b04c", "accent2": "#ffd479"},
        "fonts": {"display": "Geist", "caption": "Geist"},
        "captions": {"weight": 900, "box": "rgba(12,9,4,.88)"},
        "frame": {"border": "2px solid #e2b04c", "camera_radius": 12},
        "chapter_card": "slate", "lower_third": "plate",
        "music": {"ids": [187, 31, 623], "mood": "celebratory"},
    },
    "stories": {
        "name": "Stories (behind the scenes)", "family": "ad",
        "palette": {"bg": "#0c0c12", "bg2": "#5b2bff", "accent": "#d7ff3a", "accent2": "#ff4d6d"},
        "fonts": {"display": "Fredoka", "caption": "Geist"},
        "captions": {"weight": 900, "box": "#ffffff", "fg": "#111111", "active_fg": "#000000", "active_bg": "#d7ff3a"},
        "frame": {"camera_radius": 28, "border": "4px solid #ffffff"},
        "chapter_card": "app",
        "music": {"ids": [187, 282, 623], "mood": "light, fast"},
    },
    "predio-24h": {
        "name": "Prédio 24h (isometric company)", "family": "ad",
        "palette": {"bg": "#17184a", "bg2": "#2c2e7c", "accent": "#ffd84d", "accent2": "#7fd6c4", "surface": "#fff1d6"},
        "fonts": {"display": "Fredoka", "caption": "Fredoka"},
        "captions": {"weight": 700, "box": "#fff1d6", "fg": "#1d1b4f", "active_fg": "#000000", "active_bg": "#ffd84d"},
        "chapter_card": "app",
        "music": {"ids": [167, 187, 568, 623], "mood": "optimistic"},
        "long_notes": "Each chapter is a floor of the building lighting up; day/night cycle across the video.",
    },
    "bilheteria": {
        "name": "Bilheteria (retro box office)", "family": "ad",
        "palette": {"bg": "#120608", "bg2": "#9c1c12", "surface": "#f7e8c9", "accent": "#f2b53a", "accent2": "#e0452b",
                    "text": "#f7e8c9"},
        "fonts": {"display": "Anton", "caption": "Anton"},
        "captions": {"weight": 400, "box": "#f7e8c9", "fg": "#2b160e", "active_fg": "#ffffff", "active_bg": "#9c1c12"},
        "chapter_card": "app",
        "font_note": "Bungee / Alfa Slab One (OFL) for full fidelity",
        "music": {"ids": [31, 33, 369], "mood": "retro"},
    },
    "porta-de-aco": {
        "name": "Porta de aço (steel shutter)", "family": "ad",
        "palette": {"bg": "#07060c", "bg2": "#140b1c", "accent": "#29f0ff", "accent2": "#ff2bd6", "surface": "#23272f"},
        "fonts": {"display": "Anton", "caption": "Anton"},
        "captions": {"weight": 400, "box": "rgba(8,6,12,.9)", "active_fg": "#000000", "active_bg": "#bff9ff"},
        "chapter_card": "neon",
        "font_note": "Tilt Neon (OFL) for the signs",
        "music": {"ids": [293, 31, 597, 623], "mood": "urgent, nocturnal"},
    },
    "lapidacao": {
        "name": "Lapidação (luxury jewellery commercial)", "family": "ad",
        "palette": {"bg": "#050506", "bg2": "#0b0c10", "surface": "#111217", "text": "#eef3f7", "muted": "#9aa3b2",
                    "accent": "#edc580", "accent2": "#dce8ff", "alert": "#ff5f57", "ok": "#edc580"},
        "fonts": {"display": "Geist", "caption": "Geist", "mono": "JetBrains Mono"},
        "captions": {"weight": 800, "case": "upper", "box": None, "active_fg": "#000000", "active_bg": "#f3d79b"},
        "frame": {"border": "1px solid rgba(237,197,128,.45)", "camera_radius": 20,
                  "world": "radial-gradient(ellipse 120% 70% at 50% 30%,#0b0c10 0%,#050506 55%,#020203 100%)"},
        "transition": {"kind": "flash", "dur": 0.3, "ease": "power2.out"},
        "chapter_card": "slate", "lower_third": "plate",
        "sfx": {"chapter": "lock_click", "callout": "magic_sparkle", "set_piece": "trailer_hit", "transition": "whoosh"},
        "music": {"ids": [568, 167, 623], "mood": "driving electronic that builds to a drop on the reveal; louder bed"},
        "long_notes": "Chapters as objects under a spotlight on black velvet: the raw material of the chapter drops as "
                      "a rough stone, the explanation is the cut (laser, facets, flash) and the result is the gem with "
                      "its parts named; a jeweller's loupe reviews screen recordings; keep the case/tag/rope set "
                      "pieces for the offer chapter only.",
    },
    "manual-de-montagem": {
        "name": "Manual de montagem (assembly blueprint)", "family": "ad",
        "palette": {"bg": "#0a2c6e", "bg2": "#0f3f95", "accent": "#ffd84d", "accent2": "#ffffff", "ok": "#4ade80"},
        "fonts": {"display": "Anton", "caption": "Anton", "mono": "B612 Mono"},
        "captions": {"weight": 400, "box": "#0a2c6e", "active_fg": "#000000", "active_bg": "#ffd84d"},
        "frame": {"border": "3px solid #ffffff", "camera_radius": 4, "screen_radius": 4,
                  "world": "linear-gradient(#0f3f95,#0a2c6e)"},
        "chapter_card": "terminal",
        "music": {"ids": [167, 568, 623], "mood": "precise"},
        "long_notes": "Very good for step-by-step classes: each chapter is an assembly step with numbered parts; "
                      "the blueprint grid frames the screen share.",
    },
    "carrinho": {
        "name": "Carrinho (forgotten cart)", "family": "ad",
        "palette": {"bg": "#12070f", "bg2": "#2a1030", "accent": "#ff6a4d", "accent2": "#ffc94d", "ok": "#3ddc97"},
        "captions": {"weight": 400, "box": "#1d0d18", "active_fg": "#000000", "active_bg": "#ffd84d"},
        "fonts": {"display": "Anton", "caption": "Anton"},
        "music": {"ids": [282, 623], "mood": "friendly"},
    },
    "entrega": {
        "name": "Entrega (order tracking)", "family": "ad",
        "palette": {"bg": "#071618", "bg2": "#0c2a2c", "accent": "#d8f44a", "accent2": "#ffb547", "ok": "#1a7f5a"},
        "fonts": {"display": "Anton", "caption": "Anton"},
        "captions": {"weight": 400, "box": "rgba(6,18,20,.94)", "active_fg": "#000000", "active_bg": "#d8f44a"},
        "music": {"ids": [167, 187, 623], "mood": "brisk"},
        "long_notes": "The tracking timeline is a natural chapter bar: each chapter is a delivery stage.",
    },
    "auditorio": {
        "name": "Auditório (TV quiz show)", "family": "ad",
        "palette": {"bg": "#3a0610", "bg2": "#7c1022", "accent": "#ffc53d", "accent2": "#2f5bff", "ok": "#18d26a"},
        "fonts": {"display": "Bebas Neue", "caption": "Anton"},
        "captions": {"weight": 400, "box": "rgba(22,4,10,.95)", "active_fg": "#000000", "active_bg": "#ffd84d"},
        "chapter_card": "broadcast",
        "music": {"ids": [31, 33, 82], "mood": "playful"},
        "long_notes": "Q&A sessions and lives: each audience question is a round (chapter), the answer gets the "
                      "green light set piece.",
    },
    "album": {
        "name": "Álbum (sticker album)", "family": "ad",
        "palette": {"bg": "#392e58", "bg2": "#21182f", "surface": "#e8ddf1", "accent": "#ffd84d", "accent2": "#e1d5ec"},
        "fonts": {"display": "Anton", "caption": "Anton"},
        "captions": {"weight": 400, "box": "#21182f", "active_fg": "#000000", "active_bg": "#ffd84d"},
        "music": {"ids": [282, 623, 82], "mood": "collectible"},
        "long_notes": "Tool lists become stickers collected across the video; the recap shows the full page.",
    },
    "cassino-de-precisao": {
        "name": "Cassino de precisão", "family": "authority",
        "palette": {"bg": "#060807", "bg2": "#0c3528", "surface": "#145440", "text": "#efe6d2", "accent": "#d4b26a",
                    "accent2": "#5b6266"},
        "fonts": {"display": "Bebas Neue", "caption": "Bebas Neue"},
        "captions": {"weight": 400, "case": "upper", "box": None, "fg": "#efe6d2", "active_fg": "#000000",
                     "active_bg": "#ffd970", "scale": 1.25},
        "frame": {"border": "2px solid #b8964f"},
        "music": {"ids": [568, 597, 677], "mood": "tense to controlled"},
    },
    "mesa-de-risco": {
        "name": "Mesa de risco (trading desk)", "family": "authority",
        "palette": {"bg": "#050608", "bg2": "#0a0c0f", "surface": "#0a0c0f", "text": "#e8ecf1", "muted": "#8d97a3",
                    "accent": "#2fd27a", "alert": "#ff3b4f"},
        "fonts": {"display": "Bebas Neue", "caption": "IBM Plex Mono"},
        "captions": {"weight": 700, "box": "#0a0c0f", "active_fg": "#ffffff", "active_bg": "#c4122f"},
        "font_note": "IBM Plex Sans Condensed (OFL) for full fidelity",
        "music": {"ids": [568, 677, 680], "mood": "tense to green"},
    },
    "turno-da-madrugada": {
        "name": "Turno da madrugada (night shift)", "family": "authority",
        "palette": {"bg": "#07090c", "bg2": "#0e1216", "surface": "#151a1f", "text": "#e8ecef", "muted": "#8b949c",
                    "accent": "#ffb21c", "accent2": "#5fb8c6", "ok": "#39d98a"},
        "fonts": {"display": "Bebas Neue", "caption": "Bebas Neue"},
        "captions": {"weight": 400, "case": "upper", "box": "#0a0d11", "active_fg": "#000000", "active_bg": "#ffcf4a",
                     "scale": 1.2},
        "font_note": "Barlow Condensed (OFL) for full fidelity",
        "music": {"ids": [31, 568, 597, 677], "mood": "austere"},
        "long_notes": "Long processes and lives that run for hours: a shift clock in the corner advances with the "
                      "video; chapters are log entries.",
    },
    "arquivo-cofre": {
        "name": "Arquivo-cofre (archive)", "family": "authority",
        "palette": {"bg": "#090b0d", "bg2": "#111418", "surface": "#e7e1d2", "text": "#eef0f2", "accent": "#2f5bff",
                    "accent2": "#dfe8f0"},
        "fonts": {"display": "Bebas Neue", "caption": "IBM Plex Mono"},
        "captions": {"weight": 700, "box": "#e3e5e1", "fg": "#15171a", "active_fg": "#ffffff", "active_bg": "#2343d6"},
        "font_note": "Archivo Condensed (OFL) for full fidelity",
        "music": {"ids": [167, 597, 871], "mood": "quiet"},
    },
    "aduana-de-dados": {
        "name": "Aduana de dados (data checkpoint)", "family": "authority",
        "palette": {"bg": "#061418", "bg2": "#0a1f25", "surface": "#0f2a31", "text": "#ece6d6", "muted": "#8fb3ba",
                    "accent": "#c8102e", "accent2": "#3f7f8c"},
        "fonts": {"display": "Bebas Neue", "caption": "Bebas Neue"},
        "captions": {"weight": 400, "case": "upper", "box": "#08191e", "fg": "#ece6d6", "active_fg": "#ffffff",
                     "active_bg": "#a50e24", "scale": 1.2},
        "font_note": "Big Shoulders Display (OFL) for full fidelity",
        "music": {"ids": [293, 871], "mood": "grave"},
    },
    "laudo-de-sinistro": {
        "name": "Laudo de sinistro (forensic report)", "family": "authority",
        "palette": {"bg": "#111315", "bg2": "#191c1f", "surface": "#ebe6db", "text": "#ebe6db", "accent": "#f5c400",
                    "accent2": "#8b9095"},
        "fonts": {"display": "Bebas Neue", "caption": "Bebas Neue"},
        "captions": {"weight": 400, "case": "upper", "box": "#e2dccf", "fg": "#1a1d20", "active_fg": "#000000",
                     "active_bg": "#ffd84d", "scale": 1.2},
        "font_note": "Archivo (OFL) for full fidelity",
        "music": {"ids": [293, 369, 871], "mood": "sober"},
    },
    "lousa-de-aula": {
        "name": "Lousa de aula (chalkboard lesson)", "family": "didactic",
        "palette": {"bg": "#1d2f27", "bg2": "#23372e", "surface": "#1d2f27", "text": "#f1eee3", "muted": "#b8c4bb",
                    "accent": "#f4dc72", "accent2": "#9fd2ee", "alert": "#f2a7bd"},
        "fonts": {"display": "Caveat", "caption": "Caveat", "body": "Caveat"},
        "captions": {"weight": 700, "box": None, "stroke": None, "fg": "#f1eee3", "active_fg": "#1d2f27",
                     "active_bg": "#f4dc72", "scale": 1.25},
        "frame": {"border": "10px solid #6b4a2c", "camera_radius": 2, "screen_radius": 2,
                  "shadow": "0 12px 30px rgba(0,0,0,.6)",
                  "world": "radial-gradient(ellipse 90% 80% at 50% 45%,#23372e,#1d2f27 70%,#16241e)"},
        "overlay": {"grain": 0.1, "vignette": 0.3},
        "chapter_card": "board", "lower_third": "chalk",
        "sfx": {"chapter": "pen_write", "callout": "pen_write", "set_piece": "lightbulb_ding", "transition": "page_turn"},
        "font_note": "Kalam Bold (OFL) for full fidelity",
        "music": {"ids": [282, 31, 955], "mood": "calm, didactic"},
        "long_notes": "The natural style for classes. The slate is the world around the screen share (framed in "
                      "oak like a projected slide); chapters are syllabus items whose '?' turns into ✓; concept-map "
                      "set pieces are drawn live on the trigger words (±0.15 s); a SUMMARY board closes each chapter.",
    },
    "trailer": {
        "name": "Trailer (movie trailer)", "family": "organic",
        "palette": {"bg": "#000000", "bg2": "#03090e", "surface": "#03090e", "text": "#eceaf2", "muted": "#cfc6ff",
                    "accent": "#9a7cff", "accent2": "#edc580", "alert": "#ff5a4f"},
        "fonts": {"display": "Geist", "caption": "Geist", "body": "Geist"},
        "captions": {"weight": 700, "case": "upper", "box": "rgba(3,9,14,.46)", "stroke": "5px #03090e", "fg": "#ffffff",
                     "active_fg": "#03090e", "active_bg": "#ffffff"},
        "frame": {"border": "1.5px solid rgba(236,234,242,.7)", "camera_radius": 0, "screen_radius": 18,
                  "letterbox": True},
        "overlay": {"grain": 0.11, "vignette": 0.4},
        "transition": {"kind": "flash", "dur": 0.3},
        "chapter_card": "serif", "lower_third": "plate",
        "camera_grade": "selectivecolor=magentas='-0.25 0.32 0.12 0':yellows='0 0 -0.10 0',huesaturation=hue=-10:"
                        "saturation=-0.6:colors=m,colortemperature=temperature=7000:mix=0.5,eq=contrast=1.30:"
                        "brightness=-0.05:saturation=0.76:gamma=1.07,vignette=PI/3.9",
        "sfx": {"chapter": "trailer_hit", "callout": "bass_impact", "set_piece": "riser", "transition": "whoosh"},
        "font_note": "Geist caps, tracking 0.3-0.42 em; Mixkit cinematic stems by id in references/styles/trailer.md",
        "music": {"ids": [871, 677, 686], "mood": "suspense → escalation → reveal (v2 used Mixkit 614/1011/678/686)"},
        "long_notes": "Chapters open as black title cards (gold serif, hit + braam in a short inserted pause, voice at "
                      "1x); the speaker stays full frame with the trailer grade and letterbox, screen shares sit in a "
                      "gold-bordered window. Keep the big beats (black cards, silence, climax) for the 3-5 key "
                      "moments of the video: a long video cannot carry trailer density end to end.",
    },
    "nativo": {
        "name": "Nativo (clean native edit)", "family": "native",
        "palette": {"bg": "#000000", "bg2": "#0a0a0a", "surface": "#000000", "text": "#ffffff", "muted": "#c9c9c9",
                    "accent": "#ffd84d", "accent2": "#ffffff"},
        "fonts": {"display": "Inter", "body": "Inter", "caption": "Inter"},
        "captions": {"weight": 900, "case": "none", "fg": "#ffffff", "active_fg": "#000000", "active_bg": "#ffd84d",
                     "box": None, "stroke": "10px #000000", "scale": 1.1},
        "frame": {"border": "none", "camera_radius": 0, "screen_radius": 0, "shadow": "none", "world": "#000000"},
        "music": {"ids": [], "mood": "none (voice only unless the user asks for a soft bed)", "bed": False},
        "long_notes": "Cuts and animated captions only: pauses, false starts and repetitions removed (long edl), "
                      "camera or screen full frame with a hard cut between layouts, word-by-word captions. No set "
                      "pieces, callouts, lower thirds, SFX or music unless the user asks; chapters go to the "
                      "description (YouTube timestamps), not on screen.",
    },
    "gravidade": {
        "name": "Gravidade (the speech has weight)", "family": "organic",
        "palette": {"bg": "#020308", "bg2": "#0a0e18", "surface": "#161c2c", "text": "#f4f8fb", "muted": "#9fb3c4",
                    "accent": "#f5c66b", "accent2": "#7dffb0", "alert": "#ff6b6b", "ok": "#7dffb0"},
        "fonts": {"display": "Anton", "caption": "Anton"},
        "captions": {"weight": 400, "case": "upper", "box": None, "stroke": "6px #020308", "active_fg": "#000000",
                     "active_bg": "#ffd84d", "scale": 1.05},
        "frame": {"border": "3px solid #2a3654", "camera_radius": 24,
                  "world": "radial-gradient(ellipse 80% 60% at 50% 70%,#0a0e18 0%,#020308 75%)"},
        "transition": {"kind": "flash", "dur": 0.35, "ease": "power3.out"},
        "chapter_card": "slate", "lower_third": "plate",
        "sfx": {"chapter": "stamp", "callout": "lock_click", "set_piece": "trailer_hit", "transition": "whoosh"},
        "music": {"ids": [680, 677, 369], "mood": "restless percussion, silence before the impact"},
        "long_notes": "Physics set pieces (physkit, baked): problems fall into a heap on their words, the turn lands "
                      "as a heavy block that throws the heap, the answer stacks as a straight tower. Keep the room "
                      "to the key beats of each chapter (render cost ~1 s/frame) and a clean pip/side layout in "
                      "between; chapter cards as a block landing with the chapter name.",
    },
    "circuito": {
        "name": "Circuito (circuit board)", "family": "didactic",
        "palette": {"bg": "#020a07", "bg2": "#08261c", "surface": "#0a110e", "text": "#e6f1ea", "muted": "#8fb7a5",
                    "accent": "#d9a441", "accent2": "#7dffb0", "alert": "#ff5c6c", "ok": "#7dffb0"},
        "fonts": {"display": "JetBrains Mono", "body": "JetBrains Mono", "mono": "JetBrains Mono",
                  "caption": "JetBrains Mono"},
        "captions": {"weight": 800, "case": "upper", "box": None, "stroke": "6px #03100b", "fg": "#ffffff",
                     "active_fg": "#03100b", "active_bg": "#7dffb0", "scale": 0.9},
        "frame": {"border": "3px solid #3b6a57", "camera_radius": 10, "screen_radius": 8,
                  "shadow": "0 0 24px rgba(125,255,176,.18)",
                  "world": "radial-gradient(ellipse 85% 60% at 50% 48%,#08261c 0%,#051710 55%,#020a07 100%)"},
        "overlay": {"grain": 0.03, "vignette": 0.3},
        "transition": {"kind": "wipe", "dur": 0.5, "ease": "power2.inOut"},
        "chapter_card": "terminal", "lower_third": "terminal",
        "sfx": {"chapter": "power_up", "callout": "data_beep", "lower_third": "scan", "set_piece": "magic_transition",
                "transition": "swipe", "cta_tap": "click", "cta_done": "success_chime", "intro": "power_up"},
        "music": {"ids": [167, 568, 623], "mood": "mechanical electronic, drop on the thesis title"},
        "long_notes": "The screen share becomes the main chip (green-outlined, pins around it); chapter cards are "
                      "new boards with the chapter name in silkscreen; concept-map set pieces are components drawn "
                      "on their words (DrawSVG), copper traces on the verbs and pulses (MotionPath) for data that "
                      "travels; LEDs and flags give the verdict per part.",
    },
    "planta-de-acesso": {
        "name": "Planta de acesso (access floor plan)", "family": "didactic",
        "palette": {"bg": "#061a38", "bg2": "#0a2a55", "surface": "#0e2e5c", "text": "#e8f3ff", "muted": "#9cc7ff",
                    "accent": "#edc580", "accent2": "#ffd84d", "alert": "#ff5468", "ok": "#7dffb0"},
        "fonts": {"display": "Bebas Neue", "body": "B612 Mono", "mono": "B612 Mono", "caption": "Geist"},
        "captions": {"weight": 800, "case": "upper", "box": None, "stroke": "9px #061a38", "fg": "#ffffff",
                     "active_fg": "#000000", "active_bg": "#ffd84d", "scale": 0.9},
        "frame": {"border": "2px solid rgba(150,195,255,.45)", "camera_radius": 6, "screen_radius": 6,
                  "shadow": "0 18px 40px rgba(0,0,0,.45)",
                  "world": "radial-gradient(ellipse 85% 60% at 50% 42%,#123a72 0%,#0a2a55 48%,#061a38 100%)"},
        "overlay": {"grain": 0.06, "vignette": 0.2},
        "transition": {"kind": "page", "dur": 0.55, "ease": "power3.inOut"},
        "chapter_card": "terminal", "lower_third": "tag",
        "sfx": {"chapter": "page_turn", "callout": "pen_write", "lower_third": "click", "set_piece": "door_slam",
                "transition": "whoosh", "cta_tap": "click", "cta_done": "level_up", "intro": "scan"},
        "music": {"ids": [187, 167, 31], "mood": "hopeful electronic that builds; kick on the proposal"},
        "long_notes": "Each chapter is a new sheet of the plan (A, B, C…) with a PRELIMINARY STUDY stamp; the screen "
                      "share is the sheet's main drawing; set pieces are rooms with doors drawn on their words, "
                      "badges per role that open or lock the doors, and a legend box as the chapter recap.",
    },
    "camadas": {
        "name": "Camadas (concept layers)", "family": "layers",
        "palette": {"bg": "#07060c", "bg2": "#14101f", "accent": "#ff7a59", "accent2": "#b9a6ff", "ok": "#6ef0ff"},
        "captions": {"weight": 800, "box": None, "stroke": "2px #07060c", "active_fg": "#ff7a59", "active_bg": None},
        "music": {"ids": [167, 623, 82], "mood": "premium"},
    },
    "raio-x": {
        "name": "Raio-X (the machine's view)", "family": "layers",
        "palette": {"bg": "#06050b", "bg2": "#0e0a1c", "surface": "#0e0a1c", "text": "#e9e4ff", "accent": "#c9a8ff",
                    "accent2": "#ff5fa2", "ok": "#34d27b"},
        "captions": {"weight": 800, "case": "lower", "box": None, "active_fg": "#c9a8ff", "active_bg": None},
        "frame": {"border": "1px solid #3b2a6b"},
        "chapter_card": "terminal", "lower_third": "terminal",
        "sfx": {"chapter": "scan", "callout": "data_beep", "set_piece": "robot_processing"},
        "music": {"ids": [167, 568, 597, 623], "mood": "analytical"},
        "long_notes": "Pipeline HUD as the chapter bar (each chapter is a stage); depth scan / point cloud only in "
                      "speaker-layout set pieces.",
    },
    "duelo": {
        "name": "Duelo (A/B page)", "family": "creator",
        "palette": {"bg": "#f4f4f6", "bg2": "#e9e9ee", "surface": "#0d0d12", "text": "#0b0b0f", "accent": "#ff6b4a",
                    "accent2": "#2fe39a"},
        "fonts": {"display": "Bebas Neue", "caption": "Geist"},
        "captions": {"weight": 900, "box": None, "fg": "#0b0b0f", "active_fg": "#000000", "active_bg": "#ffd84d"},
        "frame": {"border": "0 solid transparent", "camera_radius": 24, "screen_radius": 24,
                  "shadow": "0 18px 40px rgba(0,0,0,.18)", "world": "linear-gradient(#f4f4f6,#e9e9ee)"},
        "overlay": {"grain": 0.0, "vignette": 0.0},
        "music": {"ids": [33, 623, 82], "mood": "competitive"},
        "long_notes": "Comparisons in long form: side layout with two panels A/B for the comparison chapters only.",
    },
    "bancada": {
        "name": "Bancada (proof on the workbench)", "family": "creator",
        "palette": {"accent": "#ff5a36"},
        "captions": {"weight": 900, "case": "lower", "box": None, "stroke": "5px #000000", "active_fg": "#ffffff",
                     "active_bg": None},
        "music": {"ids": [282, 623], "mood": "casual"},
        "long_notes": "Demos: whip pan from face to screen at each proof, finger/punch-in callouts on the screen "
                      "share (screen layout with zoom).",
    },
    "manchete": {
        "name": "Manchete (headline inset)", "family": "creator",
        "palette": {"bg": "#0b0b0f", "bg2": "#16161c", "accent": "#ff3b30", "accent2": "#ffffff"},
        "captions": {"weight": 900, "case": "lower", "box": None, "stroke": "5px #000000", "active_fg": "#ffffff",
                     "active_bg": None},
        "chapter_card": "broadcast",
        "music": {"ids": [293, 597, 82], "mood": "hot take"},
        "long_notes": "Reaction videos: the subject (screen) on top, the speaker below; headline banner per chapter.",
    },
    "reacao": {
        "name": "Reação (the speaker in front of the post)", "family": "layers",
        "palette": {"bg": "#0b0b0f", "bg2": "#16161c", "text": "#ffffff", "accent": "#2f6bff", "accent2": "#d8ff3e",
                    "alert": "#ff3b30"},
        "fonts": {"display": "Geist", "body": "Inter", "caption": "Geist"},
        "captions": {"weight": 900, "case": "none", "box": None, "stroke": "6px #000000", "fg": "#ffffff",
                     "active_fg": "#ffd84d", "active_bg": None},
        "frame": {"camera_shape": "cutout", "border": "0 solid transparent", "screen_radius": 18,
                  "shadow": "0 30px 90px rgba(0,0,0,.55)"},
        "transition": {"kind": "slide", "dur": 0.34, "ease": "power3.out"},
        "chapter_card": "app", "lower_third": "tag",
        "sfx": {"chapter": "swipe", "callout": "pen_write", "lower_third": "pop", "transition": "swipe"},
        "music": {"ids": [187, 82, 293, 597], "mood": "reaction, launch"},
        "long_notes": "Reactions and reviews of a page, post or demo: the subject full-bleed (screen share or "
                      "capture) with the speaker cut out in front at the bottom corner; callouts drawn on the "
                      "subject on their words; each chapter swipes to its source with a credit chip.",
    },
    "revista": {
        "name": "Revista (editorial spreads)", "family": "creator",
        "palette": {"bg": "#17171b", "bg2": "#1f1f25", "text": "#f3efe6", "muted": "#d9d4c7", "accent": "#c6ff3d",
                    "accent2": "#cdbcff"},
        "fonts": {"display": "Bebas Neue", "caption": "Geist", "serif": "Playfair Display"},
        "captions": {"weight": 800, "box": None, "active_fg": "#c6ff3d", "active_bg": None},
        "frame": {"camera_radius": 36, "border": "0 solid transparent"},
        "chapter_card": "editorial",
        "music": {"ids": [187, 282, 31], "mood": "clear, editorial"},
        "long_notes": "Very good for structured classes: each chapter is a spread (condensed keyword + italic serif "
                      "line), icon chips per item, full-frame breathers between chapters.",
    },
}

SLUGS = tuple(sorted(STYLES))


def _merge(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _merge(dst[k], v)
        else:
            dst[k] = copy.deepcopy(v)
    return dst


def get(slug="creative", overrides=None):
    """Resolved pack: BASE <- FAMILY[family] <- STYLES[slug] <- overrides (e.g. a creative-mode palette)."""
    pack = copy.deepcopy(BASE)
    if slug and slug != "creative":
        if slug not in STYLES:
            raise KeyError(f"no style pack {slug!r}; known: creative, {', '.join(SLUGS)}")
        style = STYLES[slug]
        _merge(pack, FAMILY.get(style.get("family", "organic"), {}))
        family_notes = pack.get("long_notes", "")
        _merge(pack, style)
        if family_notes and style.get("long_notes") is None:
            pack["long_notes"] = family_notes
        pack["slug"] = slug
    if overrides:
        _merge(pack, overrides)
    return pack


def css_vars(pack):
    p = pack["palette"]
    f = pack["fonts"]
    c = pack["captions"]
    out = {f"--{k}": v for k, v in p.items()}
    out.update({"--font-display": f"'{f['display']}'", "--font-body": f"'{f['body']}'", "--font-mono": f"'{f['mono']}'",
                "--font-caption": f"'{f['caption']}'", "--font-serif": f"'{f.get('serif', 'Playfair Display')}'",
                "--cap-fg": c["fg"], "--cap-active-fg": c["active_fg"],
                "--cap-active-bg": c["active_bg"] or "transparent", "--cap-box": c["box"] or "transparent"})
    return ":root{" + "".join(f"{k}:{v};" for k, v in out.items()) + "}"


def table():
    """Markdown table of every pack (used to check references/long-form.md)."""
    rows = ["| Style | Family | Captions | Chapter card | Lower third | Transition | Camera grade |",
            "|---|---|---|---|---|---|---|"]
    for slug in SLUGS:
        p = get(slug)
        cap = p["captions"]
        active = f"{cap['active_fg']} on {cap['active_bg']}" if cap["active_bg"] else f"{cap['active_fg']} text"
        rows.append(f"| `{slug}` | {p['family']} | {p['fonts']['caption']}, {active} | {p['chapter_card']} | "
                    f"{p['lower_third']} | {p['transition']['kind']} | {'yes' if p['camera_grade'] else '-'} |")
    return "\n".join(rows)


if __name__ == "__main__":
    print(table())
