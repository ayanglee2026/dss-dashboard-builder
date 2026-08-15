# CHANGELOG

## 2.1.0 (2026-08-15)

- 新增 `tools/profiler.py` 数据画像生成器：读 Excel/CSV → 自动输出字段画像 + 异常清单（负数/超大值/整列全0/重复key/格式不一致/脏值占位），替代阶段 1/3 手工画像（DeepSeek harness 评测「工具化弱」落地，工具 #1）
- 阶段 0 项目规则文件按环境自适应（Claude Code → CLAUDE.md，DSH → AGENTS.md，WorkBuddy → 项目规则.md）

## 2.0.0 (2026-08-13)

结构性重构：工作流从「6 阶段步骤清单」升级为「9 阶段 goal 导向总装流程」，对齐真实作业流程（数据范围定义 → 指标目录 → MVP 数据验证 → 指标库发布 → 应用层组装）。在真实经营日报案例上完整跑通（重现版 + 29 项自动化验收全绿）。

- **工作流 6→9 阶段**：新增「目标定义」（用户故事+成功标准填空式）、「应用层组装」（四维选配+验收标准先行）、「视觉打磨」（配色/布局/logo/署名，功能定死后才做），「数据画像」拆为「数据范围定义」+「MVP 数据验证」，指标库从「一次性口径表」升级为「目录→验证→版本化发布」
- **新增 4 篇**：`module-story.md`（目标卡+准备checklist）、`metric-library.md`（指标库全流程，含「基础指标不默认全收录」精选原则）、`assembly-config.md`（组装清单）、`visual-polish.md`（视觉打磨清单）
- **改造 5 篇**：data-profiling 重定位为数据验证、metric-dictionary 补直接vs派生、anomaly-todo 补提醒方式+enabled坑、acceptance-checklist 改模块级、tree-aggregation 补视角切换刷新筛选器
- **硬性避坑新增 4 条**：直接字段vs派生字段、字段全0要确认、异常规则enabled、视角切换同步刷新筛选器（均来自经营日报案例真实踩坑）
- 去掉「用途类型」勾选（用途由用户故事自然带出）；启动前准备 checklist 前置
- 经 产品评审全量评测 + 造数据实跑 9 阶段，修复文档一致性（6→9 重构漏改的阶段号、INSTALL 残留 v1、「8 阶段」表述）+ 补 SUM_FIELDS 盲区指引（明细表混入父级合计字段会翻倍）；版本号维持 2.0.0（未正式发布，评测修复并入同版本）
- 经 产品评审 v2 框架校准版评测（直接用户 vs 间接用户），补「间接用户独立运行」设计层：新增 end-user-usability.md（7 章，砍策略闭环/规则编辑界面）、加轻量路径（单文件单图表快速通道）、验收跨平台降级（无 Playwright 环境人工走查）、核实 Claude Code 加载机制（确认 `~/.claude/skills` 自动加载）+ Cursor frontmatter 示例、术语表 glossary；版本号维持 2.0.0
- 实测沉淀（新签看板案例）：筛选器全局化+动态选项+全模块联动、待办清单 vs 处理状态持久化区分（清单不用存、状态必须存）、指标说明页路径规划（防404）、指标库 HTML 钉死为标配交付物+阶段2生成时机、指标→呈现形式映射（先出映射表再确认）、选项卡收集+字母编号格式、导出独立 HTML 的 `</script>` 转义坑

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
