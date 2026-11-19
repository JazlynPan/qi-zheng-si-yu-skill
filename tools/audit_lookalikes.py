#!/usr/bin/env python3
"""執行：全庫形近字候選逐筆清單與原圖，絕不替換卡片。
目錄：collect（候選範圍）、main（來源定位、紅框、報告）。
"""
import re,collections,json
from review_helpers import *

def collect():
 rows=[];seen={}
 for path in sorted(K.glob('*.md')):
  text=path.read_text();sources=list(SOURCE.finditer(text))
  def add(pos,typ,cand,reason,legal=False):
   if any(m.start()<=pos<m.end()for m in sources):return
   key=(path.name,pos)
   if key in seen:
    seen[key]['類型']+='／'+typ;return
   src=next((m for m in reversed(sources)if m.end()<pos),None)
   if not src:return
   line_start=text.rfind('\n',0,pos)+1;line_end=text.find('\n',pos)
   if line_end<0:line_end=len(text)
   before=text[max(line_start,pos-8):pos];after=text[pos+1:min(line_end,pos+9)]
   row={'卡名':path.name,'行號':text.count('\n',0,pos)+1,'字元位置':pos,'類型':typ,'現字':text[pos],'候選字':cand,'前文':before,'後文':after,'書名':src[1],'起頁':int(src[2]),'迄頁':int(src[3]or src[2]),'單位':src[4],'來源類型':'待追溯','語境建議':reason,'判斷':'合法'if legal else'待看原圖','合法詞':legal,'非古籍來源':'楊國正'in src[1]}
   rows.append(row);seen[key]=row
  for m in re.finditer('昂',text):
   c=text[max(0,m.start()-5):m.start()+6];legal=bool(re.search('軒昂|昂藏|昂首|科昂',c))
   add(m.start(),'昂／昴','昴','軒昂、昂藏或科甲高昂語境，不作星宿誤字'if legal else'星宿等語境候選；同段昴字只作定位線索，不代替原圖',legal)
  for m in re.finditer(r'已[子丑寅卯辰巳午未申酉戌亥]',text):
   context=text[max(0,m.start()-20):m.end()+20]
   if '怕已丑'in context and ('孤辰'in path.name or '孤辰'in context):cand='巳';why='使用者提供的孤辰／寡宿語境指向巳、丑，仍須核原刻'
   elif m[0]=='已巳' or re.search(r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]\s*$',text[max(0,m.start()-4):m.start()]):cand='己';why='四柱或干支連記中的天干位置，候選己；不是原刻定稿'
   else:cand='己／巳';why='已可能混淆天干己或地支巳，語句不足以單向判定，逐筆看圖'
   add(m.start(),'已於干支候選',cand,why)
  for m in re.finditer(r'已(?=[宮時])|(?<=[甲乙丙丁戊己庚辛壬癸])已(?=之年|年|生人|[、，；。])|(?<=[子丑寅卯辰巳午未申酉戌亥])已(?=二宮|宮|生人|[、，；。])',text):
   cand='己'if m.start()>0 and text[m.start()-1]in'甲乙丙丁戊己庚辛壬癸'else'巳'
   add(m.start(),'已於干支候選',cand,'已位於干支列記或宮時用字處，方向僅依語句作候選，原刻待看圖')
  for m in re.finditer(r'(?:^|[。；：\n])[ \t　]*(巳[子丑寅卯辰巳午未申酉戌亥])',text):
   pos=m.start(1);ctx=text[pos:pos+12]
   if re.match(r'巳酉丑|巳申寅亥',ctx):continue
   add(pos,'己／巳干支首位候選','己','句首或四柱首字的巳可能是己；不把兩地支連記直接當錯字')
  for m in re.finditer('巳巳',text):add(m.start(),'巳巳另列','己','重字不等於誤字，先看原圖，不批量換為己巳')
  patterns=[(r'甲巳(?=之年|年|生人)','己',1),(r'丑已(?=二宮|宮)','巳',1),(r'戌己(?=生人)','巳',1),(r'庚戌日戊時','午',3),(r'戍(?=[年月日時宮])','戌',0),(r'[年月日時宮]戍','戌',1),(r'末(?=[宮時])','未',0),(r'士(?=[宮時星])','土',0),(r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]曰','日',2),(r'牛(?=[宮時])','午',0),(r'子牛卯酉','午',1),(r'甲(?=[宮時])','申',0),(r'[甲乙丙丁己庚辛壬癸]戊(?=[年月日柱，。\s])','戌',1),(r'己(?=[宮時])','巳',0)]
  for pat,cand,offset in patterns:
   for m in re.finditer(pat,text):add(m.start()+offset,'其他形近字語境',cand,'僅為干支、時辰或宮位附近的候選；合法詞與字形須回原頁逐筆確認')
 return rows

def main():
 rows=collect();stats=collections.Counter()
 for i,row in enumerate(rows,1):
  ident=f'XJ-{i:04d}';row['編號']=ident;result=locate(row,ident)
  row.update(result)
  if row['合法詞']:row['判斷']='合法'
  row['問題']=f'請看紅框內的字，是「{row["現字"]}」還是「{row["候選字"]}」？'if '／'not in row['候選字']else'請看紅框內的字，是「己」還是「巳」？'
  stats[row['定位']]+=1
  if i%30==0:print(json.dumps({'已處理':i,'總數':len(rows),'定位':dict(stats)},ensure_ascii=False),flush=True)
 save('形近字批量修訂清單.json',{'限制':'只掃疑似語境，不把合法干支的每一個正常字列作錯字；語境建議不是原圖判決。文字層對應字不當作字形判讀。來源類型依原頁文字層／既有校讀證據記錄，不宣稱全卡建置流程均已追溯。','候選總數':len(rows),'按書分布':dict(collections.Counter(x['書名']for x in rows)),'定位分布':dict(stats),'明細':rows})
 lines=['# 形近字批量修訂清單','','## 目錄','','- [範圍與數量](#範圍與數量)','- [逐筆證據](#逐筆證據)','- [待看原圖與需要決定](#待看原圖與需要決定)','','## 範圍與數量','',f'全庫19,769張卡。候選{len(rows)}筆；合法詞另標，不批量替換。下表每筆保留卡片行號及前後各最多8字。','來源類型表示可追溯的頁面或校讀資料；文字層定位成功仍須人眼核字。任何語境規律、同段其他寫法都只作線索，不能證明原刻應改。','']
 for b,n in sorted(collections.Counter(x['書名']for x in rows).items()):lines.append(f'- {b}：{n}筆。')
 lines+=['','## 逐筆證據','','|編號／卡名|行號|類型|前8字〔現字〕後8字|書名／頁段|來源類型|判斷／候選與理由|原圖／一題|','|---|---|---|---|---|---|---|---|']
 for x in rows:
  link=f'[紅框](../{x["原圖"].removeprefix("docs/")})'if x.get('原圖')else'未定位／沒有可用原頁圖'
  note='；非古籍來源：影片字幕／講義逐字稿'if x['非古籍來源']else''
  lines.append(f'|{x["編號"]} {x["卡名"]}|{x["行號"]}|{x["類型"]}|{x["前文"]}〔{x["現字"]}〕{x["後文"]}|{x["書名"]} {x["起頁"]}–{x["迄頁"]}{x["單位"]}{note}|{x["來源類型"]}|{x["判斷"]}；候選{x["候選字"]}；{x["語境建議"]}|{link}；{x["問題"]}|')
 lines+=['','## 待看原圖與需要決定','','所有非合法詞候選均未寫成正確。已附圖者仍待逐筆裁決，未定位者不得用語境代填。','']
 lines += [f'- {x["編號"]} {x["卡名"]}：{x.get("原因",x["定位"])}' for x in rows if not x.get('原圖')]
 (D/'形近字批量修訂清單.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'總數':len(rows),'定位':dict(stats)},ensure_ascii=False))
if __name__=='__main__':main()
