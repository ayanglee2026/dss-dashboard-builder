# 指标异常监控规则 + 对应策略（待办）模式

> **依赖与前置**
> - 前置：`domain-mapping.md`（字段骨架）、`metric-dictionary.md`（`deriveMetrics` 派生指标）
> - 被依赖：`tree-aggregation.md` 的"异常看板"段（规则命中记入树节点的 `anomalies[]`）
> - 可独立读，做"规则文件 + 树"形态时需配合 tree-aggregation。

通用模式：把业务规则从代码里"提"出来，集中声明式管理。适用于任何"按规则命中 → 生成待办 → 分级给策略"的监控型看板。核心链路：

```
规则定义 → 逐条打标签 → 优先级链定 actionType → 待办清单 → 分级策略 → 详情弹窗
```

## 1. 规则集中定义 + 逐条打标签

每条规则是一个布尔判定，命中就给数据打上标签。规则写在一个函数里集中管理，方便改：

```javascript
// 逐条规则，每条命中打一个标签（按你的业务口径填阈值和字段）
// 下面是三类常见异常模式的通用示例
var isOffTarget  = (actual > 0 && actual < target * 0.5);           // 达成严重不足
var isStagnant   = (status === 'pending' && pending_days > 29);      // 状态停滞过久
var isHighAttn   = (views > 100 && conversions < 2);                 // 高关注低转化
var isSilent     = (views < 4 && age_days > 14);                     // 长期无人关注
```

> 规则的语义由你的业务决定。上面四类是通用异常模式：未达目标 / 状态停滞 / 高关注低转化 / 长期沉默。

## 2. 优先级链 → actionType

一条数据可能同时命中多条规则（比如既停滞又沉默）。用**优先级链**取最高优先级的那个动作，避免待办重复：

```javascript
var actionType = isOffTarget ? 'off_target' : (isStagnant ? 'cleanup'
  : (isHighAttn ? 'investigate' : (isSilent ? 'promote' : null)));
```

优先级顺序写死在链里（按业务紧急度排），新增规则时插进链的对应位置。

## 3. ACTION_META：动作元数据

每个 actionType 的展示元数据集中定义，UI 和逻辑共用一份：

```javascript
var ACTION_META = {
  off_target:  { label: '目标跟进', icon: '🎯', tip: '达成率严重不足，需排查原因', strategies: null },
  investigate: { label: '转化排查', icon: '🔍', tip: '高关注但低转化，综合排查', strategies: STRATEGIES.investigate },
  promote:     { label: '激活推广', icon: '📢', tip: '长期无人关注，需主动激活', strategies: STRATEGIES.promote },
};
var ACTION_ORDER = ['off_target', 'cleanup', 'investigate', 'promote']; // 待办渲染顺序
```

## 4. STRATEGIES：策略库（通用 + 分级）

策略分"通用策略（所有分级）"和"分级专属策略"。分级策略让不同级别的实体用不同打法（分级维度由业务定，如 A/B/C 优先级、大/中/小客户）：

```javascript
var STRATEGIES = {
  investigate: {
    title: '转化排查策略',
    general: [  // 通用步骤
      { icon: '🔍', title: '原因调研', text: '了解同类对比，判断差距来源' },
      { icon: '🛠', title: '现场排查', text: '检查影响转化的具体环节' },
    ],
    grade: {   // 分级专属
      'A': [{ icon: '💰', title: '优化策略', text: 'A级：微调即可，保持优势' }],
      'B': [{ icon: '💰', title: '优化策略', text: 'B级：适度加力，提升竞争力' }],
      'C': [{ icon: '💰', title: '优化策略', text: 'C级：大幅调整，快速突破' }],
    }
  }
};
```

## 5. 待办清单渲染（分组 → 归类 → 计数）

```
按团队/分组维度分组 → 组内按 actionType 归类 → 计数 + 查看明细按钮
```

```javascript
function renderTodoList(items, groups) {
  if (!items.length) return '<div>无待办 🎉</div>';
  groups.forEach(function (g) {
    var groupItems = items.filter(d => d.group === g);
    if (!groupItems.length) return;
    // 渲染分组行：g + 数量 + 展开
    ACTION_ORDER.forEach(function (at) {
      var typeItems = groupItems.filter(d => d.actionType === at);
      if (!typeItems.length) return;
      // 渲染动作类型块：icon + label + count + 「查看明细及建议」按钮
    });
  });
}
```

- 空态要友好：「本期无异常行动项 🎉」
- 分组行可折叠，动作类型块点「查看明细及建议」打开详情弹窗

## 6. 明细弹窗：策略 + 分级联动

点「查看明细」弹窗内展示：该动作的通用策略 + 该实体分级的专属策略。点按需打开，不预渲染全部。

## 待办数据的持久化

待办是"规则算出来的"，不必单独存表。存一份 `todo_list`（由 actionType 命中的行组成）在快照里，跨设备一致即可。真正要存的是规则配置，不是待办结果。

## 另一种形态：规则文件（异常看板）

另一种实现：规则做成 JSON 文件，支持导入配置。字段：`{ rule_id, category, field, operator, threshold, unit, level, suggestion, strategy }`，遍历树节点用 `compare(v, operator, threshold)` 判断，命中记 `node.anomalies[]`。适合规则多变、需要非程序员改规则的场景。见 `tree-aggregation.md` 里的异常看板部分。
