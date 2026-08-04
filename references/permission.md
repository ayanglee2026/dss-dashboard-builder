# 声明式权限框架（data-auth 模式）

> **依赖与前置**
> - 前置：无（独立模块，不依赖其他 reference）
> - 被依赖：无
> - 可独立读。做登录、权限、按钮显隐时读这篇。

从 DSS 权限模块沉淀。核心思路：**角色 + 权限点声明式配置，UI 按钮用 `data-auth` 属性自动控制显隐/禁用，逻辑只认配置文件不认业务代码。**

## 结构

```
auth-config.js（配置文件，只改这里）→ auth.js（通用逻辑，不动）
```

## 1. 配置文件（auth-config.js）

```javascript
window.AUTH_CONFIG = {
  keys: {
    admin: ['口令A', '口令B'],   // 管理员可多口令（不同人各一个，展示不同名字）
    whitelist: '口令C'           // 白名单单口令
  },
  operators: {
    '口令A': '张管理员',
    '口令B': '李管理员',
    whitelist: '维护人'
  },
  permissions: {                 // 权限矩阵：action → 允许的角色数组
    history:       ['admin', 'whitelist'],   // 查看历史
    importExcel:   ['admin', 'whitelist'],   // 导入Excel
    upload:        ['admin'],                // 上传到服务器
    exportAll:     ['admin'],                // 导出报表
  }
};
```

## 2. 通用逻辑（auth.js 核心）

```javascript
var Auth = (function () {
  function getRole() { /* 从 sessionStorage 读，游客返回 'guest' */ }
  function can(action) {
    var role = getRole();
    var perms = window.AUTH_CONFIG && window.AUTH_CONFIG.permissions;
    if (!perms || !perms[action]) return false;
    return perms[action].indexOf(role) !== -1;
  }
  function login(key) {
    var adminKeys = Array.isArray(keys.admin) ? keys.admin : [keys.admin];
    if (adminKeys.indexOf(key) !== -1) { role = 'admin'; operator = operators[key]; }
    else if (key === keys.whitelist)    { role = 'whitelist'; operator = operators.whitelist; }
    else return false;
    sessionStorage.setItem(KEY, JSON.stringify({ role: role, operator: operator,
      uploadKey: (role === 'admin') ? adminKeys[0] : '' }));
    applyPermissions(); renderBadge();
    return true;
  }
  return { getRole, can, login, logout, applyPermissions, renderLoginEntry };
})();
```

## 3. 按钮级控制（data-auth 声明式）

HTML 按钮加 `data-auth="action名"`，`applyPermissions()` 自动处理：

```html
<button data-auth="upload">上传到服务器</button>
<button data-auth="exportAll">导出报表</button>
```

- 有权限：显示，disabled 按钮恢复可用
- 无权限：`display:none`（比 disabled 更彻底，不暴露功能入口）
- 逻辑里再套 `Auth.can('xxx')` 做二次防护，防被 F12 调用函数

## 4. 登录 UI

- 游客：header 显示「登录」链接
- 已登录：显示角色徽章（颜色区分管理员/白名单）+ 操作人姓名 + 登出
- 登录弹窗：口令输入 → `login(key)` → 成功关闭 / 失败提示

## 5. 后端二次校验（重要）

前端口令明文，仅防君子（F12 可看源码）。**真正的安全靠后端**：

- 上传类接口要求 `authKey` 参数，后端校验 `authKey === 环境变量 UPLOAD_KEY`
- UPLOAD_KEY 存环境变量，不进代码、不进前端源码
- 前端只把 admin 的第一个口令当作 uploadKey 传给后端

## 6. 改权限只动配置文件

- 加角色口令：auth-config.js 的 keys + operators 各加一行
- 加权限点：permissions 加一行 + HTML 按钮加 `data-auth`
- 逻辑层 auth.js 永远不用改

## 安全说明

V1 权限模型 = 防误操作 + 防绕过 UI，不是防攻击者。要求更高时上 OAuth / JWT / 服务端 RBAC。
