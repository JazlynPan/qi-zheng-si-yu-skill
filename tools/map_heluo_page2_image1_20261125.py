"""執行：原圖1的50個0度OCR框作位置對照；只產生定位，不以OCR定字。"""
from review_helpers import *
from collections import Counter

stem='河洛第2頁原圖1之50框位置對照-2026-11-25'
source=ROOT/'docs/ocr/機器候選/河洛旋轉/河洛2圖1旋轉0-PaddleOCRv5.json'
r=json.loads(source.read_text())['結果'][0]['res']
assert len(r['dt_polys'])==len(r['rec_texts'])==50
targets=[x for x in json.loads((D/'T17逐條紅框對照.json').read_text())['明細'] if x['原圖頁碼']==2 and x['原圖序號']==1]
rows=[]
for i,poly in enumerate(r['dt_polys'],1):
    b=[min(p[0] for p in poly),min(p[1] for p in poly),max(p[0] for p in poly),max(p[1] for p in poly)]
    area=max(1,(b[2]-b[0])*(b[3]-b[1]))
    hits=[]
    for x in targets:
        c=x['原圖框位']
        ratio=max(0,min(b[2],c[2])-max(b[0],c[0]))*max(0,min(b[3],c[3])-max(b[1],c[1]))/area
        if ratio>=.5:
            hits.append(x['編號'])
    pic=None
    if not hits:
        pic=framed_image(Path('/workspace/review/ocr/河洛-2-原圖1.png'),b,PIC/stem/f'HL2-1-{i:02}.png',f'HL2-1-{i:02}／河洛第2頁原圖1：候選未定字',scale=4,margin=25)
    rows.append({'編號':f'HL2-1-{i:02}','原框':b,'機器候選':r['rec_texts'][i-1],'位置交疊':hits,'狀態':'與既有T17框交疊，非文字核定' if hits else '框外候選，待人工看圖','紅框圖':pic})
summary=dict(Counter(x['狀態'] for x in rows))
(D/(stem+'.json')).write_text(json.dumps({'日期':'2026-11-25','證據等級':'E0位置對照，非原字正確率','門檻':'單一T17框交集／本候選框面積至少0.5','來源':str(source.relative_to(ROOT)),'統計':summary,'明細':rows},ensure_ascii=False,indent=2)+'\n')
md=['# 河洛第2頁原圖1之50框位置對照','','只對照0度50框與既有T17框的位置，不能把框數當成字數、卡數或整頁覆蓋率。機器候選尚未核字，不據此入卡。',str(summary)+'。','','|編號|機器候選（非原字裁決）|位置交疊|狀態／圖|','|---|---|---|---|']
for x in rows:
    link=f'[紅框](../{x["紅框圖"].removeprefix("docs/")})' if x['紅框圖'] else x['狀態']
    md.append(f'|{x["編號"]}|{x["機器候選"]}|'+','.join(x['位置交疊'])+'|'+link+'|')
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
print(json.dumps(summary,ensure_ascii=False))
print(json.dumps([x for x in rows if x['紅框圖']],ensure_ascii=False))
