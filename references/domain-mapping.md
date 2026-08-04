# 领域映射表（Domain Mapping）

> **依赖与前置**
> - 前置：无（第一个读的 reference，开工先读它建立通用字段概念）
> - 被依赖：`data-profiling.md`、`metric-dictionary.md`、`excel-import.md`、`tree-aggregation.md` 全部用它的通用字段骨架
> - 可独立读。这篇是整个 skill 的字段字典。

本文件把 skill 里的**通用字段骨架**映射到具体业务领域。skill 的代码示例用通用名（`metric_total`/`metric_part`/`inflow_field`/`outflow_field`/`entity_l1`/`entity_l2`/`entity_l3`），落地时按本表替换成你的业务字段。

## 通用字段命名约定

| 通用名 | 含义 | 用途 |
|--------|------|------|
| `entity_id` | 叶子实体唯一 ID | 聚合 key，防重名串数据 |
| `entity_l1` | 实体层级 1（最高） | 聚合分组维度 |
| `entity_l2` | 实体层级 2（中间） | 聚合分组维度 |
| `entity_l3` | 实体层级 3（叶子） | 聚合叶子节点 |
| `metric_total` | 总量基数 | 占比率的分母、规模指标 |
| `metric_part` | 部分量 | 占比率的分子 |
| `inflow_field` | 流入量 | 净变动的加项 |
| `outflow_field` | 流出量 | 净变动的减项 |
| `actual_field` | 实际值 | 达成率的分子 |
| `target_field` | 目标值 | 达成率的分母 |

时间口径用后缀区分：`_day` / `_month` / `_quarter`（如 `inflow_field_day`、`inflow_field_month`）。

## 四领域映射对照

| 通用字段 | 长租公寓 | 电商零售 | SaaS 订阅 | 制造业库存 |
|---------|---------|---------|----------|----------|
| entity_l1 | 区域 | 大区 | 公司主体 | 工厂 |
| entity_l2 | 组/经理 | 门店 | 团队 | 车间 |
| entity_l3 | 楼栋 | SKU | 席位/账号 | 库位 |
| entity_id | building_id | sku_id | account_id | bin_id |
| metric_total | 总规模(可出租) | 总上架商品 | 总订阅席位 | 总库位 |
| metric_part | 在租房源 | 在售商品 | 活跃席位 | 可用库存 |
| inflow_field | 新签 | 上架 | 新购 | 入库 |
| outflow_field | 退租 | 下架 | 流失 | 出库 |
| actual_field | 当月完成 | 实际销售额 | 实际消耗席位 | 实际产出 |
| target_field | 月度目标 | 销售目标 | 消耗目标 | 产出目标 |
| 占比率 | 入住率 | 动销率 | 活跃率 | 可用率 |
| 净变动 | 净增长 | 净上架 | 净增席位 | 净增库存 |
| 达成率 | 目标达成率 | 销售达成率 | 消耗达成率 | 产出达成率 |

## 映射步骤（开工时先做这步）

1. **识别业务实体层级**：你的数据按几个层级聚合？把每层命名填进 `entity_l1/l2/l3`
2. **找唯一 ID**：叶子实体有没有唯一 ID？有就用 `entity_id`，没有就用 `entity_l1 || entity_l2 || entity_l3` 复合 key
3. **对齐总量/部分字段**：哪个字段是"总量基数"（`metric_total`）？哪个是"部分量"（`metric_part`）？两者口径要对齐
4. **识别流入/流出**：净变动类指标的两个驱动字段（`inflow_field` / `outflow_field`）
5. **识别实际/目标**：有没有目标值？有就填 `actual_field` / `target_field`
6. **确定时间口径**：每个流入流出字段要 day/month 哪些版本？在字段名加后缀
7. **把映射结果写进《指标口径表》**：通用名 → 业务字段名，给用户确认

## 反向校验

映射完成后，用这个清单自检：
- [ ] 同一个通用名在所有代码里映射到同一个业务字段（一处定义，到处引用——`SUM_FIELDS` 模式）
- [ ] `metric_total` 和 `metric_part` 口径匹配（部分量是总量基数的一个子集）
- [ ] `inflow_field` 和 `outflow_field` 时间口径一致（别一个 day 一个 month）
- [ ] 复合 key 的拼接符不会出现在业务名里（用 `||` 而非 `-`，避免"上海-区"撞 key）
- [ ] 所有派生指标都有除零保护

## 新领域怎么扩展

如果业务不在上面四个领域里，按这个模板自己填一行：

```
| 通用字段 | <你的领域> |
|---------|----------|
| entity_l1 | ? |
| entity_l2 | ? |
| entity_l3 | ? |
| entity_id | ? |
| metric_total | ? |
| metric_part | ? |
| inflow_field | ? |
| outflow_field | ? |
| actual_field | ? |
| target_field | ? |
```

填完照着 `metric-dictionary.md` 的口径表模板写指标，代码骨架不用改。
