#!/usr/bin/env python3
"""執行：批次核對已發布卡片文字保留、四欄及已授權來源定位；不提煉內容。"""
import argparse
import json
from pathlib import Path
import re
import subprocess
from stage1_audit import sections, FIELDS


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--report', type=Path, required=True)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    raw = subprocess.check_output(['git', 'ls-tree', '-r', '-z', args.baseline, '--', 'qi-zheng-si-yu/knowledge'], cwd=root)
    entries = [x for x in raw.split(b'\0') if x]
    info = [(x.split(b'\t', 1)[0].split()[2].decode(), x.split(b'\t', 1)[1].decode()) for x in entries]
    proc = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    errors = []
    for oid, name in info:
        proc.stdin.write((oid+'\n').encode())
        proc.stdin.flush()
        header = proc.stdout.readline()
        size = int(header.split()[-1])
        old = proc.stdout.read(size).decode()
        proc.stdout.read(1)
        path = root/name
        if not path.exists():
            errors.append({'檔案': name, '問題': '既有檔案遺失'})
            continue
        before, after = sections(old), sections(path.read_text())
        for field in FIELDS:
            if field not in after or before[field] not in after[field]:
                errors.append({'檔案': name, '問題': '原有欄位改寫：'+field})
    proc.stdin.close()
    proc.wait()
    structural = []
    files = list((root/'qi-zheng-si-yu/knowledge').glob('*.md'))
    for path in files:
        text = path.read_text()
        fields = sections(text)
        problems = []
        if text.splitlines()[0] != '#七政四餘': problems.append('首行標籤錯誤')
        for field in FIELDS:
            if not fields.get(field): problems.append('欄位缺失或空白：'+field)
        if not re.search(r'《[^》]+》', text): problems.append('缺書名')
        pdf = re.search(r'第\s*\d+[^\n]*頁', text)
        word = re.search(r'《楊國正七政四餘彙編》第\d+(?:[—–-]\d+)?段', text)
        if not pdf and not word: problems.append('缺PDF頁碼或已授權Word段落定位')
        if problems: structural.append({'檔案': path.name, '問題': problems})
    report = {'基準提交': args.baseline, '既有卡片數': len(info), '目前卡片數': len(files),
              '原文保留問題數': len(errors), '原文保留問題': errors,
              '結構問題數': len(structural), '結構問題': structural,
              '限制': '只驗證文字保留及結構，不替代全量原書語義核對。'}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False)+'\n')
    print(json.dumps({k: v for k, v in report.items() if not isinstance(v, list)}, ensure_ascii=False))
    return 1 if errors or structural else 0

if __name__ == '__main__':
    raise SystemExit(main())
