"""執行：先prepare列逐格預覽，再t14或fs套用；verify核對指定替換外零異動。
目錄：PLAN（授權值）、prepare（完整舊新稿）、apply（限定替換）、verify（全庫邊界）。
"""
from review_helpers import *
import argparse,subprocess,shutil
DATE='2026-11-20';PREFIX='2026-11-20-T14伏尸使用者授權'
PLAN={1:[('長生星','玉璽星')],2:[('天臂星','天暉星')],4:[('天旺','天聰')],5:[('天溫星','天濕星')],6:[('天宗','天琮'),('喜宮','入廟')],7:[('閑宮星','困苦星')],8:[('天垣','天空'),('富貴','主孤獨')],10:[('天空','玉垣'),('主孤獨','富貴')],12:[('天娼','天姬')],14:[('天災','天坎')],16:[('天元','天亢')],17:[('天醜','天酷')],22:[('主清高','主清廟')],23:[('天祿','天慘')],25:[('相火同','拍火同')],26:[('絕根星','絕祿星')]}
FORBIDDEN=[3,13,15,18,19,20,21,24,27]
FSNEW=['子虛二','丑女二','寅尾四十','卯尾一','辰角一','巳軫十','午星二','未柳四','申井一','酉畢四','戌婁一','亥壁五']
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT).decode()
def path(stage):return ROOT/'docs/勘校修訂'/f'{PREFIX}-{stage}.json'
def replace_exact(raw,ops):
 for old,new in ops:
  a=('\n\n'+old+'\n\n').encode();b=('\n\n'+new+'\n\n').encode()
  if '\n' in old:a=(old+'\n').encode();b=(new+'\n').encode()
  assert raw.count(a)==1,(old,raw.count(a));raw=raw.replace(a,b,1)
 return raw

