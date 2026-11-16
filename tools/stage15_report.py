#!/usr/bin/env python3
"""執行：以已盤點資料及逐書完成紀錄重建階段1.5帳本與進度，不下載、不提煉卡片。"""
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--paused', action='store_true', help='依使用者指示暫停時才使用')
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    docs = root / 'docs'
    folder = docs / '階段1.5檢查'
    inventory = json.loads((folder / '雲端盤點資料.json').read_text())
    progress = json.loads((folder / '逐書進度.json').read_text())
    completed = {k: v for k, v in progress.items() if v.get('完成', True)}
    rows = inventory['逐檔結果']
    cards = len(list((root / 'qi-zheng-si-yu/knowledge').glob('*.md')))
    pdfs = [r for r in rows if r['類型'] == 'application/pdf']
    new = [r for r in rows if r['來源'] == '新增']
    table = ['# 階段1.5：雲端全庫補齊進度', '', '由 tools/stage15_report.py 產生。先前已依流量限制指示推送工作稿；使用者隨後指示繼續，目前使用已下載原檔接續提煉。本階段尚未完成，不進入階段2。' if not args.paused else '依使用者指示發布工作稿並暫停，本階段未完成。', '',
             f'- 初次盤點：{len(rows)}份來源（{len(pdfs)}本PDF及{len(rows)-len(pdfs)}份Word），子資料夾0；PDF共{sum(r["PDF頁數"] for r in pdfs):,}頁。',
             '- 原帳本19本的識別碼、檔名、大小與雲端修改時間均與先前下載紀錄一致；本機SHA256及頁數重新核對。未重新下載這19本，也未將本機雜湊冒稱為雲端回傳值。',
             f'- 新增11份：已完成首輪{len(completed)}份，待處理{len(new)-len(completed)}份；目前卡片{cards:,}張。',
             '- 新增10本PDF與1份Word原檔均已取得，存放工作區；PDF、Word原檔不提交git。',
             '- 未完成收尾的第二次雲端盤點；此為暫停點，不是全庫完成報告。', '',
             '|新增書籍／文件|PDF頁數|狀態|', '|---|---:|---|']
    for row in new:
        state = progress.get(row['雲端識別碼'], {})
        title = state.get('書名', row.get('書名', row['檔名']))
        status = state.get('狀態', '待逐書結構核對及逐節提煉')
        if row['類型'] != 'application/pdf': status = state.get('狀態', '待提煉')+'；使用節題＋原始段落編號'
        elif row['僅頁尾水印或頁碼頁']: status += '；無正文文字層頁另待處理'
        table.append(f'|{title}|{row["PDF頁數"] or "不適用"}|{status}|')
    table += ['', '## 無正文文字層頁', '', '排除水印及頁碼後沒有正文文字的頁面如下；部分為掃描圖表，未做OCR、未提煉圖內文字，也未將水印當成正文。無圖頁是否留白仍待核對。', '']
    for row in new:
        pages = row['僅頁尾水印或頁碼頁']
        if pages:
            table.append('- ' + row['檔名'] + '：' + '、'.join(str(p['PDF頁碼']) for p in pages) + '。')
    table += ['', '## 本次完成與保留事項', '', '- 《源髓歌》13頁讀完：正文兩部分；三命部56個引文段落、七政四餘部11個明示篇題。113筆來源卡片段通過閘門，原批新增61張、追加既有12張；異名候選修復另補建22張。',
              '- 異名同文閘門修復：補建262張，原19本133張、《源髓歌》22張、Word16張、《欽定日課》5張及《璇璣抉微》卷一86張；詳見「階段1.5檢查/異名同文漏建修復.json」。沒有刪卡或改寫既有文字。',
              '- 三命部卡名以篇名限定，避免混用；適用範圍索引仍待階段2建立。第9及12頁各有不可辨字「�」，保留原字另待核對。',
              '- 《楊國正七政四餘彙編》253段已讀完；269筆來源卡片段通過閘門，原批新增98張、追加既有92張；異名候選修復另補建16張。原檔所稱外部原講義及影音未另取得核對，文件最後一講未完，不補寫。',
              '- Word定位方式依使用者明確回覆：使用「節題＋原始段落編號」，不虛構PDF頁碼。',
              '- 先前14張既有卡片的「永珍」問題仍保留待核對，未擅自改寫。',
              '- 原書序言、版本故事、宣傳、一般研讀提醒未製卡。', '', '## 復工順序', '',
              '先接續新增書籍的逐書結構核對及逐節提煉，按帳本更新進度；掃描頁的處理方式尚未獲明確答覆。完成後再盤點一次雲端全庫。階段1.5完成並經使用者確認後才進入階段2。', '']
    (docs / '階段1.5-工作進度.md').write_text('\n'.join(table))
    ledger = docs / '來源清單.md'
    text = ledger.read_text()
    lines = text.splitlines()
    known = {line.split('|')[3] for line in lines if line.startswith('|') and len(line.split('|')) == 10}
    for row in new:
        state = progress.get(row['雲端識別碼'], {})
        title = state.get('書名', row.get('書名', row['檔名']))
        status = state.get('狀態', '待逐書結構核對及逐節提煉')
        span = state.get('已處理範圍', '尚未逐節提煉')
        if row['類型'] != 'application/pdf': status += '；定位方式為節題＋原始段落編號'
        rendered = '|'+ '|'.join([title, row['檔名'], row['雲端位置'], str(row['PDF頁數'] or '不適用（Word）'), row['SHA256'] or '待計算', status, span, '2026-11-16（階段1.5盤點）']) +'|'
        existing = next((i for i, line in enumerate(lines) if line.startswith('|') and len(line.split('|'))==10 and line.split('|')[3]==row['雲端位置']), None)
        if existing is None: lines.append(rendered)
        else: lines[existing] = rendered
    lines[2] = f'目前盤點{len(rows)}份來源：{len(pdfs)}本PDF共{sum(r["PDF頁數"] for r in pdfs):,}頁，以及1份Word講義。原19本首輪提煉與欄位結構核對完成；新增來源的完成範圍以本帳本及階段1.5工作進度為準。PDF實際頁碼與Word原始段落編號分別記錄，不混用。'
    ledger.write_text('\n'.join(lines)+'\n')
    readme = root / 'README.md'
    text = readme.read_text(); a = text.index('目前工作稿：'); b = text.index('\n\n', a)
    text = text[:a] + f'目前工作稿：已盤點29本PDF、3,430頁及1份Word；目前{cards:,}張卡片檔案。原19本的階段1首輪補齊與結構檢查完成；階段1.5新增來源已完成{len(completed)}份，其餘{len(new)-len(completed)}份仍待處理，目前使用已下載原檔接續提煉；跨書整理、來源抽查及評測尚未完成，技能仍在建置中。' + text[b:]
    link = '- [階段1.5工作進度](docs/階段1.5-工作進度.md)：全庫盤點、新增書籍完成範圍及復工位置。\n'
    if link not in text: text = text.replace('- [工作階段與順序]', link + '- [工作階段與順序]', 1)
    readme.write_text(text)
    print(json.dumps({'來源': len(rows), 'PDF本數': len(pdfs), 'PDF頁數': sum(r['PDF頁數'] for r in pdfs), '卡片': cards, '新增來源完成': len(completed), '新增來源待處理': len(new)-len(completed), '階段1.5完成': False}, ensure_ascii=False))

if __name__ == '__main__':
    main()
