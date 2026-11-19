#!/usr/bin/env python3
"""執行：依實際題名重建28筆抽查及不同紅框，讀值取使用者回覆，不改卡。
目錄：picture（按題框位）、main（核定讀值、報告及來源界線）。
"""
import json,re,collections
from review_helpers import *
# 題名與物理大欄位置分開；科名不能因在續欄內而標成貴元。
BOX={'催官':(.0,.055,.10,.19),'祿勳':(.085,.055,.225,.175),'官印':(.085,.165,.225,.265),'玉堂':(.085,.235,.225,.34),'文魁':(.085,.315,.225,.435),'貴元':(.865,.04,1,.205),'科名':(.865,.395,1,.60)}
def picture(row,page):
 src=Path(f'/workspace/review/ocr/綱目-{page}-原圖0.png');w,h=Image.open(src).size;name=row['題名'];f=BOX[name];box=(f[0]*w,f[1]*h,f[2]*w,f[3]*h)
 dest=PIC/'科甲欄'/(row['編號']+'.png');label=f'{row["編號"]} {row["年份"]} 題名：{name} PDF{page}'
 if row['狀態']=='底本圖像缺邊，未確認':label+=' 原頁缺邊，不能補畫'
 framed_image(src,box,dest,label,scale=4,margin=20)
 return str(dest.relative_to(ROOT)),list(box)
def main():
 answers=json.loads((D/'催官貴元抽查使用者回覆.json').read_text());rows=[]
 for r in answers['明細']:
  name=r['題名'];y=r['年份'];odd=73+2*'子丑寅卯辰巳午未申酉戌亥'.index(y[1]);page=odd+1 if name in ['貴元','科名']else odd
  path=K/r['卡名'];old=None;span=None
  if path.exists():
   text=path.read_text();m=re.search(r'\n'+name+r'(?:\n\n|[ \t　]*)([^\n]+)',text);old=m[1]if m else'未解析';s=SOURCE.search(text);span=[int(s[2]),int(s[3]or s[2])]if s else None
  fig,box=picture(r,page);actual=r['使用者讀值'];state=r['狀態'];note='已確認，不重複詢問；本輪不改卡。'
  if actual is None:note='原頁右緣未完整顯示；外書木／水記載另列，不填入底本原圖值。'
  elif old is None:note='使用者已核圖，現庫缺此卡；只記補卡清單，本輪未補。'
  elif ''.join(old.split())!=''.join(actual.split()):note='使用者指定讀值與現值有差異，留待修訂；本輪不改卡。'
  rows.append({'編號':r['編號'],'卡名':r['卡名'],'原欄':name,'題名':name,'物理位置說明':'次頁右緣續欄'if page!=odd else'本頁催官題位'if name=='催官'else'年字欄內的'+name+'題位（位置不是題名）','現標頁碼':span,'原圖實際頁碼':page,'現值':old,'原圖值':actual if actual is not None else'底本影像缺邊，未確認','前輪原圖暫讀':r['前輪原圖暫讀'],'狀態':state,'來源類型':'使用者人工校讀'if actual is not None else'底本待核／外書轉錄另列','外書參考值':r['外書參考值'],'原圖':fig,'紅框原像素座標':box,'問題':note})
 count=collections.Counter(r['狀態']for r in rows)
 save('催官貴元跨頁抽查.json',{'日期':'2026-11-19','總數':28,'年組數':4,'題目數':7,'使用者讀值已確認':27,'底本未確認':1,'狀態分布':dict(count),'說明':'原欄欄位現存真正題名；物理位置另列。27項已回覆，不再把已確認答案寫成重複問題。前輪錯字保留在前輪原圖暫讀以供追查；既有卡片不動。','明細':rows})
 lines=['# 催官、貴元等跨頁組抽查（已依使用者回覆更正）','','## 更正原因','','前版把物理大欄位置寫成題名：文魁等錯標年干支欄，科名錯標貴元欄；並用同一大裁切圖及同一問題，造成重複提問。現在題名、物理位置分列，每題用不同紅框。','前版科名裁切只到頁高51%，漏掉下方值字；已擴到60%。己巳貴元在目前底本影像右緣仍不完整，不聲稱補出了原字。','使用者已回覆27項（明示8、其餘與現值一致19），底本未確認1項；不改卡、不補卡。前版己卯及己巳官印的羅水暫讀撤回，按使用者確認的現值羅木記錄。','','## 逐筆結果','','|卡名|真正題名／物理位置|現標頁／定位頁|現值|使用者核讀值|狀態／後續|紅框|','|---|---|---|---|---|---|---|']
 for x in rows:lines.append(f'|{x["卡名"]}|{x["題名"]}／{x["物理位置說明"]}|{x["現標頁碼"]}／{x["原圖實際頁碼"]}|{x["現值"]if x["現值"]is not None else"缺卡"}|{x["原圖值"]}|{x["狀態"]}；{x["問題"]}|[原圖](../{x["原圖"].removeprefix("docs/")})|')
 lines+=['','## 己巳貴元外書查核','','[外書查核報告](己巳貴元網路文獻查核.md)：《星平會海》己巳年條轉錄寫貴元木、科名土；《星學大成》巳年條另記水星。兩者不可混成底本已核值。','','## 補卡與修訂界線','','四張科名目前缺卡，使用者均讀土，已另記清單；本次未新增卡。文魁己丑金炁與現值一致，不需修字。','頁碼確認與字值確認分開；使用者只回覆字值，本報告不擴張成所有頁碼與跨頁歸屬都經使用者確認。']
 (D/'催官貴元跨頁抽查.md').write_text('\n'.join(lines)+'\n');print(json.dumps({'已確認':27,'底本未確認':1,'各題框位不同':True,'卡片異動':0},ensure_ascii=False))
if __name__=='__main__':main()