def prepare():
 assert not path('T14').exists()and not path('伏尸').exists()
 base=git('rev-parse','HEAD').strip();source=json.loads((D/'命海16_T14本輪逐筆複核.json').read_text())['明細'];byid={int(r['編號'].split('-')[1]):r for r in source};rows=[]
 for no,ops in PLAN.items():
  r=byid[no];name=r['卡片'];old=(K/name).read_bytes();new=replace_exact(old,ops);rows.append({'編號':r['編號']+('/09'if no==8 else'/11'if no==10 else''),'卡名':name,'原頁':16,'替換':ops,'原圖':r['原圖'],'舊全文':old.decode(),'新全文':new.decode(),'舊SHA256':hashlib.sha256(old).hexdigest(),'新SHA256':hashlib.sha256(new).hexdigest()})
 assert all(byid[n]['卡片']not in {r['卡名']for r in rows}for n in FORBIDDEN if n!=15)
 assert '\n\n主阻滯\n\n'in next(r['新全文']for r in rows if r['編號']=='T14-14')
 assert '\n\n享福\n\n'in next(r['舊全文']for r in rows if r['編號']=='T14-04')
 snapshot={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in K.glob('*.md')}
 rec={'日期':DATE,'授權':'使用者本輪逐項授權；只改指定值，其餘位元組保留','基準提交':base,'原卡總數':len(snapshot),'修改卡數':16,'替換欄值數':sum(len(x['替換'])for x in rows),'T14-04旁註核對':'現卡享福與使用者相同，原字保留，旁註異動0','禁止修改卡':{byid[n]['卡片']:snapshot[byid[n]['卡片']]for n in FORBIDDEN if n!=15},'保護同卡欄位':{'T14-15':'子宮火卡的主阻滯逐字保留，只改T14-14曜名'},'明細':rows};path('T14').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
 # 第100頁實檔只有一張，第二段是同檔第二引文，不新增／刪除／合併卡片。
 name='伏尸已核並列字列（星學綱目第100頁續表）.md';old=(K/name).read_bytes();ops=[('辰角二\n巳軫十','辰角一\n巳軫十'),('午星三\n未柳四','午星二\n未柳四'),('申井二\n酉畢四','申井一\n酉畢四'),('寅尾十四\n戌婁一','寅尾四十\n戌婁一')];new=replace_exact(old,ops)
 fs={'日期':DATE,'基準提交':base,'原卡總數':len(snapshot),'使用者十二值':FSNEW,'處理方式':'實際只有一個卡檔、兩段引文。保留兩段和現有順序，只改四個指定值；第二段更新為寅尾四十、戌婁一。不重排、不增刪卡。','明細':[{'卡名':name,'替換':ops,'原頁':100,'原圖':'docs/待裁決/原圖/綱目100整欄/伏尸-整欄紅框.png','舊全文':old.decode(),'新全文':new.decode(),'舊SHA256':hashlib.sha256(old).hexdigest(),'新SHA256':hashlib.sha256(new).hexdigest()}]};path('伏尸').write_text(json.dumps(fs,ensure_ascii=False,indent=2)+'\n')
 for stage,rec in [('T14',rec),('伏尸',fs)]:
  lines=['# '+stage+'授權修訂前逐格清單','','日期：2026-11-20。先讀現卡與授權值、產生本清單及完整舊新稿，再執行限定替換。','','|格／卡名|舊值|授權新值|原PDF頁|紅框原圖|','|---|---|---|---|---|']
  if stage=='T14':
   for r in rec['明細']:
    for old,new in r['替換']:lines.append(f'|{r["編號"]} {r["卡名"]}|{old}|{new}|16|[原圖](../{r["原圖"].removeprefix("docs/")})|')
   lines+=['','亥宮孛旁註現為「享福」，與授權相同：保留，不補字、不改旁註。','卯宮月現旁註「喜宮」與授權「入廟」不同，已列為明確授權替換，並非自行補註。','','## 與舊候選不同的三筆','','T14-05：現天溫星、舊候選天漫星、使用者天濕星。T14-22：現主清高、舊候選主清貴、使用者主清廟。T14-25：現相火同、舊候選柏火同、使用者拍火同。只按本輪授權，不把三者視為同字。']
   picdir=PIC/'本輪T14授權';picdir.mkdir(parents=True,exist_ok=True)
   for n in [5,22,25]:
    r=byid[n];dest=picdir/(r['編號']+'-原生放大.png');shutil.copyfile(ROOT/r['原圖'],dest);lines+=['',f'![{r["編號"]}原生圖放大](../{str(dest.relative_to(ROOT)).removeprefix("docs/")})']
  else:
   olds=re.findall(r'^[子丑寅卯辰巳午未申酉戌亥][虛女尾角軫星柳井畢婁壁][一二三四五十]+$',rec['明細'][0]['舊全文'],re.M);assert len(olds)==12;oldmap={v[0]:v for v in olds}
   for i,new in enumerate(FSNEW,1):lines.append(f'|{new[0]}／{name}|{oldmap[new[0]]}|{new}|100|[原圖](../待裁決/原圖/綱目100整欄/FS-{i:02d}.png)|')
   lines+=['','只有四值改動，其餘八值維持。實際不是兩個卡片檔：既有檔的第一段10項、第二段2項。保留兩段，第二段寅改為尾四十；兩段合計十二支各一次，不留下尾十四的相反版本。闌干一律不動。']
  (D/f'{stage}授權修訂前清單-2026-11-20.md').write_text('\n'.join(lines)+'\n')
 print('已備T14 16卡19值、伏尸1卡4值完整舊新稿及逐格預覽；尚未改卡。')

