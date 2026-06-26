# -*- coding: utf-8 -*-
"""
从 nations/ 与 players/ 各国档案的 frontmatter + 面板表，派生聚合视图。
单一真相源 = 各国档案；本脚本只读不写源文件，输出到 _generated/。
用法：  python scripts/gen_nations_table.py
"""
import os, re, glob, io, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTRS = ['行政治理','经济基础','军事能力','社会整合','科研潜力','对外影响力','技术体系能力']
ABBR  = ['行','经','军','社','研','外','技']
PRED  = ('前身存档','已被取代','已被吞并')  # 归档/前身，不计入活跃聚合表


def frontmatter(text):
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.S)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                fm[k.strip()] = v.strip()
    return fm


def panel(text):
    vals = {}
    for a in ATTRS:
        m = re.search(r'\|\s*' + a + r'\s*\|\s*([^|]*?)\s*\|', text)
        cell = (m.group(1) if m else '').strip()
        num = re.search(r'\d+', cell)
        vals[a] = num.group(0) if num else (cell[:2] or '?')
    return vals


def tier(text):
    # 找含“技术等级”的行，取其中的 T<数字>（含范围）
    for line in text.splitlines():
        if '技术等级' in line and 'T' in line:
            seg = re.sub(r'T0\s*[–\-—~]\s*T?9', '', line)  # 去掉标签 “T0–T9”
            for sep in ('：', ':'):                          # 取冒号后的实际取值
                if sep in seg:
                    seg = seg.split(sep, 1)[1]
                    break
            r = re.findall(r'T\s*\d(?:\s*[–\-—→/~]\s*T?\d)?', seg)
            if r:
                return re.sub(r'\s+', '', r[0])
    return '?'


def collect():
    rows = []
    files = glob.glob(os.path.join(ROOT, 'nations', '*.md')) + \
            glob.glob(os.path.join(ROOT, 'players', '*.md'))
    for f in sorted(files):
        name = os.path.splitext(os.path.basename(f))[0]
        if name == '_template':
            continue
        text = open(f, encoding='utf-8').read()
        fm = frontmatter(text)
        typ = fm.get('类型', '')
        rows.append({
            'file': os.path.relpath(f, ROOT).replace('\\', '/'),
            'name': fm.get('国名', name),
            'type': typ,
            'status': fm.get('状态', ''),
            'cont': fm.get('所属大陆', fm.get('区域', '')),
            'tier': tier(text),
            'panel': panel(text),
            'pred': any(p in typ for p in PRED),
            'player': '玩家国' in typ,
            'hive': name.startswith('蜂巢帝国-') or name == '蜂巢帝国',
        })
    return rows


def fmt_table(rows):
    out = ['| 国家 | 类型 | 状态 | 技术 | ' + ' | '.join(ABBR) + ' | 区域 |',
           '|---|---|---|---|' + '---|' * 7 + '---|']
    def clean(s):
        return re.split(r'[（(]', s or '', maxsplit=1)[0].strip()
    for r in rows:
        p = r['panel']
        typ = ('前身' if r['pred'] else
               '玩家' if r['player'] else
               'NPC' if 'NPC' in r['type'] else clean(r['type']))
        out.append('| {n} | {t} | {s} | {ti} | {pp} | {c} |'.format(
            n=clean(r['name']), t=typ, s=clean(r['status']), ti=r['tier'],
            pp=' | '.join(p[a] for a in ATTRS), c=clean(r['cont'])[:14]))
    return '\n'.join(out)


def main():
    rows = collect()
    active = [r for r in rows if not r['pred']]
    pred   = [r for r in rows if r['pred']]
    hive   = [r for r in active if r['hive']]
    main_  = [r for r in active if not r['hive']]
    # 主表按技术等级降序、玩家优先
    def key(r):
        tm = re.search(r'\d', r['tier'])
        return (-(int(tm.group(0)) if tm else 0), 0 if r['player'] else 1, r['name'])
    main_.sort(key=key)

    buf = io.StringIO()
    w = buf.write
    w('# 国家面板聚合表（自动生成 · 勿手改）\n\n')
    w('> 由 `scripts/gen_nations_table.py` 从各国档案的面板表派生。**单一真相源 = `nations/`、`players/` 各档案**；\n')
    w('> 改数值请改各国档案后重跑脚本。本文件是“派生视图”，不是真相源。\n')
    w('> 词条简称：行=行政治理 经=经济基础 军=军事能力 社=社会整合 研=科研潜力 外=对外影响力 技=技术体系能力。\n\n')
    w('## 主权国家 / 势力（活跃，{} 个）\n\n'.format(len(main_)))
    w(fmt_table(main_) + '\n\n')
    w('## 蜂巢联盟（{} 个）\n\n'.format(len(hive)))
    w(fmt_table(hive) + '\n\n')
    if pred:
        w('## 前身存档 / 已被取代（{} 个，仅供溯源）\n\n'.format(len(pred)))
        w(fmt_table(pred) + '\n')

    out_path = os.path.join(ROOT, '_generated', 'nations-table.auto.md')
    open(out_path, 'w', encoding='utf-8').write(buf.getvalue())
    print('OK ->', os.path.relpath(out_path, ROOT), '| active=%d hive=%d pred=%d' %
          (len(main_), len(hive), len(pred)))


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    main()
