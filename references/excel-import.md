# Excel / CSV 导入解析模式

> **依赖与前置**
> - 前置：`domain-mapping.md`（通用字段 → 业务字段映射）、`metric-dictionary.md`（直接字段定义）
> - 被依赖：`data-source-patterns.md`（Excel/CSV 是四种数据源之一）、`cloud-deploy.md`（SUM_FIELDS → 建表列名）
> - 可独立读，但 `SUM_FIELDS` 的取值要配合 metric-dictionary。

通用模式：**表头模糊匹配 → 字段映射 → 数据清洗 → 交叉校验 → 聚合**。适用于任何从 Excel/CSV 导入明细数据再聚合的场景。

## 流程

```
原始 Sheet → 数组化 → 表头归一化 → 列映射 → 逐行清洗 → 交叉校验 → 聚合树
```

## 1. 表头归一化 + 模糊匹配

Excel 表头常见坑：全角/半角括号、多余空格、`\n` 换行、中英文混用。用一个 `NORMALIZED_HEADER_MAP` 映射表 + `normalizeHeader` 清洗：

```javascript
function normalizeHeader(h) {
  return String(h || '')
    .replace(/[\s　]+/g, '')      // 去所有空格（含全角）
    .replace(/[（）()]/g, '')      // 去括号（全角/半角）
    .replace(/\n/g, '');           // 去换行
}
// 映射表：把业务表头归一化成通用字段名（按你的领域填，见 domain-mapping.md）
// NORMALIZED_HEADER_MAP = { '总量': 'metric_total', '部分量': 'metric_part', ... }
```

**表头缺失列必须报错**，不能静默跳过。报错要列全缺失项和实际找到的表头，方便用户定位：

```javascript
var missing = [];
for (var r = 0; r < required.length; r++) {
  if (!map.hasOwnProperty(required[r])) missing.push(required[r]);
}
if (missing.length > 0) {
  throw new Error('缺少必要列（共 ' + missing.length + ' 个）：\n  - ' + missing.join('\n  - ') +
    '\n\n找到的表头: ' + JSON.stringify(headers));
}
```

## 2. 数值字段集中定义（SUM_FIELDS 模式）

把"哪些是数值列"集中在一个数组里，解析、清洗、聚合、上传、建表全部引用它——**一个来源，到处一致**：

```javascript
// 按你的业务字段填，对应 metric-dictionary.md 里的直接字段
const SUM_FIELDS = ['metric_total', 'metric_part', 'inflow_field', 'outflow_field', /* ... */];
```

好处：改字段只改一处，前端解析、树聚合、后端上传、数据库建表不会漂移。**建表 SQL 的列名直接用 SUM_FIELDS 里的通用字段名**（见 `cloud-deploy.md` 的 MySQL 建表模板），数据链路从头到尾一套名字。

## 3. 逐行清洗规则

```javascript
// 数值字段标准化 + 转 Number，格式修正和失败都记 warning（不静默改数据）
if (SUM_FIELDS.indexOf(key) !== -1) {
  var rawStr = String(rawVal === undefined || rawVal === null ? '' : rawVal).trim();
  var cleaned = rawStr
    .replace(/,/g, '')        // 去千分位逗号："12,500" → "12500"
    .replace(/[　\s]/g, '');   // 去全角/空格："1 200" → "1200"
  if (cleaned !== rawStr) {
    warnings.push('第' + rowIdx + '行 ' + key + ' 格式修正："' + rawStr + '" → "' + cleaned + '"');
  }
  var num = Number(cleaned);
  if (isNaN(num)) {
    warnings.push('第' + rowIdx + '行 ' + key + ' 无法转为数字: "' + rawStr + '"，视为0');
    num = 0;
  }
  row[key] = num;
}
```

- 空行跳过（整行无有效数据）
- **格式修正也记 warning**（去逗号/去空格），不只是转 Number 失败——用户必须知道数据被改过
- 数字清洗失败记 warning 列表，解析完后展示给用户

## 4. 交叉校验（cross-validation）

聚合前先校验数据自洽性，这是**防止"数据悄悄错"的关键**。模式：**分项之和 = 合计字段**（适用所有领域）：

```javascript
// 通用校验：分项A + 分项B 应等于合计字段（误差容忍 0.01 防浮点）
// 例：流入 = 新增 + 回流；总流出 = 主动流出 + 被动流出
var calc = r.subfield_a + r.subfield_b;
if (Math.abs(calc - r.total_field) > 0.01) {
  mismatches.push({ key: key, entity: r.entity_l3,
    msg: '合计校验失败 字段=' + r.total_field + ' 分项之和=' + calc });
}
```

- 误差容忍用 `> 0.01` 而不是 `!==`，避免浮点
- 逐行 key 用**复合 key** 或唯一 ID（`entity_id`），避免重名实体串数据
- 校验结果 mismatchMap 按 key 建索引，供 UI 打警告图标

## 5. 解析后给用户验证摘要

解析完输出摘要：总叶子实体数、L1/L2 分组数、校验是否通过，让用户确认"解析对了"再往下走。