def apply(stage):
 rec=json.loads(path(stage).read_text());before={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in K.glob('*.md')}
 for r in rec['明細']:
  p=K/r['卡名'];raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==r['舊SHA256'];new=replace_exact(raw,r['替換']);assert new.decode()==r['新全文'];p.write_bytes(new)
 actual={p.name for p in K.glob('*.md')if hashlib.sha256(p.read_bytes()).hexdigest()!=before[p.name]};assert actual=={r['卡名']for r in rec['明細']};assert len(before)==len(list(K.glob('*.md')))
 if stage=='T14':
  assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==h for n,h in rec['禁止修改卡'].items());allowed={f'T14-{n:02d}'for n in [1,2,4,5,6,7,8,9,10,11,12,14,16,17,22,23,25,26]}
 else:
  s=(K/rec['明細'][0]['卡名']).read_text();values=re.findall(r'^[子丑寅卯辰巳午未申酉戌亥][虛女尾角軫星柳井畢婁壁][一二三四五十]+$',s,re.M);assert len(values)==12 and len({x[0]for x in values})==12 and set(values)==set(FSNEW);allowed={'綱目100-伏尸'}
 p=ROOT/'docs/待你處理.md';s=p.read_text();lines=s.splitlines();removed=[];keep=[]
 for line in lines:
  key=line[2:].split('｜')[0]if line.startswith('- ')else''
  if key in allowed:removed.append(key)
  else:keep.append(line)
 s='\n'.join(keep)+'\n';s=re.sub(r'；本輪與上一輪已回填[^；]+；','；已確認並回填項目的全文見下方紀錄；',s);groups={x.splitlines()[0]:len(re.findall(r'^- ',x,re.M))for x in re.split(r'^## ',s,flags=re.M)[1:]};total=sum(groups.values());s=re.sub(r'待處理共\d+項（有圖\d+、規則\d+、等補圖\d+','待處理共'+str(total)+'項（有圖'+str(list(groups.values())[0])+'、規則'+str(list(groups.values())[1])+'、等補圖'+str(list(groups.values())[2]),s);p.write_text(s)
 with(ROOT/'docs/決定紀錄.md').open('a')as f:f.write(DATE+'｜'+stage+'逐項修訂授權｜依本輪使用者原圖讀值套用；完整授權值與舊新全文已保存｜'+('16張19值，未授權9題與旁註享福不動；天濕、清廟、拍火同採本輪確認。'if stage=='T14'else'伏尸同檔兩段只改四值；十二支校驗一致，闌干與貫索未動。')+'\n')
 with(ROOT/'docs/勘校修訂紀錄.md').open('a')as f:f.write('\n## '+DATE+'　【勘校修正】'+stage+'使用者授權\n\n授權日期2026-11-20。只改指定值，其他位元組不變；[修訂前逐格清單](檢查/'+stage+'授權修訂前清單-2026-11-20.md)、[完整舊新全文](勘校修訂/'+PREFIX+'-'+stage+'.json)。'+('亥宮孛原註享福已核相同；卯宮月喜宮依明確授權改入廟。'if stage=='T14'else rec['處理方式'])+'\n')
 p=ROOT/'docs/狀態.md';s=p.read_text();s=s.replace('## 現在停在哪\n','## 現在停在哪\n',1);s=s.replace('階段1.5未驗收，未進階段2；','階段1.5未驗收，未進階段2；'+stage+'本輪授權已套用（'+str(len(actual))+'卡），舊新全文已存；',1);p.write_text(s)
 save(stage+'授權限定修改驗證-2026-11-20.json',{'日期':DATE,'本批修改卡數':len(actual),'本批替換值數':sum(len(r['替換'])for r in rec['明細']),'全庫逐檔核對數':len(before),'其餘卡異動':0,'卡片增刪':0,'只改授權字值其餘位元組一致':True,'移除已決入口項':removed,'剩餘入口項':total,'驗證限制':'本輪使用者裁字；腳本只驗證邊界與字值，不冒稱獨立原圖評分。'})
 print(stage,sorted(actual),'入口剩餘',total)
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=['prepare','t14','fs']);a=ap.parse_args()
 if a.mode=='prepare':prepare()
 else:apply('T14'if a.mode=='t14'else'伏尸')
