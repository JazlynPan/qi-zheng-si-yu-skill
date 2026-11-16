#!/usr/bin/env python3
"""執行：唯讀檢查現有卡片，產生階段2前置暫定報告。

目錄：正規化；來源與欄位解析；全庫統計；報告輸出；命令入口。
只寫 docs/階段2前置/；不改卡、不刪卡、不產生正式索引、不判定語義衝突。
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata

FIELDS = ('核心概念', '使用規則', '操作步驟', '原文例子')
# 僅作文字候選比對；不把財／才等可能有不同詞義的字一律合併。
PAIRS = (('余', '餘'), ('閑', '閒'))
CITE = re.compile(r'《(?P<book>[^》]+)》\s*(?:正文)?第\s*(?P<loc>\d+(?:\s*[—–－\-～~至、，,]\s*\d+)*)\s*(?P<unit>頁|段)')


def normalized(text, mapping):
    """異體字、空白及標點正規化；保留文字、數字及數學符號。"""
    text = unicodedata.normalize('NFC', text).translate(mapping)
    return ''.join(c for c in text if not c.isspace() and not unicodedata.category(c).startswith('P'))


def parse(text):
    parts = re.split(r'^## ([^\n]+?)\s*$', text, flags=re.M)
    sections = {}
    repeated = []
    for i in range(1, len(parts), 2):
        name = parts[i].strip()
        if name in sections:
            repeated.append(name)
        sections[name] = parts[i + 1].strip()
    sources = set()
    for m in CITE.finditer(text):
        for part in re.split(r'[、，,]', m['loc']):
            nums = [int(x) for x in re.findall(r'\d+', part)]
            sources.add((m['book'], nums[0], nums[-1], m['unit']))
    sources = sorted(sources)
    return sections, sources, repeated


def substantive(value):
    """移除明確來源題頭及缺載標記，只用於保守辨識純圖表指標。"""
    lines = []
    for line in value.splitlines():
        line = line.strip()
        if not line or line in ('原文未提及', '無'):
            continue
        if CITE.match(line) and (line.endswith(('：', ':')) or CITE.fullmatch(line)):
            continue
        lines.append(line)
    return ''.join(lines)


def inventory(root):
    cards = []
    counts = Counter()
    for path in sorted((root / 'qi-zheng-si-yu/knowledge').glob('*.md')):
        raw = path.read_bytes()
        text = raw.decode('utf-8')
        counts.update(text)
        sections, sources, repeated = parse(text)
        cards.append({'路徑': path.relative_to(root).as_posix(), '標題': path.stem,
                      'sha256': hashlib.sha256(raw).hexdigest(), '文字': text,
                      '欄位': sections, '來源': sources, '重複欄位': repeated})
    active = [pair for pair in PAIRS if all(counts[c] for c in pair)]
    mapping = str.maketrans({a: b for a, b in active})
    return cards, counts, active, mapping


def generate(root, out):
    cards, chars, pairs, mapping = inventory(root)
    problems, figures, duplicates = [], [], defaultdict(list)
    books, multi = Counter(), []
    source_free = []
    for card in cards:
        path, fields, src = card['路徑'], card['欄位'], card['來源']
        issues = []
        if not card['文字'].splitlines() or card['文字'].splitlines()[0] != '#七政四餘':
            issues.append('首行標籤不符')
        issues.extend('缺欄位或空白：'+f for f in FIELDS if not fields.get(f))
        if card['重複欄位']:
            issues.append('重複欄位標題')
        if not re.search(r'《[^》]+》', card['文字']):
            issues.append('未偵測到書名')
        if re.search(r'正文第\d+頁', card['文字']):
            issues.append('引文標示正文頁碼，尚須核對是否等於PDF實際頁碼')
        if not src:
            issues.append('未偵測到書名與頁碼／段落的連續定位')
            source_free.append(path)
        for book in {s[0] for s in src}:
            books[book] += 1
        if any(a > b for _, a, b, _ in src):
            issues.append('來源起訖倒置')
        if issues:
            problems.append({'路徑': path, '問題': issues})
        if len({s[0] for s in src}) > 1:
            multi.append(path)
        body = '\n'.join(fields.get(f, '') for f in FIELDS)
        if '原文以圖表呈現' in body:
            payload = ''.join(substantive(fields.get(f, '')) for f in FIELDS)
            rest = payload.replace('原文以圖表呈現', '')
            pure = not normalized(rest, mapping)
            figures.append({'路徑': path, '來源': src,
                            '分類': '純圖表指標候選' if pure else '含圖表標示及其他文字',
                            '處理': '保留；正式階段2再逐卡核對，不轉錄圖像'})
        # A類預篩：只納入單一書名、單一PDF頁碼範圍、四欄完整者。
        # 圖表卡、Word、混合來源與多頁碼組合均不自動判作A類。
        if '原文以圖表呈現' not in body and len(src) == 1 and src[0][3] == '頁' and all(fields.get(f) for f in FIELDS) and not card['重複欄位']:
            content = tuple(normalized(fields[f], mapping) for f in FIELDS)
            duplicates[(tuple(src[0]), content)].append(path)
    groups = []
    for (source, _), paths in sorted(duplicates.items()):
        if len(paths) > 1:
            groups.append({'來源': source, '卡片': paths, '狀態': 'A類機械候選，尚未人工確認，不刪除'})
    baseline = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    result = {'狀態': '階段2前置試跑，非正式完成報告；階段1.5仍未完成',
              '基準提交': baseline, '卡片數': len(cards), '來源書名數': len(books),
              '來源分布': dict(sorted(books.items())),
              '來源計數說明': '同一卡片可計入多書；不同書名寫法尚未校同，不能當成實際書籍數。',
              '結構問題卡片數': len(problems), '結構問題': problems,
              '檢查項目問題數': dict(Counter(issue for row in problems for issue in row['問題'])),
              '完全重複候選群數': len(groups), '完全重複候選卡片數': sum(len(g['卡片']) for g in groups),
              '完全重複候選': groups, '圖表標示卡片數': len(figures),
              '純圖表指標候選數': sum(f['分類'] == '純圖表指標候選' for f in figures),
              '多書來源卡片數': len(multi),
              '限制': ['多書來源不等於多書同文，尚未做B類判讀。',
                       '未做近似分群、同名異義與衝突判讀；未建立正式cards.jsonl。',
                       'A類候選以單一PDF頁碼範圍預篩；所有含圖表標示的卡片排除，複合來源可能漏列。',
                       '只檢查字面結構，不證明欄位分配及原文語義正確；純圖表辨識為保守候選。',
                       '完成階段1.5後必須重跑，未改動或刪除任何卡片。']}
    out.mkdir(parents=True, exist_ok=True)
    def write(name, obj):
        (out/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
    write('暫定檢查結果.json', result)
    write('圖表卡片清單.json', figures)
    write('卡片雜湊基準.json', [{'路徑': c['路徑'], 'sha256': c['sha256']} for c in cards])
    lines = ['# 階段2前置試跑報告', '', '## 目錄', '', '- 範圍與重跑', '- 統計', '- 完全重複候選', '- 限制', '',
             '## 範圍與重跑', '', result['狀態']+'。本次只保存腳本與暫定報告，不變更卡片或階段1.5帳本。', '',
             '執行：`python tools/stage2_preflight.py`。僅使用Python標準函式庫，不需網路。', '',
             '基準提交：`'+baseline+'`。所有卡片逐檔雜湊見「卡片雜湊基準.json」。', '', '## 統計', '',
             '|檢查項目|數量|', '|---|---:|']
    for name in ('卡片數', '來源書名數', '結構問題卡片數', '完全重複候選群數', '完全重複候選卡片數', '圖表標示卡片數', '純圖表指標候選數', '多書來源卡片數'):
        lines.append(f'|{name}|{result[name]}|')
    lines += ['', result['來源計數說明'], '', '完整問題及來源分布見「暫定檢查結果.json」；圖表逐卡清單見「圖表卡片清單.json」。', '',
              '## 完全重複候選', '', '僅移除空白、標點及本庫兩字皆實際出現的余／餘、閑／閒差異；保留其他字及數學符號。比較四欄完整文字，不比較檔名。財／才不作全域等同。', '',
              '候選均未確認，禁止依此報告直接刪除。']
    for i, group in enumerate(groups, 1):
        book, a, b, unit = group['來源']
        lines += ['', f'### 候選{i}：《{book}》第{a}–{b}{unit}', '']
        lines += ['- '+p for p in group['卡片']]
    if not groups:
        lines += ['', '本次保守預篩未發現候選，不代表不存在其他重複。']
    lines += ['', '## 限制', '']+['- '+s for s in result['限制']]+['']
    (out/'暫定報告.md').write_text('\n'.join(lines))
    (out/'正規化用字暫定.md').write_text('# 正規化用字暫定\n\n只列預篩實際採用且兩字均在本庫出現的配對，不是完整異體字表，也不改寫卡片。\n\n|配對|原字次數|對照字次數|\n|---|---:|---:|\n'+''.join(f'|{a}／{b}|{chars[a]}|{chars[b]}|\n' for a, b in pairs)+'\n財／才等需語境判讀的用字未作全域正規化。完整異體用字統計及正式references/variants.md留待後續階段。\n')
    print(json.dumps({k: v for k, v in result.items() if k.endswith(('數', '提交')) and not isinstance(v, (dict, list))}, ensure_ascii=False))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    generate(args.root, args.root/'docs/階段2前置')
