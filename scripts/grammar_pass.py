#!/usr/bin/env python3
"""British English grammar and spelling pass for RPG Maker MZ dialogue text."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SKIP_ASSET = re.compile(r"\.(woff|woff2|ttf|png|jpg|rpgmvp|rpgmvm|rpgmvo|ogg|m4a)$", re.I)
CREDITS_USER = re.compile(r"^\s*-\s+\S")
TEXT_KEYS = frozenset({
    "name", "description", "nickname", "profile",
    "message1", "message2", "message3", "message4",
})
SKIP_KEYS = frozenset({
    "note", "battleback1Name", "battleback2Name", "battlerName",
    "mainFontFilename", "numberFontFilename", "fallbackFonts",
})

# Longest first
EXACT = [
    ("Hello Liv, i hear its your 5th aniversary!", "Hello Liv, I hear it's your 5th anniversary!"),
    ("and charasmatic you are.", "and charismatic you are."),
    ("Hey Liv, just saying, You dont wanna go up", "Hey Liv, just saying, you don't wanna go up"),
    ("Uhmmm. Thats a bit sus", "Uhmmm. That's a bit sus"),
    ("Yeah listen its fine.", "Yeah listen, it's fine."),
    ("Just dont go up there", "Just don't go up there"),
    ("Its your Nintendo Switch!", "It's your Nintendo Switch!"),
    ("Its the town well. The water's suspiciously clean at", "It's the town well. The water's suspiciously clean at"),
    ("Very funny, Liv. i cant believe you came 16", "Very funny, Liv. I can't believe you came 16"),
    ("As herself. the main character", "As herself, the main character"),
    ("Cast And Community:", "Cast and community:"),
    ("looks (sorry i tried my best).", "looks (sorry, I tried my best)."),
    ("im not very active in your streams at the time", "I'm not very active in your streams at the time"),
    ("im very glad that i stumbled upon your stream", "I'm very glad that I stumbled upon your stream"),
    ("its always very chill hanging out with you.", "it's always very chill hanging out with you."),
    ("You know, its a learning curve. but its alright", "You know, it's a learning curve. But it's alright"),
    ("Funny, just because im not in the game.", "Funny, just because I'm not in the game."),
    ("At least you didnt abandon me and fall asleep", "At least you didn't abandon me and fall asleep"),
    ("Anyway, thats quite enough of that.", "Anyway, that's quite enough of that."),
    ("I dont know why you're talking to yourself.", "I don't know why you're talking to yourself."),
    ("Im going to bed now, good night gamers", "I'm going to bed now, good night gamers"),
    ("Im gonna go take a nap with cam to calm down", "I'm gonna go take a nap with Cam to calm down"),
    ("Im not even meant to be talking to you.", "I'm not even meant to be talking to you."),
    ("Im surprised you managed to get out of bed", "I'm surprised you managed to get out of bed"),
    ("Woo guys look at me, Im on the stage", "Woo, guys, look at me, I'm on the stage"),
    ("could blame him. But i dont know where they", "could blame him. But I don't know where they"),
    ("  - if you see this then hi im not actually a real username",
     "  - if you see this then hi I'm not actually a real username"),
    ("acomplished", "accomplished"),
    ("elipsis", "ellipsis"),
    ("Thank you so much. that means", "Thank you so much. That means"),
    ("there. trust me", "there. Trust me"),
    ("Oh my. that was beautiful", "Oh my. That was beautiful"),
]

CONTRACTION_RULES = [
    (r"\bdont\b", "don't"),
    (r"\bdidnt\b", "didn't"),
    (r"\bwont\b", "won't"),
    (r"\bwouldnt\b", "wouldn't"),
    (r"\bhavent\b", "haven't"),
    (r"\bshouldnt\b", "shouldn't"),
    (r"\bcant\b", "can't"),
    (r"\bCant\b", "Can't"),
    (r"\bDont\b", "Don't"),
    (r"\bThats\b", "That's"),
    (r"\bthats\b", "that's"),
    (r"\bIm\b", "I'm"),
    (r"\bLets\b", "Let's"),
    (r"\byoure\b", "you're"),
    (r"\bYoure\b", "You're"),
    (r"\btheyre\b", "they're"),
    (r"\bTheyre\b", "They're"),
    (r"\bweve\b", "we've"),
    (r"\bWeve\b", "We've"),
    (r"\bIve\b", "I've"),
    (r"\bive\b", "I've"),
    (r"\bwanna\b", "wanna"),  # keep informal
]

ITS_CONTRACTION = [
    (r"\bIts\b", "It's"),
    (r"\bits your\b", "it's your"),
    (r"\bits a\b", "it's a"),
    (r"\bits the\b", "it's the"),
    (r"\bits fine\b", "it's fine"),
    (r"\bits alright\b", "it's alright"),
    (r"\bits always\b", "it's always"),
    (r"\bits okay\b", "it's okay"),
    (r"\bits not\b", "it's not"),
    (r"\bits been\b", "it's been"),
    (r"\bits just\b", "it's just"),
]

BRITISH = [
    (r"\brealize\b", "realise"),
    (r"\bRealize\b", "Realise"),
    (r"\brealized\b", "realised"),
    (r"\bRealized\b", "Realised"),
    (r"\bcolor\b", "colour"),
    (r"\bColor\b", "Colour"),
]

TYPO = [
    (r"\baniversary\b", "anniversary"),
    (r"\bcharasmatic\b", "charismatic"),
    (r"\bdefinately\b", "Definitely"),
    (r"\bwierdo\b", "weirdo"),
    (r"\bfurnature\b", "furniture"),
    (r"\bintresting\b", "interesting"),
]


def should_transform(s: str, key, in_event_text: bool, in_terms: bool) -> bool:
    if not s or SKIP_ASSET.search(s):
        return False
    if CREDITS_USER.match(s) and " - " in s[:10]:
        return True  # still fix grammar in credit lines with sentences
    if key in SKIP_KEYS:
        return False
    if key and key.endswith("Name") and key not in ("displayName", "gameTitle"):
        if " " not in s and not re.search(r"[—–'\"]", s):
            return False
    if in_event_text or in_terms or key in TEXT_KEYS or key in ("gameTitle",):
        return bool(re.search(r"[A-Za-z]", s))
    if key in ("switches", "variables"):
        return bool(s.strip())
    return False


def fix_pronoun_i(text: str) -> str:
    text = re.sub(r"\bi'm\b", "I'm", text, flags=re.I)
    text = re.sub(r"\bi've\b", "I've", text, flags=re.I)
    text = re.sub(r"\bi'll\b", "I'll", text, flags=re.I)
    text = re.sub(r"\bi'd\b", "I'd", text, flags=re.I)
    return re.sub(r"(?<![A-Za-z])i(?![A-Za-z'])", "I", text)


def transform(text: str) -> str:
    if CREDITS_USER.match(text) and not re.search(
        r"\b(i|im|its|dont|didnt|aniversary|charasmatic)\b", text, re.I
    ):
        return text
    for old, new in EXACT:
        if old in text:
            text = text.replace(old, new)
    for pat, rep in TYPO + BRITISH + ITS_CONTRACTION + CONTRACTION_RULES:
        text = re.sub(pat, rep, text)
    text = fix_pronoun_i(text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\s+([,.!?])", r"\1", text)
    return text


def walk_strings(obj, key=None, in_event=False, in_terms=False):
    if isinstance(obj, dict):
        if obj.get("code") in (101, 401, 405) and "parameters" in obj:
            in_event = True
        in_terms = in_terms or key == "terms"
        for k, v in obj.items():
            yield from walk_strings(v, k, in_event, in_terms)
    elif isinstance(obj, list):
        if key in ("switches", "variables"):
            for i, item in enumerate(obj):
                if isinstance(item, str) and item.strip():
                    yield ("switch", item)
        for item in obj:
            yield from walk_strings(item, key, in_event, in_terms)
    elif isinstance(obj, str):
        if should_transform(obj, key, in_event, in_terms):
            yield (key, obj)


def apply_to_obj(obj, key=None, in_event=False, in_terms=False):
    changed = 0
    if isinstance(obj, dict):
        if obj.get("code") in (101, 401, 405) and "parameters" in obj:
            in_event = True
            params = obj["parameters"]
            if isinstance(params, list):
                for i, item in enumerate(params):
                    if isinstance(item, str) and should_transform(item, str(i), True, in_terms):
                        new = transform(item)
                        if new != item:
                            params[i] = new
                            changed += 1
                    elif isinstance(item, list):
                        for j, c in enumerate(item):
                            if isinstance(c, str) and should_transform(c, str(j), True, in_terms):
                                new = transform(c)
                                if new != c:
                                    item[j] = new
                                    changed += 1
        in_terms = in_terms or key == "terms"
        for k, v in obj.items():
            changed += apply_to_obj(v, k, in_event, in_terms)
    elif isinstance(obj, list):
        if key in ("switches", "variables"):
            for i, item in enumerate(obj):
                if isinstance(item, str) and item.strip():
                    new = transform(item)
                    if new != item:
                        obj[i] = new
                        changed += 1
        for item in obj:
            changed += apply_to_obj(item, key, in_event, in_terms)
    elif isinstance(obj, str):
        if should_transform(obj, key, in_event, in_terms):
            new = transform(obj)
            if new != obj:
                return 1
    return changed


def main():
    total = 0
    for path in sorted(DATA.glob("*.json")):
        if path.name in ("Animations.json", "Tilesets.json"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        n = apply_to_obj(data)
        if n:
            path.write_text(
                json.dumps(data, ensure_ascii=False, separators=(",", ":")),
                encoding="utf-8",
            )
            print(f"{path.name}: {n} fixes")
            total += n
    print(f"Total: {total} string updates")


if __name__ == "__main__":
    main()
