#!/usr/bin/env python3
"""執行：抽查跨頁年組催官、貴元及年欄題目的頁碼與可核字；不改卡。"""
import json,re,collections
from review_helpers import *
YEARS=['戊子','己丑','己卯','己巳'];ITEMS=['催官','貴元','祿勳','文魁','玉堂','官印','科名']
# 以下僅為本輪實看整欄後可確認的八項；其餘不從舊紀錄回填原圖值。
READ={'戊子':{'催官':'水','官印':'土孛'},'己丑':{'催官':'炁','官印':'羅木'},'己卯':{'催官':'炁','官印':'羅水'},'己巳':{'催官':'炁','官印':'羅水'}}

def main():
 rows=[]
 for y in YEARS:
  odd=73+2*'子丑寅卯辰巳午未申酉戌亥'.index(y[1])
  for item in ITEMS:
   page=odd+1 if item in ['貴元','科名']else odd;x=.95 if page!=odd else .05 if item=='催官'else.15
   name=f'{item}圖列·{y}（星學綱目圖說下）.md';path=K/name;old=None;span=None
   if path.exists():
    text=path.read_text();m=re.search(r'\n'+item+r'(?:\n\n|[ \t　]*)([^\n]+)',text);old=m[1]if m else'未解析';s=SOURCE.search(text);span=[int(s[2]),int(s[3]or s[2])]if s else None
   im=Path(f'/workspace/review/ocr/綱目-{page}-原圖0.png');w,h=Image.open(im).size;ident=f'CY-{len(rows)+1:02d}';dest=PIC/'科甲欄'/(ident+'.png');framed_image(im,(max(0,(x-.075)*w),0,min(w,(x+.075)*w),h*.51),dest,ident+' '+y+' '+item+f' PDF{page} 原欄',scale=4,margin=2)
   actual=READ[y].get(item);pageok=span is not None and span[0]<=page<=span[1]
   same=actual is not None and old is not None and set(old.replace('　','').replace(' ',''))==set(actual)
   state='缺卡／待看原圖'if old is None else'頁碼錯'if not pageok else'原圖可核字一致'if same else'現值未解析，不判錯'if old=='未解析'else'原圖值不一致（待裁）'if actual else'頁碼可對上，字值待看原圖'
   rows.append({'編號':ident,'卡名':name,'原欄':('貴元欄'if page!=odd else'催官欄'if item=='催官'else'年干支欄'),'現標頁碼':span,'原圖實際頁碼':page,'現值':old,'原圖值':actual or'待看原圖／無法判斷','狀態':state,'來源類型':'人工校讀','原圖':str(dest.relative_to(ROOT)),'問題':f'請看紅框內「{item}」旁字，是「{old or "尚未建卡"}」還是「{actual or "另有字形，待原圖裁讀"}」？'})
 save('催官貴元跨頁抽查.json',{'總數':len(rows),'年組數':4,'題目數':7,'原圖可核字項目':8,'狀態分布':dict(collections.Counter(x['狀態']for x in rows)),'限制':'腳本按原頁年欄、催官、貴元位置抽查；不能因頁碼包含正確頁就判字值無錯，也不能由8項推論全庫皆無錯配。','明細':rows})
 lines=['# 催官、貴元等跨頁組抽查','','四組×七題，共28筆。只執行本支腳本，不全量更改。8項原圖可核字另列，其餘20項字值仍待原圖，不拿現卡反填。','原圖頁碼由欄位位置核：年欄與催官仍在前頁，戊己組貴元／科名續至次頁右緣；不能一律把整組移到次頁。','','|卡名|原欄|現標頁|原圖頁|現值|原圖值|結果|來源類型／原圖／問題|','|---|---|---|---|---|---|---|---|']
 for x in rows:lines.append(f'|{x["卡名"]}|{x["原欄"]}|{x["現標頁碼"]}|{x["原圖實際頁碼"]}|{x["現值"]}|{x["原圖值"]}|{x["狀態"]}|人工校讀；[圖](../{x["原圖"].removeprefix("docs/")})；{x["問題"]}|')
 lines+=['','## 需要使用者決定','','1. 頁碼錯與字值錯分開裁決；這次不改任何卡。','2. 尚未可靠辨讀的20項先保留，不宣告整組不存在相同錯配。']
 (D/'催官貴元跨頁抽查.md').write_text('\n'.join(lines)+'\n');print(json.dumps({'總數':28,'字值可核':8,'分布':dict(collections.Counter(x['狀態']for x in rows))},ensure_ascii=False))
if __name__=='__main__':main()
