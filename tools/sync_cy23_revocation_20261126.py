"""執行：依第四輪既有決定同步CY-23摘要；保留文件舊新全文，不改卡。"""
from review_helpers import *
from collections import Counter
stem='CY23舊摘要同步-2026-11-26';a=ROOT/'docs/勘校修訂'/stem
assert not (K/'貴元圖列·己巳（星學綱目圖說下）.md').exists()
assert a.exists() is False,'已同步，不再重複套用'
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.md')};files=[]
p=D/'催官貴元跨頁抽查.json';old=p.read_bytes();j=json.loads(old)
r=next(r for r in j['明細'] if r['編號']=='CY-23');r['前輪已撤銷快照']={k:r.get(k) for k in ['現值','原圖值','狀態','問題','套用狀態','目前卡值','目前卡頁碼']}
r.update({'現值':None,'原圖值':'貴元原字未確認；戌屬歲殿／登籍共值','狀態':'第四輪已撤銷錯補，貴元待核','問題':'不再詢問是否採戌；第四輪已決定撤銷，未另確認貴元星名','套用狀態':'錯補的貴元己巳戌卡已撤銷歸檔；己巳歲殿、登籍另有戌卡，不拿來回填貴元','目前卡值':None,'目前卡頁碼':None,'撤銷依據':'docs/決定紀錄.md：2026-11-21第四輪使用者授權；docs/檢查/第四輪授權修訂-2026-11-21.md'})
j['日期']='2026-11-26';j['使用者讀值已確認']=27;j['底本未確認']=1;j['狀態分布']=dict(Counter(r['狀態'] for r in j['明細']));j['說明']='目前27項沿用使用者確認；CY-23己巳貴元戌已依第四輪撤銷，原貴元星名未確認。前輪戌已補卡說法只作歷史快照，不再代表現狀。不得恢復錯補卡。'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n');files.append({'檔案':str(p.relative_to(ROOT)),'舊全文':old.decode(),'舊SHA256':hashlib.sha256(old).hexdigest(),'新全文':p.read_text(),'新SHA256':hashlib.sha256(p.read_bytes()).hexdigest()})
p=D/'催官貴元跨頁抽查.md';old=p.read_bytes();lines=old.decode().splitlines()
for i,line in enumerate(lines):
 if line.startswith('|貴元圖列·己巳（星學綱目圖說下）.md|'):
  lines[i]='|貴元圖列·己巳（星學綱目圖說下）.md|貴元／原欄星名字待核|無現卡／84|已撤銷錯補|貴元原字未確認|第四輪已撤銷戌錯補；戌屬歲殿／登籍，不回填貴元；不重問已決定事項。|[原圖](../待裁決/原圖/科甲欄/CY-23.png)|'
lines+=['','## 2026-11-26同步第四輪撤銷','','上一段「CY-23戌已補卡、28項均已確認」是2026-11-20快照，已被2026-11-21第四輪決定取代。錯補貴元己巳戌卡已撤銷，原貴元星名仍未確認；戌另屬己巳歲殿、登籍，不恢復貴元錯卡。現在27項沿用確認、1項撤錯待核。','[第四輪修訂](第四輪授權修訂-2026-11-21.md)；[文件舊新全文與SHA256](../勘校修訂/'+stem+'/文件舊新全文與SHA256.json)。']
p.write_text('\n'.join(lines)+'\n');files.append({'檔案':str(p.relative_to(ROOT)),'舊全文':old.decode(),'舊SHA256':hashlib.sha256(old).hexdigest(),'新全文':p.read_text(),'新SHA256':hashlib.sha256(p.read_bytes()).hexdigest()})
a.mkdir();(a/'文件舊新全文與SHA256.json').write_text(json.dumps({'日期':'2026-11-26','依據':'既有2026-11-21第四輪決定，不新增決定、不改卡','文件':files,'卡片異動':0},ensure_ascii=False,indent=2)+'\n')
(D/(stem+'.md')).write_text('# CY-23舊摘要同步\n\n抽查JSON仍將已撤銷的己巳貴元戌列為現值，MD末段亦仍寫已補卡。依既有第四輪授權同步為撤錯待核，保留前輪快照與完整舊新全文。\n\n卡片新增0、修改0、刪除0；文件同步2份。現在27項沿用確認、1項貴元星名未確認。\n\n[舊新全文與SHA256](../勘校修訂/'+stem+'/文件舊新全文與SHA256.json)；[第四輪依據](第四輪授權修訂-2026-11-21.md)。\n')
with (ROOT/'docs/勘校修訂紀錄.md').open('a') as f:f.write('\n## 2026-11-26【文件同步】CY-23撤銷狀態\n\n只同步舊抽查摘要，不改卡、不新增決定；貴元己巳戌仍為已撤銷。[兩份文件的舊新全文與SHA256](勘校修訂/'+stem+'/文件舊新全文與SHA256.json)。\n')
assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==h for n,h in before.items())
print(json.dumps({'同步文件':2,'卡片異動':0,'沿用確認':27,'撤錯待核':1},ensure_ascii=False))
