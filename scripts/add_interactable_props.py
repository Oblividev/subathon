#!/usr/bin/env python3
"""Append flavour interactable events to RPG Maker MZ maps without modifying existing events.

Tagged with note ``auto-added interactable`` for SubtleInteractHint.js (ellipsis balloon
when the player can press Z nearby).
"""

from __future__ import annotations

import json
import random
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# map_id -> list of (lines, kind)  kind: "sign" | "prop" (visible !Other2)
MAP_PROPS: dict[int, list[tuple[list[str], str]]] = {
    1: [
        (["A wooden bench with someone's name carved in.", "The carving just says \"Liv was here.\" Again."], "sign"),
        (["A community notice board.", "Today's headline: \"Please stop feeding the pig.\""], "sign"),
        (["Wildflowers in a planter.", "They smell nice. Chat agrees they look fake."], "sign"),
        (["A red postbox.", "Nothing outgoing. Typical streamer inbox."], "sign"),
        (["Town fountain. The water's suspiciously clean.", "You resist the urge to toss coins in."], "prop"),
    ],
    2: [
        (["A vending machine hums quietly.", "Every button is out of stock except \"mystery.\""], "prop"),
        (["Graffiti on the wall: \"Pog Cubs 4 lyfe\".", "Artistic. Legally questionable."], "sign"),
        (["A sewer grate.", "You hear something squeak. Probably fine."], "sign"),
        (["A pigeon.", "It stares like you owe it bits."], "prop"),
    ],
    3: [
        (["Digital departure board.", "Next train: \"eventually\"."], "sign"),
        (["Ticket machine.", "It ate someone's card. Not yours. Yet."], "prop"),
        (["Rubbish bin.", "Smells like expired meal deals."], "sign"),
    ],
    4: [
        (["Fridge magnets from places you've never been.", "One says \"World's Okayest House\"."], "sign"),
        (["A wall calendar crossed out after \"Subathon Day 1\".", "Time is a social construct here."], "sign"),
        (["Coat rack with one hoodie.", "It's seen things."], "prop"),
    ],
    5: [
        (["A houseplant on the windowsill.", "Somehow healthier than you on three hours' sleep."], "prop"),
        (["Games console under the TV.", "Controller battery: critically low."], "sign"),
        (["A framed photo of the stream setup.", "Do is photobombing in the corner."], "sign"),
    ],
    6: [
        (["Unmade bed.", "Peak content-creator aesthetic."], "sign"),
        (["Poster: \"World Domination Plan\".", "Step one is illegible."], "sign"),
        (["Bedside lamp.", "Warm light. Zero productivity increase."], "prop"),
    ],
    7: [
        (["Snack shelf.", "Everything is two-for-one except dignity."], "sign"),
        (["Microwave with suspicious stains.", "The instructions just say \"good luck\"."], "prop"),
        (["Slushie machine.", "Brain freeze speedrun any%."], "prop"),
    ],
    8: [
        (["Driftwood on the shore.", "Nature's free decoration DLC."], "sign"),
        (["Tide pool.", "Tiny crabs. Massive vibes."], "sign"),
        (["Binoculars on a stand.", "You can almost see the city. Almost."], "prop"),
    ],
    9: [
        (["Mile marker: \"Floroma — 2 km\".", "Your legs disagree."], "sign"),
        (["Guardrail.", "Sturdy. Like the gate, but horizontal."], "sign"),
        (["Wildflowers by the path.", "Bees are off doing side quests."], "prop"),
    ],
    10: [
        (["Station bench.", "Someone left a half-finished crossword."], "sign"),
        (["Timetable poster.", "All trains marked \"TBC\"."], "sign"),
    ],
    11: [
        (["A mug on the counter.", "Still warm. Cutscene energy."], "sign"),
        (["Window overlooking town.", "The view's nice. The plot's thicker."], "sign"),
    ],
    12: [
        (["Trophy case.", "Most awards say \"Participant\"."], "sign"),
        (["Pool table.", "The chalk's missing. Drama."], "prop"),
        (["Speaker stack.", "Bass loud enough to scare the pig."], "prop"),
    ],
    13: [
        (["Bunk beds.", "Top bunk reserved for chaos."], "sign"),
        (["Closet.", "Just hoodies and one suspicious box."], "sign"),
    ],
    14: [
        (["LED strip around the desk.", "RGB: Really Good Broadcasting."], "prop"),
        (["Stack of games.", "Half are \"for content\"."], "sign"),
    ],
    15: [
        (["Backstage crate.", "Labelled \"DO NOT OPEN ON STREAM\"."], "sign"),
        (["Coiled cable.", "The universal sign of a live show."], "prop"),
        (["Water bottle tower.", "Hydration or hubris."], "prop"),
    ],
    16: [
        (["A flickering torch.", "It refuses to explain itself."], "prop"),
        (["Strange symbol on the floor.", "You pretend you understand it."], "sign"),
        (["Whispering wall.", "…Probably just the BGS track."], "sign"),
    ],
    18: [
        (["Parked car.", "Alarm set to \"dramatic tension\"."], "sign"),
        (["Puddle.", "Reflects the sky. Deep."], "sign"),
        (["Vending machine.", "Only sells energy drinks and regret."], "prop"),
    ],
    19: [
        (["Train seat.", "Window seat claimed by a jacket."], "sign"),
        (["Overhead handrail.", "For standing. And life choices."], "sign"),
        (["Window.", "Scenery scrolls by at mach narrative."], "sign"),
    ],
    20: [
        (["Train seat.", "Someone carved \"AFK\" into the table."], "sign"),
        (["Emergency intercom.", "Do not press. (You want to press.)"], "sign"),
        (["Luggage rack.", "One bag. Enormous aura."], "prop"),
    ],
}

