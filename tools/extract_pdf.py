#!/usr/bin/env python3
"""執行：機械抽取 PDF 或核對既有文字；無文字層即停止，不執行 OCR。"""
import argparse, collections, hashlib, json, re, subprocess, sys
from pathlib import Path
import fitz

def normalized(text):
    return re.sub(r'\s+', '', text)

def inspect(pdf, existing=None):
    pdf = Path(pdf)
    with fitz.open(pdf) as document:
        count = len(document)
        no_text = [i + 1 for i, page in enumerate(document) if not page.get_text().strip()]
    samples = sorted({1, 1 + (count - 1) // 4, 1 + (count - 1) // 2,
                      1 + 3 * (count - 1) // 4, count})
    checks = []
    old = Path(existing).read_text().split('\f') if existing else None
    for page in samples:
        fresh = subprocess.check_output(['pdftotext', '-f', str(page), '-l', str(page),
                                         '-layout', str(pdf), '-']).decode('utf-8')
        matches = old is not None and page <= len(old) and normalized(fresh) == normalized(old[page - 1])
        checks.append({'PDF頁碼': page, '既有文字一致': matches,
                       '本頁文字SHA256': hashlib.sha256(fresh.encode()).hexdigest()})
    return {'檔名': pdf.name, 'PDF頁數': count,
            '檔案SHA256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
            '無文字層頁碼': no_text, '抽查頁': checks,
            '既有文字可沿用': bool(existing) and all(x['既有文字一致'] for x in checks) and not no_text}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--existing', type=Path, help='既有以換頁字元分頁的 pdftotext 文字')
    parser.add_argument('--output', type=Path, help='逐頁 JSONL；每筆保留 PDF 實際頁碼')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.pdf, args.existing)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    if result['無文字層頁碼']:
        print('停止：無文字層頁碼 ' + '、'.join(map(str, result['無文字層頁碼'])))
        return 2
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        raw = subprocess.check_output(['pdftotext', '-layout', str(args.pdf), '-']).decode().split('\f')
        with args.output.open('w') as stream:
            for i in range(result['PDF頁數']):
                stream.write(json.dumps({'PDF頁碼': i + 1, '文字': raw[i]}, ensure_ascii=False) + '\n')
    print(json.dumps(result, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    sys.exit(main())
