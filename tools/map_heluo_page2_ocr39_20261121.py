"""執行：原圖0之0度PP-OCRv5的39框與既有T17框作位置對照；不判原字、不改卡。"""
from review_helpers import *
from collections import Counter
source=ROOT/'docs/ocr/機器候選/河洛旋轉/河洛2圖0旋轉0-PaddleOCRv5.json';data=json.loads(source.read_text());r=data['結果'][0]['res'];boxes=r['dt_polys'];texts=r['rec_texts'];scores=r['rec_scores'];assert len(boxes)==len(texts)==39
old=[x for x in json.loads((D/'T17逐條紅框對照.json').read_text())['明細']if x['原圖頁碼']==2 and x['原圖序號']==0];rows=[];folder=PIC/'河洛2頁續核-2026-11-21';src=Path('/workspace/review/ocr/河洛-2-原圖0.png')
for i,poly in enumerate(boxes):
 b=[min(p[0]for p in poly),min(p[1]for p in poly),max(p[0]for p in poly),max(p[1]for p in poly)];area=max(1,(b[2]-b[0])*(b[3]-b[1]));hits=[]
 for x in old:
  c=x['原圖框位'];ratio=max(0,min(b[2],c[2])-max(b[0],c[0]))*max(0,min(b[3],c[3])-max(b[1],c[1]))/area
  if ratio>=.5:hits.append(x['編號'])
 status='與T17框位置交疊（非文字核定）'if hits else'框外候選，待讀原圖';path=None
 if not hits:path=framed_image(src,b,folder/f'原圖0-OCR39-{i+1:02}.png',f'河洛第2頁原圖0／OCR框{i+1}：機器候選未定字',scale=4,margin=18)
 rows.append({'編號':f'HL2-0-{i+1:02}','原框':b,'機器候選':texts[i],'機器分數':scores[i],'位置交疊':hits,'狀態':status,'新紅框':path})
summary=dict(Counter(x['狀態']for x in rows));(D/'河洛第2頁原圖0之39框位置對照-2026-11-21.json').write_text(json.dumps({'日期':'2026-11-21','證據等級':'E0位置比對；不是辨字正確率或整頁覆蓋率','來源檔':str(source.relative_to(ROOT)),'框數':39,'門檻':'單個T17矩形交集／本候選矩形面積至少0.5；只作框位對照','統計':summary,'明細':rows},ensure_ascii=False,indent=2)+'\n')
md=['# 河洛第2頁原圖0之39框位置對照','','這份只對照原圖0、0度PP-OCRv5檔的39框，與整頁及四方向候選數不同。位置交疊不能證明候選字已核定。',f'統計：{summary}。所有框外候選先留紅框，不自動入卡。','','|編號|機器候選（未確認）|相交T17框|狀態／新圖|','|---|---|---|---|']
for x in rows:
 link=f'[原圖](../{x["新紅框"].removeprefix("docs/")})'if x['新紅框']else x['狀態'];md.append(f'|{x["編號"]}|{x["機器候選"]}|'+','.join(x['位置交疊'])+'|'+link+'|')
md+=['','[54框文字核銷及新增原文](河洛第2頁54候選框核銷-2026-11-21.md)。框外單字、空辨識與斜字仍要看原圖，不按上下文補字。'];(D/'河洛第2頁原圖0之39框位置對照-2026-11-21.md').write_text('\n'.join(md)+'\n')
print(json.dumps(summary,ensure_ascii=False));print(json.dumps([x for x in rows if x['新紅框']],ensure_ascii=False))
