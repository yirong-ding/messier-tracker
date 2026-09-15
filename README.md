# 梅西耶马拉松 · 110

用 DWARF 智能望远镜拍全部 110 个梅西耶天体的进度页。

## 更新

1. 把望远镜存储连上电脑（`H:\Astronomy`）
2. 双击 `update.bat`，它会扫描拍摄文件夹，生成 `data.json`、复制缩略图，然后推送到 GitHub
3. 大约 1 分钟后网页更新

扫描规则：文件夹名形如 `DWARF_RAW_TELE_M 31_EXP_...` 的都算已拍。
没写目标名的文件夹可以在 `manual.json` 里手动指定：

```json
{ "DWARF_RAW_TELE_EXP_30_GAIN_100_2026-01-21-21-53-36-413": 42 }
```
