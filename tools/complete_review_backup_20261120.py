"""執行：fixed、t15、t17分批落實使用者裁決；每批保存舊新全文、SHA256及差異。
目錄：helpers（交易與留存）；fixed（已確認字值）；fragments（圖中文字追加）；main（分批執行）。
"""
from review_helpers import *
import subprocess,difflib,shutil,argparse
from collections import Counter,defaultdict
DEST=ROOT/'docs/勘校修訂/2026-11-20完整裁決';PLAN=json.loads((ROOT/'tools/review_decisions_data_20261120.json').read_text());CHANGES=[];SNAP={};BASE=''
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT).decode()
def start(stage):
 global SNAP,BASE
 DEST.mkdir(parents=True,exist_ok=True);assert not(DEST/(stage+'.json')).exists();BASE=git('rev-parse','HEAD').strip();SNAP={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in K.glob('*.md')}
def edit(p,new,why):
 old=p.read_bytes()if p.exists()else None;new=new.encode()if isinstance(new,str)else new
 if old==new:return
 CHANGES.append({'檔案':str(p.relative_to(ROOT)),'理由':why,'舊全文':old.decode()if old is not None else None,'新全文':new.decode(),'舊SHA256':hashlib.sha256(old).hexdigest()if old is not None else None,'新SHA256':hashlib.sha256(new).hexdigest()});p.write_bytes(new)
def card(name,payload):return '#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n'+payload+'\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n'
def entry_remove(keys):
 p=ROOT/'docs/待你處理.md';s=p.read_text();lines=[]
 for line in s.splitlines():
  if line.startswith('- ')and line[2:].split('｜')[0]in keys:continue
  lines.append(line)
 s='\n'.join(lines)+'\n';groups=[len(re.findall(r'^- ',v,re.M))for v in re.split(r'^## ',s,flags=re.M)[1:]];s=re.sub(r'待處理共\d+項（有圖\d+、規則\d+、等補圖\d+',f'待處理共{sum(groups)}項（有圖{groups[0]}、規則{groups[1]}、等補圖{groups[2]}',s);p.write_text(s)
