# -*- coding: utf-8 -*-
"""
瑟斯芬尼亚推演 · 标准掷骰器（可复算 2d6）。

同一「种子」永远产出同一结果——GM 掷骰后，任何人跑同一条命令即可独立复验，
杜绝作弊。种子约定：R{年}-{国家}-{行动}（纯英文/数字、逐行动唯一、掷前定死）。

用法：
  python scripts/roll.py R1900-Bolwenkira-Arlinheim
  python scripts/roll.py R1900-Bolwenkira-Arlinheim --mod 4 --dc 12
  python scripts/roll.py R1900-Bolwenkira-Arlinheim --mod 4 --dc 12 --log

规则（同 rules/resolution-rules.md 六）：
  裸 12（双6）= 大成功；裸 2（双1）= 大失败（恒定，压过数值比较）。
  --mod = 相关词条值（加到 2d6）；--dc = 难度目标（2d6+mod ≥ dc → 成功）。
  --log = 追加一行到 rolls/rolls.log（留痕，可选带路径）。

注：随机源 = Python 标准库 random.Random(种子)，字符串种子经 sha512 稳定映射，
    Python 3.2+ 跨版本/跨平台一致。请勿改用 PowerShell Get-Random（算法不同、不可复验）。
"""
import argparse
import datetime
import os
import random
import sys

# 避免 Windows 控制台默认编码（cp1252/gbk）遇中文报错
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LOG = os.path.join(ROOT, 'rolls', 'rolls.log')


def roll_2d6(seed):
    """从固定种子产出可复算的 2d6，返回 (a, b)。"""
    r = random.Random(seed)
    return r.randint(1, 6), r.randint(1, 6)


def adjudicate(seed, mod=None, dc=None):
    """掷 2d6 并（可选）比对难度，返回结果字典。"""
    a, b = roll_2d6(seed)
    raw = a + b
    nat12 = (a == 6 and b == 6)
    nat2 = (a == 1 and b == 1)
    o = {'seed': seed, 'dice': (a, b), 'raw': raw,
         'nat12': nat12, 'nat2': nat2, 'mod': mod, 'dc': dc}
    if mod is not None:
        o['sum'] = raw + mod
    # 裸 12/裸 2 恒定压过数值比较
    if nat12:
        o['result'] = '大成功（裸12）'
    elif nat2:
        o['result'] = '大失败（裸2）'
    elif mod is not None and dc is not None:
        o['result'] = '成功' if raw + mod >= dc else '失败'
    return o


def format_line(o):
    s = f"[{o['seed']}]  2d6 = {o['dice'][0]}+{o['dice'][1]} = {o['raw']}"
    if o.get('mod') is not None:
        s += f"  (+词条{o['mod']} = {o['sum']})"
    if o.get('dc') is not None:
        s += f"  vs 难度{o['dc']}"
    if 'result' in o:
        s += f"  ->  {o['result']}"
    return s


def main(argv=None):
    p = argparse.ArgumentParser(description='瑟斯芬尼亚可复算 2d6 掷骰器')
    p.add_argument('seed', help='固定种子/行动标签，如 R1900-Bolwenkira-Arlinheim')
    p.add_argument('--mod', type=int, default=None, help='相关词条值（加到 2d6）')
    p.add_argument('--dc', type=int, default=None, help='难度目标（2d6+mod ≥ dc → 成功）')
    p.add_argument('--log', nargs='?', const=DEFAULT_LOG, default=None,
                   help='追加记录到掷骰日志（默认 rolls/rolls.log）')
    args = p.parse_args(argv)

    o = adjudicate(args.seed, args.mod, args.dc)
    line = format_line(o)
    print(line)

    if args.log:
        os.makedirs(os.path.dirname(args.log), exist_ok=True)
        ts = datetime.datetime.now().isoformat(timespec='seconds')
        with open(args.log, 'a', encoding='utf-8') as f:
            f.write(f"{ts}  {line}\n")
        print(f"（已记入 {os.path.relpath(args.log, ROOT)}）")


if __name__ == '__main__':
    main()
