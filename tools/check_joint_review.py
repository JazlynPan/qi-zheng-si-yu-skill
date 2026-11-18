"""由人工原圖字形紀錄重建69卡比對報告；不改卡、不判定旁字歸屬。"""
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def read(name):
    return json.loads((ROOT / 'docs/檢查' / name).read_text())
base = read('綱目歲殿登籍69卡逐張複核.json')
extra = read('綱目聯列29卡字形續核證據.json')
values = {(x['PDF實際頁碼'], x['年欄']): x['聯列下方字形'] for x in extra['明細']}
authorized = read('歲殿八筆授權修字與四欄重看.json')
for record in authorized['四張重看']:
    values[(record['PDF實際頁碼'], record['年欄'])] = record['原圖可辨下方字']
rows = []
for old in base['明細']:
    row = dict(old)
    filename = row['卡片檔名']
    text = (ROOT / 'qi-zheng-si-yu/knowledge' / filename).read_text()
    title = row['既有題名']
    match = re.search(r'\n' + re.escape(title) + r'\n\n([^\n]+)', text)
    row['卡片字值'] = match.group(1) if match else '未解析'
    key = (row['PDF實際頁碼'], row['年欄'])
    raw = values.get(key, row['聯列下方字形'])
    row['聯列下方字形'] = raw
    row['字形狀態'] = ('字形仍待確認' if raw == '原字未確認' else
        '字形相同；歸屬未確認' if raw == row['卡片字值'] else
        '字形差異候選；歸屬未確認')
    rows.append(row)
counts = {key: sum(r['字形狀態'] == key for r in rows)
          for key in sorted({r['字形狀態'] for r in rows})}
report = {'書名': '星學綱目正傳', '卡片範圍數': len(rows), '分類統計': counts,
          '證據限制': '人工圖像觀察＋腳本比對；字形相同不代表可獨立分卡；歸屬仍未確認，非驗收通過。',
          '卡片異動數': 0, '明細': rows}
(ROOT / 'docs/檢查/綱目歲殿登籍69卡字形續核結果.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(counts, ensure_ascii=False))
