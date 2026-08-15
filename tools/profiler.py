#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据画像生成器（dss-dashboard-builder 工具 #1）

把阶段 1/3 的数据画像从「每次现场手写脚本」变成一条命令。
读 Excel/CSV → 自动输出字段画像 + 异常清单 + 待确认项。

用法：
    python3 profiler.py <文件路径>
    python3 profiler.py <文件路径> --output 画像报告.md

依赖：openpyxl（读 .xlsx），csv 标准库（读 .csv）。不强制 pandas。

设计原则：
    - 纯机械画像，不硬编码任何业务字段名
    - 语义判断（业务含义 / 明细还是聚合 / 单位）不猜，列为「待确认」交给 AI 问用户
    - 对齐 references/data-profiling.md 的检查清单
"""
import sys
import csv
import re
import argparse
import datetime
from collections import Counter

# 脏值占位（当成了真数据的占位符）
DIRTY = {'', '-', '--', 'NULL', '(null)', 'None', 'nan', 'NA', 'N/A', 'null', '—'}

# 超大值判据：值 > 中位数 × 10（data-profiling.md 约定）
OUTLIER_RATIO = 10.0
# 0 占比异常高阈值
ZERO_RATIO = 0.30
# 主键候选判据：唯一值数 > 行数 × 此比例 且 < 行数（有少量重复）
KEY_RATIO = 0.90


def is_dirty(v):
    """判断是否脏值占位"""
    if v is None:
        return True
    if isinstance(v, str) and v.strip() in DIRTY:
        return True
    return False


def read_file(path):
    """按扩展名读文件，返回 (header, rows)"""
    if path.lower().endswith('.csv'):
        return _read_csv(path)
    return _read_excel(path)


def _read_csv(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    header = [h.strip() for h in rows[0]]
    return header, rows[1:]


def _read_excel(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    header = [str(h).strip() if h is not None else '' for h in rows[0]]
    return header, rows[1:]


def to_num(v):
    """转数字，失败返回 None"""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.strip().replace(',', '').replace('，', ''))
        except (ValueError, AttributeError):
            return None
    return None


def _str_is_date(s):
    return bool(re.match(r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}', s.strip()))


def classify(vals):
    """判断列类型：数字 / 日期 / 文本 / 空列"""
    nums = dates = texts = nonnull = 0
    for v in vals:
        if is_dirty(v):
            continue
        nonnull += 1
        if isinstance(v, bool):
            texts += 1
        elif isinstance(v, (int, float)):
            nums += 1
        elif isinstance(v, (datetime.datetime, datetime.date, datetime.time)):
            dates += 1
        elif isinstance(v, str):
            s = v.strip()
            if to_num(v) is not None:
                nums += 1
            elif _str_is_date(s):
                dates += 1
            else:
                texts += 1
        else:
            texts += 1
    if nonnull == 0:
        return '空列'
    total = nonnull
    if nums / total >= 0.6:
        return '数字'
    if dates / total >= 0.6:
        return '日期'
    return '文本'


def _sample(vals):
    """取第一个非空样例，截断"""
    for v in vals:
        if not is_dirty(v):
            s = str(v).strip()
            return s[:20] + ('…' if len(s) > 20 else '')
    return ''


def profile_column(name, vals, nrows):
    """单列画像，返回 dict"""
    nonnull = [v for v in vals if not is_dirty(v)]
    coltype = classify(vals)
    nonnull_rate = len(nonnull) / max(nrows, 1) * 100
    uniq = len(set(str(v) for v in nonnull))
    sample = _sample(vals)
    anomalies = []

    info = {
        'name': name, 'type': coltype, 'rate': nonnull_rate,
        'uniq': uniq, 'sample': sample, 'anomalies': anomalies,
        'nums': [], 'nonnull': nonnull,
    }

    if coltype == '空列':
        anomalies.append('空列')
        return info

    # 数字列：数值类异常
    nums = [to_num(v) for v in nonnull]
    nums = [n for n in nums if n is not None]
    info['nums'] = nums
    if coltype == '数字' and nums:
        # 负数
        neg = sum(1 for n in nums if n < 0)
        if neg > 0:
            anomalies.append('负数 %d' % neg)
        # 整列全 0
        if all(n == 0 for n in nums):
            anomalies.append('整列全0')
        # 0 占比异常高
        zero = sum(1 for n in nums if n == 0) / len(nums)
        if zero > ZERO_RATIO and not all(n == 0 for n in nums):
            anomalies.append('0占比%.0f%%' % (zero * 100))
        # 超大值：> 中位数 × 10（中位数为 0 时判据失效，跳过）
        med = _median(nums)
        if med > 0:
            outliers = [n for n in nums if n > med * OUTLIER_RATIO]
            if outliers:
                anomalies.append('超大值 %d(最大%.0f)' % (len(outliers), max(outliers)))
        # 格式不一致：数字列里混入文本（非空但转不成数字）
        mixed = len(nonnull) - len(nums)
        if mixed > 0:
            anomalies.append('混文本 %d' % mixed)

    # 主键候选：唯一值接近行数但有少量重复
    if coltype in ('文本', '数字') and nonnull:
        if uniq >= nrows * KEY_RATIO and uniq < nrows:
            anomalies.append('重复key %d' % (nrows - uniq))

    # 脏值占位
    dirty_cnt = nrows - len(nonnull)
    if dirty_cnt > 0:
        anomalies.append('脏值 %d' % dirty_cnt)

    return info


def _median(nums):
    s = sorted(nums)
    m = len(s) // 2
    return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2


def render(header, rows):
    nrows = len(rows)
    ncols = len(header)
    lines = []
    lines.append('# 数据画像报告\n')
    lines.append('## 概览\n')
    lines.append('- 数据行数（不含表头）：%d' % nrows)
    lines.append('- 字段数：%d' % ncols)
    lines.append('- 表头：第 1 行\n')

    # 逐列画像
    infos = []
    for i, h in enumerate(header):
        col = [row[i] if i < len(row) else None for row in rows]
        infos.append(profile_column(h, col, nrows))

    lines.append('## 字段画像表\n')
    lines.append('| # | 字段 | 类型 | 非空率 | 唯一值 | 样例 | 异常 |')
    lines.append('|---|------|------|--------|--------|------|------|')
    for i, info in enumerate(infos):
        anom = '、'.join(info['anomalies']) if info['anomalies'] else '-'
        lines.append('| %d | %s | %s | %.0f%% | %s | %s | %s |'
                     % (i + 1, info['name'], info['type'], info['rate'],
                        info['uniq'], info['sample'], anom))

    # 异常清单
    lines.append('\n## 异常清单\n')
    found = False
    for info in infos:
        for a in info['anomalies']:
            if a in ('负数', '整列全0') or a.startswith('超大值') or a.startswith('0占比'):
                found = True
                break
    # 负数
    lines.append('### 负数')
    neg_list = [i for i in infos if any(a.startswith('负数') for a in i['anomalies'])]
    if neg_list:
        for i in neg_list:
            lines.append('- `%s`：%s 个负值' % (i['name'], next(a for a in i['anomalies'] if a.startswith('负数')).split()[-1]))
    else:
        lines.append('- 无')
    # 超大值
    lines.append('\n### 超大值（> 中位数 × %d）' % OUTLIER_RATIO)
    out_list = [i for i in infos if any(a.startswith('超大值') for a in i['anomalies'])]
    if out_list:
        for i in out_list:
            a = next(a for a in i['anomalies'] if a.startswith('超大值'))
            lines.append('- `%s`：%s' % (i['name'], a))
        lines.append('- ⚠️ 中位数×10 会误报「大楼栋/大门店」这类正常的大值，判据须结合业务上限确认')
    else:
        lines.append('- 无')
    # 整列全 0
    lines.append('\n### 整列全 0')
    zero_list = [i for i in infos if '整列全0' in i['anomalies']]
    if zero_list:
        for i in zero_list:
            lines.append('- `%s`：整列全 0，须问用户「本期无此业务」还是「字段已废弃」' % i['name'])
    else:
        lines.append('- 无')
    # 重复 key
    lines.append('\n### 重复 key（唯一值接近行数但有少量重复）')
    dup_list = [i for i in infos if any(a.startswith('重复key') for a in i['anomalies'])]
    if dup_list:
        for i in dup_list:
            lines.append('- `%s`：%s，可能是一单多间/续签，确认是否主键' % (i['name'], next(a for a in i['anomalies'] if a.startswith('重复key'))))
    else:
        lines.append('- 无')
    # 格式不一致
    lines.append('\n### 格式不一致（数字列混入文本）')
    mix_list = [i for i in infos if any(a.startswith('混文本') for a in i['anomalies'])]
    if mix_list:
        for i in mix_list:
            lines.append('- `%s`：%s' % (i['name'], next(a for a in i['anomalies'] if a.startswith('混文本'))))
    else:
        lines.append('- 无')
    # 脏值占位
    lines.append('\n### 脏值占位')
    dirty_list = [i for i in infos if any(a.startswith('脏值') for a in i['anomalies'])]
    if dirty_list:
        for i in dirty_list:
            lines.append('- `%s`：%s（- / NULL / 空）' % (i['name'], next(a for a in i['anomalies'] if a.startswith('脏值'))))
    else:
        lines.append('- 无')

    # 待确认项
    lines.append('\n## 待确认项（语义层面，工具不猜，问用户）\n')
    lines.append('- 哪些字段是**维度**（分组/筛选）、**度量**（统计）、**日期**？')
    lines.append('- 数据是**明细级**还是已经聚合过？（聚合过的数据再聚合会失真）')
    lines.append('- 各度量字段的**单位**？（元/万元/套/人/天）')
    lines.append('- **主键**是哪个字段？（唯一值接近行数的字段是候选）')

    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description='数据画像生成器')
    ap.add_argument('file', help='Excel/CSV 文件路径')
    ap.add_argument('--output', '-o', help='报告输出文件（默认打印到 stdout）')
    args = ap.parse_args(argv)

    try:
        header, rows = read_file(args.file)
    except Exception as e:
        print('读取失败：%s' % e, file=sys.stderr)
        return 1

    report = render(header, rows)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print('已写入 %s' % args.output)
    else:
        print(report)
    return 0


if __name__ == '__main__':
    sys.exit(main())
