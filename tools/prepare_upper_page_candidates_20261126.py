"""執行：列出34張卡的來源頁範圍候選與完整預覽；不套用、不改卡。"""
from review_helpers import *
import difflib
stem='綱目上表來源頁碼34候選-2026-11-26';data=json.loads((D/'綱目上表現卡與舊定位對照-2026-11-26.json').read_text());rows=[];patch=[]
for r in data['明細']:
 if not r['存在'] or any(x['起頁']<=r['舊定位實際頁']<=x['迄頁'] for x in r['目前引用']):continue
 p=K/r['卡片'];old=p.read_bytes();low=min([r['舊定位實際頁']]+[x['起頁'] for x in r['目前引用']]);high=max([r['舊定位實際頁']]+[x['迄頁'] for x in r['目前引用']]);span=str(low) if low==high else f'{low}–{high}'
 pattern=r'《星學綱目正傳》第\s*\d+(?:[—–-]\d+)?\s*頁';new,count=re.subn(pattern,'《星學綱目正傳》第'+span+'頁',old.decode());assert count and new.encode()!=old
 before_body=re.sub(pattern,'<來源頁>',old.decode());after_body=re.sub(pattern,'<來源頁>',new);assert before_body==after_body
 row={**r,'擬列來源範圍':span,'修訂狀態':'候選預覽，未裁定、未套用；舊定位可能有欄位問題','舊全文':old.decode(),'舊SHA256':hashlib.sha256(old).hexdigest(),'擬新全文':new,'擬新SHA256':hashlib.sha256(new.encode()).hexdigest(),'非來源文字異動':0};rows.append(row)
 filename='qi-zheng-si-yu/knowledge/'+p.name;patch.extend(difflib.unified_diff(old.decode().splitlines(True),new.splitlines(True),fromfile='a/'+filename,tofile='b/'+filename))
assert len(rows)==34
report={'日期':'2026-11-26','候選數':34,'卡片異動':0,'限制':'來源範圍由現有引用和舊定位頁形成預覽；不是把舊定位當正確答案。原圖年欄、值欄、擎遊配側都要分開確認，不能直接批量套用。預覽不動字值，亦不代表字值正確。','明細':rows}
(D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(D/(stem+'.patch')).write_text(''.join(patch))
md=['# 綱目上表來源頁碼34候選','','## 注意','','34張現卡的來源引用未包含舊報告定位的值欄頁。這是**待核候選，不是已判定34張都錯**；本次沒有改任何卡。','擬跨頁範圍只提供可逐項審閱的完整預覽。要先確認原圖的年份與該欄位置；擎遊未分配側等疑點仍另處理，不能用改頁碼把字值問題遮掉。','[34張舊全文、擬新全文與SHA256]('+stem+'.json)；[只含來源範圍的預覽差異]('+stem+'.patch)。','','## 逐項預覽','','|編號|卡片|現列頁範圍|舊定位頁|擬列範圍（未套用）|原圖|','|---|---|---|---|---|---|']
for r in rows:md.append(f'|{r["編號"]}|{r["卡片"]}|'+ '、'.join(f'{x["起頁"]}–{x["迄頁"]}' for x in r['目前引用'])+f'|{r["舊定位實際頁"]}|{r["擬列來源範圍"]}|[紅框](../{r["舊原圖"].removeprefix("docs/")})|')
md+=['','## 需要確認','','逐項確認紅框值欄屬於卡名年份，且擬列頁範圍包含正確位置後，才可授權套用；不確定的保留。這份預覽沒有補卡，也沒有改原值。','28筆無此題名卡是這148筆局部抽查的缺口，不等於全庫登籍缺卡數；31組登籍原圖待確認另見[入口](../待你處理.md)。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
print(json.dumps({'來源範圍候選':len(rows),'非來源文字異動':0,'卡片異動':0},ensure_ascii=False))
