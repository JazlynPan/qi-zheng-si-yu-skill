#!/usr/bin/env python3
"""執行：檢查本次複核報告、紅框檔與卡片不變性；不修改卡片。"""
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs/檢查'
KNOWLEDGE = ROOT / 'qi-zheng-si-yu/knowledge'

def read(name):
    return json.loads((DOCS / name).read_text())

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

checks = {}
rows = read('丙丁戊己錯配逐筆複核.json')['明細']
checks['指定卡22張'] = len(rows) == 22
checks['歲殿16登籍6'] = sum(x['卡片'].startswith('歲殿') for x in rows) == 16 and sum(x['卡片'].startswith('登籍') for x in rows) == 6
checks['圖讀21不同1未確認'] = sum(x['圖上讀值'] == '未確認' for x in rows) == 1 and sum(x['圖上讀值'] != '未確認' and x['圖上讀值'] != x['現值'] for x in rows) == 21
checks['指定卡檔存在'] = all((KNOWLEDGE / x['卡片']).is_file() for x in rows)
checks['頁欄位置齊全'] = all(all(x.get(k) for k in ['年欄頁碼', '科甲共值頁碼', '年欄位置', '科甲位置', '是否下一頁右緣']) for x in rows)
missing = read('丙丁戊己錯配逐筆複核.json')['缺卡清單']
checks['丙子不新增'] = all('不新增' in x['處理'] for x in missing if x['年欄'] == '丙子')
t10 = read('T10擎天44筆四類清單.json')
checks['T10共44筆'] = len(t10['明細']) == sum(t10['分類數'].values()) == 44
checks['T10逐筆有兩書頁碼'] = all(x['原圖頁碼']['綱目'] and x['原圖頁碼']['張果'] == 40 for x in t10['明細'])
questions = []
for code in ['T14', 'T15', 'T17']:
    rr = read(code + '逐條紅框對照.json')['明細']
    checks[code + '逐條五項齊全一問'] = all(all(x.get(k) for k in ['現存讀字', '候選修訂字', '一句話差異', '原圖', '問題']) and x['問題'].count('？') == 1 for x in rr)
    questions.extend(rr)
checks['逐條編號不重複'] = len({x['編號'] for x in questions}) == len(questions)
checks['候選均有紅框圖'] = all((DOCS / x['原圖']).is_file() for x in questions)
checks['24頁紅框齊全'] = all((ROOT / f'docs/待裁決/原圖/丙丁戊己-綱目{p}-年欄與科甲紅框.png').is_file() for p in range(73,97))
link_errors = []
reports = list(DOCS.glob('*逐條紅框對照.md')) + [DOCS / n for n in ['丙丁戊己錯配逐筆複核.md', 'T10擎天44筆四類清單.md', '使用者決定與T09核驗.md', '2026-11-19複核總覽.md']] + [ROOT / 'docs/待辦事項.md']
for path in reports:
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        target = target.strip('<>').split('#', 1)[0]
        if not target or '://' in target or target.startswith('mailto:'):
            continue
        if not (path.parent / unquote(target)).exists():
            link_errors.append({'檔案': str(path.relative_to(ROOT)), '連結': target})
checks['本次報告檔案連結可解析'] = not link_errors
checks['長報告有目錄'] = all(len(p.read_text().splitlines()) <= 100 or '## 目錄' in '\n'.join(p.read_text().splitlines()[:15]) for p in reports if p.name != '待辦事項.md')
checks['報告提交卡片異動0'] = not git('diff', '045ca940', '--', 'qi-zheng-si-yu/knowledge').strip()
checks['卡片總數不變19756'] = len(list(KNOWLEDGE.glob('*.md'))) == 19756
changes = git('diff', '--name-only', 'f6c76ad6', '045ca940', '--', 'qi-zheng-si-yu/knowledge').decode().splitlines()
checks['直接決定提交僅4卡'] = len(changes) == 4
checks['未新增卡片'] = not git('diff', '--name-only', '--diff-filter=A', 'f6c76ad6', '--', 'qi-zheng-si-yu/knowledge').strip()
checks['未提交PDF原檔'] = not any(p.lower().endswith('.pdf') for p in git('ls-files', '--cached', '--others', '--exclude-standard').decode().splitlines())
checks['狀態50行內'] = len((ROOT / 'docs/狀態.md').read_text().splitlines()) <= 50
result = {'日期': '2026-11-19', '證據等級': 'E0：檔案結構與數量檢查，不代表OCR候選已核定', '通過': all(checks.values()), '通過項數': sum(checks.values()), '檢查項數': len(checks), '檢查': checks, '失效檔案連結': link_errors, '逐條紅框候選總數': len(questions), '說明': '紅框位置人工抽看73–96頁年欄代表圖與T09/T14/T15/T17代表圖；不把機械檢查當成全量字讀正確性。'}
(DOCS / '2026-11-19複核驗證.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if result['通過'] else 1)
