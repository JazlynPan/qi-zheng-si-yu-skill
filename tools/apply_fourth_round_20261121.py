"""執行：第四輪使用者授權限定修訂；完整舊新卡、SHA256、差異與原圖留存。"""
from review_helpers import *
import subprocess,shutil,difflib
DATE='2026-11-21';A=ROOT/'docs/勘校修訂/第四輪-2026-11-21';I=PIC/'第四輪-2026-11-21';A.mkdir(exist_ok=False);I.mkdir(exist_ok=False)
base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip();before={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in K.glob('*.md')};records=[]
def edit(name,pairs,page):
 p=K/name;old=p.read_text();new=old
 for a,b in pairs:assert new.count(a)==1,(name,a);new=new.replace(a,b,1)
 assert new!=old
 records.append({'卡片':name,'處理':'修改','原頁':page,'舊全文':old,'新全文':new,'舊SHA256':hashlib.sha256(old.encode()).hexdigest(),'新SHA256':hashlib.sha256(new.encode()).hexdigest()});p.write_bytes(new.encode())
def frame(label,box,clip):
 src=Path('/workspace/review/ocr/綱目-100-原圖0.png');im=Image.open(src).convert('RGB');tile=im.crop(clip);tile=tile.resize((tile.width*4,tile.height*4));out=Image.new('RGB',(max(650,tile.width),tile.height+65),'white');out.paste(tile,(0,65));d=ImageDraw.Draw(out);d.text((5,5),label+'｜PDF第100頁',font=FONT,fill='black');d.text((5,30),'字值依第四輪使用者裁決；原圖作格位定位',font=FONT,fill='red');x0,y0,x1,y1=box;d.rectangle(((x0-clip[0])*4,65+(y0-clip[1])*4,(x1-clip[0])*4,65+(y1-clip[1])*4),outline='red',width=3);out.save(I/(label+'.png'))
frame('伏尸-寅-尾十四',[270,231,324,280],[264,0,327,603])
for label,y in [('午-張七',265),('申-井四',335),('戌-婁十',405),('寅-箕刀',545)]:frame('貫索-'+label,[110,y,169,y+43],[106,0,171,603])
frame('闌干-卯-尾刀',[170,472,223,515],[169,0,225,603])
for title in ['歲殿','登籍']:
 im=Image.open('/workspace/review/ocr/綱目-84-原圖0.png').convert('RGB');clip=(420,228,514,323);tile=im.crop(clip).resize((470,475));out=Image.new('RGB',(900,590),'white');out.paste(tile,(10,100));d=ImageDraw.Draw(out);d.text((5,5),f'己巳{title}共值戌｜PDF第83–84頁跨頁',font=FONT,fill='black');d.text((5,35),'第84頁右緣續欄；使用者已確認歲殿／登籍共值',font=FONT,fill='red');d.rectangle((10,180,310,530),outline='red',width=4);out.save(I/(f'己巳-{title}-84頁右緣.png'))
edit('伏尸已核並列字列（星學綱目第100頁續表）.md',[('寅尾四十','寅尾十四')],100)
edit('貫索已核並列字列（星學綱目第100頁續表）.md',[('午張二十','午張七'),('丑牛四\n','丑牛四\n\n申井四\n戌婁十\n寅箕刀\n\n【勘校修正】「刀」照原字記錄。通行字：初（據使用者雲端河洛抄本，同一手寫例並見（三二一刀）、（一初））。\n')],100)
edit('闌干已核並列字列（星學綱目第100頁續表）.md',[('巳翼十二\n','巳翼十二\n\n卯尾刀\n\n【勘校修正】疑註：圖糊。「刀」照原字記錄。通行字：初（據使用者雲端河洛抄本，同一手寫例並見（三二一刀）、（一初））。\n')],100)
for name,word,pno,more in [('命例·狀元沈懋學命（總會命海末卷兼載子平）.md','火井王',334,'，也可能是十一'),('命例·探花鄧以贊命（總會命海末卷兼載子平）.md','羅張王',333,'，也可能是十一'),('命例·狀元翁正春命（總會命海末卷兼載子平）.md','付壁九度',331,'')]:edit(name,[(word+'\n',word+'\n\n【勘校修正】疑註：原字待核'+more+'；維持「'+word+'」，未代改字。\n')],pno)
name='首例星盤邊欄文字（河洛五星合參案例抄本）.md';p=K/name;assert '火迫金龍' in p.read_text();assert '辰巳午' not in p.read_text();edit(name,[('母后\n','母后\n\n辰巳午\n')],2)
retired='貴元圖列·己巳（星學綱目圖說下）.md';old=(K/retired).read_text();dest=A/'撤銷卡';dest.mkdir();subprocess.run(['git','mv',str(K/retired),str(dest/retired)],check=True,cwd=ROOT);records.append({'卡片':retired,'處理':'撤銷並移出knowledge完整歸檔','原頁':'83–84','舊全文':old,'新全文':None,'舊SHA256':hashlib.sha256(old.encode()).hexdigest(),'歸檔SHA256':hashlib.sha256((dest/retired).read_bytes()).hexdigest(),'歸檔路徑':str((dest/retired).relative_to(ROOT))})
newnames=[]
for title in ['歲殿','登籍']:
 name=f'{title}圖列·己巳（星學綱目圖說下）.md';assert not(K/name).exists();t=f'#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n《星學綱目正傳》第83–84頁〈六十年甲子圖〉：\n\n原文以圖表呈現\n\n己巳\n\n{title}\n\n戌\n\n【勘校修正】年欄在第83頁，共值位於第84頁右緣跨頁續欄；原表歲殿／登籍聯列共用同一地支值。\n\n[紅框原圖](../../docs/待裁決/原圖/第四輪-2026-11-21/己巳-{title}-84頁右緣.png)\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n';(K/name).write_text(t);newnames.append(name);records.append({'卡片':name,'處理':'新增','原頁':'83–84（值在84頁右緣）','舊全文':None,'新全文':t,'新SHA256':hashlib.sha256(t.encode()).hexdigest()})
