# 报表导出模式（汇报型看板）

> **依赖与前置**
> - 前置：无（独立模块）
> - 被依赖：无
> - 可独立读。汇报型看板做导出功能时读这篇。

从演示项目沉淀。汇报型看板的核心交付方式之一：**把看板导出成一份可独立分发、离线可看的文件**。导出的报表往往要发群、发邮件、发给不在内网的人——所以导出物必须脱离运行环境也能看。

## 核心原则

1. **导出物必须静态化**：脱离依赖（脚本、CDN、后端接口）后仍能完整呈现
2. **图表不能导出成空 canvas**：canvas 离开页面就是空白，要转成图片内嵌
3. **导出物和在线版长一样**：所见即所得，否则用户不信任导出结果

## 静态快照导出（推荐做法）

导出当前页面 DOM 的快照，替换依赖为内嵌资源：

```javascript
function doExport() {
  var clone = document.documentElement.cloneNode(true);

  // 1. 图表 canvas → PNG base64 img（脱离 Chart.js 依赖）
  [['#salesChart', 'salesChart'], ['#refundChart', 'refundChart']].forEach(function (pair) {
    var node = clone.querySelector(pair[0]);
    var srcNode = document.getElementById(pair[1]);
    if (node && srcNode) {
      var img = clone.ownerDocument.createElement('img');
      img.src = srcNode.toDataURL('image/png');   // canvas 转 PNG
      img.style.cssText = 'width:100%;height:100%;object-fit:contain;';
      node.parentNode.replaceChild(img, node);
    }
  });

  // 2. 移除所有脚本（含 Chart.js CDN 和 init 逻辑）
  clone.querySelectorAll('script').forEach(function (s) { s.remove(); });

  // 3. 移除导出按钮（快照里按钮没意义）
  var btn = clone.querySelector('#btnExport');
  if (btn) btn.remove();

  // 4. 下载
  var html = '<!DOCTYPE html>\n' + clone.outerHTML;
  var blob = new Blob([html], { type: 'text/html;charset=utf-8' });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = '报表名-2026年7月.html';
  a.click();
  URL.revokeObjectURL(a.href);
}
```

## 导出内容取舍

| 内容 | 在线版 | 导出版 | 说明 |
|------|--------|--------|------|
| KPI 卡片 | DOM | DOM | 保留，无依赖 |
| 图表 | canvas（Chart.js） | PNG img | **必须转图** |
| 明细表 | DOM | DOM | 保留 |
| 导出按钮 | 有 | 移除 | 快照里没意义 |
| 内联脚本 | 有 | 移除 | 已静态化 |
| CSS | 外链 | 内联/保留 | 相对路径会 404，要内联 |

## 两种导出形态

- **HTML 快照**（上例）：保留 DOM 结构，可二次编辑，但需内联 CSS
- **PNG 长图**：整页截图，最通用（发微信/PPT），但不可编辑，超长页会被截断

需求是"发出去给别人看" → PNG 长图最省事；"别人可能要改/存" → HTML 快照。

## 导出时的踩坑

1. **canvas.toDataURL 必须在页面渲染完成后调用**，否则拿到空白图
2. **相对路径 CSS/图片 404**：导出的 HTML 独立打开时相对路径失效，CSS 要内联、logo 要转 base64
3. **中文文件名**：`a.download` 中文名在 Chrome 正常，个别老浏览器乱码（可用拼音/日期兜底）
4. **导出前等图表动画/异步完成**：Chart.js 有动画，导出太早图表是初始空帧
5. **JS 里拼接 `<script>`/`</script>` 字符串会提前闭合外层 script 标签**：导出函数里 `html.replace('<script src="data.js">', ...)` 这类字符串里的 `</script>` 会让浏览器把当前 `<script>` 标签提前截断，后面所有代码失效（页面白屏、按钮失灵）。字符串里的 `</script>` 必须写成 `<\/script>`（转义斜杠）

## 验收

- [ ] 导出文件**离线打开**（file://）内容完整、无报错
- [ ] 导出文件不含 script 标签、不含 CDN 依赖
- [ ] 导出文件的图表是 PNG 图（不是空 canvas）
- [ ] 导出文件名语义化（含日期/主题，不用"最终版"）
