#!/usr/bin/env python3
"""Add social photo interactable events to RPG Maker MZ map JSON files."""

import json
import copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

STANDARD_CONDITIONS = {
    "actorId": 1,
    "actorValid": False,
    "itemId": 0,
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

STANDARD_PAGE_TAIL = {
    "moveFrequency": 3,
    "moveRoute": {"list": [{"code": 0, "parameters": []}], "repeat": True, "skippable": False, "wait": False},
    "moveSpeed": 3,
    "moveType": 0,
    "priorityType": 1,
    "stepAnime": False,
    "through": False,
    "trigger": 0,
    "walkAnime": True,
}


def make_photo_event(
    event_id: int,
    name: str,
    x: int,
    y: int,
    picture: str,
    intro: str,
    look_prompt: str,
    liv_line: str,
    *,
    zoom: int = 45,
    origin: int = 1,
    pos_x: int = 408,
    pos_y: int = 312,
):
    show_picture = [1, picture, origin, 0, pos_x, pos_y, zoom, zoom, 255, 0]
    return {
        "id": event_id,
        "name": name,
        "note": "social photo from Twitch/Instagram",
        "pages": [
            {
                "conditions": copy.deepcopy(STANDARD_CONDITIONS),
                "directionFix": False,
                "image": {
                    "characterIndex": 0,
                    "characterName": "",
                    "direction": 2,
                    "pattern": 0,
                    "tileId": 0,
                },
                "list": [
                    {"code": 101, "indent": 0, "parameters": ["", 0, 1, 2, ""]},
                    {"code": 401, "indent": 0, "parameters": [intro]},
                    {"code": 101, "indent": 0, "parameters": ["", 0, 1, 2, ""]},
                    {"code": 401, "indent": 0, "parameters": [look_prompt]},
                    {"code": 102, "indent": 0, "parameters": [["Yes", "No"], 1, 0, 2, 0]},
                    {"code": 402, "indent": 0, "parameters": [0, "Yes"]},
                    {"code": 231, "indent": 1, "parameters": show_picture},
                    {"code": 101, "indent": 1, "parameters": ["LivFaceV2", 0, 0, 2, "Liv"]},
                    {"code": 401, "indent": 1, "parameters": [liv_line]},
                    {"code": 230, "indent": 1, "parameters": [250]},
                    {"code": 235, "indent": 1, "parameters": [1]},
                    {"code": 0, "indent": 1, "parameters": []},
                    {"code": 402, "indent": 0, "parameters": [1, "No"]},
                    {"code": 0, "indent": 1, "parameters": []},
                    {"code": 404, "indent": 0, "parameters": []},
                    {"code": 0, "indent": 0, "parameters": []},
                ],
                **copy.deepcopy(STANDARD_PAGE_TAIL),
            }
        ],
        "x": x,
        "y": y,
    }


# map_id -> list of photo specs (without event id)
MAP_PHOTOS = {
    5: [  # Liv's House
        {
            "name": "Photo Twitch Profile",
            "x": 3,
            "y": 4,
            "picture": "LivTwitchProfile",
            "intro": "A framed photo from Twitch — your official profile pic.",
            "look_prompt": "Look closer?",
            "liv_line": "That's me on twitch.tv/obliviosaofficial. Hi chat!",
            "zoom": 50,
            "origin": 0,
            "pos_x": 168,
            "pos_y": -16,
        },
        {
            "name": "Photo Twitch Clip 1",
            "x": 12,
            "y": 4,
            "picture": "LivClip01",
            "intro": "A poster for a legendary Twitch clip.",
            "look_prompt": "Watch the moment?",
            "liv_line": "AND ANOTHER ONE! Still one of my favorites.",
        },
        {
            "name": "Photo Twitch Clip 2",
            "x": 13,
            "y": 8,
            "picture": "LivClip02",
            "intro": "Another clip thumbnail on the wall.",
            "look_prompt": "Take a peek?",
            "liv_line": "She's just better. Don't @ me.",
        },
    ],
    15: [  # Mainstage Theatre
        {
            "name": "Photo Backstage Clip",
            "x": 2,
            "y": 6,
            "picture": "LivClip04",
            "intro": "Backstage: a still from a Freaky Friday stream.",
            "look_prompt": "Look at the poster?",
            "liv_line": "Good vibes only on stream. (=^-^=)",
        },
        {
            "name": "Photo Lobby Banner",
            "x": 16,
            "y": 6,
            "picture": "LivTwitchBanner",
            "intro": "The theatre lobby has your Twitch channel banner.",
            "look_prompt": "Admire it?",
            "liv_line": "Feels like opening night every day.",
            "zoom": 35,
            "origin": 0,
            "pos_x": 80,
            "pos_y": 40,
        },
        {
            "name": "Photo Clip Wall",
            "x": 8,
            "y": 5,
            "picture": "LivClip05",
            "intro": "A clip highlight: \"thats what she said\".",
            "look_prompt": "Relive it?",
            "liv_line": "Chat never lets me live that down.",
        },
        {
            "name": "Photo Clip Wall 2",
            "x": 10,
            "y": 5,
            "picture": "LivClip07",
            "intro": "Poster: \"dont clip the sneeze\".",
            "look_prompt": "Look anyway?",
            "liv_line": "They clipped it. Of course they did.",
        },
    ],
    1: [  # Floroma Town Upper
        {
            "name": "Photo Town Board",
            "x": 20,
            "y": 8,
            "picture": "LivClip03",
            "intro": "The community board has a Twitch clip flyer.",
            "look_prompt": "Read the flyer?",
            "liv_line": "Poudre a canon par hazard... classic jumpscare energy.",
        },
    ],
    12: [  # Pog Cubs Mansion 1F
        {
            "name": "Photo Pog Cubs",
            "x": 10,
            "y": 6,
            "picture": "LivClip06",
            "intro": "Someone pinned a stream moment in the mansion.",
            "look_prompt": "Check it out?",
            "liv_line": "A sacrifice... for content.",
        },
    ],
    7: [  # Convenience Store
        {
            "name": "Photo Magazine Rack",
            "x": 3,
            "y": 3,
            "picture": "LivClip08",
            "intro": "A magazine cover looks suspiciously like a Twitch clip.",
            "look_prompt": "Flip through it?",
            "liv_line": "Je ne veux pas travailler... mood.",
        },
    ],
    6: [  # Nunya House 2F
        {
            "name": "Photo Twitch Hall",
            "x": 14,
            "y": 8,
            "picture": "LivClip01",
            "intro": "Another Obliviosa photo on the wall.",
            "look_prompt": "Look closer?",
            "liv_line": "The squad house needs more Pog energy.",
        },
    ],
}


def next_event_id(events: list) -> int:
    max_id = 0
    for ev in events:
        if ev and isinstance(ev, dict) and "id" in ev:
            max_id = max(max_id, ev["id"])
    return max_id + 1


def load_map(map_id: int) -> dict:
    path = DATA / f"Map{map_id:03d}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f), path


def save_map(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def upgrade_map005_stream_photo(events: list) -> None:
    """Turn 'stream setup' interactable into a real photo viewer."""
    for ev in events:
        if not ev or ev.get("id") != 10:
            continue
        upgraded = make_photo_event(
            10,
            "Photo Stream Setup",
            ev["x"],
            ev["y"],
            "LivTwitchProfile",
            "A framed photo of the stream setup.",
            "Look closer?",
            "Do is photobombing in the corner. Classic.",
            zoom=50,
            origin=0,
            pos_x=168,
            pos_y=-16,
        )
        ev["name"] = upgraded["name"]
        ev["note"] = upgraded["note"]
        ev["pages"] = upgraded["pages"]
        return


def main() -> None:
    for map_id, photos in MAP_PHOTOS.items():
        data, path = load_map(map_id)
        events = data.setdefault("events", [None])
        if map_id == 5:
            upgrade_map005_stream_photo(events)

        next_id = next_event_id(events)
        for spec in photos:
            # Skip duplicate coords on map 5 for profile if we upgraded event 10
            if map_id == 5 and spec["picture"] == "LivTwitchProfile":
                continue
            ev = make_photo_event(next_id, **spec)
            while len(events) <= next_id:
                events.append(None)
            events[next_id] = ev
            next_id += 1
            print(f"  Map{map_id:03d}: added {ev['name']} at ({ev['x']},{ev['y']})")

        save_map(path, data)
        print(f"Saved {path.name}")


if __name__ == "__main__":
    main()
