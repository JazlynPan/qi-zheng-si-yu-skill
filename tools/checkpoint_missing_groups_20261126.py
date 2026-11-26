"""執行：保存八組候選與雲端再盤點；不改卡片，不裁決候選。"""
from pathlib import Path
import json, re

R = Path(__file__).resolve().parents[1]
D = R / 'docs/檢查'
stem = '其餘八組歲殿登籍原圖-2026-11-26'
old = json.loads((D/'雲端盤點-2026-11-25-連接器證據.json').read_text())
new = json.loads((D/'雲端盤點-2026-11-26-連接器證據.json').read_text())
a = {r['id']: r for r in old['files']}
b = {r['id']: r for r in new['files']}
fields = ['title', 'size', 'modified_time', 'mime_type']
changed = [{'id': k, '欄位': f, '先前': a[k].get(f), '本次': b[k].get(f)}
           for k in a.keys() & b.keys() for f in fields if a[k].get(f) != b[k].get(f)]
inventory = {'日期': '2026-11-26', '來源數': len(b),
             '新增': sorted(b.keys()-a.keys()), '缺少': sorted(a.keys()-b.keys()),
             '中繼資料差異': changed,
             '子資料夾數': sum(r.get('file_or_folder') == 'folder' for r in b.values()),
             '下一頁權杖': new['next_page_token'],
             '限制': '本日比對識別碼、檔名、大小、修改時間、類型；SHA256及實際頁數沿用昨日重取原檔結果。'}
assert len(b) == 30 and not inventory['新增'] and not inventory['缺少'] and not changed
assert not inventory['子資料夾數'] and inventory['下一頁權杖'] is None
(D/'雲端盤點-2026-11-26-比較.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n')
rows = json.loads((D/(stem+'-預覽.json')).read_text())['明細']
p = R/'docs/待你處理.md'
s = p.read_text()
removed = [line for line in s.splitlines() if line.startswith(('- GM97-01｜','- GM99-01｜'))]
assert len(removed) == 2
s = '\n'.join(line for line in s.splitlines() if line not in removed)+'\n'
items = []
for r in rows:
    topic = r['上方原題候選']; value = r['原圖小字候選']
    items.append(f'- {r["編號"]} {r["年份"]}兩張補卡｜請看紅框，題字「{topic}」、共值「{value}」是否同意照錄補卡？｜[完整預覽](檢查/{stem}-預覽.md)｜[圖1]({r["原圖"].removeprefix("docs/")})｜選項：同意本組兩卡／更正題字或小字／先不補')
assert not any('- '+r['編號']+' ' in s for r in rows)
s = s.replace('## 需要先確認規則','\n'.join(items)+'\n\n## 需要先確認規則')
s = s.replace('待處理共90項（有圖86、規則4、等補圖0；含37筆形近字字位圖及31組登籍原圖）','待處理共96項（有圖92、規則4、等補圖0；含37筆形近字字位圖、31組登籍原圖及8組雙題缺卡候選）')
assert len(re.findall(r'^- ',s,re.M)) == 96
p.write_text(s)
note = ['# 八組候選與雲端再盤點存檔（2026-11-26）', '',
        '- 雲端30份與昨日相比：新增0、缺少0、中繼資料差異0、子資料夾0；原檔雜湊與頁數採昨日實際重取結果，今天未冒稱重算。',
        '- [八組原圖與16份補卡預覽]('+stem+'-預覽.md)：正式卡片新增0、修改0。戊午題名候選歲駕，與歲殿分開；己亥淡字保留待確認。',
        '- 丙子依使用者禁止新增而排除；戊寅、己丑原圖空白沿用原決定。',
        '- 入口移除已照原圖收錄的GM97-01天嗣下注、GM99-01飛廉下注兩條舊問題；不是刪卡或裁定其他字。',
        '- 原入口兩行留存：', '', *['> '+line.replace('(檢查/','(').replace('(待裁決/','(../待裁決/') for line in removed], '',
        '- 入口96項：有圖92、規則4。31組登籍補卡問題與本8組分開，等待使用者確認才正式新增。',
        '- 本批未改knowledge/；文件與連結的機械檢查另存JSON，不代表圖字驗收。']
(D/'八組候選與雲端再盤點存檔-2026-11-26.md').write_text('\n'.join(note)+'\n')
catalog = R/'docs/catalog/星學綱目正傳.md'
with catalog.open('a') as f:
    f.write('\n### 2026-11-26：其餘八組缺卡原圖\n\n原九組雙題皆缺中，丙子依使用者禁止新增排除；其餘八組備原圖與16份完整候選，未新增卡。戊午題名較像歲駕，未當作歲殿；己亥小字淡損。見[逐組預覽](../檢查/'+stem+'-預覽.md)。31組登籍另案待確認，原圖空白戊寅、己丑不代填。\n')
p = R/'docs/來源清單.md'; lines=p.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('|星學綱目正傳|'):
        cells=line.split('|'); cells[7]+='；2026-11-26另八組缺卡原圖與16份擬新增全文已備，戊午題名候選歲駕；丙子禁補、空白兩處維持，未正式新增卡'; lines[i]='|'.join(cells)
p.write_text('\n'.join(lines)+'\n')
p=R/'docs/狀態.md';s=p.read_text()
s=s.replace('下一個第一動作：核對其餘兩題皆缺的組是否已有禁補或原題異名，列進同一份待補覆蓋報告；不新增卡。','其餘九組雙題皆缺已核：丙子禁補排除，八組備16份全文預覽；戊午題名候選歲駕，未套成歲殿。下一個第一動作：對照現帳本與逐頁分界產出結束前未完成清單，不自行驗收；收到補卡授權才回填。')
s=s.replace('CY-23舊摘要','今天再盤點仍30份，新增0、中繼資料差異0。CY-23舊摘要')
s=s.replace('31組登籍缺卡已備全文預覽與原圖，等使用者確認後才補；','31組登籍及另八組共16份候選已備全文預覽與原圖，等使用者確認後才補；')
p.write_text(s)
print(json.dumps({'來源':len(b),'新增來源':0,'八組預覽':16,'正式新增卡':0,'待決入口':96},ensure_ascii=False))
