"""執行：河洛第3頁39個0度候選框分流；卦畫、爻旁記號不冒充方法原文。"""
from review_helpers import *
from collections import Counter

stem='河洛第3頁39框分區覆核-2026-11-25'
source=ROOT/'docs/ocr/機器候選/河洛旋轉/河洛3圖0旋轉0-PaddleOCRv5.json'
j=json.loads(source.read_text())['結果'][0]['res']
assert len(j['rec_texts'])==39
src=Path('/workspace/review/ocr/河洛-3-原圖0.png')
card=K/'首例河洛數圖中文字（河洛五星合參案例抄本）.md'
body=''.join(card.read_text().split())
words={12:'反對兌卦',13:'後天巽卦',14:'正對震卦',15:'反對節卦',16:'先天渙卦',17:'正對豐卦',18:'至四十六歲轉入後天不記',19:'先天運程共管四十五年',26:'元堂',31:'候值卦未逢',32:'節值',33:'化工',34:'地元巽',35:'天元坤卦未逢',36:'六月初四日',37:'十四',38:'卦見',39:'後天全'}
rows=[]
for n,(text,poly) in enumerate(zip(j['rec_texts'],j['dt_polys']),1):
    b=[min(x[0] for x in poly),min(x[1] for x in poly),max(x[0] for x in poly),max(x[1] for x in poly)]
    image=framed_image(src,b,PIC/stem/f'HL3-{n:02}.png',f'河洛PDF第3頁／框{n:02}：原字與記號分開',scale=4,margin=18)
    if n in words:
        reading=words[n]
        # 原卡分格保存的片段，不把空白當作字值變更。
        found=reading in body
        if not found and n==31:
            found='候值' in body and '卦未逢' in body
        if not found and n==35:
            found=all(s in body for s in ['天元','坤','卦未逢'])
        assert found,(n,reading)
        status='原字可辨，現卡已有文字或分格片段'
    elif n<=11:
        reading=''
        status='頁題／上方數字格位，不拆成通則卡'
    elif n==20:
        reading='元堂'
        status='含已收元堂及卦畫；卦畫與爻旁記號不當文字推讀'
    elif n==25:
        reading=''
        status='紅筆痕跡，非可辨字句'
    else:
        reading=''
        status='卦畫／爻旁記號，未見可照錄的完整詞句；不依卦義轉寫'
    rows.append({'編號':f'HL3-{n:02}','原頁':3,'原框':b,'機器候選':text,'來源類型':'人工校讀','可辨原字':reading,'結果':status,'紅框圖':image})
report={'日期':'2026-11-25','範圍':'原圖0之0度OCR39框，另看整張原圖的上下文；不是所有角度候選的聯集','判讀方式':'單代理讀原圖，不是獨立代理盲評','統計':dict(Counter(x['結果'] for x in rows)),'新增卡數':0,'既有卡異動':0,'明細':rows,'限制':'上方數字格位、卦畫與爻旁細記保留原圖，不由卦形或記憶推演；不把未轉寫的記號標成方法已提取。'}
(D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 河洛第3頁39框分區覆核','','本批不改卡、不新增卡。逐框對原圖，文字與圖形記號分開，不採機器候選作答案。先前兩條氣值地元原文已另存完整舊新卡。','',report['限制'],'',str(report['統計'])+'。','','|編號|原字或處理|結果|圖|','|---|---|---|---|']
for r in rows:
    md.append(f'|{r["編號"]}|{r["可辨原字"] or "不轉寫"}|{r["結果"]}|[紅框](../{r["紅框圖"].removeprefix("docs/")})|')
md+=['','[逐框座標及完整紀錄]('+stem+'.json)。39框不是39張卡；不把非文字記號送入知識卡，也不從圖形補造卦義。','接續第12頁已收文字與未收邊欄對照；T17-082末字未定仍保留，不擅改既有引文。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
with (ROOT/'docs/catalog/河洛五星合參案例抄本.md').open('a') as f:
    f.write('\n### 2026-11-25：第3頁分區覆核\n\n0度39候選框逐框對原圖，已收文字不重複建卡；頁題、數字格位、卦畫及爻旁記號保留圖示，不從符號推造取法。[39框逐項結果](../檢查/'+stem+'.md)。此表不是所有角度或框外字位的完整性保證。\n\n|概念名稱／定位編號|書名|PDF頁碼|原因|\n|---|---|---|---|\n|河洛數上方格位、兩組卦畫及爻旁細記|河洛五星合參案例抄本|3|原文以圖表呈現，數字及符號沒有在本頁展開通則；保留紅框，不依卦義轉寫、不建空殼卡。|\n')
p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('|河洛五星合參案例抄本|'):
        c=line.strip('|').split('|');c[6]+='；同日第3頁39候選框逐框分流，已收文字不重複入卡，數字格位與卦畫爻記保留原圖不推讀；不作所有角度完整性保證';c[7]='2026-11-25';lines[i]='|'+'|'.join(c)+'|'
p.write_text('\n'.join(lines)+'\n')
p=ROOT/'docs/狀態.md';s=p.read_text()
s=re.sub(r'復工位置：[^\n]+','復工位置：《河洛五星合參案例抄本》第3頁39個0度候選框已逐框分流，已收字不重複建卡，卦畫與爻旁記號留圖、不推義。第2頁原圖0五框、原圖1七框仍未確認。下一個第一動作：第12頁未收邊欄與命例數字對照，T17-082末字未定保留；原37頁1358段另已建立同頁文字查找線索，非人工驗收完成。',s,1)
p.write_text(s)
print(json.dumps(report['統計'],ensure_ascii=False))
