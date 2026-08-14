# dss-dashboard-builder

数据看板 / DSS（决策支持）系统从0到1构建方法。源自一个真实 DSS 经营管理平台（经营日报 + 库存分析）的项目沉淀，已去业务化成领域无关的通用骨架，通过 `domain-mapping.md` 适配长租/电商/SaaS/制造等领域。

让 AI 拿到「做个数据看板」需求时，**不直接写代码**，而是先摸清数据、再定口径、再写逻辑、最后验收。核心信念：**数据看板的价值是数据准确，不是页面好看。**

## 适用场景

- 「帮我做份经营日报/库存分析/运营大屏/销售仪表盘」
- 「把这份 Excel 做成报表/可视化/分析平台」
- 任何以数据为核心的展示、统计、监控、待办系统

## 核心流程

```
阶段0 定规则+目标 → 阶段1 数据范围定义 → 阶段2 指标目录 → 阶段3 MVP数据验证
                 → 阶段4 指标库发布 → 阶段5 应用层组装 → 阶段6 视觉打磨 → 阶段7 部署上线 → 阶段8 验收
```

九个阶段，一个引导对话 + 一个产出物，层层累积拼成成品。核心是 3 个价值点：**用户故事定目标**（阶段0）、**指标库定义→验证→发布**（阶段2-4）、**应用层组装选配**（阶段5），外加**视觉打磨**（阶段6，功能定死后做）。

## 为什么这套流程值得用

| 环节 | 不这样做会踩的坑 |
|------|-----------------|
| 数据先行 | 拿到脏数据直接写逻辑，聚合结果全是 NaN 或静默丢数据 |
| 口径先行 | 指标口径一变，所有代码白写 |
| 规则先行 | 异常规则没对齐就写规则引擎，规则引擎写完发现规则就错了 |
| 分步交付 | 方向跑偏，做越多错越多 |
| 复合 key 聚合 | 同名楼栋跨组撞 key，数据悄悄串 |
| 换文件名绕过 CDN 缓存 | 改了代码用户永远看到旧版 |
| 自动化验收 | 靠肉眼点验，滚动/图表溢出问题发现不了 |
| 直接字段 vs 派生字段 | 把业务手填字段当派生指标算，页面和公式对不上（真实案例 141/360 差异） |
| 字段全 0 要确认 | 整列全 0 默认当对，实际是字段已废弃 |
| 异常规则 enabled | 规则对象漏 enabled 字段，规则全跳过、异常永远 0 |
| 视角切换刷新筛选器 | 切视角重建树后筛选器停在旧维度 |

## 使用方式

对 AI 说「用 dss-dashboard-builder 帮我做……」，或直接描述数据看板需求，skill 会被自动触发（各平台安装见 `INSTALL.md`）。

## 目录结构

```
dss-dashboard-builder/
├── SKILL.md                      # 主文件：核心原则 + 9阶段工作流 + 硬性避坑 + 前置依赖
├── README.md                     # 项目说明
├── INSTALL.md                    # 多平台安装指南（Claude Code / WorkBuddy / Cursor）
├── MAINTENANCE.md                # 维护手册（版本规则、更新流程、过期检测）
├── CHANGELOG.md                  # 版本更新记录
└── references/                   # 按需读取的模式文档（每篇顶部有依赖声明）
    ├── module-story.md           # 模块定义卡 + 启动前准备 checklist（阶段0）
    ├── domain-mapping.md         # 领域映射表（通用字段 → 业务字段，长租/电商/SaaS/制造）
    ├── data-source-patterns.md   # 数据源接入模式（Excel/DB/API/JSON 选型决策树）
    ├── data-profiling.md         # 数据验证检查清单（阶段3）
    ├── metric-dictionary.md      # 指标口径字典模板（通用字段骨架）
    ├── metric-library.md         # 指标库全流程（目录→验证→发布，阶段2-4）
    ├── excel-import.md           # Excel/CSV 解析模式（表头匹配、交叉校验）
    ├── assembly-config.md        # 应用层组装清单（四维选项+验收标准，阶段5）
    ├── visual-polish.md          # 视觉打磨清单（配色/布局/logo/署名，阶段6）
    ├── anomaly-todo.md           # 异常监控规则 + 提醒方式 + 待办策略
    ├── tree-aggregation.md       # 树形聚合 / 多维钻取
    ├── permission.md             # 声明式权限（data-auth）
    ├── cloud-sync-adapter.md     # 数据访问层适配器（CloudBase/fetch/MySQL 后端）
    ├── cloud-deploy.md           # 部署上线（CDN 缓存坑、MySQL 建表模板）
    ├── export-report.md          # 报表导出静态化（图表转图、去依赖、离线可看）
    └── acceptance-checklist.md   # 模块级分层验收清单
```

## 来源项目

- 源项目：一个 DSS 经营管理平台（经营日报 + 库存分析 + 数据日历）
- 源技术栈：纯前端 HTML/CSS/JS + CloudBase Serverless → 后期改 MySQL
- 沉淀方式：从真实踩坑复盘提炼成可复用模式，**已去业务化**——字段用通用骨架（metric_total/metric_part/inflow/outflow 等），通过 `domain-mapping.md` 适配到具体领域

## 许可

开源，欢迎使用和反馈。署名约定：`Powered by dss-dashboard-builder`