DEFAULT_PROPS = [
    (["Something ordinary catches your eye.", "Nothing game-changing. Just flavour."], "sign"),
    (["A small decoration.", "Shane added another thing to poke. Classic."], "prop"),
]

STANDARD_CONDITIONS = {
    "actorId": 1,
    "actorValid": False,
    "itemId": 1,
    "itemValid": False,
    "selfSwitchCh": "A",
    "selfSwitchValid": False,
    "switch1Id": 1,
    "switch1Valid": False,
    "switch2Id": 1,
    "switch2Valid": False,
    "variableId": 1,
    "variableValid": False,
    "variableValue": 0,
}

PROP_IMAGE_VARIANTS = [
    {"tileId": 0, "characterName": "!Other2", "direction": 2, "pattern": 0, "characterIndex": 0},
    {"tileId": 0, "characterName": "!Other2", "direction": 4, "pattern": 1, "characterIndex": 1},
    {"tileId": 0, "characterName": "!Other2", "direction": 6, "pattern": 2, "characterIndex": 2},
    {"tileId": 0, "characterName": "!Other2", "direction": 8, "pattern": 0, "characterIndex": 3},
]


def tile_index(w: int, h: int, x: int, y: int, z: int) -> int:
    return z * w * h + y * w + x


def build_command_list(lines: list[str]) -> list[dict]:
    cmds: list[dict] = []
    window_style = 2  # bottom window for multi-line flavour
    for line in lines:
        cmds.append({"code": 101, "indent": 0, "parameters": ["", 0, 1, window_style, ""]})
        cmds.append({"code": 401, "indent": 0, "parameters": [line]})
    cmds.append({"code": 0, "indent": 0, "parameters": []})
    return cmds


def make_page(lines: list[str], kind: str, variant_idx: int) -> dict:
    if kind == "prop":
        image = deepcopy(PROP_IMAGE_VARIANTS[variant_idx % len(PROP_IMAGE_VARIANTS)])
        direction_fix = True
        step_anime = True
        priority = 1
    else:
        image = {
            "characterIndex": 0,
            "characterName": "",
            "direction": 2,
            "pattern": 0,
            "tileId": 0,
        }
        direction_fix = False
        step_anime = False
        priority = 1

    return {
        "conditions": deepcopy(STANDARD_CONDITIONS),
        "directionFix": direction_fix,
        "image": image,
        "list": build_command_list(lines),
        "moveFrequency": 3,
        "moveRoute": {"list": [{"code": 0, "parameters": []}], "repeat": True, "skippable": False, "wait": False},
        "moveSpeed": 3,
        "moveType": 0,
        "priorityType": priority,
        "stepAnime": step_anime,
        "through": False,
        "trigger": 0,
        "walkAnime": True,
    }


