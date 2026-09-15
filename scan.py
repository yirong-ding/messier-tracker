"""扫描 DWARF 拍摄文件夹，生成 data.json 并复制缩略图到 img/。

用法：python scan.py [拍摄根目录]
默认根目录为 H:\\Astronomy（望远镜存储），只读取，不会写入。
没写目标名的文件夹可以在 manual.json 里手动指定，例如：
  {"DWARF_RAW_TELE_EXP_30_GAIN_100_2026-01-21-21-53-36-413": 42}
"""
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"H:\Astronomy")
IMG = HERE / "img"

PATTERN = re.compile(
    r"^DWARF_RAW_(?P<cam>TELE|WIDE)_(?:(?P<target>.+?)_)?EXP_(?P<exp>[\d.]+)_GAIN_(?P<gain>\d+)_"
    r"(?P<date>\d{4}-\d{2}-\d{2})-(?P<time>\d{2}-\d{2})"
)
MESSIER = re.compile(r"^M(?:essier)?\s*(\d{1,3})$", re.I)


def load_manual():
    path = HERE / "manual.json"
    if not path.exists():
        return {}
    return {k: int(v) for k, v in json.loads(path.read_text(encoding="utf-8")).items()}


def read_info(folder):
    try:
        return json.loads((folder / "shotsInfo.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def main():
    if not ROOT.is_dir():
        sys.exit(f"找不到 {ROOT}，望远镜存储连上了吗？")
    manual = load_manual()
    objects = {}
    for folder in sorted(ROOT.iterdir()):
        if not folder.is_dir():
            continue
        match = PATTERN.match(folder.name)
        if not match:
            continue
        m = manual.get(folder.name)
        if m is None:
            target = MESSIER.match((match["target"] or "").strip())
            if not target:
                continue
            m = int(target[1])
        if not 1 <= m <= 110:
            continue

        info = read_info(folder)
        exp = float(match["exp"])
        frames = len(list(folder.glob("*.fits")))
        stacked = int(info.get("shotsStacked") or 0)
        thumb = next((folder / n for n in ("stacked_thumbnail.jpg", "stacked.jpg")
                      if (folder / n).exists()), None)
        objects.setdefault(m, []).append({
            "folder": folder.name,
            "camera": match["cam"],
            "date": match["date"],
            "time": match["time"].replace("-", ":"),
            "exp": exp,
            "gain": int(match["gain"]),
            "frames": frames,
            "stacked": stacked,
            "integration": round((stacked or frames) * exp),
            "_thumb": thumb,
        })

    IMG.mkdir(exist_ok=True)
    result = {}
    for m, sessions in sorted(objects.items()):
        sessions.sort(key=lambda s: (s["date"], s["time"]))
        with_thumb = [s for s in sessions if s["_thumb"]]
        image = None
        if with_thumb:
            best = max(with_thumb, key=lambda s: (s["stacked"], s["date"]))
            image = f"img/M{m}.jpg"
            dest = HERE / image
            if not dest.exists() or dest.stat().st_mtime < best["_thumb"].stat().st_mtime:
                shutil.copy2(best["_thumb"], dest)
        for s in sessions:
            del s["_thumb"]
        result[m] = {"image": image, "sessions": sessions}

    data = {"updated": datetime.now().strftime("%Y-%m-%d %H:%M"), "objects": result}
    (HERE / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"已拍 {len(result)}/110：" + ", ".join(f"M{m}" for m in result))


if __name__ == "__main__":
    main()
