# Messier Marathon Tracker

A static progress page for photographing all 110 Messier objects. It runs on GitHub Pages and has no backend.
The page is in English and can be switched to Chinese.

- Progress ring, total integration time and session count
- Tonight's sky panel: Moon phase and brightness, dark-sky hours and an hourly cloud forecast from [Open-Meteo](https://open-meteo.com/) (free, no API key)
- A **recommended time** for every object: the earliest stretch (at least 1 hour) in the next 3 nights when it's dark, the object is above 30°, cloud cover is at most 40% and the Moon isn't too close
- Filter by shot, not shot, or **doable tonight**, and by object type
- A "use my location" button; the location is only saved in the viewer's browser
- Thumbnails and per-session details (date, camera, exposure, gain, frames) for objects you have shot

## Use it yourself

1. **Fork** this repo, then go to **Settings → Pages → Deploy from a branch → `main` / root**.
2. Clone your fork and edit `config.json`:

   | key | meaning |
   |---|---|
   | `title` | page title |
   | `telescope` | shown under the title |
   | `photos_dir` | folder holding your shooting sessions (only read, never written) |
   | `scan_depth` | how many folder levels to search (1 = direct subfolders) |
   | `thumbnail_names` | image file names inside a session folder to use as the thumbnail |
   | `latitude`, `longitude` | default observing site for "tonight" (rounding to 1 decimal is enough) |
   | `default_language` | `en` or `zh` |
   | `repo` | link shown in the footer |

3. Clear out the author's progress: delete the `img/M*.jpg` files and set `data.json` to `{"objects": {}}`.
4. Run the update script after each night:

   ```bash
   ./update.sh        # macOS / Linux
   ```
   On Windows, double-click `update.bat`.

   It needs Python 3.8+. [Pillow](https://pypi.org/project/Pillow/) is optional; with it, thumbnails are resized and their EXIF data is removed.

### How folders are recognised

A session folder counts as an object when its name contains `M31`, `M 31`, `M_31` or `Messier 31`.
Folders from DWARF smart telescopes (`DWARF_RAW_TELE_M 31_EXP_15_GAIN_60_...`) work out of the box. For them the exposure, gain and stacked frame count come from the folder name and `shotsInfo.json`.

Use `manual.json` for everything else:

```json
{
  "folders": { "DWARF_RAW_TELE_EXP_30_GAIN_100_2026-01-21-21-53-36-413": 42 },
  "objects": [57, 27]
}
```

- `folders` maps unnamed folders to a Messier number.
- `objects` marks targets as shot when there is no folder for them, for example ones shot with other gear.

To use your own processed image instead of the auto thumbnail, put it at `img/custom/M31.jpg`.

---

## 中文说明

这是一个拍摄全部 110 个梅西耶天体的进度网页，托管在 GitHub Pages 上，不需要服务器。页面默认显示英文，右上角可以切换中文。

**自己使用：**
1. Fork 本仓库，然后在 Settings → Pages 里选择 `main` 分支、根目录。
2. 修改 `config.json`，主要改拍摄目录 `photos_dir` 和观测地的经纬度。
3. 删除 `img/M*.jpg`，把 `data.json` 改成 `{"objects": {}}`。
4. 每次拍完，运行 `update.bat`（Windows）或 `./update.sh`（macOS / Linux），网页约 1 分钟后更新。

文件夹名里带 `M31`、`M 31` 或 `Messier 31` 就会被识别。没写目标的文件夹，或者用其他设备拍的天体，写进 `manual.json`。已拍的天体会显示拍摄日期和时间（从文件夹名读取），未拍的天体不显示时间。
