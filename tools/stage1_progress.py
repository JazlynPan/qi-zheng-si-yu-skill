#!/usr/bin/env python3
"""執行：依本機可稽核的檢查結果更新階段一進度與候選清單；不修改卡片。"""
import argparse
import json
from pathlib import Path
from stage1_gate import tw

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--review-dir', type=Path, required=True)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    docs = root / 'docs'
    folder = docs / '階段1檢查'
    folder.mkdir(exist_ok=True)
    validation = json.loads((folder / '階段1-十九本文字層與分頁核對.json').read_text())
    (folder / '階段1-十九本文字層與分頁核對.json').write_text(json.dumps(validation, ensure_ascii=False) + '\n')
    # 結構報告請先執行 stage1_audit.py 重新產生。
    cards = json.loads((folder / '階段1-卡片保留與結構核對.json').read_text())
    table = ['# 階段 1：來源與分頁檢查', '', '本報告由 tools/stage1_progress.py 產生。文字層存在不代表圖表內文字已提取；抽查一致不取代逐卡語義複核。', '',
             '|原始檔名|PDF 頁數|抽查頁數|無文字層頁數|既有文字可沿用|', '|---|---:|---:|---:|---|']
    for item in validation['逐書結果']:
        table.append(f'|{item["檔名"]}|{item["PDF頁數"]}|{len(item["抽查頁"])}|{len(item["無文字層頁碼"])}|{"是" if item["既有文字可沿用"] else "否"}|')
    table += ['', f'合計：{validation["書籍數"]} 本、{validation["PDF總頁數"]} 頁、抽查 {validation["抽查頁數"]} 頁。', '',
              '原始檔名保留實際字形；完整 SHA256 與各頁比對值見「階段1-十九本文字層與分頁核對.json」。', '']
    (folder / '來源與分頁檢查.md').write_text('\n'.join(table))
    pending = json.loads((args.review_dir / '天官113-165語義待核對.json').read_text())
    lines = ['# 階段 1：待人工核對清單（持續更新）', '', '## 目錄', '', '- [版本與原文問題](#版本與原文問題)', '- [賦文斷句候選](#賦文斷句候選)', '',
             '此處的人工核對包括後續由本代理逐項複核；目前不要求使用者逐項決定。候選未當作完成卡片，也未丟棄。', '', '## 版本與原文問題', '',
             '- 《增訂天官五星集腋》第70–71頁：星名重複、缺名及疑字，未自行補正。',
             '- 同書第75頁〈太陰身度主說——存參〉：只有節題，未見文字正文，不補造內容。',
             '- 同書第319頁：月支對應與擎天立成為表列指標，沒有自行轉錄成規則。',
             '- 同書第320–321頁：月正列日與太陰行度日期有疑誤，須保留原文另行核對。',
             '- 同書第293–294頁：正次垣列式另留圖表指標；後文〈論垣殿〉的文字說明另行照錄。',
             '- 同書第299–306頁〈靈臺一百二十格〉目前定位118條格句（兩格同排一行者分別計），尚須再核對篇名數與實列數的差異。',
             '- 同書第309–314頁〈論富貴六十九格〉實列70個獨立節題，已按正文保留，不自行湊數或刪格。', '',
             '## 賦文斷句候選', '', f'共 {len(pending)} 筆，僅是早期機械斷句候選，並非 {len(pending)} 個已確認概念；部分已由另外的明示格局卡收錄，仍待逐項對應。', '',
             '|序號|候選原題|出處|狀態|', '|---:|---|---|---|']
    for i, item in enumerate(pending, 1):
        lines.append(f'|{i}|{tw(item["標題"])}|{tw(item["出處"])}|待語義及注解邊界複核|')
    (docs / '階段1-待人工核對清單.md').write_text('\n'.join(lines) + '\n')
    report = ['# 階段 1：工作進度（尚未完成）', '', '本報告由 tools/stage1_progress.py 產生；不是階段結束報告。', '',
              '- 《三辰通載》第237–323頁的首輪引文已套用，待總複核。',
              '- 《張果星宗》397頁已讀完並套用首輪引文，仍待結構清單定稿及語義總複核。',
              '- 《增訂天官五星集腋》341頁已全部讀完；第113–165頁賦文仍有923筆斷句候選待逐項對應；後段引文已套用，仍待逐概念、定義與步驟欄複核。',
              '- 不把讀完頁數、機械候選數或來源字串比對通過數當作完成提煉數。', '',
              f'- 本機卡片：{cards["目前卡片數"]} 張；基準：{cards["基準卡片數"]} 張。',
              f'- 原有欄位文字保留問題：{cards["原文保留問題數"]}；結構待核對卡片：{cards["結構待核對卡片數"]}。',
              '- 19本PDF共1,965頁；95頁分層抽查與舊文字檔一致，完全無文字層頁面0頁。',
              '- 已為《五星捷要便覽》19張缺頁碼卡追加實際頁碼與原文引文，既有正文保留。',
              '- 本次依使用者要求先發布階段一工作稿；此為進度提交，不代表階段一完成或通過驗收。',
              '- 未開始階段二去重、刪卡或後續階段。', '', '詳細檔案：', '',
              '- 階段1檢查/來源與分頁檢查.md', '- 階段1檢查/階段1-卡片保留與結構核對.json', '- 階段1-待人工核對清單.md', '- catalog/增訂天官五星集腋.md', '']
    (docs / '階段1-工作進度.md').write_text('\n'.join(report))
    ledger = docs / '來源清單.md'
    content = ledger.read_text().splitlines()
    updates = {
        '張果星宗': ('397頁已讀完，首輪引文已在本機套用；工作稿先發布，待語義總複核', '1–397（首輪本機工作稿；非每頁均製卡）'),
        '三辰通載': ('第237–323頁首輪引文已在本機套用；工作稿先發布，待總複核', '1–323（首輪覆蓋；第237頁後為本機工作稿）'),
        '增訂天官五星': ('341頁已讀完；部分引文已在本機套用，賦文等尚待逐概念複核', '1–341已讀；已套用及未完成範圍見階段1-工作進度.md')}
    for i, line in enumerate(content):
        parts = line.split('|')
        if len(parts) == 10 and parts[1] in updates:
            parts[6], parts[7] = updates[parts[1]]
            parts[8] = '2026-11-16（階段一持續處理）'
            content[i] = '|'.join(parts)
    ledger.write_text('\n'.join(content) + '\n')
    print(json.dumps({'本機卡片': cards['目前卡片數'], '語義待核對候選': len(pending), '階段1完成': False}, ensure_ascii=False))

if __name__ == '__main__': main()