changed={r['卡片']for r in records if r['處理']=='修改'};assert len(changed)==7;assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==v for n,v in before.items()if n not in changed and n!=retired)
rows=['# 第四輪授權修訂','','|卡片／項目|舊值|新值或處理|原頁|','|---|---|---|---|','|伏尸寅|尾四十|尾十四|100|','|貫索午|張二十|張七|100|','|貫索申、戌、寅|未收|井四、婁十、箕刀|100|','|闌干卯|未收|尾刀，疑註圖糊|100|','|己巳貴元|戌|撤銷，全文移出知識庫歸檔|83–84|','|己巳歲殿、登籍|缺卡|各補戌，84頁右緣跨頁共值|83–84|','|沈懋學／鄧以贊／翁正春命|火井王／羅張王／付壁九度|原字不改，加疑註；前兩項另註也可能是十一|334／333／331|','|T17-040／052|040未收；052已為火迫金龍|040補辰巳午；052原字不改|河洛2|','','貫索原有9格中，午依本次明示更正，其餘8格逐字不動；補3格後為12格。闌干其他11格不動，補卯後12格。','新增與修改分列；撤銷卡完整保留，不刪舊全文。刀字不換初，旁註為使用者裁決，非偽作原文。','','## 原圖','']
for p in sorted(I.glob('*.png')):rows.append(f'- [{p.name}](../待裁決/原圖/第四輪-2026-11-21/{p.name})')
rows+=['','## 完整證據','','[舊新全文與SHA256](../勘校修訂/第四輪-2026-11-21/修訂全文與SHA256.json)。修改7張、新增2張、撤銷歸檔1張；其餘卡片雜湊不變。']
(D/'第四輪授權修訂-2026-11-21.md').write_text('\n'.join(rows)+'\n');result={'日期':DATE,'標記':'【勘校修正】','授權':'使用者第四輪逐項裁決','基準提交':base,'修改卡數':7,'新增卡數':2,'撤銷歸檔卡數':1,'其餘舊卡異動':0,'卡片總數':len(list(K.glob('*.md'))),'明細':records};(A/'修訂全文與SHA256.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');patch=''.join(''.join(difflib.unified_diff((r['舊全文']or'').splitlines(True),(r['新全文']or'').splitlines(True),fromfile='舊/'+r['卡片'],tofile='新/'+r['卡片']))for r in records);(A/'修訂差異.patch').write_text(patch)
for fn,line in [('docs/勘校修訂紀錄.md','\n## 2026-11-21【勘校修正】第四輪\n\n使用者授權伏尸寅尾十四、貫索四格與闌干卯尾刀；己巳貴元戌撤銷歸檔，改補歲殿與登籍戌；三命例保留原字加疑註，T17-040辰巳午補錄、052火迫金龍不動。\n\n[逐項舊新值與原頁](檢查/第四輪授權修訂-2026-11-21.md)；[舊新全文與SHA256](勘校修訂/第四輪-2026-11-21/修訂全文與SHA256.json)。\n'),('docs/決定紀錄.md','2026-11-21｜第四輪使用者授權｜伏尸寅尾十四；貫索午張七、申井四、戌婁十、寅箕刀；闌干卯尾刀圖糊；刀照原字加通行字註；己巳貴元戌撤銷，補歲殿登籍共戌；三命例保留原字加疑註；T17-040辰巳午、052火迫金龍｜限定本輪指定卡與格位，完整舊文及SHA256留存。\n')]:
 with(ROOT/fn).open('a')as f:f.write(line)
p=ROOT/'docs/待你處理.md';s=p.read_text();s='\n'.join(x for x in s.splitlines()if not x.startswith('- T17-040｜'))+'\n';p.write_text(s)
p=ROOT/'docs/狀態.md';s=p.read_text().replace('共20,078張；綱目5,514張','共20,079張；綱目5,515張');s=s.replace('CY己巳貴元戌及T21簊金已補卡，原圖空白兩卡保持不動。','第四輪己巳貴元戌錯卡已撤銷歸檔，歲殿／登籍戌已補；伏尸寅改尾十四、貫索四格與闌干卯已依授權更新。');s=s.replace('目前5處字疑：T15-016、T15-032、T15-075、T17-040、T17-082','目前4處字疑：T15-016、T15-032、T15-075、T17-082');s=s.replace('第100頁闌干整欄未確認前，不續核T22原暫停的其他項及貫索。','第100頁本輪指定伏尸、貫索與闌干卯已修；其他未授權格位不動。');p.write_text(s)
print(json.dumps({k:v for k,v in result.items()if k!='明細'},ensure_ascii=False))
