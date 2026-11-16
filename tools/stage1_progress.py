#!/usr/bin/env python3
"""執行：依來源檢查、923筆逐項判讀及保留檢查，重建階段一報告；不修改卡片。

目錄：write_json（資料輸出）；main（候選匯入、來源檢查、待核對清單、進度及帳本）。
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--review-dir', type=Path, help='首次匯入逐項判讀紀錄的本機目錄；之後可省略')
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    docs = root / 'docs'
    folder = docs / '階段1檢查'
    decisions_path = folder / '天官113-165複核決策.json'
    if args.review_dir:
        decisions = []
        for p in sorted(args.review_dir.glob('天官*-*複核決策.json')):
            decisions.extend(json.loads(p.read_text()))
        assert len(decisions) == 923 and {x['候選編號'] for x in decisions} == set(range(923))
        write_json(decisions_path, decisions)
        reports = {}
        for p in sorted(args.review_dir.glob('天官*-*複核*套用.json')):
            reports[p.name] = json.loads(p.read_text())
        write_json(folder / '天官113-165晉升檢查.json', reports)
    decisions = json.loads(decisions_path.read_text())
    validation = json.loads((folder / '階段1-十九本文字層與分頁核對.json').read_text())
    cards = json.loads((folder / '階段1-卡片保留與結構核對.json').read_text())
    assert len(decisions) == 923
    table = ['# 階段 1：來源與分頁檢查', '', '由 tools/stage1_progress.py 產生。文字層存在不表示圖表內文字已提取；分頁抽查不取代逐卡語義核對。', '',
             '|原始檔名|PDF頁數|抽查頁數|無文字層頁數|既有文字可沿用|', '|---|---:|---:|---:|---|']
    for item in validation['逐書結果']:
        table.append(f'|{item["檔名"]}|{item["PDF頁數"]}|{len(item["抽查頁"])}|{len(item["無文字層頁碼"])}|{"是" if item["既有文字可沿用"] else "否"}|')
    table += ['', f'合計：{validation["書籍數"]}本、{validation["PDF總頁數"]}頁、抽查{validation["抽查頁數"]}頁。完整雜湊與比對值見同目錄JSON。', '']
    (folder / '來源與分頁檢查.md').write_text('\n'.join(table))
    conversions = []
    for p in sorted((root / 'qi-zheng-si-yu/knowledge').glob('*.md')):
        if '永珍' in p.read_text():
            conversions.append({'檔案': p.relative_to(root).as_posix(), '問題': '既有轉換把原文「萬象／万象」轉成「永珍」；保留既有文字，待使用者決定修訂方式。'})
    write_json(folder / '既有字形轉換待核對.json', conversions)
    manual = ['# 階段 1：待人工核對清單', '', '由 tools/stage1_progress.py 產生。候選已逐項判讀；此清單保留不能自行補正的來源疑義及既有卡片問題，不把疑義當作有效規則。', '',
              '- 《增訂天官五星集腋》第70–71頁：星名重複、缺名及疑字。',
              '- 同書第75頁〈太陰身度主說——存參〉：只有節題，未見正文。',
              '- 同書第128頁〈劃度玄奧經〉「金木與奎木」字樣：照錄並以篇名區分，未自行改成其他星宿。',
              '- 同書第153頁：「孝服娶妻因此曜，官司打死是斯星。」指代不明；候選747未新增卡片。',
              '- 同書第293–294、319頁的表列內容保留圖表指標，未自行轉錄成規則。',
              '- 同書第299–306頁〈靈臺一百二十格〉：實際定位118條格句；第309–314頁〈論富貴六十九格〉實列70個獨立節題。未湊數、刪格。',
              '- 同書第320–321頁：月正列日、太陰行度日期有疑字，保留原文。',
              f'- 既有{len(conversions)}張卡有「永珍」轉換問題，詳見「階段1檢查/既有字形轉換待核對.json」。新轉換已保護「萬象」，未改寫既有文字。',
              '- 既有卡片中對原文的改寫及例子是否確為原例，仍須階段3來源抽查檢驗；結構檢查通過不等同語義全面通過。',
              '- 圖表卡片的全庫標記、跨書同文及衝突清單於階段2另做；本階段不刪卡。', '',
              '923筆候選全部判讀完成；完整去向保存在「階段1檢查/天官113-165複核決策.json」。', '']
    (docs / '階段1-待人工核對清單.md').write_text('\n'.join(manual))
    counts = Counter(x['處理'] for x in decisions)
    complete = not cards['原文保留問題數'] and not cards['結構待核對卡片數'] and validation['可沿用書籍數'] == 19
    report = ['# 階段 1：首輪補齊與欄位核對結果', '', '由 tools/stage1_progress.py 產生。此階段完成首輪補齊，不表示後續去重、衝突處理、來源抽查或Skill評測已完成。', '',
              '- 《張果星宗》397頁：首輪逐節閱讀及引文提煉完成，正文10卷與主要篇章已核對；538筆縮排定位資料不是538章。',
              '- 《增訂天官五星集腋》341頁：首輪逐節閱讀及提煉完成，294筆目錄子目與正文定位已核對；異名、併題及錯卷已記錄。',
              '- 《三辰通載》第237–323頁：補完首輪引文，合併原有1–236頁處理紀錄。',
              '- 其餘16本：全量檢查出處、頁碼及四欄；《五星捷要便覽》19張缺頁碼卡已追加來源及原文，未改寫既有正文。',
              f'- 卡片{cards["目前卡片數"]}張；原基準{cards["基準卡片數"]}張。原有欄位文字保留問題{cards["原文保留問題數"]}；首行、四欄及出處結構問題{cards["結構待核對卡片數"]}。',
              '- 19本共1,965頁；每本5頁、共95頁與PDF實際分頁比對一致；全頁無文字層0頁。',
              '- 圖表未擅自轉錄；原書疑字、指代不明及既有字形轉換問題另留待核對清單。', '', '## 923筆候選處理結果', '']
    report += [f'- {k}：{v}筆。' for k, v in counts.items()]
    report += ['', '新增的來源段均先核對書名、PDF實際頁碼、四欄及原文對應；同一概念追加來源引文，沒有刪卡或改寫原有欄位。只按完整字串檢查的新卡重複閘門，不等同階段2的去重分群。', '',
               f'首輪補齊與結構閘門：{"通過" if complete else "未通過"}。語義與版本保留事項見「階段1-待人工核對清單.md」。', '',
               '依使用者授權，完成本階段後直接進入階段1.5，重新盤點雲端全庫。階段1.5完成並獲確認前不進入階段2。', '']
    (docs / '階段1-工作進度.md').write_text('\n'.join(report))
    ledger = docs / '來源清單.md'
    content = ledger.read_text().splitlines()
    for i, line in enumerate(content):
        parts = line.split('|')
        if len(parts) == 10 and re.fullmatch(r'\d+', parts[4]):
            parts[6] = '首輪提煉、出處頁碼及四欄結構核對完成；保留事項見階段1待核對清單；跨書整理尚未執行'
            parts[7] = f'1–{parts[4]}（首輪覆蓋；非每頁均製卡）'
            parts[8] = '2026-11-16（階段1核對）'
            content[i] = '|'.join(parts)
    ledger.write_text('\n'.join(content) + '\n')
    readme = root / 'README.md'
    text = readme.read_text()
    a = text.index('目前工作稿：'); b = text.index('\n\n', a)
    text = text[:a] + f'目前工作稿：19本PDF、1,965頁、{cards["目前卡片數"]:,}張卡片檔案（原基準4,039張）。階段1首輪補齊與欄位結構檢查完成；923筆賦文斷句候選已全部判讀。接續進入階段1.5雲端全庫補齊。保留問題見待核對清單；跨書整理、來源抽查及評測尚未完成，技能仍在建置中。' + text[b:]
    text = text.replace('本次先發布工作稿，不代表階段驗收通過。', '首輪補齊、檢查數字與保留事項。')
    readme.write_text(text)
    workflow = docs / '工作階段.md'
    text = workflow.read_text().replace('補齊提煉、複核四欄及出處、更新帳本。目前進行中。', '首輪補齊、四欄與出處結構核對已完成；保留事項見階段1報告。')
    workflow.write_text(text)
    print(json.dumps({'卡片數': cards['目前卡片數'], '候選判讀數': len(decisions), '首輪與結構閘門通過': complete, '既有字形問題卡': len(conversions)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
