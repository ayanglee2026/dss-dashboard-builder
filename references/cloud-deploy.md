# 部署上线模式

> **依赖与前置**
> - 前置：`data-source-patterns.md`（数据源选型，决定部署形态）、`cloud-sync-adapter.md`（后端接口契约）
> - 被依赖：无
> - 可独立读，但部署形态先看 data-source-patterns。

从 DSS 的 CloudBase 部署踩坑沉淀。**部署阶段是最容易翻车的地方**，CDN 缓存一年、云函数环境问题、本地云端不同步，都真实踩过。

## 0. 先定部署形态

| 场景 | 方案 |
|------|------|
| 本地用 / 内部展示，数据不共享 | 纯前端，静态文件打开即可 |
| 数据多人共享、要持久化 | 后端 + 前端，二选一 |
| 后端持久化、数据量不大 | 云函数/Serverless（免运维） |
| 数据量大、要复杂查询 | 自建服务器（自己运维，慎选） |
| 公司有现成 MySQL | Node 服务 + MySQL（见下方建表模板） |

**后端优先级：云函数/Serverless > 自建服务器**。自建 = 自己扛运维、备份、安全。**公司已有 MySQL 时直接用**，不重复造轮子。

## 1. 静态资源 CDN 缓存坑（大坑）

**现象**：改了 JS/CSS，用户浏览器还是旧版。因为静态托管对 JS/CSS 设了 `max-age=31536000`（1年）缓存。

**关键认知**：
- **query string 不能绕过缓存**：`daily-report.js?v=20260802` 还是会被缓存（部分平台）
- **必须换文件名**：`daily-report-20260802-1430.js` 才能强制刷新

**解决方案**：部署脚本自动生成带时间戳的文件名，并同步改 HTML 引用：

```bash
TODAY=$(date +%Y%m%d-%H%M%S)
DATED_JS="daily-report-${TODAY}.js"
sed -i '' "s|js/daily-report[^\"]*\.js|js/${DATED_JS}|g" daily-report.html
tcb hosting deploy "./js/daily-report.js" "/js/${DATED_JS}" -e "${ENV_ID}"
```

**如果用户反馈"还是旧版"**：先查 CDN 缓存，别怀疑代码。改版本号文件名是标准解法。

## 2. 云函数部署的三座大山（CloudBase 特例）

1. **在线编辑器创建的函数没有 node-sdk**：控制台点测试能跑，但代码里 `require('@cloudbase/node-sdk')` 会报错。CLI 部署带 package.json 又会因为 Nodejs20 的 `mjs` 报错
2. **解决方案**：CLI 部署**不带 package.json**（函数代码本身不 require 云 sdk 时）
3. **目录污染**：`tcb hosting deploy .` 会把 node_modules 也传上去。必须有 `.tcbignore` 排除，否则 CDN 路径被 5000+ 文件污染

## 3. 本地 ↔ 云端不同步（团队协作坑）

**规则**：控制台改代码必须同步回本地，本地是唯一真实来源。

```
改代码 → 本地改 → CLI 部署（保持本地权威）
        ↘ 控制台改了 → 立刻同步回本地，否则下次部署覆盖云端修复
```

## 4. 部署后验证清单

- [ ] 页面能打开，无 404（HTML/JS/CSS/图片路径都对）
- [ ] console 无报错（特别是 `Unexpected token '<'` = JS 被 CDN 返回成了 HTML）
- [ ] 数据能正常加载（调后端接口成功）
- [ ] 登录 / 上传 / 导出核心流程走一遍
- [ ] 让一个**没开过这个页面的人**访问一次——验证不是浏览器缓存

## 5. 交接场景（换公司部署）

纯静态 + 自建 API 是最好交接的组合：
- 前端一个文件夹扔 Nginx/CDN 就能跑
- 后端 7 个 POST 接口，契约在 API 文档里
- 数据库用 MySQL，schema 一条 SQL 建完
- 换后端只改 `cloudsync.js` 的 BASE_URL

### MySQL 建表模板（快照表）

树形聚合结果整存为快照，按日期 + 通用字段查询。列名直接沿用 `SUM_FIELDS` 的通用名（见 `excel-import.md`），保持一处定义不漂移：

```sql
CREATE TABLE report_snapshot (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  report_date DATE NOT NULL,                 -- 报表日期，建索引
  entity_l1   VARCHAR(64) NOT NULL,          -- 通用实体层级，见 domain-mapping.md
  entity_l2   VARCHAR(64) NOT NULL,
  entity_l3   VARCHAR(64) NOT NULL,
  metric_total DECIMAL(14,2) DEFAULT 0,      -- 直接字段，列名 = SUM_FIELDS
  metric_part DECIMAL(14,2) DEFAULT 0,
  inflow_field DECIMAL(14,2) DEFAULT 0,
  outflow_field DECIMAL(14,2) DEFAULT 0,
  actual_field DECIMAL(14,2) DEFAULT 0,
  target_field DECIMAL(14,2) DEFAULT 0,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  KEY idx_date (report_date, entity_l1, entity_l2)
);
```

要点：
- **列名 = SUM_FIELDS 通用名**，解析、聚合、上传、建表全引用同一套名字
- **report_date 单独建索引**，按日期加载才快（不要依赖 JSON 列做查询键）
- 明细行可能上千条：上传用**事务 DELETE + INSERT 批量写入**，保证原子性

## 6. 部署前确认

部署 = 影响线上的动作。**部署前问用户**：目标是测试环境还是生产？改哪些文件？要不要动数据库？（数据库变更/迁移属于红线，必须先问）
