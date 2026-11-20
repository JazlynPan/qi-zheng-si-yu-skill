"""執行：在既有引用頁，以上下文定位37筆未定位字；只備原圖，不改卡。
定位暫時折合醜／丑是為避免文字轉換器對干支的不同處理，絕不回寫原文。
"""
from review_helpers import *
from collections import Counter

def folded(s):return shape(s).replace('醜','丑')
def main():
 out=D/'形近字37筆補定位-2026-11-20.json';assert not out.exists()
 data=json.loads((D/'形近字批量修訂清單.json').read_text());rows=[]
 for r in data['明細']:
  if r['定位']!='僅附引用頁紅框；未定位字位':continue
  b=folded(r['前文']);a=folded(r['後文']);doc=pdf(r['書名']);found=[];method=''
  if doc:
   for mode in ['雙側至少6字','單側至少6字']:
    for n in range(r['起頁'],min(r['迄頁'],len(doc))+1):
     raw,boxes=pagechars(r['書名'],n);s=folded(raw)
     for i in range(len(s)):
      if mode=='雙側至少6字':
       ok=len(b[-3:])+len(a[:3])>=6 and s[max(0,i-3):i]==b[-3:] and s[i+1:i+4]==a[:3]
      else:
       ok=(len(b)>=6 and s[max(0,i-len(b)):i]==b)or(len(a)>=6 and s[i+1:i+1+len(a)]==a)
      if ok:found.append((n,i,boxes[i],raw))
    found=list({(v[0],v[1]):v for v in found}.values())
    if len(found)==1:method=mode;break
    found=[]
  row={'編號':r['編號'],'書名':r['書名'],'卡名':r.get('卡名',r.get('卡片')),'現字':r['現字'],'候選字':r['候選字'],'前文':r['前文'],'後文':r['後文'],'引用頁碼':[r['起頁'],r['迄頁']],'原圖':None,'狀態':'未定位，仍待看原圖','定位條件':method,'來源類型':r.get('來源類型','文字層')}
  if len(found)==1:
   n,i,bb,raw=found[0];pg=doc[n-1];cl=(bb+(-100,-45,100,45))&pg.rect;pix=pg.get_pixmap(matrix=fitz.Matrix(3,3),clip=cl);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);pan=Image.new('RGB',(max(780,im.width),im.height+105),'white');pan.paste(im,(0,105));dr=ImageDraw.Draw(pan);dr.text((8,5),r['編號']+f' PDF第{n}頁：依語境定位，尚未裁決',font=FONT,fill='black');dr.text((8,35),f'請看紅框：是「{r["現字"]}」還是「{r["候選字"]}」？亦可回答兩者皆非／看不清',font=FONT,fill='black');dr.text((8,65),'紅框是字位，不是修改結論；未改卡片',font=FONT,fill='red');dr.rectangle(((bb.x0-cl.x0)*3,105+(bb.y0-cl.y0)*3,(bb.x1-cl.x0)*3,105+(bb.y1-cl.y0)*3),outline='red',width=3)
   dest=PIC/'形近字37筆補定位'/f'{r["編號"]}.png';dest.parent.mkdir(parents=True,exist_ok=True);pan.save(dest)
   row.update({'原圖':str(dest.relative_to(ROOT)),'原圖實際頁碼':n,'框位':list(bb),'文字層對應字':raw[i],'定位語境':raw[max(0,i-10):i]+'〔'+raw[i]+'〕'+raw[i+1:i+11],'狀態':'已依語境定位，原字待看圖裁決'})
  rows.append(row)
 obj={'日期':'2026-11-20','來源候選數':len(rows),'補定位數':sum(bool(r['原圖'])for r in rows),'仍未定位數':sum(not r['原圖']for r in rows),'卡片修改':0,'限制':'只用既有引用頁的語境定位；轉換器醜／丑差異只影響搜尋。字形仍以原頁圖判定，未自動修字。','明細':rows};save(out.name,obj)
 md=['# 形近字37筆補定位','','## 本次範圍','','不改卡；只在既有引用頁以兩側至少6字，或單側至少6字唯一語境定位。目標字不作搜尋條件。','醜／丑暫時折合只為避免文字轉換器影響干支搜尋，不更動卡片。紅框是字位，不代表已確認候選字。',f'共{len(rows)}筆；補定位{obj["補定位數"]}筆，仍未定位{obj["仍未定位數"]}筆。','','|編號|書名／頁碼|卡片現字／候選字|定位語境（文字層，非核定讀值）|原圖／狀態|','|---|---|---|---|---|']
 for r in rows:
  link=f'[紅框圖](../{r["原圖"].removeprefix("docs/")})'if r['原圖']else'未定位，不猜字'
  md.append(f'|{r["編號"]}|{r["書名"]} {r.get("原圖實際頁碼",str(r["引用頁碼"]))}|{r["現字"]}／{r["候選字"]}|{r.get("定位語境","")}|{link}|')
 (D/'形近字37筆補定位-2026-11-20.md').write_text('\n'.join(md)+'\n');print({k:v for k,v in obj.items()if k!='明細'})
if __name__=='__main__':main()
