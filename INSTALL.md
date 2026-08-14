# dss-dashboard-builder 安装说明

一个跨平台 AI Skill，帮助 AI 从0到1构建数据看板 / DSS（决策支持）系统。支持 **Claude Code / WorkBuddy / Cursor** 三个平台。

## 安装（各平台）

### Claude Code

1. 关闭所有正在运行的 Claude Code 会话
2. 把 `dss-dashboard-builder` 文件夹复制到：
   - **macOS**：`~/.claude/skills/`
   - **Windows**：`C:\Users\<你的用户名>\.claude\skills\`
3. 重新打开 Claude Code，即可使用

> `~/.claude/skills/` 是 Claude Code 的官方自动加载路径，重启后自动加载，无需额外配置（已在 Claude Code 实测确认）。如果该目录不存在，手动创建即可。

### WorkBuddy

1. 把 `dss-dashboard-builder` 文件夹复制到：
   - **用户级**：`~/.workbuddy/skills/`
   - **项目级**：`.workbuddy/skills/`（项目根目录下，仅该项目生效）
2. 重新打开 WorkBuddy，即可使用

### Cursor

Cursor 用规则（`.mdc`）而非 skill 格式，需要转换。在项目 `.cursor/rules/` 下创建 `dss-dashboard-builder.mdc`，frontmatter 转换示例：

```
---
description: 数据看板/DSS 构建流程，触发词"做个数据看板/经营报表/库存分析"等
globs: "**/*"
alwaysApply: false
---
```

然后把 `SKILL.md` 正文粘进来，`references/` 里的模式文档按需复制到项目 `docs/` 或 `.cursor/rules/` 子目录。

## 验证安装

在任意项目里对 AI 说一句：

```
做个数据看板
```

如果 AI 开始按「定规则+目标 → 数据范围定义 → 指标目录 → MVP 数据验证 → 指标库发布 → 应用层组装 → 视觉打磨 → 部署上线 → 验收」的 9 阶段流程走，并引用 `dss-dashboard-builder`，说明安装成功。

## 它做什么

数据看板 / DSS 系统从0到1构建方法，核心原则：

- **数据先行**：拿到数据先确认「范围及定义」、定指标，再验证数据对不对——没验证通过不写展示逻辑
- **口径先行**：先定义指标公式/口径，跟用户对齐再写代码
- **分步交付**：每完成一个模块先确认方向，不一口气做完
- **验收先行**：交付前对齐"什么样算做完"，按清单逐项核验

## 适用场景

- 「帮我做份经营日报 / 库存分析 / 运营大屏 / 销售仪表盘」
- 「把这份 Excel 做成报表 / 可视化 / 分析平台」
- 任何以数据为核心的展示、统计、监控、待办系统

## 目录结构

```
dss-dashboard-builder/
├── SKILL.md                      # 主文件：核心原则 + 9阶段工作流 + 硬性避坑 + 前置依赖
├── README.md                     # 项目说明
├── INSTALL.md                    # 本文件（多平台安装）
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
    ├── tree-aggregation.md       # 树形聚合 / 多维钻取
    ├── anomaly-todo.md           # 异常监控规则 + 提醒方式 + 待办策略
    ├── permission.md             # 声明式权限（data-auth）
    ├── cloud-sync-adapter.md     # 数据访问层适配器（CloudBase/fetch/MySQL 后端）
    ├── cloud-deploy.md           # 部署上线（CDN 缓存坑、MySQL 建表模板）
    ├── export-report.md          # 报表导出静态化（图表转图、去依赖、离线可看）
    └── acceptance-checklist.md   # 模块级分层验收清单
```

## 反馈

使用中有问题、有想补充的模式，欢迎反馈给分享者。

---
*Powered by 羊哥&C妹*
