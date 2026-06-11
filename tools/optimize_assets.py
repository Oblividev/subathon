#!/usr/bin/env python3
"""Lossy-safe optimizer for Obliviosa RPG Maker MZ assets."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FFMPEG = ROOT / "node_modules" / "ffmpeg-static" / "ffmpeg"

# Game canvas is 816x624; pictures rarely need more than this on the long edge.
PICTURE_MAX_DIM = 816

# Folders that must keep exact pixel dimensions (tile/sprite grids).
NO_RESIZE_DIRS = {
    "tilesets",
    "characters",
    "faces",
    "sv_actors",
    "sv_enemies",
    "system",
    "icons",
    "parallaxes",
    "battlebacks1",
    "battlebacks2",
    "enemies",
    "animations",
    "pictures",  # handled separately with resize allowed
}

# Vorbis quality: 0=worst, 10=best. 4 is a good BGM sweet spot.
BGM_QUALITY = "4"
BGS_QUALITY = "4"
SE_ME_QUALITY = "5"
MENU_BGM_QUALITY = "3"  # audio_bgm_waiting.ogg


def human_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024**2:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1024**2:.1f} MB"


def dir_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def optimize_png(path: Path, allow_resize: bool, max_dim: int) -> tuple[int, int]:
    before = path.stat().st_size
    with Image.open(path) as img:
        original_mode = img.mode
        work = img.convert("RGBA") if img.mode in ("RGBA", "LA", "P") else img.convert("RGB")
        if allow_resize and max(work.size) > max_dim:
            work.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        if original_mode == "P":
            # Preserve indexed assets if we didn't resize.
            if work.size == img.size:
                work = img
            else:
                work = work.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)
        elif original_mode == "RGB" and work.mode == "RGBA" and work.getextrema()[3] == (255, 255):
            work = work.convert("RGB")

        tmp = path.with_suffix(path.suffix + ".opt")
        save_kwargs: dict = {"optimize": True, "compress_level": 9}
        if work.mode == "JPEG":
            save_kwargs["quality"] = 85
        work.save(tmp, format="PNG", **save_kwargs)

    after = tmp.stat().st_size
    if after < before:
        tmp.replace(path)
        return before, after
    tmp.unlink(missing_ok=True)
    return before, before


def optimize_images() -> tuple[int, int]:
    saved = 0
    processed = 0
    img_root = ROOT / "img"
    for path in sorted(img_root.rglob("*.png")):
        rel_parts = path.relative_to(img_root).parts
        top = rel_parts[0] if rel_parts else ""
        allow_resize = top == "pictures"
        max_dim = PICTURE_MAX_DIM
        before, after = optimize_png(path, allow_resize, max_dim)
        if after < before:
            saved += before - after
        processed += 1
    return processed, saved


def ffmpeg_reencode_ogg(src: Path, quality: str) -> tuple[int, int]:
    before = src.stat().st_size
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        cmd = [
            str(FFMPEG),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(src),
            "-map_metadata",
            "-1",
            "-c:a",
            "libvorbis",
            "-q:a",
            quality,
            str(tmp_path),
        ]
        subprocess.run(cmd, check=True)
        after = tmp_path.stat().st_size
        if after < before:
            shutil.move(str(tmp_path), src)
            return before, after
        return before, before
    finally:
        tmp_path.unlink(missing_ok=True)


def optimize_audio() -> tuple[int, int]:
    saved = 0
    processed = 0
    audio_root = ROOT / "audio"
    for path in sorted(audio_root.rglob("*.ogg")):
        rel = path.relative_to(audio_root)
        if rel.parts[0] == "bgm":
            quality = MENU_BGM_QUALITY if path.stem.lower() == "audio_bgm_waiting" else BGM_QUALITY
        elif rel.parts[0] == "bgs":
            quality = BGS_QUALITY
        else:
            quality = SE_ME_QUALITY
        before, after = ffmpeg_reencode_ogg(path, quality)
        if after < before:
            saved += before - after
        processed += 1
    return processed, saved


def optimize_video() -> tuple[int, int]:
    path = ROOT / "movies" / "prizegottigaming.webm"
    if not path.exists():
        return 0, 0
    before = path.stat().st_size
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        # VP8 + Vorbis for broad RPG Maker / browser compatibility.
        cmd = [
            str(FFMPEG),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(path),
            "-vf",
            "scale=816:-2",
            "-c:v",
            "libvpx",
            "-crf",
            "28",
            "-b:v",
            "0",
            "-cpu-used",
            "4",
            "-c:a",
            "libvorbis",
            "-q:a",
            "4",
            str(tmp_path),
        ]
        subprocess.run(cmd, check=True, timeout=300)
        after = tmp_path.stat().st_size
        if after < before:
            shutil.move(str(tmp_path), path)
            return before, before - after
        return before, 0
    finally:
        tmp_path.unlink(missing_ok=True)


def main() -> int:
    if not FFMPEG.exists():
        print("Missing ffmpeg. Run: npm install ffmpeg-static", file=sys.stderr)
        return 1

    before_img = dir_size(ROOT / "img")
    before_audio = dir_size(ROOT / "audio")
    before_movies = dir_size(ROOT / "movies")

    print("Optimizing PNG images...")
    img_count, img_saved = optimize_images()
    print(f"  {img_count} PNGs, saved {human_bytes(img_saved)}")

    print("Re-encoding OGG audio...")
    audio_count, audio_saved = optimize_audio()
    print(f"  {audio_count} OGGs, saved {human_bytes(audio_saved)}")

    print("Re-encoding movie...")
    video_before, video_saved = optimize_video()
    if video_before:
        print(f"  prizegottigaming.webm: {human_bytes(video_before)} -> {human_bytes(video_before - video_saved)}")

    after_img = dir_size(ROOT / "img")
    after_audio = dir_size(ROOT / "audio")
    after_movies = dir_size(ROOT / "movies")

    summary = {
        "img": {"before": before_img, "after": after_img},
        "audio": {"before": before_audio, "after": after_audio},
        "movies": {"before": before_movies, "after": after_movies},
    }
    print("\nTotals:")
    for key, vals in summary.items():
        delta = vals["before"] - vals["after"]
        print(f"  {key}: {human_bytes(vals['before'])} -> {human_bytes(vals['after'])} ({human_bytes(delta)} saved)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
