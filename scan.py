"""Scan your astrophotography folders and build data.json + thumbnails for the Messier tracker.

Usage:  python scan.py [photos_dir]

Settings live in config.json. The photos directory is only read, never written.
A folder counts as a Messier object when its name contains "M31", "M 31", "M_31" or "Messier 31".
Folders that don't say which object they are can be mapped in manual.json:
  {"folders": {"<folder name>": 42}, "objects": [57]}
"objects" marks targets as shot even without any folder (e.g. shot with other gear).
Shooting dates and times are never written to data.json.
"""
import json
import re
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # Pillow is optional: without it thumbnails are copied as-is
    Image = None

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"
CUSTOM = IMG / "custom"
FRAME_EXT = {".fits", ".fit", ".fts"}
THUMB_MAX = 800

MESSIER = re.compile(r"(?<![A-Za-z0-9])M(?:essier)?[ _-]?(\d{1,3})(?!\d)", re.I)
DWARF = re.compile(r"_EXP_(?P<exp>[\d.]+)_GAIN_(?P<gain>\d+)_")
CAMERA = re.compile(r"_(TELE|WIDE)_")


def load_json(name, default):
    path = HERE / name
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def folders(root, depth):
    level = [root]
    for _ in range(depth):
        level = [d for parent in level for d in sorted(parent.iterdir()) if d.is_dir()]
        yield from level


def messier_number(name, manual):
    if name in manual:
        return int(manual[name])
    match = MESSIER.search(name)
    return int(match[1]) if match else None


def session(folder):
    try:
        info = json.loads((folder / "shotsInfo.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        info = {}
    dwarf = DWARF.search(folder.name)
    camera = CAMERA.search(folder.name)
    exp = float(dwarf["exp"]) if dwarf else float(info["exp"]) if info.get("exp") else None
    gain = int(dwarf["gain"]) if dwarf else info.get("gain")
    frames = sum(1 for f in folder.iterdir() if f.suffix.lower() in FRAME_EXT)
    stacked = int(info.get("shotsStacked") or 0)
    return {
        "camera": camera[1] if camera else None,
        "exp": exp,
        "gain": gain,
        "frames": frames,
        "stacked": stacked,
        "integration": round((stacked or frames) * exp) if exp else None,
    }


def save_thumbnail(src, dest):
    if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
        return
    if Image is None:
        shutil.copy2(src, dest)
        return
    with Image.open(src) as im:  # re-encode: shrinks the file and drops EXIF (incl. timestamps)
        im = im.convert("RGB")
        im.thumbnail((THUMB_MAX, THUMB_MAX))
        im.save(dest, "JPEG", quality=85)


def main():
    config = load_json("config.json", {})
    root = Path(sys.argv[1] if len(sys.argv) > 1 else config.get("photos_dir", "."))
    if not root.is_dir():
        sys.exit(f"Photos folder not found: {root}")
    manual = load_json("manual.json", {})
    thumb_names = config.get("thumbnail_names", ["stacked_thumbnail.jpg", "stacked.jpg"])

    found = {}
    for folder in folders(root, int(config.get("scan_depth", 1))):
        m = messier_number(folder.name, manual.get("folders", {}))
        if m is None or not 1 <= m <= 110:
            continue
        thumb = next((folder / n for n in thumb_names if (folder / n).exists()), None)
        found.setdefault(m, []).append((folder.name, session(folder), thumb))
    for m in manual.get("objects", []):
        found.setdefault(int(m), [])

    IMG.mkdir(exist_ok=True)
    objects = {}
    for m, entries in sorted(found.items()):
        entries.sort(key=lambda e: e[0])
        image = None
        if (CUSTOM / f"M{m}.jpg").exists():
            image = f"img/custom/M{m}.jpg"
        else:
            thumbs = [e for e in entries if e[2]]
            if thumbs:
                best = max(thumbs, key=lambda e: e[1]["stacked"])
                image = f"img/M{m}.jpg"
                save_thumbnail(best[2], HERE / image)
        objects[m] = {"image": image, "sessions": [e[1] for e in entries]}

    (HERE / "data.json").write_text(
        json.dumps({"objects": objects}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(objects)}/110 shot: " + ", ".join(f"M{m}" for m in objects))


if __name__ == "__main__":
    main()
