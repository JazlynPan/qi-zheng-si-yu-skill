"""執行：由已保存的人工候選JSON重建36張原格圖與報告；不判字、不改卡。"""
from review_helpers import *
from audit_kejia import layout
stem='綱目跨頁右緣三元36格續核-2026-11-26'
data=json.loads((D/(stem+'.json')).read_text());same=0
for r in data['明細']:
 year=r['年組'];topic=r['題名'];page=r['原格實際頁'];headpage=r['年頭頁'];box=r['原格框']
 src=Path('/workspace/review/ocr')/f'綱目-{page}-原圖0.png';headsrc=src.with_name(f'綱目-{headpage}-原圖0.png')
 assert hashlib.sha256(src.read_bytes()).hexdigest()==r['原圖SHA256']
 assert hashlib.sha256(headsrc.read_bytes()).hexdigest()==r['年頭圖SHA256']
 im=Image.open(src).convert('RGB');head=Image.open(headsrc);w,h=im.size;hw,hh=head.size
 # layout只取既有原頁版式的題頭座標；讀字不由座標或天干公式產生。
 _,_,_,hx=layout(year);dest=ROOT/r['原圖'];old=hashlib.sha256(dest.read_bytes()).hexdigest()
 canvas=Image.new('RGB',(1050,1070),'white');d=ImageDraw.Draw(canvas)
 d.text((5,5),f'{year} {topic}｜前頁年頭；次頁原格（只備候選，不補卡）',font=FONT,fill='black')
 cut=head.crop((max(0,int((hx-.075)*hw)),0,min(hw,int((hx+.075)*hw)),int(.15*hh)))
 cut=cut.resize((int(cut.width*3),int(cut.height*3)));canvas.paste(cut,(5,70))
 d.text((5,45),f'原PDF第{headpage}頁年頭',font=FONT,fill='black')
 tile=im.crop((int(.88*w),0,w,int(.54*h)));scale=min(430/tile.width,950/tile.height)
 tile=tile.resize((int(tile.width*scale),int(tile.height*scale)));canvas.paste(tile,(540,75))
 d.text((540,45),f'原PDF第{page}頁右緣',font=FONT,fill='black')
 d.rectangle(((box[0]-int(.88*w))*scale+540,box[1]*scale+75,(box[2]-int(.88*w))*scale+540,box[3]*scale+75),outline='red',width=3)
 canvas.save(dest);same+=old==hashlib.sha256(dest.read_bytes()).hexdigest()
md=['# 綱目跨頁右緣祿元、仁元、壽元36格續核','','12組、36個原格已逐格回圖：22格備完整候選全文、14格字形未取定；正式新增0，不建缺字空殼。所有候選仍須使用者確認，不與前次原圖空白的歲殿、登籍混用。','','|年組|題名|原格PDF頁|候選|圖|','|---|---|---|---|---|']
for r in data['明細']:
 year=r['年組']+('（年頭有損）'if r['年組']=='戊申'else'')
 md.append(f'|{year}|{r["題名"]}|{r["原格實際頁"]}|{r["候選讀字"]or"未確認，不填"}|[年頭及原格](../{r["原圖"].removeprefix("docs/")})|')
md+=['','[22份完整預覽、36格圖源雜湊及限制]('+stem+'.json)。','','需要使用者決定：只對讀字及歸組均同意的候選授權補卡；不同意或看不清的保留未確認。未確認14格不以其他年組補值。','','戊申三格的年頭局部破損，讀字與歸組均須確認，不把前次定位當完整可見原刻。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
check={'日期':'2026-11-26','原格圖數':len(data['明細']),'重建前後圖像逐位元組相同':same,'來源雜湊核對':36,'卡片異動':0,'限制':'只核重建與圖源，不代替字形裁決。'}
(D/(stem+'-重建檢查.json')).write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(check,ensure_ascii=False));assert same==36