def make_event(event_id: int, x: int, y: int, lines: list[str], kind: str, variant_idx: int) -> dict:
    return {
        "id": event_id,
        "name": f"Interact ({event_id})",
        "note": "auto-added interactable",
        "pages": [make_page(lines, kind, variant_idx)],
        "x": x,
        "y": y,
    }


def is_occupied(events: list, x: int, y: int) -> bool:
    for e in events:
        if e and e["x"] == x and e["y"] == y:
            return True
    return False


def manhattan_min_dist(events: list, x: int, y: int) -> int:
    best = 999
    for e in events:
        if not e:
            continue
        d = abs(e["x"] - x) + abs(e["y"] - y)
        best = min(best, d)
    return best


def has_decoration(data: list, w: int, h: int, x: int, y: int) -> bool:
    for z in (1, 2, 3):
        tid = data[tile_index(w, h, x, y, z)]
        if tid > 0:
            return True
    return False


def is_walkable_ground(data: list, w: int, h: int, x: int, y: int) -> bool:
    ground = data[tile_index(w, h, x, y, 0)]
    return ground > 0


def candidate_positions(m: dict, events: list) -> list[tuple[int, int, int]]:
    """Return (x, y, score) sorted best-first."""
    w, h = m["width"], m["height"]
    data = m["data"]
    out: list[tuple[int, int, int]] = []
    for y in range(h):
        for x in range(w):
            if is_occupied(events, x, y):
                continue
            if not is_walkable_ground(data, w, h, x, y):
                continue
            dist = manhattan_min_dist(events, x, y)
            if dist < 2:
                continue
            score = 0
            if has_decoration(data, w, h, x, y):
                score += 10
            # prefer interior, not map edge
            margin = 2
            if margin <= x < w - margin and margin <= y < h - margin:
                score += 3
            score += min(dist, 6)
            out.append((x, y, score))
    out.sort(key=lambda t: (-t[2], t[1], t[0]))
    return out


def next_event_id(events: list) -> int:
    max_id = 0
    for e in events:
        if e:
            max_id = max(max_id, e["id"])
    return max_id + 1


def ensure_array_size(events: list, event_id: int) -> None:
    while len(events) <= event_id:
        events.append(None)


def apply_map(map_id: int, rng: random.Random) -> int:
    path = DATA / f"Map{map_id:03d}.json"
    if not path.exists():
        return 0

    with path.open(encoding="utf-8") as f:
        m = json.load(f)

    if map_id == 17:
        return 0  # intro-only strip map

    props = MAP_PROPS.get(map_id, DEFAULT_PROPS)
    events = m.setdefault("events", [])
    candidates = candidate_positions(m, events)
    if not candidates:
        return 0

    added = 0
    used_cells: set[tuple[int, int]] = set()
    for i, (lines, kind) in enumerate(props):
        placed = False
        # shuffle top candidates slightly for variety between runs while deterministic per map
        pool = candidates[:80]
        rng.shuffle(pool)
        for x, y, _score in pool:
            if (x, y) in used_cells:
                continue
            if manhattan_min_dist(events, x, y) < 2:
                continue
            for ux, uy in used_cells:
                if abs(ux - x) + abs(uy - y) < 2:
                    break
            else:
                eid = next_event_id(events)
                ensure_array_size(events, eid)
                events[eid] = make_event(eid, x, y, lines, kind, i)
                used_cells.add((x, y))
                added += 1
                placed = True
                break
        if not placed:
            break

    if added:
        with path.open("w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

    return added


def main() -> None:
    total = 0
    for map_id in range(1, 21):
        rng = random.Random(map_id * 7919)
        n = apply_map(map_id, rng)
        if n:
            print(f"Map{map_id:03d}: added {n} interactables")
            total += n
    print(f"Done. {total} new events across maps.")


if __name__ == "__main__":
    main()
