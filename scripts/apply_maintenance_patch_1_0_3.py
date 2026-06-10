#!/usr/bin/env python3
"""Post-subathon maintenance patch (v1.0.3): past-tense event copy and title bump."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PLUGINS = ROOT / "js" / "plugins.js"

REPLACEMENTS = [
    ("Welcome to the Obliviosa Subathon game!", "Welcome to the Obliviosa game!"),
    (
        "This little game and this subathon might be coming to a",
        "The subathon is over, and this little game was part of",
    ),
    (
        "close, but the impact you've had is unparalleled.",
        "it—but the impact you've had is unparalleled.",
    ),
    (
        "Throughout this anniversary event, every sub, every",
        "Throughout the anniversary subathon, every sub, every",
    ),
    (
        "donation, and every single bit has increased the timer all",
        "donation, and every single bit kept the timer going—all",
    ),
    (
        "Oh this was during the halloween subathon",
        "Oh, this was from the Halloween subathon.",
    ),
    (
        "last subathon, unlike Shane",
        "the subathon, unlike Shane",
    ),
    (
        "Very funny, Liv. I can't believe you came 16",
        "Very funny, Liv. I can't believe you took about",
    ),
    ("hours late.", "an hour to beat my game."),
]


def patch_maps() -> int:
    changed = 0
    for path in sorted(DATA.glob("Map*.json")):
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
            print(f"updated {path.name}")
    return changed


def patch_plugins() -> None:
    text = PLUGINS.read_text(encoding="utf-8")
    text = text.replace('Subtitle:str\\\\\\":\\\\\\"Subathon\\\\\\"', 'Subtitle:str\\\\\\":\\\\\\"Thanks for playing\\\\\\"')
    text = text.replace('Version:str\\\\\\":\\\\\\"v1.0.2\\\\\\"', 'Version:str\\\\\\":\\\\\\"v1.0.3\\\\\\"')
    PLUGINS.write_text(text, encoding="utf-8")
    print("updated js/plugins.js (title v1.0.3)")


def main() -> None:
    n = patch_maps()
    patch_plugins()
    print(f"done — {n} map file(s) changed")


if __name__ == "__main__":
    main()
