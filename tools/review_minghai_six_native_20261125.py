"""執行：保存命海331–336原始內嵌盤圖、解析度及未清字位；不改卡。"""
from review_helpers import *
from collections import Counter
import subprocess

stem='命海六盤原生解析度續核-2026-11-25'
folder=PIC/stem;folder.mkdir(exist_ok=True)
document=pdf('星平總會命海')
cases=json.loads((D/'命海331至336命例盤圖核對.json').read_text())['明細']
notes={331:'上弧木張之後的小字與盤線接近，不能確定末字；原卡其餘已收字不改。',332:'T15-016原格與相鄰文星格須分開；原格末數仍未確認，不把下一格文字接入。',333:'T15-022、024依使用者圖糊未確認指示保留；其他已裁決字不改。',334:'T15-032文星／文室仍待裁決；火井王依使用者授權保留，疑註十一不代填。',335:'月氐吉、土亥三等已裁決值保留；淡損小字不依其他盤的序列補足。',336:'T15-075畢五之前的首字有金字形候選，仍未裁決；近旁羅張後數字受盤線影響，不採猜測數。'}
rows=[]
for case in cases:
    n=case['PDF實際頁碼'];page=document[n-1];images=page.get_images(full=True)
    assert len(images)==1
    data=document.extract_image(images[0][0])
    source=Path(f'/workspace/review/ocr/命海{n}-內嵌底圖.png')
    assert source.read_bytes()==data['image']
    im=Image.open(source).convert('RGB');w,h=im.size
    native=folder/f'命海{n}-原生盤圖.png';im.save(native)
    # 盤圖上、下、左、右四區均給原方向紅框，只定位、不補筆畫。
    regions={'上弧':(int(w*.23),int(h*.09),int(w*.75),int(h*.38)),'下弧':(int(w*.21),int(h*.63),int(w*.77),int(h*.92)),'左弧':(int(w*.08),int(h*.22),int(w*.35),int(h*.78)),'右弧':(int(w*.65),int(h*.2),int(w*.94),int(h*.77))}
    pictures={label:framed_image(source,box,folder/f'命海{n}-{label}.png',f'命海PDF第{n}頁／{label}：原生{w}×{h}，不補筆畫',scale=4,margin=12) for label,box in regions.items()}
    rows.append({'書名':'星平總會命海','原頁':n,'來源類型':'人工校讀','原生圖尺寸':[w,h],'原始嵌圖SHA256':hashlib.sha256(data['image']).hexdigest(),'原始圖保存':str(native.relative_to(ROOT)),'原圖檢視':'本輪查看整頁／盤圖及旋轉方向；不以OCR成功當文字驗收','待核':notes[n],'紅框圖':pictures,'原命例卡':case['既有命例卡']})
report={'日期':'2026-11-25','檢視圖頁':6,'原生嵌圖數':6,'新增卡數':0,'既有卡異動':0,'限制':'嵌圖約410像素寬，原圖沒有更高解析度的隱藏版本；放大只是視覺輔助，不能還原缺筆。既有使用者裁決全部保留，本表不將候選作修訂答案。','明細':rows}
(D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 命海六盤原生解析度續核','','## 結果','','六頁原始內嵌圖均已抽出核對；本輪不新增、不修改卡片。已裁決的原字全部保留。',report['限制'],'','','|PDF頁|原生像素|仍未確認範圍|原生圖／四區紅框|','|---|---|---|---|']
for r in rows:
    links=[f'[原生圖](../{r["原始圖保存"].removeprefix("docs/")})']+[f'[{label}](../{path.removeprefix("docs/")})' for label,path in r['紅框圖'].items()]
    md.append(f'|{r["原頁"]}|'+ '×'.join(map(str,r['原生圖尺寸']))+'|'+r['待核']+'|'+' '.join(links)+'|')
md+=['','## 判讀界線','','331木張末字、332尾宿末數、334文室／文星、336畢五首字等，均未用他書、模型或排盤規律代填。336畢五首字的新字形線索只供使用者看圖，不會自行入卡。','卦宿、宮支圓環屬原盤圖的位置標示；沒有額外方法文字就不拆成新通則卡。原文例子中已有明寫盤字照舊保留，未列為六盤全字驗收。','下一步核《星學綱目正傳》97–101頁尚未確認細註與欄旁字；此批盤圖保留待裁決，不以原卡存在當作缺口已解決。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
with (ROOT/'docs/catalog/星平總會命海.md').open('a') as f:
    f.write('\n### 2026-11-25：331–336頁原始嵌圖續核\n\n六盤原生嵌圖僅410–416像素寬，逐頁核對原始影像與旋轉盤圖；已裁決讀字保持。木張末字、尾宿末數、文室／文星及畢五首字等仍不明，不由正文或他盤補值。[原生解析度與四區紅框](../檢查/'+stem+'.md)。新增卡0，改卡0；不標全圖完成。\n\n|概念名稱／定位編號|書名|PDF頁碼|原因|\n|---|---|---|---|\n')
    for r in rows:
        f.write(f'|盤圖未清細字|星平總會命海|{r["原頁"]}|{r["待核"]}|\n')
p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('|星平總會命海|'):
        c=line.strip('|').split('|');c[6]+='；2026-11-25六盤原生圖逐頁續核，原始嵌圖410–416像素寬，四區紅框已存；木張末字、尾宿末數、文室／文星與畢五首字等仍未確認，未改卡';c[7]='2026-11-25';lines[i]='|'+'|'.join(c)+'|'
p.write_text('\n'.join(lines)+'\n')
p=ROOT/'docs/狀態.md';s=p.read_text();s=re.sub(r'復工位置：[^\n]+','復工位置：《命海》331–336六盤原生嵌圖與四區紅框已核存，低解析度黏線字保留待裁決，未猜數值、未改卡。下一個第一動作：《綱目》97頁天嗣下注與玉堂首列，讀原生嵌圖確認未收細字；河洛第2頁12框、15頁候卦末字及其他待決項保留。',s,1);p.write_text(s)
print(json.dumps({k:v for k,v in report.items() if k!='明細'},ensure_ascii=False))
