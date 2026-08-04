---
name: dss-dashboard-builder
description: 数据看板 / DSS（决策支持）系统从0到1的构建流程与方法。当用户说"做个数据看板/经营报表/库存分析/运营大屏/销售仪表盘/管理驾驶舱/DSS系统"，或给出 Excel/CSV 数据要求做统计、展示、监控、待办时使用。强调数据先行、口径先行、规则先行、分步交付、验收先行。也适用于"帮我把这份数据可视化/做成报表/分析平台"这类需求。
version: 1.2.1
agent_compatibility: [claude-code, workbuddy, cursor]
install:
  claude-code: ~/.claude/skills/
  workbuddy: ~/.workbuddy/skills/
  cursor: 项目 .cursor/rules/（需按其 rule 格式转换）
---

# 数据看板从0到1构建法

从真实 DSS 经营管理平台（经营日报 + 库存分析）沉淀，已去业务化成领域无关的通用骨架——见 `references/domain-mapping.md` 做领域适配（长租/电商/SaaS/制造等）。核心信念：**数据看板的价值是数据准确，不是页面好看。**

## 核心原则（不可跳过，违背前先跟用户说明）

1. **数据先行**：拿到数据先做画像，不画像不写逻辑。默认数据有坑，验证后再分析。
2. **口径先行**：先定义每个指标的公式/口径，跟用户对齐后再写代码。指标口径一变，所有代码白写。
3. **规则先行**：异常监控类的需求，先列规则清单（阈值、优先级、对应策略）给用户确认，再写代码。
4. **分步交付**：每完成一个模块先给用户确认方向，不一口气做完。方向跑偏，做越多错越多。
5. **V1 手动跑通，V2 再自动化**：需求模糊阶段不投入复杂工具。手动时间成本明显超过自动化时才直接走自动化。
6. **验收标准先行**：交付前跟用户对齐"什么样算做完"，按清单逐项核验。验收 = 满足使用场景，不是功能做完。

## 开工前必问（3 问，问清楚再动手）

1. **谁在用？** 决定权限模型、界面复杂度、要不要登录/口令。（只有内部几个人用？还是对外？）
2. **看什么指标？** 决定数据范围、聚合粒度、要哪些图表。（Top 5 指标是哪些？）
3. **数据从哪来？** Excel/数据库/接口？多久更新一次？谁来更新？(决定导入 vs 直连、要不要"上传"功能)

如果用户没回答完整，用这 3 问引导，但不要反复追问——先给最合理假设并说明，让用户纠正。

**不要单独问"主题是什么"**。看板主题（经营/库存/销售/运维……）只是领域外壳，由「看什么指标」自然带出。需要显式对齐看板定位时，用**用途维度**而不是领域维度：

| 用途 | 核心目标 | 设计重点 |
|------|---------|---------|
| 监控型 | 盯住关键指标、发现异常 | 告警、状态色、待办/策略 |
| 分析型 | 探索数据、找原因 | 筛选器、多维钻取、对比 |
| 汇报型 | 向上呈现结论 | 指标少而精、可视化、可导出 |

同一个领域可以做出三种完全不同定位的看板，用途决定设计，领域不决定。

## 工作流

### 阶段 0：定规则（不写业务代码）
- 新建项目目录结构：`src/` 源码、`data/` 原始数据、`output/` 产出物
- 写项目 `CLAUDE.md`：做什么、输入什么、输出什么、验收标准、技术选型
- 项目完成后进 `_archive/` 的归档约定，一并在 CLAUDE.md 里定好

### 阶段 1：数据画像
- 读原始数据，输出：字段清单、字段分布、缺失/空值统计、异常值（负数、超范围、文本里混数字）、格式不一致（同列多种格式、表头有全角/空格/换行）
- 用表格呈现画像结果，**给用户确认后再进入下一步**
- 参考 `references/data-profiling.md`

### 阶段 2：指标口径
- 列出看板全部指标，每个指标一行：指标名 | 定义 | 公式/口径 | 数据来源字段 | 聚合粒度 | 单位
- 区分"直接字段"（数据源里就有）和"派生指标"（算出来的，比如占比率、净变动、达成率）
- 输出《指标口径表》给用户确认
- 参考 `references/metric-dictionary.md`，业务字段怎么映射到通用骨架见 `references/domain-mapping.md`

