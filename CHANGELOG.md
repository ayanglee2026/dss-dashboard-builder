# CHANGELOG

## 1.2.1 (2026-08-04)

- `data-profiling.md`「超大值」补可执行判据：`> 中位数 × 10` 或 `> 业务上限` 标记待确认，不得直接参与聚合
- `data-profiling.md` 补硬规则：画像确认前不允许进入聚合（测试演示流程也不例外）
- `excel-import.md` 清洗规则：格式修正（去千分位逗号/去空格）也记 warning，不再静默改数据
- MAINTENANCE.md 待校准清单记入两条实测发现（已修复）

## 1.2.0 (2026-08-04)

- 新增 `data-source-patterns.md`：Excel/CSV、数据库直连、API 拉取、静态 JSON 四种数据源接入模式 + 选型决策树
- `cloud-sync-adapter.md` 补 MySQL 后端适配器（Node + Express + mysql2 连接池，含代码示例）
- `cloud-deploy.md` 补 MySQL 部署形态 + 快照表建表 SQL 模板
- `excel-import.md` 补建表列名与 SUM_FIELDS 联动的提示
- 新增 `MAINTENANCE.md` 维护手册（版本规则、更新流程、过期检测）
- 新增 `CHANGELOG.md`（本文件）
- references 全部加"依赖与前置"声明，SKILL.md references 表加前置依赖列，跨文件概念加锚点
- SKILL.md frontmatter 兼容多 agent（version / agent_compatibility / install）
- INSTALL.md 补三平台安装指南（Claude Code / WorkBuddy / Cursor）

## 1.1.0 (2026-08-04)

- 去业务化：字段抽象成通用骨架（metric_total / metric_part / inflow / outflow / entity_l1/l2/l3）
- 新增 `domain-mapping.md`（长租/电商/SaaS/制造四领域映射）
- tree-aggregation / excel-import / anomaly-todo / data-profiling 去公寓业务味
- SKILL / README 淡化来源、加领域适配引导

## 1.0.0

- 首版：从源项目沉淀 6 阶段工作流 + 10 篇 references
