# 数据访问层适配器（CloudSync 模式）

> **依赖与前置**
> - 前置：`data-source-patterns.md`（数据源选型，决定要不要后端）
> - 被依赖：`cloud-deploy.md`（部署时配合后端实现）
> - 可独立读，但"要不要后端"先看 data-source-patterns。

核心思路：**前端不直接碰后端 SDK，统一走一个 `CloudSync.callFunction(name, data)` 接口。换后端只改这一个文件，前端其他代码零改动。**

## 为什么

DSS 最初用 CloudBase 云函数，交接时公司要换成自建 API。因为所有业务代码都通过 `CloudSync.callFunction` 调后端，**换后端只重写了 cloudsync.js 一个文件**，其他 JS 全部不动。这是"数据访问层适配器"的价值。

## 统一接口

```javascript
CloudSync.init()                          // 初始化，返回 Promise
CloudSync.callFunction(name, data)        // 调后端函数/接口
CloudSync.isReady()                       // 是否可用
```

所有业务函数调用长这样（业务代码不关心后端是什么）：

```javascript
CloudSync.callFunction('uploadDailyData', {
  rows: rows, snapshot: snapshot, meta: meta,
  authKey: Auth.getUploadKey(), operator: Auth.getOperator()
}).then(function (res) { /* res.success ? ... */ });
```

## 前端适配器实现

### CloudBase 版

```javascript
var CloudSync = (function () {
  var app = null, ready = false;
  function init() {
    if (ready) return Promise.resolve();
    app = cloudbase.init({ env: ENV_ID, accessKey: ACCESS_KEY, region: 'ap-shanghai' });
    ready = true; return Promise.resolve();
  }
  function callFunction(name, data) {
    if (!ready) return Promise.reject(new Error('cloud not ready'));
    return app.callFunction({ name: name, data: data }).then(res => res.result);
  }
  return { init, callFunction, isReady: () => ready };
})();
```

### fetch 版（自建 API）

```javascript
var CloudSync = (function () {
  var BASE_URL = 'https://your-api-domain.com/api';  // ★ 改这里
  var ready = false;
  function init() { ready = true; return Promise.resolve(); }
  function callFunction(name, data) {
    if (!ready) return Promise.reject(new Error('not ready'));
    return fetch(BASE_URL + '/' + name, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data || {})
    }).then(function (res) {
      if (!res.ok) throw new Error('API ' + name + ' returned ' + res.status);
      return res.json();
    });
  }
  return { init, callFunction, isReady: () => ready };
})();
```

## 接口命名 = 后端函数名

`callFunction('loadReportByDate', { report_date })` → 后端 `POST /api/loadReportByDate`。**接口签名固定成契约**，前端和后端各按契约实现，可并行开发。

## 后端适配器实现

### MySQL 后端（Node + Express + mysql2）

公司常用 MySQL 做持久化。前端适配器**用上面的 fetch 版**（BASE_URL 指向 Node 服务），业务代码零改动；后端用 Node + Express + mysql2 连接池实现接口：

```javascript
// server/api.js —— Node + Express + mysql2 连接池
const express = require('express');
const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,   // 密钥走环境变量，不进代码
  database: process.env.DB_NAME,
  connectionLimit: 10,                 // 连接池必用，单连接会被并发打满
  waitForConnections: true,
});

const app = express();
app.use(express.json({ limit: '10mb' }));

// 后端接口名 = 前端 CloudSync.callFunction 的 name（契约一致）
app.post('/api/loadReportByDate', async (req, res) => {
  try {
    const { report_date } = req.body;
    const [rows] = await pool.query(
      'SELECT * FROM report_snapshot WHERE report_date = ? ORDER BY entity_l1, entity_l2',
      [report_date]
    );
    res.json({ success: true, rows });      // 统一返回 { success, ... }
  } catch (err) {
    // 业务错误用 { success: false, reason }，不抛 HTTP 5xx
    res.json({ success: false, reason: String(err.message) });
  }
});

app.listen(process.env.PORT || 3000);
```

要点：
- **连接池必用**：`createPool` 而非单连接，并发查询不会打满
- **接口名 = name**：`/api/{name}` 和前端 `callFunction(name)` 一一对应，可并行开发
- **统一返回格式**：`{ success: true, ... }` / `{ success: false, reason }`，前端只认 success 不认 HTTP 状态码
- **SQL 用参数化查询**（`?` 占位符），不要字符串拼接——防 SQL 注入
- **密钥走环境变量**（`DB_PASSWORD` 等），`.env` 不进 git
- **表名列名用 SUM_FIELDS 的通用名**（见 `excel-import.md`），前端解析、树聚合、建表一处定义不漂移

## 关键约定

1. **统一返回格式**：`{ success: boolean, ... }`，错误用 `{ success: false, reason: 'xxx' }`，不抛 HTTP 5xx
2. **ready 门禁**：`callFunction` 在 init 前调用直接 reject，避免静默失败
3. **window.__cloudReady 标志**：页面等 init 完成后才渲染数据
4. **别在业务代码里 new fetch()**：任何后端起变化，业务代码全部要改

## 适用场景

- 后端可替换（云函数 → 自建服务器 → MySQL → 别人的接口）
- 前端先开发，后端并行开发（先用 mock 版适配器）
- 多模块共用同一后端（日报 + 库存 + 日历，都走 CloudSync）
