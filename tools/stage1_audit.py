#!/usr/bin/env python3
"""執行：核對既有卡片保留情形及十九本 PDF 的文字層、分頁與雜湊。

目錄：參數與來源核對（main）；卡片保留核對（audit_cards）。
此工具不提煉內容、不執行 OCR，也不把文字比對視為語義審核。
"""
import argparse
import json
import re
import subprocess
from pathlib import Path
from extract_pdf import inspect

FIELDS = ['核心概念', '使用規則', '操作步驟', '原文例子']

def sections(text):
    parts = re.split(r'^## (.+)\s*$', text, flags=re.M)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}

def audit_cards(root, baseline):
    folder = 'qi-zheng-si-yu/knowledge/'
    names = subprocess.check_output(['git', 'ls-tree', '-r', '-z', '--name-only', baseline, '--', folder], cwd=root).decode().strip('\0').split('\0')
    errors = []
    for name in names:
        p = root / name
        if not p.exists():
            errors.append({'檔案': name, '問題': '基準檔案遺失'})
            continue
        old = subprocess.check_output(['git', 'show', f'{baseline}:{name}'], cwd=root).decode()
        now = p.read_text()
        before = sections(old)
        after = sections(now)
        for field in FIELDS:
            if field not in before or field not in after or before[field] not in after[field]:
                errors.append({'檔案': name, '問題': f'原有欄位文字未完整保留：{field}'})
    files = list((root / folder).glob('*.md'))
    structural = []
    for p in files:
        text = p.read_text()
        fields = sections(text)
        problems = []
        if text.splitlines()[0] != '#七政四餘': problems.append('首行標籤錯誤')
        for field in FIELDS:
            if not fields.get(field): problems.append('欄位缺失或空白：' + field)
        if not re.search(r'《[^》]+》', text): problems.append('未偵測到書名')
        if not re.search(r'第\s*\d+[^\n]*頁', text): problems.append('未偵測到 PDF 頁碼')
        if problems: structural.append({'檔案': p.relative_to(root).as_posix(), '問題': problems})
    return {'基準提交': baseline, '基準卡片數': len(names), '目前卡片數': len(files),
            '原文保留問題數': len(errors), '原文保留問題': errors,
            '結構待核對卡片數': len(structural), '結構待核對卡片': structural,
            '限制': '僅檢查檔案結構及原文保留；未取代逐卡來源與語義複核。'}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', type=Path)
    ap.add_argument('--baseline', default='d241d349f8472d64ec40ae02977869b2f2a9d462')
    ap.add_argument('--report-dir', type=Path, required=True)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.report_dir.mkdir(parents=True, exist_ok=True)
    cards = audit_cards(root, args.baseline)
    (args.report_dir / '階段1-卡片保留與結構核對.json').write_text(json.dumps(cards, ensure_ascii=False) + '\n')
    print(json.dumps({k: cards[k] for k in ['基準卡片數', '目前卡片數', '原文保留問題數', '結構待核對卡片數']}, ensure_ascii=False), flush=True)
    if args.manifest:
        results = []
        for item in json.loads(args.manifest.read_text()):
            result = inspect(item['pdf'], item['text'])
            results.append(result)
            print(json.dumps({'檔名': result['檔名'], '頁數': result['PDF頁數'], '可沿用': result['既有文字可沿用']}, ensure_ascii=False), flush=True)
        report = {'書籍數': len(results), 'PDF總頁數': sum(x['PDF頁數'] for x in results),
                  '抽查頁數': sum(len(x['抽查頁']) for x in results),
                  '無文字層頁數': sum(len(x['無文字層頁碼']) for x in results),
                  '可沿用書籍數': sum(x['既有文字可沿用'] for x in results), '逐書結果': results}
        (args.report_dir / '階段1-十九本文字層與分頁核對.json').write_text(json.dumps(report, ensure_ascii=False) + '\n')

if __name__ == '__main__': main()