def finish(stage,details):
 names={p.name for p in K.glob('*.md')};assert set(SNAP)<=names
 changed={n for n in SNAP if hashlib.sha256((K/n).read_bytes()).hexdigest()!=SNAP[n]};new=names-set(SNAP);expected={Path(r['檔案']).name for r in CHANGES if r['檔案'].startswith('qi-zheng-si-yu/knowledge/')};assert changed|new==expected
 obj={'日期':'2026-11-20','基準提交':BASE,'授權來源':'使用者完整裁決＋qizheng_review_backup.json；本輪文字及T21-1後續回覆優先','修改既有卡':len(changed),'新增卡':len(new),'其餘舊卡異動':0,'刪卡':0,'目前卡數':len(names),'處理明細':details,'完整舊新與SHA256':CHANGES};(DEST/(stage+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 diff=''.join(''.join(difflib.unified_diff((r['舊全文']or'').splitlines(True),r['新全文'].splitlines(True),fromfile='舊/'+r['檔案'],tofile='新/'+r['檔案']))for r in CHANGES);(DEST/(stage+'.patch')).write_text(diff)
 with(ROOT/'docs/勘校修訂紀錄.md').open('a')as f:f.write('\n## 2026-11-20　【勘校修正】完整裁決-'+stage+'\n\n依使用者本輪原圖裁決執行；既有卡修訂'+str(len(changed))+'張、新增'+str(len(new))+'張，其餘舊卡異動0，不刪卡。[完整舊新全文與SHA256](勘校修訂/2026-11-20完整裁決/'+stage+'.json)、[差異](勘校修訂/2026-11-20完整裁決/'+stage+'.patch)。讀序、分格、重複與待確認項另見本批報告。\n')
 with(ROOT/'docs/決定紀錄.md').open('a')as f:f.write('2026-11-20｜完整裁決-'+stage+'｜依使用者本輪逐項文字與附件裁決；T21-1後續回覆記簊金｜'+str(len(changed))+'張舊卡限定修訂、'+str(len(new))+'張新增；所有舊全文與SHA256留存，不刪既有檔案。\n')
 p=ROOT/'docs/狀態.md';s=p.read_text();s=re.sub(r'共[\d,]+張；綱目[\d,]+張',f'共{len(names):,}張；綱目{sum("星學綱目正傳" in (K/n).read_text() for n in names):,}張',s,count=1);s=s.replace('復工位置：','復工位置：完整裁決-'+stage+'已保存（修'+str(len(changed))+'、新'+str(len(new))+'）；',1);p.write_text(s)
 print(json.dumps({k:v for k,v in obj.items()if k not in ['處理明細','完整舊新與SHA256']},ensure_ascii=False))
def fixed():
 start('定字與既有核對');attachment=Path('/tmp/codex-remote-attachments/6af9f7e7-b9d0-8191-bca3-7a0654c7d0bd/51620374-0373-46c8-bf9a-158d79aec490/1-qizheng_review_backup.json');shutil.copyfile(attachment,DEST/'使用者備份原檔.json');details=[]
 ops={'亥宮火':[('天縻','天纛')],'子宮木':[('不淨地','不淂地')],'寅宮金':[('不淨地','不淂地')],'酉宮火':[('不淨地','不淂地')],'寅宮日':[('天柔','天桑')],'寅宮炁':[('天飾','天餙')],'辰宮月':[('天睿','天璿')]}
 for stem,pairs in ops.items():
  p=K/(stem+'圖列（星平總會命海）.md');s=p.read_text()
  for a,b in pairs:assert s.count('\n\n'+a+'\n\n')==1;s=s.replace('\n\n'+a+'\n\n','\n\n'+b+'\n\n',1)
  edit(p,s,'T14本輪新增授權，原頁16，只改指定值');details.append({'項目':stem,'頁碼':16,'替換':pairs})
 # 先前已完成的18題與旁註不重複套用。
 prior=json.loads((ROOT/'docs/勘校修訂/2026-11-20-T14伏尸使用者授權-T14.json').read_text())
 assert all((K/r['卡名']).read_text()==r['新全文']for r in prior['明細']);assert '\n\n享福\n\n'in (K/'亥宮孛圖列（星平總會命海）.md').read_text()
 # 使用者後續答覆簊金：只記原字，不改成箕、不推定歸屬取法。
 edit(K/'正廟左旁簊金字列（星學綱目第98頁）.md',card('', '《星學綱目正傳》第98頁：\n\n原文以圖表呈現\n\n正廟\n\n簊金'),'T21-1後續回覆採簊金；不含斜線，不推定左旁標記取法')
 edit(K/'貴元圖列·己巳（星學綱目圖說下）.md',card('', '《星學綱目正傳》第83–84頁〈六十年甲子圖〉：\n\n原文以圖表呈現\n\n己巳\n\n貴元\n\n戌'),'CY-己巳貴元使用者原圖確認戌，不採外書木／水')
 for fn in ['催官貴元跨頁抽查.json','催官貴元抽查使用者回覆.json']:
  p=D/fn;x=json.loads(p.read_text());row=next(r for r in x['明細']if r['編號']=='CY-23');row['狀態']='使用者本輪原圖確認';row['套用狀態']='已新增貴元己巳戌字列卡，外書參考保留作歷史';row['來源類型']='使用者人工校讀'
  if '原圖值'in row:row['原圖值']='戌';row['問題']='使用者已確認戌，不重複詢問。'
  else:row['使用者讀值']='戌'
  x['使用者讀值已確認']=28;x['底本未確認']=0
  if '狀態分布'in x:x['狀態分布']=dict(Counter(r['狀態']for r in x['明細']))
  edit(p,json.dumps(x,ensure_ascii=False,indent=2)+'\n','CY-23原圖讀值更新；完整原始紀錄另存舊全文')
 p=D/'催官貴元跨頁抽查.md';old=p.read_text();edit(p,old+'\n## 2026-11-20完整裁決更新\n\nCY-23己巳貴元：使用者確認原圖第83–84頁讀值戌，已補卡；抽查28項均有使用者讀值。上方27／1與木／水是歷史快照，不再代表目前待核狀態。完整舊新與SHA256存入完整裁決紀錄。\n','補註最新確認，不抹除歷史')
 suidian=json.loads((ROOT/'docs/勘校修訂/2026-11-20歲殿16張回填.json').read_text())['明細'];check=[]
 for r in suidian:
  if r['年份']=='戊寅':continue
  text=(K/r['卡名']).read_text();assert '\n\n'+r['新值']+'\n'in text;check.append({'卡名':r['卡名'],'原頁':r['修訂後頁碼'],'紅框圖':r['紅框圖路徑'],'先前舊值':r['舊值'],'本輪前現值':r['新值'],'本輪裁決':r['新值'],'處理':'已套用，本輪不重複改寫'})
 fs=json.loads((ROOT/'docs/勘校修訂/2026-11-20-T14伏尸使用者授權-伏尸.json').read_text());assert (K/fs['明細'][0]['卡名']).read_text()==fs['明細'][0]['新全文'];details+=check;details.append({'T22':'十二值與上輪修訂完全一致，保留現卡兩段，不再改一次'})
 for n in ['歲殿圖列·戊寅（星學綱目圖說下）.md','登籍圖列·己丑（星學綱目圖說下）.md']:assert (K/n).exists();details.append({'原圖空白卡':n,'處理':'現卡保持不動，他書理論值只列報'})
 entry_remove({'T14-03','T14-18','T14-20','T14-21','T14-13／19／24','T14-15','T21-1'})
 lines=['# 完整裁決：定字與既有核對','','## 本次處理','','T14新增授權7卡7值已套用；先前16卡19值已核相同，不重複改寫。亥宮孛享福原註相同、主阻滯及主喜怒維持。','T21-1依後續回覆記簊金，新增原字卡；CY-23依原圖確認戌，新增字列卡並更新抽查紀錄，不取外書木水。','T22伏尸十二值已核與前輪完全一致，同檔兩段保持不變，不刪檔。','','## T07十五張逐卡核對','','|卡名|原頁|先前舊值|本輪前現值／本輪裁決|紅框圖|','|---|---|---|---|---|']
 for r in check:lines.append(f'|{r["卡名"]}|{r["原頁"]}|{r["先前舊值"]}|{r["本輪前現值"]}／{r["本輪裁決"]}|[原圖](../{r["紅框圖"].removeprefix("docs/")})|')
 lines+=['','## 原圖空白與理論值','','戊寅歲殿77–78頁、己丑登籍75–76頁維持現卡，不用理論覆蓋空白。庫內原書頁核對另見本輪總報告；戊寅按歲殿法可得午，己丑登籍只能在採共值／歲殿同法的前提下條件式得午，不能當原圖有字。','T21-1新卡只記簊金原字及正廟題名，不把它當作已知星宿或補出取法。']
 (D/'完整裁決定字與十五歲殿核對-2026-11-20.md').write_text('\n'.join(lines)+'\n');finish('定字與既有核對',details)

def fragments(stage):
 start(stage);source=json.loads((D/(stage+'逐條紅框對照.json')).read_text())['明細'];byid={int(r['編號'].split('-')[1]):r for r in source};values=PLAN[stage+'定稿'];grouped=defaultdict(list);details=[]
 for num,parts in values.items():
  n=int(num);r=byid[n];grouped[r['卡片']].append((r,parts))
 for name,items in grouped.items():
  p=K/name;old=p.read_text();s=old
  if stage=='T17':
   for a,b in PLAN['T17現卡替換'].get(name,[]):assert s.count(a)==1,(name,a);s=s.replace(a,b,1)
  added=[]
  for r,parts in items:
   for part in parts:
    assert not any(c in part for c in ['?','？','/','（','）']),part
    if part.replace('臺','台')in s.replace('臺','台') or part in added:action='既有引文或本批已涵蓋，僅保留此圖位對照'
    else:added.append(part);action='依獨立格／直行原文追加'
    details.append({'編號':r['編號'],'卡名':name,'頁碼':r['原圖頁碼'],'原圖':r['原圖'],'原圖框位':r['原圖框位'],'原文片段':part,'處理':action})
  if added:
   page=items[0][0]['原圖頁碼'];book='星平總會命海'if stage=='T15'else'河洛五星合參案例抄本';s+='\n《'+book+'》第'+str(page)+'頁：\n\n原文以圖表呈現\n\n'+'\n\n'.join(added)+'\n'
  edit(p,s,stage+'使用者校讀；追加獨立格與正確直行／右至左讀序，舊引文保留。T17明列衝突原字另以指定詞組限定替換。')
 if stage=='T15':details.append({'重複切片不再收':PLAN['T15重複'],'保留未確認':PLAN['T15保留未確認'],'原圖補核':PLAN['T15原圖補核']})
 else:details.append({'排除卦象圖形':PLAN['T17排除圖形'],'排除重複切片':PLAN['T17重複切片'],'保留未確認':PLAN['T17保留未確認'],'說明':'排除只作用於本次候選與追加，不刪任何既有卡檔；重複短語只追加一次，全部圖位保存在明細'})
 lines=['# 完整裁決：'+stage+'逐條整理','','## 目錄','','- [處理界線](#處理界線)','- [逐條原圖與定字](#逐條原圖與定字)','- [排除與仍須確認](#排除與仍須確認)','','## 處理界線','','保留舊引文；跨格詞分成獨立文字片段，不把斜線、下一格註或問號放入卡片。反覆出現的相同片段只追加一次，來源圖位逐筆保留。','T17明列原句衝突在卡內修正，原句全文與SHA256保存於修訂紀錄；不刪任何既有檔案。','','## 逐條原圖與定字','','|編號|卡名／PDF頁|本次原文片段|處理|原圖|','|---|---|---|---|---|']
 for x in details[:-1]:lines.append(f'|{x["編號"]}|{x["卡名"]}／{x["頁碼"]}|{x["原文片段"]}|{x["處理"]}|[紅框圖]({x["原圖"]})|')
 lines+=['','## 排除與仍須確認','','```json',json.dumps(details[-1],ensure_ascii=False,indent=2),'```'];(D/('完整裁決-'+stage+'逐條整理-2026-11-20.md')).write_text('\n'.join(lines)+'\n');finish(stage,details)
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('stage',choices=['fixed','T15','T17']);a=ap.parse_args()
 if a.stage=='fixed':fixed()
 else:fragments(a.stage)
