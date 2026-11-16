#!/usr/bin/env python3
"""執行：逐段核對來源、四欄與重複候選；只新增卡片或追加引文，不重寫既有文字。

目錄：tw與norm（字形）；source_text與gate（來源閘門）；additions（追加）；main（批次與保留檢查）。
"""
import argparse, hashlib, json, re
from pathlib import Path
from opencc import OpenCC
CC = OpenCC('s2twp')
FIELDS = ['核心概念', '使用规则', '操作步骤', '原文例子']
HEADINGS = ['核心概念', '使用規則', '操作步驟', '原文例子']

def tw(s):
    protected = {'斗':'QZDOUPROTECT','丑':'QZCHOUPROTECT','干':'QZGANPROTECT',
                 '天后':'QZTIANHOUPROTECT','消息':'QZXIAOXIPROTECT',
                 '万象':'QZWANXIANGPROTECT','萬象':'QZTRADWANXIANGPROTECT'}
    for term, key in protected.items(): s = s.replace(term, key)
    s = CC.convert(s).replace('司檯', '司臺')
    for term, key in protected.items(): s = s.replace(key, "萬象" if term in ("万象", "萬象") else term)
    return s

def norm(s):
    return re.sub(r'[\s，。；：、！？“”「」『』（）()【】《》〈〉,.!?;:"\[\]—–-]', '', s)

def source_text(pages, first, last):
    return '\n'.join(line for page in pages[first-1:last] for line in page.splitlines()
                     if not line.strip().isdigit() and not line.strip().startswith(('如果有错漏','如果有内容有错漏')))

def gate(record, pages, unit="页"):
    errors = []
    m = re.search(r'《([^》]+)》第(\d+)(?:[—–-](\d+))?' + re.escape(unit), record.get('source', ''))
    if not m: return ['書名或來源定位無法解析']
    first, last = int(m[2]), int(m[3] or m[2])
    if not 1 <= first <= last <= len(pages): return ['來源定位越界']
    raw = norm(source_text(pages, first, last))
    for field in FIELDS:
        value = record.get('fields', {}).get(field, '').strip()
        if not value: errors.append('欄位空白：' + tw(field)); continue
        if value in ['原文未提及', '无', '無']: continue
        for part in re.split(r'\n\s*\n|\n(?=\d+\. )', value):
            part = re.sub(r'^\d+\.\s*', '', part.strip())
            if part in ['原文以图表呈现', '原文以圖表呈現']: continue
            if norm(part) not in raw: errors.append('原文未逐字對應：' + tw(field) + '／' + tw(part[:90]))
    return errors

def additions(record, original):
    source = tw(record['source'])
    result = original
    for i, field in enumerate(FIELDS):
        value = record['fields'][field].strip()
        if value in ['原文未提及','无','無']: continue
        value = tw(value)
        # 同一來源與引文已存在即不重複追加，不刪改原有資料。
        marker = f'\n\n{source}：\n\n{value}\n'
        if marker.strip() in result: continue
        heading = '## ' + HEADINGS[i]
        start = result.index(heading) + len(heading)
        end = result.find('\n## ', start)
        if end == -1: end = len(result)
        section = result[start:end]
        blocks = re.split(r'(?=^《[^》]+》第)', section, flags=re.M)
        if any(block.startswith(source + '：') and norm(value) in norm(block.split('：', 1)[1]) for block in blocks): continue
        result = result[:end].rstrip('\n') + marker + result[end:]
    return result

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('batch', type=Path); ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--apply', action='store_true'); ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--source-format', choices=['pdf-text', 'docx-paragraphs'], default='pdf-text')
    args = ap.parse_args()
    if args.source_format == 'docx-paragraphs':
        paragraphs = json.loads(args.source.read_text())
        assert [x['原始段落編號'] for x in paragraphs] == list(range(1, len(paragraphs)+1))
        pages = [x['文字'] for x in paragraphs]
    else: pages = args.source.read_text().split('\f')
    if pages[-1] == '': pages.pop()
    batch = json.loads(args.batch.read_text()); folder = args.root/'qi-zheng-si-yu/knowledge'
    rows = []; created = set(); updated = set(); before = {}
    signatures = {}
    for existing in folder.glob('*.md'):
        digest = hashlib.sha256(norm(existing.read_text()).encode()).hexdigest()
        signatures.setdefault(digest, existing.name)
    for record in batch:
        errors = gate(record, pages, "段" if args.source_format == "docx-paragraphs" else "页")
        name = tw(record['name']).translate(str.maketrans('/:\\*?"<>|','／：＼＊？＂＜＞｜'))
        path = folder/(name + '.md')
        original = path.read_text() if path.exists() else None
        status = '待人工核對' if errors else '來源與四欄通過'
        if not errors and args.apply:
            if original is None:
                original = '#七政四餘\n' + ''.join('\n## '+h+'\n\n'+('無' if i==3 else '原文未提及')+'\n' for i,h in enumerate(HEADINGS))
                pass  # 確認新卡不是完全同文後才登記新增。
            elif path.name not in created:
                before.setdefault(path, original); updated.add(path.name)
            result = additions(record, original)
            digest = hashlib.sha256(norm(result).encode()).hexdigest()
            # 異名同文可能是不同概念或圖表指標；僅報候選，不能自動折疊。
            # 概念辨義由逐節判讀處理；階段2才分群，任何刪卡仍須使用者確認。
            candidate = signatures.get(digest) if not path.exists() else None
            if candidate:
                status = '異名同文候選，保留不同卡名供後續辨義'
            if not path.exists(): created.add(path.name)
            signatures[digest] = path.name
            if result != original: path.write_text(result)
            elif path.exists(): status = '引文已存在，未重複追加'
        rows.append({'標題':name, '出處':tw(record['source']), '結果':status, '問題':errors})
    # 確認所有原有段落仍逐字存在；只允許在四欄末尾追加來源原句。
    preserved = 0
    for path, original in before.items():
        now = path.read_text()
        for oldpart in re.split(r'\n## ', original):
            if oldpart.strip() not in now: raise RuntimeError('原有內容被改寫：'+path.name)
        preserved += 1
    report = {'候選數':len(rows),'通過數':sum(not r['問題']for r in rows),
              '待核對數':sum(bool(r['問題'])for r in rows), '新增檔數':len(created),
              '追加既有檔數':len(updated), '既有內容保留檢查通過':preserved,'明細':rows}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k!='明細'},ensure_ascii=False))

if __name__ == '__main__': main()
