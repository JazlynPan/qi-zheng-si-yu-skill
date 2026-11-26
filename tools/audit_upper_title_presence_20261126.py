"""執行：盤點六十年二十題的精確檔名是否存在；不是原圖應有卡數或去重分類。"""
from pathlib import Path
from collections import Counter, defaultdict
import json,csv
R=Path(__file__).resolve().parents[1];D=R/'docs/檢查';K=R/'qi-zheng-si-yu/knowledge'
stem='綱目上表題名存在性-2026-11-26'
topics=['祿勳','官印','玉堂','文魁','文昌','催官','祿神','喜神','天廚','天嗣','貴元','祿元','仁元','壽元','科名','空亡','擎天','遊奕','歲殿','登籍']
st='甲乙丙丁戊己庚辛壬癸';br='子丑寅卯辰巳午未申酉戌亥';names={p.name for p in K.glob('*.md')}
drafts={}
for file in ['登籍31組補卡預覽-2026-11-26.json','其餘八組歲殿登籍原圖-2026-11-26-預覽.json']:
 data=json.loads((D/file).read_text())
 for row in data['明細']:
  if '擬新增卡名'in row:drafts[row['擬新增卡名']]=file
  for card in row.get('擬新增卡',[]):drafts[card['卡名']]=file
for file in ['綱目75乙丑未見題名原格-2026-11-26.json','綱目乙年頭右緣續核-2026-11-26.json','綱目跨頁右緣三元36格續核-2026-11-26.json','綱目上表其餘32格原圖-2026-11-26-結果.json','綱目73丙子原欄20題讀圖-2026-11-26-結果.json']:
 data=json.loads((D/file).read_text())
 if '擬新增卡名'in data:drafts[data['擬新增卡名']]=file
 if '官印完整預覽'in data:drafts[data['官印完整預覽']['卡名']]=file
 for row in data.get('明細',[]):
  if '擬新增卡名'in row:drafts[row['擬新增卡名']]=file
rows=[];missing=defaultdict(list);bytopic=Counter();covered=0
for n in range(60):
 year=st[n%10]+br[n%12]
 for topic in topics:
  name=f'{topic}圖列·{year}（星學綱目圖說下）.md';exists=name in names
  row={'年組':year,'題名':topic,'檔名':name,'精確檔名存在':exists,'已有完整預覽':drafts.get(name),'限制':'精確題名存在不等於原值已驗收；不存在不等於漏卡，可能圖題異名、原圖空白、切邊或既有禁止補卡。'}
  if not exists:missing[year].append(topic);bytopic[topic]+=1;covered+=name in drafts
  rows.append(row)
assert len(rows)==1200 and sum(not r['精確檔名存在'] for r in rows)==151
report={'日期':'2026-11-26','比較欄位數':1200,'精確題名存在':1049,'精確題名未見':151,'未見題名已有完整預覽':covered,'其他未見題名':151-covered,'未見按題名':dict(bytopic),'未見按年組':dict(missing),'卡片異動':0,'不得解讀為':'151張漏卡、1200張應有卡、1049張原值正確或階段2分類結果；均不能由本表推論。','明細':rows}
(D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
with (D/(stem+'.tsv')).open('w',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['年組',*topics])
 for n in range(60):
  year=st[n%10]+br[n%12];w.writerow([year,*['精確檔名未見'if t in missing[year]else'有檔，不表示已核值'for t in topics]])
md=['# 綱目上表題名存在性（2026-11-26）','','## 口徑與限制','',
    '以既有常見20種題名，逐一比較60年組的精確檔名，得到1,200個檔名位置：有檔1,049、未見151。**不是151張漏卡，也不是原圖應有1,200張卡。**',
    '原題可能異名、格值可能空白或切邊；存在的卡也可能缺載或未驗收。本表不使用天干偏移、他書值或記憶推定原刻。沒有改卡或建立空殼。',
    f'未見151個題名中，{covered}個已有前述完整預覽，其餘{151-covered}個仍須回原格確認是否真有可收文字；不因此直接補卡。戊午歲駕候選不當歲殿，所以不算歲殿題名已覆蓋。',
    '丙子沿用不新增的限制；己巳貴元原錯值已撤，不以缺檔為理由恢復戌。戊寅、己丑原空白及所有既有未確認值都不由本表補寫。','',
    '## 未見題名逐組表','','|年組|精確題名未見|','|---|---|']
for year,ts in missing.items():md.append('|'+year+'|'+'、'.join(ts)+'|')
md+=['','## 檔案','',
     '[完整1,200格及來源限制](綱目上表題名存在性-2026-11-26.json)；[六十年逐題TSV](綱目上表題名存在性-2026-11-26.tsv)。',
     '本盤點只檢查工作成果的精確題名存在性，不作跨書去重、不進階段2、不宣稱這些位置都必須建卡。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
catalog=R/'docs/catalog/星學綱目正傳.md'
with catalog.open('a') as f:
 if ('未見中'+str(covered)+'項已有完整候選') not in catalog.read_text():f.write('\n### 2026-11-26：上表題名存在性\n\n六十年×20種常見題名的精確檔名比對有1,049、未見151；不是原圖應有卡數或漏卡數，未見中'+str(covered)+'項已有完整候選，其餘須原格確認，不以缺檔造值。[口徑與逐組表](../檢查/'+stem+'.md)。\n')
p=R/'docs/狀態.md';s=p.read_text();import re;s=re.sub(r'未見中\d+項已有全文候選','未見中'+str(covered)+'項已有全文候選',s);s=s.replace('下一個第一動作：續查73–96頁尚未連到原圖紀錄的框；保留既有裁決，對未定字只補證據、不改卡。','上表精確題名存在性已另盤點：1,200位置有檔1,049、未見151（不是漏卡數），未見中'+str(covered)+'項已有全文候選。下一個第一動作：回查未見題名的原格，先乙丑祿勳、科名；遇切邊或空白只記catalog，不造值、不改已裁決項。');p.write_text(s)
print(json.dumps({k:report[k]for k in ['比較欄位數','精確題名存在','精確題名未見','未見題名已有完整預覽','其他未見題名','卡片異動']},ensure_ascii=False))
