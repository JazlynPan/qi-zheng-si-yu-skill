"""執行：只為未定位候選縮短文字層錨點；原字仍待人工看圖，不改卡。"""
from review_helpers import *
import collections
p=D/'形近字批量修訂清單.json';data=json.loads(p.read_text());fixed=[]
for r in data['明細']:
 if r['定位']!='僅附引用頁紅框；未定位字位':continue
 doc=pdf(r['書名']);before=shape(r['前文']);after=shape(r['後文']);found=[]
 if not doc:continue
 # 不限制目標字讀成何字；定位僅靠兩側原文，至少共6字。
 for size in [4,3]:
  bb=before[-size:];aa=after[:size]
  if len(bb)+len(aa)<6:continue
  for pgno in range(r['起頁'],min(r['迄頁'],len(doc))+1):
   raw,boxes=pagechars(r['書名'],pgno);s=shape(raw)
   for i in range(len(s)):
    if bb and s[max(0,i-len(bb)):i]!=bb:continue
    if aa and s[i+1:i+1+len(aa)]!=aa:continue
    found.append((pgno,boxes[i],raw[i]))
  if found:break
 if len(found)!=1:continue
 pgno,box,glyph=found[0];pg=doc[pgno-1];cl=(box+(-70,-35,70,35))&pg.rect;pix=pg.get_pixmap(matrix=fitz.Matrix(3,3),clip=cl);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);pan=Image.new('RGB',(700,im.height+70),'white');pan.paste(im,(0,70));dr=ImageDraw.Draw(pan);dr.text((8,5),r['編號']+f' PDF{pgno} 依兩側原文定位；原字待看圖',font=FONT,fill='black');dr.rectangle(((box.x0-cl.x0)*3,(box.y0-cl.y0)*3+70,(box.x1-cl.x0)*3,(box.y1-cl.y0)*3+70),outline='red',width=3);dest=PIC/'全庫形近字'/(r['編號']+'-補定位.png');pan.save(dest)
 old=r['原圖'];r.update({'原圖':str(dest.relative_to(ROOT)),'定位':'兩側原文唯一定位；不以目標字讀值判定','原圖實際頁碼':pgno,'文字層對應字':glyph,'判斷':'待看原圖','問題':f'請看紅框內的字，是「{r["現字"]}」還是「{r["候選字"]}」？'})
 fixed.append({'編號':r['編號'],'原引用頁圖':old,'原圖':r['原圖']})
data['定位分布']=dict(collections.Counter(r['定位']for r in data['明細']));p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');save('形近字補定位結果.json',{'補定位數':len(fixed),'剩餘未定位':sum(r['定位']=='僅附引用頁紅框；未定位字位'for r in data['明細']),'明細':fixed})
md=D/'形近字批量修訂清單.md';s=md.read_text()
for r in data['明細']:
 if r['定位']!='兩側原文唯一定位；不以目標字讀值判定':continue
 lines=s.splitlines();s='\n'.join(re.sub(r'\[引用頁範圍，未定位字位\]\([^)]*\)',f'[補定位原圖](../{r["原圖"].removeprefix("docs/")})',line)if line.startswith('|'+r['編號']+' ')else line for line in lines)+'\n'
s+='\n## 補定位核對\n\n'+f'以兩側至少6字唯一定位補足{len(fixed)}筆；目標字讀值沒有作定位條件。尚餘{sum(r["定位"]=="僅附引用頁紅框；未定位字位"for r in data["明細"])}筆未定位到字，仍不得稱已核。\n';md.write_text(s);print(data['定位分布'])
