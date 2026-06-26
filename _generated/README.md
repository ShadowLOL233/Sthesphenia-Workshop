# _generated/ — 自动派生视图（勿手改）

本目录的文件都是**脚本从各国档案派生**出来的聚合视图，**不是真相源**。

- `nations-table.auto.md` — 全国家面板聚合表，由 `scripts/gen_nations_table.py` 从 `nations/`、`players/` 各档案的面板表生成。

## 单一真相源原则
- **真相源 = 各国档案**（`nations/<国名>.md`、`players/<国名>.md`）的面板表与 frontmatter。
- 改数值/技术等级 → 改对应国家档案 → 重跑脚本刷新本目录。
- **不要手改本目录文件**，会在下次生成时被覆盖。

## 刷新命令
```
python scripts/gen_nations_table.py
```

> 手工整理的 `nations-table.md`（含天下四分/蜂巢联盟分组、特性表、脚注等叙事性内容）仍为正式展示表；本自动表用于**快速核对一致性**与防漂移。两者并存，待 GM 决定是否合并。
