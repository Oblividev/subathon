#!/usr/bin/env python3
"""
Contextual balloon icons for map dialogue (RPG Maker MZ command 213).

Standard Balloon.png icons (IDs 1–10):
  1 Exclamation   2 Question     3 Music note   4 Heart
  5 Sweat         6 Frustration  7 Silence      8 Light bulb
  9 Sleep (Zzz)  10 (custom — used in wake gag on Map011)

Removes blanket "!" (id 1) on every speaker change, then adds varied balloons
only where dialogue tone warrants it (with spacing so scenes do not spam).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

LIV_FACE = "LivFaceV2"
PLAYER_NAMES = {"liv", "obliviosa"}

# (regex, balloon_id, score_weight) — highest total score wins; need min score >= MIN_SCORE
EMOTION_RULES: list[tuple[str, int, int]] = [
    (r"love you|thank you so|congrats|proud of|you'?re so sweet|hits the spot", 4, 4),
    (r"goodnight|thank you for everything|hardest worker|best at reminding", 4, 4),
    (r"aww+|very funny|match made in heaven|finger.?lickin|five years|here'?s to five", 4, 3),
    (r"hey,|ohayo|ay up|hi, liv|hi, puppy|bob!|bobby", 4, 2),
    (r"don'?t you\?|aren'?t you|right\?|guess so|you know", 2, 3),
    (r"\?\s*$|what on earth|are you fucking|how are you|who should|what sort", 2, 3),
    (r"what brings you|and what would|fancy a ticket|which way", 2, 2),
    (r"wait,|wait no|wait\.|never mind|oh wait|oh dear|confus|hang on", 2, 3),
    (r"won't even|give me dots|trek all|dots\?", 5, 3),
    (r"hmph|grief me|shocking|did me dirty|league games|sharp words", 5, 4),
    (r"you hate me|flame my|take that\?|hater of|sureee|rethink that", 5, 3),
    (r"sorry|sad about|goodbye|g o o d b y|dying on me|feel this sad", 7, 4),
    (r"usb drive died|not paid|overslept|what time is it|oh dear", 7, 3),
    (r"beep boop|sing a cappella|dj angle|big ras|beats lately|cooking up|spinnah", 3, 3),
    (r"fourth wall|prove it to you|locked in|livestream as we know|bot that can", 8, 3),
    (r"overslept|still isn'?t awake|waking up|lazy backside|hoo boy|tick tock", 9, 3),
    (r"ha! i fooled|omg,|ahh+.*kidding|task failed|obsolete|i am b|evil", 6, 4),
    (r"never mind|ribbit|lil ol me", 10, 2),
    (r"wow\.|danngggg|yikes|dang,|no hidden boss|hits the spot", 1, 2),
    (r"omg|ahh+|ha! i", 1, 3),
    (r"kitchen\?|wardrobe|diary|coffee|empty cup|drinking problem", 2, 2),
    (r"map on the wall|searchin|somethin|colonel|kfc", 8, 2),
    (r"peaceful up here|relaxed|wind in the trees", 4, 2),
    (r"gate blocks|social battery|talk to everyone", 2, 2),
]

MIN_SCORE = 2
MIN_TURNS_BETWEEN = 1
MIN_CMDS_BETWEEN = 5
BALLOON_SPEECH = 1


def clean_dialogue(text: str) -> str:
    if not isinstance(text, str):
        return ""
    t = re.sub(r"\\[\.\|\^!><\{\}]", " ", text)
    t = re.sub(r"\\[A-Za-z]+", " ", t)
    return re.sub(r"\s+", " ", t).strip().lower()


def speaker_key(params: list) -> str | None:
    if not params or len(params) < 5:
        return None
    face = params[0] if isinstance(params[0], str) else ""
    name = params[4] if isinstance(params[4], str) else ""
    if not face:
        return None
    if face == LIV_FACE or name.strip().lower() in PLAYER_NAMES:
        return "player"
    return f"npc:{face.lower()}"


def balloon_target(key: str) -> int:
    return -1 if key == "player" else 0


def page_has_character_sprite(page: dict) -> bool:
    image = page.get("image") or {}
    return bool(image.get("characterName"))


def is_character_101(params: list) -> bool:
    return speaker_key(params) is not None


def pick_balloon(texts: list[str]) -> int | None:
    combined = clean_dialogue(" ".join(texts))
    if not combined:
        return None
    scores: dict[int, int] = {}
    for pattern, balloon_id, weight in EMOTION_RULES:
        if re.search(pattern, combined, re.IGNORECASE):
            scores[balloon_id] = scores.get(balloon_id, 0) + weight
    if not scores:
        return None
    best_id, best_score = max(scores.items(), key=lambda x: (x[1], -x[0]))
    if best_score < MIN_SCORE:
        return None
    # Avoid generic "!" unless clearly emphatic
    if best_id == BALLOON_SPEECH and best_score < 4:
        return None
    return best_id


def make_balloon_cmd(indent: int, target: int, balloon_id: int) -> dict:
    return {
        "code": 213,
        "indent": indent,
        "parameters": [target, balloon_id, False],
    }


def strip_speech_balloons_before_dialogue(cmd_list: list) -> tuple[list, int]:
    """Remove auto-inserted ! balloons immediately before character Show Text."""
    out: list = []
    removed = 0
    i = 0
    while i < len(cmd_list):
        cmd = cmd_list[i]
        if (
            cmd.get("code") == 213
            and (cmd.get("parameters") or [0, 0])[1] == BALLOON_SPEECH
            and i + 1 < len(cmd_list)
            and cmd_list[i + 1].get("code") == 101
            and is_character_101(cmd_list[i + 1].get("parameters") or [])
        ):
            removed += 1
            i += 1
            continue
        out.append(cmd)
        i += 1
    return out, removed


def iter_dialogue_turns(cmd_list: list):
    """Yield (index of 101, indent, speaker_key, line texts)."""
    i = 0
    while i < len(cmd_list):
        cmd = cmd_list[i]
        if cmd.get("code") != 101:
            i += 1
            continue
        params = cmd.get("parameters") or []
        key = speaker_key(params)
        if not key:
            i += 1
            continue
        indent = cmd.get("indent", 0)
        texts: list[str] = []
        j = i + 1
        while j < len(cmd_list):
            nxt = cmd_list[j]
            if nxt.get("code") == 401 and nxt.get("indent", 0) == indent:
                p = nxt.get("parameters") or []
                if p:
                    texts.append(p[0])
                j += 1
            else:
                break
        yield i, indent, key, texts
        i = j


def has_balloon_near(cmd_list: list, index: int, lookback: int = 3) -> bool:
    for j in range(max(0, index - lookback), index):
        if cmd_list[j].get("code") == 213:
            return True
    return False


def apply_contextual_balloons(
    cmd_list: list, event_has_sprite: bool
) -> tuple[list, int]:
    if not cmd_list:
        return cmd_list, 0

    insertions: list[tuple[int, int, int, int]] = []
    turns_since_balloon = MIN_TURNS_BETWEEN
    last_balloon_cmd_index = -100

    for cmd_index, indent, key, texts in iter_dialogue_turns(cmd_list):
        turns_since_balloon += 1
        balloon_id = pick_balloon(texts)
        if balloon_id is None:
            continue
        if key != "player" and not event_has_sprite:
            continue
        if turns_since_balloon < MIN_TURNS_BETWEEN:
            continue
        if cmd_index - last_balloon_cmd_index < MIN_CMDS_BETWEEN:
            continue
        if has_balloon_near(cmd_list, cmd_index):
            continue
        target = balloon_target(key)
        insertions.append((cmd_index, indent, target, balloon_id))
        turns_since_balloon = 0
        last_balloon_cmd_index = cmd_index

    if not insertions:
        return cmd_list, 0

    out = list(cmd_list)
    for cmd_index, indent, target, balloon_id in reversed(insertions):
        out.insert(cmd_index, make_balloon_cmd(indent, target, balloon_id))

    return out, len(insertions)


def patch_command_list(cmd_list: list, event_has_sprite: bool) -> tuple[list, int, int]:
    cleaned, stripped = strip_speech_balloons_before_dialogue(cmd_list)
    patched, added = apply_contextual_balloons(cleaned, event_has_sprite)
    return patched, stripped, added


def patch_map_file(path: Path) -> tuple[int, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    stripped = 0
    added = 0
    events = data.get("events")
    if not isinstance(events, list):
        return 0, 0

    for ev in events:
        if not ev:
            continue
        if (ev.get("name") or "").lower() == "baloon":
            continue
        for page in ev.get("pages") or []:
            lst = page.get("list")
            if not isinstance(lst, list):
                continue
            has_sprite = page_has_character_sprite(page)
            new_lst, s, a = patch_command_list(lst, has_sprite)
            if s or a:
                page["list"] = new_lst
                stripped += s
                added += a

    if stripped or added:
        path.write_text(
            json.dumps(data, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
    return stripped, added


def main() -> None:
    total_strip = 0
    total_add = 0
    files = 0
    for path in sorted(DATA.glob("Map*.json")):
        if path.name == "MapInfos.json":
            continue
        s, a = patch_map_file(path)
        if s or a:
            files += 1
            print(f"{path.name}: removed {s} ! bubbles, added {a} contextual")
            total_strip += s
            total_add += a
    print(
        f"Done. Removed {total_strip} speech bubbles, "
        f"added {total_add} contextual across {files} maps."
    )


if __name__ == "__main__":
    main()
