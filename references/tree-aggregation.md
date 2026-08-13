# 树形聚合 / 多维钻取模式

> **依赖与前置**
> - 前置：`metric-dictionary.md`（`deriveMetrics` 定义于该文）、`excel-import.md`（`SUM_FIELDS` 定义于该文）
> - 被依赖：`anomaly-todo.md` 的"异常看板"段调用本文的 `buildAggregatedTree`
> - 可独立读，但派生指标 / 数值字段需配合上述两篇，缺了会拼接错。

通用模式：**明细行如何聚合成可钻取的树，且聚合值准确。** 适用于任何"按层级聚合 + 多视角钻取"的看板。

## 核心原则

1. **聚合 key 必须唯一**：同名叶子实体跨层级会撞 key。用唯一 ID（`entity_id`）优先，回退到 `entity_l1 || entity_l2 || entity_l3` 复合 key
2. **父节点 = 子节点求和**：聚合后必须校验 sum 一致性，校验不过就报警，防止静默丢数据
3. **直接字段求和，派生指标后算**：`SUM_FIELDS` 累加，占比/率这类派生指标在节点上重新算（不能把率加起来）

> 实体层级 `entity_l1/l2/l3` 怎么对应你的业务字段，见 `domain-mapping.md`。

## 通用流程

```
明细行 → Step1 按叶子实体聚合（复合key去重） → Step2 按 L1 分组 → Step3 按 L2 分组 → 建树
```

```javascript
function buildAggregatedTree(rows, dims) {
  var l1Key = dims[0], l2Key = dims[1], l3Key = dims[2];

  // Step 1: 明细行 Roll up 到叶子级（复合 key 防串）
  var entityMap = {};
  rows.forEach(function (row) {
    var l1 = row[l1Key] || '', l2 = row[l2Key] || '', leafName = row[l3Key];
    if (!leafName) return;
    var key = row.entity_id || (l1 + '||' + l2 + '||' + leafName);
    if (!entityMap[key]) {
      entityMap[key] = { leaf: leafName, entity_id: row.entity_id || '', _count: 0 };
      SUM_FIELDS.forEach(f => entityMap[key][f] = 0);
    }
    var ln = entityMap[key];
    SUM_FIELDS.forEach(f => ln[f] += row[f]);   // SUM_FIELDS 定义见 excel-import.md
    ln._count++;
  });

  // Step 2+3: 按 L1 → L2 分组建树（叶子 → L2 节点 → L1 节点）
  // createAggregateNode: SUM_FIELDS 全求和 + deriveMetrics
  // createLeafNode: 单独一行叶子实体，显示名去重
}
```

## 聚合节点创建（两层复用）

```javascript
function createLeafNode(src, level, path) {
  var node = { name: displayName, level: level, path: path.slice(), children: [], _leafCount: src._count || 1 };
  SUM_FIELDS.forEach(f => node[f] = src[f] || 0);
  deriveMetrics(node);   // 派生指标在叶子节点就算一次。deriveMetrics 定义见 metric-dictionary.md
  return node;
}
function createAggregateNode(children, name, level, path) {
  var node = { name: name, level: level, path: path.slice(), children: children, _leafCount: 0 };
  SUM_FIELDS.forEach(f => node[f] = 0);
  children.forEach(function (child) {
    SUM_FIELDS.forEach(f => node[f] += child[f]);
    node._leafCount += child._leafCount || 1;
  });
  deriveMetrics(node);   // 聚合节点重新派生（率类指标按本层总数算）。deriveMetrics 定义见 metric-dictionary.md
  return node;
}
```

叶子层派生一次 + 聚合层各自派生 = 每个节点都有完整指标，UI 渲染不用递归算。

## 多视角切换

同一份 rows，用**不同的 dims** 生成不同视角的树，切换时重新渲染：

```javascript
// dims = [L1字段, L2字段, L3字段]，按你的业务字段填
const VIEW_A_DIMS = ['entity_l1', 'entity_l2', 'entity_l3'];   // 视角A（如组织视角）
const VIEW_B_DIMS = ['dim_b_l1', 'dim_b_l2', 'dim_b_l3'];     // 视角B（如地理视角）
```

切换视角 = 换 dims 重建树。关键：**两个视角的叶子实体总数必须一致**，不一致说明聚合 key 有问题。

**切换视角要同步刷新筛选器**（真实踩坑）：换 dims 重建树后，三级筛选器的维度变了（组织视角是「经营组→店长→楼栋」，村视角是「项目→小区→楼栋」），筛选器必须一起重建并重置选中值，否则停在旧维度、筛错数据。切视角的完整动作 = 重建树 + 重建筛选器 + 重渲染。

## 节点 path 的妙用

每个节点带 `path: [l1, l2, l3]`，一路传递。钻取/筛选时直接用 path 匹配：
- 按 L1 筛选：`path[0] === filter.l1`
- 按 L2 筛选：`path[1] === filter.l2`
- 展开/收起：`hideDescendants(path)` / `showDirectChildren(path)` 精确操作该分支

## 校验：树 sum 一致性

```javascript
function validateTreeSums(tree) {
  // 对每个父节点：children 各 SUM_FIELDS 之和 === 父节点值
  // 误差容忍 0.01，不一致则报警
}
```

## 异常看板（树 + 规则联动）

树节点带 `anomalies[]` 数组（规则命中结果），可向上汇总、按规则/实体聚合：

- `walkTree(tree, fn)`：遍历整树
- `collectAnomalyNodes(tree)`：收集所有带异常的节点，按层级排序（L1 > L2 > 叶子）
- `buildAnomalyTree(nodes)`：按 规则类别 → 规则ID → 实体 三层重组，供看板渲染
- `filterAnomalyNodes(nodes, filter)`：用 path 过滤
