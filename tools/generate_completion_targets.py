#!/usr/bin/env python3
"""Build data/CompletionTargets.json for CompletionTracker.js."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERACT_TAG = "auto-added interactable"
COUNT_VAR = 1


def event_has_npc_counter(event: dict) -> bool:
    for page in event.get("pages") or []:
        lst = page.get("list") or []
        for i in range(len(lst) - 1):
            cmd, nxt = lst[i], lst[i + 1]
            if (
                cmd.get("code") == 111
                and cmd.get("indent") == 0
                and cmd.get("parameters") == [2, "A", 1]
                and nxt.get("code") == 122
                and nxt.get("indent") == 1
                and nxt.get("parameters") == [COUNT_VAR, COUNT_VAR, 1, 0, 1]
            ):
                return True
    return False


def main() -> None:
    map_infos = json.loads((ROOT / "data/MapInfos.json").read_text(encoding="utf-8"))
    total = 0
    interactables: list[dict[str, int]] = []

    for map_id in range(1, len(map_infos)):
        if not map_infos[map_id]:
            continue
        path = ROOT / f"data/Map{map_id:03d}.json"
        if not path.exists():
            continue
        map_data = json.loads(path.read_text(encoding="utf-8"))
        for event in map_data.get("events") or []:
            if not event:
                continue
            note = event.get("note") or ""
            is_interactable = INTERACT_TAG in note
            has_npc_counter = event_has_npc_counter(event)
            if not is_interactable and not has_npc_counter:
                continue
            total += 1
            if is_interactable and not has_npc_counter:
                interactables.append({"mapId": map_id, "eventId": event["id"]})

    out = {"totalTargets": total, "interactableTargets": interactables}
    out_path = ROOT / "data/CompletionTargets.json"
    out_path.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {out_path.relative_to(ROOT)}: {total} targets, {len(interactables)} interactables")


if __name__ == "__main__":
    main()
