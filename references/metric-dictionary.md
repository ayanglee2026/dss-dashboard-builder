# 指标口径字典模板（Metric Dictionary）

> **依赖与前置**
> - 前置：`domain-mapping.md`（通用字段 → 业务字段映射）
> - 被依赖：`tree-aggregation.md`（调用本文的 `deriveMetrics`）、`excel-import.md`（直接字段 = SUM_FIELDS）
> - 可独立读，但涉及派生指标时需配合 tree-aggregation。

**口径先行**：写代码前，把看板要展示的所有指标定义清楚，跟用户对齐。口径一变，代码全白写。

本模板用**领域无关的通用字段名**描述指标结构。具体业务字段怎么映射到这些通用名，见 `domain-mapping.md`。

## 指标分类

- **直接字段**：数据源里就有的原始字段（通用记作 `metric_total`、`metric_part`、`inflow_field`、`outflow_field`、`actual_field`、`target_field`）
- **派生指标**：算出来的（如占比率、净变动、达成率）。每个派生指标必须写清公式，公式是代码的核心，也是用户确认的重点

## 三类通用派生模式（覆盖绝大多数看板）

| 模式 | 公式 | 适用场景 |
|------|------|---------|
| 占比率 | `metric_part / metric_total * 100` | 在租率/活跃率/良品率/达成覆盖率 |
| 净变动 | `inflow_field - outflow_field` | 净增长/净流入/净增库存 |
| 达成率 | `actual_field / target_field * 100` | 目标完成率/KPI 达成 |

## 指标口径表模板

| 指标名 | 类型 | 定义/业务含义 | 公式/口径 | 数据来源字段 | 聚合粒度 | 单位 |
|--------|------|--------------|----------|-------------|---------|------|
| 总量基数 | 直接 | 可统计的总量（总规模/总库存/总目标） | 直接取数 | metric_total | 实体L1/L2/L3/总 | 个/套/元 |
| 占比率 | 派生 | 部分量占总量的比例 | 部分 ÷ 总量 × 100 | metric_part ÷ metric_total | 实体L1/L2/L3/总 | % |
| 当期净变动 | 派生 | 当期净增减量 | 流入 − 流出 | inflow_field − outflow_field | 实体L1/L2/L3/总 | 个/套/元 |
| 达成率 | 派生 | 实际完成占目标比 | 实际 ÷ 目标 × 100 | actual_field ÷ target_field | 实体L1/L2/L3/总 | % |

> 把"实体L1/L2/L3"替换成你的业务层级（组/门店/品类、部门/团队/员工、区域/城市/门店）。多领域映射见 `domain-mapping.md`。

## 口径确认要点（易混的坑）

1. **分子分母口径要匹配**：比如"流失率"分母用"期初存量 + 当期流入"还是"总量基数"，结果差很多。写进表格让用户拍板
2. **"当期" vs "累计"**：很多指标有 day/month/quarter 多个时间口径版本，漏一个报表就不完整。时间口径要在字段名后缀体现（如 `inflow_day` / `inflow_month`）
3. **时点 vs 时期**：时点值（如 `metric_part` 当前在租）和时期累计（如 `inflow_month` 月累计）不能混为一谈
4. **除零保护**：分母为 0 时返回 0，不要返回 Infinity 或 NaN
5. **口径表就是需求文档**：用户确认后，代码按表实现，实现完再对照表验收

## 派生指标公式的代码落地（通用骨架）

```javascript
// 通用派生：占比率、净变动、达成率三类
function deriveMetrics(node) {
  // 占比率：部分 ÷ 总量（除零保护）
  node.ratio_metric = node.metric_total > 0
    ? (node.metric_part / node.metric_total) * 100 : 0;
  // 净变动：流入 − 流出（字段缺失用 || 0 兜底）
  node.net_change = (node.inflow_field || 0) - (node.outflow_field || 0);
  // 达成率：实际 ÷ 目标
  node.achievement_rate = node.target_field > 0
    ? (node.actual_field / node.target_field) * 100 : 0;
}
```

注意 `|| 0` 兜底：字段缺失时不产生 NaN。**派生指标在每个聚合层级都重新算**（不能把率加起来），详见 `tree-aggregation.md`。

## 多领域映射示例（节选，完整见 domain-mapping.md）

| 通用字段 | 长租公寓 | 电商零售 | SaaS 订阅 | 制造业库存 |
|---------|---------|---------|----------|----------|
| metric_total | 可出租房源 | 总上架商品 | 总订阅席位 | 总库位 |
| metric_part | 在租房源 | 在售商品 | 活跃席位 | 可用库存 |
| inflow_field | 新签 | 上架 | 新购 | 入库 |
| outflow_field | 退租 | 下架 | 流失 | 出库 |
| 占比率 | 入住率 | 动销率 | 活跃率 | 可用率 |
| 净变动 | 净增长 | 净上架 | 净增席位 | 净增库存 |
