#!/usr/bin/env python3
"""執行：按Word本文XML順序輸出原始段落（含表格及空段），不虛構PDF頁碼。"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


def extract(path):
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(path) as source:
        doc = ET.fromstring(source.read('word/document.xml'))
    rows = []
    for i, para in enumerate(doc.find('w:body', ns).iter('{'+ns['w']+'}p'), 1):
        style = para.find('w:pPr/w:pStyle', ns)
        rows.append({'原始段落編號': i, '樣式': style.get('{'+ns['w']+'}val') if style is not None else None,
                     '文字': ''.join(t.text or '' for t in para.findall('.//w:t', ns))})
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('docx', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    args = ap.parse_args()
    rows = extract(args.docx)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, ensure_ascii=False)+'\n')
    report = {'檔名': args.docx.name, 'SHA256': hashlib.sha256(args.docx.read_bytes()).hexdigest(),
              '原始段落數': len(rows), '空段落數': sum(not x['文字'].strip() for x in rows),
              '文字字數': sum(len(x['文字']) for x in rows),
              '定位方式': '依word/document.xml本文中w:p的文件順序，自1起算，包含表格儲存格及空段落；引用時加節題。',
              '依據': '使用者2026-11-16明確同意使用節題＋原始段落編號。'}
    args.report.write_text(json.dumps(report, ensure_ascii=False)+'\n')
    print(json.dumps(report, ensure_ascii=False))

if __name__ == '__main__':
    main()
