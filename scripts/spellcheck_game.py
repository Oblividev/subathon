#!/usr/bin/env python3
"""Extract RPG Maker MZ game text and spell-check it."""
import json
import re
import sys
from pathlib import Path

from spellchecker import SpellChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# Event command codes that carry player-facing text
EVENT_TEXT_CODES = {
    101: lambda p: [p[4]] if len(p) > 4 and isinstance(p[4], str) and p[4] else [],
    401: lambda p: [p[0]] if p and isinstance(p[0], str) else [],
    102: lambda p: [x for x in p if isinstance(x, str)],
    405: lambda p: [x for x in p if isinstance(x, str)],
}

DB_STRING_KEYS = {
    "name",
    "description",
    "nickname",
    "profile",
    "message1",
    "message2",
    "message3",
    "message4",
}

# Names, places, slang, engine terms — not spelling errors
CUSTOM_WORDS = {
    "liv",
    "olivia",
    "cammy",
    "cam",
    "kotaro",
    "junes",
    "nova",
    "nunya",
    "pog",
    "ohayo",
    "yeehaw",
    "cowgirl",
    "adc",
    "lol",
    "poggers",
    "pogchamp",
    "kernel",
    "saunders",
    "sanders",
    "kfc",
    "lickin",
    "finger",
    "bobby",
    "bob",
    "cape",
    "mansions",
    "mansion",
    "rpg",
    "rmmz",
    "autosave",
    "bgm",
    "bgs",
    "tp",
    "exp",
    "hp",
    "mp",
    "lv",
    "npc",
    "npcs",
    "debug",
    "metadata",
    "visumz",
    "wasd",
    "unova",  # if used
    "intro",
    "tutcomplete",
    "peeps",
    "cubs",
    "residence",
    "residences",
}

RMMZ_CODE_RE = re.compile(r"\\[\\{}<>\$\.|!^><]|\\[A-Za-z]+\[?\d*\]?|\\G", re.IGNORECASE)
NON_WORD_RE = re.compile(r"[^a-zA-Z']+")


def strip_rmmz_codes(text: str) -> str:
    t = RMMZ_CODE_RE.sub(" ", text)
    return t.strip()


def iter_event_commands(obj, source: str, texts: list):
    if isinstance(obj, dict):
        if "code" in obj and "parameters" in obj:
            code = obj["code"]
            params = obj.get("parameters") or []
            if code in EVENT_TEXT_CODES:
                for s in EVENT_TEXT_CODES[code](params):
                    if s and s.strip():
                        texts.append((source, s))
        for k, v in obj.items():
            iter_event_commands(v, source, texts)
    elif isinstance(obj, list):
        for item in obj:
            iter_event_commands(item, source, texts)


def iter_db_strings(obj, source: str, texts: list, in_note=False):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "note":
                continue  # plugin markup, not dialogue
            if k in DB_STRING_KEYS and isinstance(v, str) and v.strip():
                texts.append((source, v))
            else:
                iter_db_strings(v, source, texts)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if item is None:
                continue
            iter_db_strings(item, source, texts)


def extract_system_terms(system: dict, texts: list):
    if system.get("gameTitle"):
        texts.append(("System.json:gameTitle", system["gameTitle"]))
    for i, s in enumerate(system.get("switches") or []):
        if s:
            texts.append((f"System.json:switches[{i}]", s))
    for i, s in enumerate(system.get("variables") or []):
        if s:
            texts.append((f"System.json:variables[{i}]", s))
    terms = system.get("terms") or {}
    for section, values in terms.items():
        if isinstance(values, list):
            for i, v in enumerate(values):
                if isinstance(v, str) and v:
                    texts.append((f"System.json:terms.{section}[{i}]", v))
        elif isinstance(values, dict):
            for k, v in values.items():
                if isinstance(v, str) and v:
                    texts.append((f"System.json:terms.{section}.{k}", v))


def tokenize_for_spellcheck(text: str) -> list[str]:
    cleaned = strip_rmmz_codes(text)
    tokens = []
    for part in NON_WORD_RE.split(cleaned):
        part = part.strip("'")
        if len(part) < 2:
            continue
        if part.isupper() and len(part) > 1:
            continue  # acronyms like ADC, CONGRATS
        tokens.append(part)
    return tokens


def main():
    spell = SpellChecker()
    spell.word_frequency.load_words(CUSTOM_WORDS)

    texts: list[tuple[str, str]] = []

    # Database JSON (excluding maps)
    db_files = [
        "Actors.json",
        "Classes.json",
        "Skills.json",
        "Items.json",
        "Weapons.json",
        "Armors.json",
        "Enemies.json",
        "States.json",
        "Troops.json",
        "CommonEvents.json",
        "Animations.json",
    ]
    for fname in db_files:
        path = DATA / fname
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            iter_db_strings(data, fname, texts)

    system_path = DATA / "System.json"
    if system_path.exists():
        system = json.loads(system_path.read_text(encoding="utf-8"))
        extract_system_terms(system, texts)

    map_infos = DATA / "MapInfos.json"
    if map_infos.exists():
        infos = json.loads(map_infos.read_text(encoding="utf-8"))
        for i, m in enumerate(infos):
            if m and isinstance(m, dict):
                if m.get("name"):
                    texts.append((f"MapInfos.json[{i}].name", m["name"]))

    for path in sorted(DATA.glob("Map*.json")):
        if path.name == "MapInfos.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        iter_event_commands(data, path.name, texts)

    # Dedupe while keeping all sources
    seen_text = {}
    for source, text in texts:
        seen_text.setdefault(text, []).append(source)

    issues = []
    for text, sources in sorted(seen_text.items(), key=lambda x: x[0].lower()):
        # Credits donor list: usernames, not prose
        if re.match(r"^\s*-\s+\S", text) and " " not in text.strip().split(maxsplit=1)[-1][:20]:
            if not re.search(r"\b(the|and|you|your|dont|its)\b", text, re.I):
                continue
        bad_words = set()
        for token in tokenize_for_spellcheck(text):
            word = token.lower()
            if word in CUSTOM_WORDS:
                continue
            if word.isdigit():
                continue
            if not spell.known([word]):
                # try without trailing possessive
                base = word.rstrip("'s").rstrip("s") if word.endswith("'s") else word
                if base != word and spell.known([base]):
                    continue
                bad_words.add(token)
        if bad_words:
            issues.append((text, bad_words, sources))

    print(f"Scanned {len(seen_text)} unique text strings from RPG Maker data.\n")
    if not issues:
        print("No probable misspellings found (custom dictionary applied).")
        return 0

    print(f"Found {len(issues)} strings with possible misspellings:\n")
    for text, bad, sources in issues:
        loc = sources[0] if len(sources) == 1 else f"{sources[0]} (+{len(sources)-1} more)"
        print(f"  [{loc}]")
        print(f"    Text: {text!r}")
        print(f"    Flagged: {', '.join(sorted(bad, key=str.lower))}")
        if len(sources) > 1:
            print(f"    Also in: {', '.join(sources[1:5])}")
        print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