### 阶段 3：MVP 跑通
- 用最简单方式实现可用版本：读取数据 → 关键指标展示。可先不做视觉打磨
- 给用户演示核心流程，确认方向没跑偏
- 数据可视化用成熟库（Chart.js/ECharts），不手写图表

### 阶段 4：叠加细节（每加一个功能先确认）
- 功能顺序建议：多指标展示 → 筛选器/视角切换 → 树形钻取 → 异常监控/待办 → 导出 → 权限 → 趋势
- 异常监控：先出规则清单（阈值、优先级、策略）确认后，再写规则引擎
- 汇报型看板的导出：必须静态化（图表转图、去依赖），参考 `references/export-report.md`
- 参考 `references/tree-aggregation.md`、`references/anomaly-todo.md`、`references/export-report.md`

### 阶段 5：部署上线
- 先定"要不要后端"：需要持久化/多人共享数据 → 后端；一次性展示/本地用 → 纯前端即可
- 后端选型优先级：云函数/Serverless > 自建服务器（自建 = 自己运维）
- 读接口要不要加口令校验：先问用户，别默认全加
- 静态资源缓存坑、部署验证，参考 `references/cloud-deploy.md`

### 阶段 6：验收
- 按 `references/acceptance-checklist.md` 分层验收：数据准确性 → 功能完整性 → 交互可用性
- 涉及滚动/图表渲染，必须实测 + 查 DOM overflow，不能只靠代码推断
- 用自动化测试（如 Playwright）替代手动点验

## 硬性避坑（来自真实踩坑）

- **表头缺失列必须报错**，不能静默填 0——静默 = 数据悄悄错
- **同名叶子实体跨组撞名**：聚合必须用复合 key（L1||L2||L3）或唯一 ID，否则串数据
- **数字字段转 Number 失败**：记 warning 而不是吞掉，方便排查
- **父节点 = 子节点求和**：聚合树必须做 sum 一致性校验，校验不过就报警
- **导出独立 HTML 时**：相对路径 CSS/图片会 404，要内联或转 base64
- **导出物必须静态化**：图表转 PNG 内嵌、去掉脚本/CDN 依赖，保证离线也能看（详见 `references/export-report.md`）

## 交付物标准

- 数据准确性优先于视觉效果
- 每个页面能自动化测试跑通
- 产出物语义化版本命名：`项目-v主.次.ext`，禁止"最终版""最终版2"
- 署名约定（如用户要求）：`Powered by 羊哥&C妹`

## 维护

- 版本与更新记录见 `CHANGELOG.md`，维护规则见 `MAINTENANCE.md`
- 源项目技术栈/字段变更时，必须同步更新 `domain-mapping.md` 和对应 reference
- 每季度对照源项目走一次校准（见 MAINTENANCE.md 的过期检测）
- 更新完重打包分享包，同步所有安装位置（Claude Code / WorkBuddy / Cursor）

## References

按需读取，不要一次全读。每个文件顶部有「依赖与前置」声明，读前看要补读哪篇：

| 文件 | 何时读 | 前置依赖 |
|------|--------|---------|
| `references/domain-mapping.md` | 开工先把通用字段骨架映射到业务领域 | 无（字段字典，先读） |
| `references/data-source-patterns.md` | 「数据从哪来」答完后定接入模式 | domain-mapping |
| `references/data-profiling.md` | 拿到数据要画像时 | domain-mapping |
| `references/metric-dictionary.md` | 定义指标口径、输出口径表时 | domain-mapping |
| `references/excel-import.md` | 涉及 Excel/CSV 导入、表头匹配、字段映射时 | domain-mapping、metric-dictionary |
| `references/anomaly-todo.md` | 做异常监控、规则、待办清单、对应策略时 | tree-aggregation |
| `references/tree-aggregation.md` | 做树形聚合、多维度钻取、视角切换时 | metric-dictionary、excel-import |
| `references/permission.md` | 做登录、权限、按钮级控制、上传口令校验时 | 无 |
| `references/cloud-sync-adapter.md` | 设计前端如何接后端时 | data-source-patterns |
| `references/cloud-deploy.md` | 部署上线时 | cloud-sync-adapter |
| `references/export-report.md` | 做汇报型看板、实现导出功能时 | 无 |
| `references/acceptance-checklist.md` | 验收阶段 | metric-dictionary |
