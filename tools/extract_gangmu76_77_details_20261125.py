"""執行：76、77頁五處新圖字與貫索亢字續錄，保留舊引文及全文雜湊。"""
from review_helpers import *
import subprocess

stem='綱目76至77頁細字續核-2026-11-25';before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.md')};base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
specs=[(76,'巳','天戟','天戟',[0,407,30,477],[108,424,163,479],[0,402,260,490]),(76,'丑','黃旛','黃旛',[268,667,304,726],[359,687,413,744],[260,661,520,751]),(77,'未','拔鞍','拔鞍',[146,414,184,482],[103,431,159,493],[0,405,260,499]),(77,'戌','黃旛','黃旛',[463,586,520,648],[361,588,419,652],[260,579,521,668]),(77,'亥','卷舌','卷舌\n\n壁十',[319,672,369,758],[361,682,421,755],[260,665,521,760])]
folder=PIC/stem;folder.mkdir(exist_ok=True);rows=[]
def picture(page,label,circle,box,cb,clip):
    src=Path(f'/workspace/review/ocr/綱目-{page}-原圖0.png');im=Image.open(src).convert('RGB');tile=im.crop(clip);tile=tile.resize((tile.width*4,tile.height*4));panel=Image.new('RGB',(1050,tile.height+65),'white');panel.paste(tile,(0,65));d=ImageDraw.Draw(panel);d.text((8,8),f'綱目PDF第{page}頁／{label}及{circle}字圈：原字照錄',font=FONT,fill='black')
    for b in (box,cb):d.rectangle(((b[0]-clip[0])*4,65+(b[1]-clip[1])*4,(b[2]-clip[0])*4,65+(b[3]-clip[1])*4),outline='red',width=3)
    output=folder/f'{page}-{label}-{circle}.png';panel.save(output);return str(output.relative_to(ROOT)),hashlib.sha256(src.read_bytes()).hexdigest()
for page,circle,label,words,box,cb,clip in specs:
    name=f'{label}圖列·第{page}頁{circle}字圈（星學綱目圖說下）.md';path=K/name;assert not path.exists()
    image,digest=picture(page,label,circle,box,cb,clip)
    body=f'#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n《星學綱目正傳》第{page}頁〈六十年甲子圖〉：\n\n原文以圖表呈現\n\n{circle}\n\n{words}\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n'
    assert not any(body==p.read_text() for p in K.glob('*.md'));path.write_text(body)
    rows.append({'卡片':name,'原頁':page,'原字':words,'圖中圈字':circle,'來源類型':'人工校讀','紅框圖':image,'原圖SHA256':digest,'舊全文':None,'舊SHA256':None,'新全文':body,'新SHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'處理':'新增'})
name='貫索圖列·第76頁辰字圈（星學綱目圖說下）.md';path=K/name;old=path.read_bytes();assert '\n亢\n' not in old.decode()
addition='\n《星學綱目正傳》第76頁：\n\n原文以圖表呈現\n\n亢\n'.encode();point=old.index(b'\n## '+ '操作步驟'.encode()+b'\n');new=old[:point]+addition+old[point:];assert new[:point]+new[point+len(addition):]==old;path.write_bytes(new)
image,digest=picture(76,'貫索亢','辰',[64,499,110,566],[103,514,160,569],[0,492,260,578])
rows.append({'卡片':name,'原頁':76,'原字':'亢','圖中圈字':'辰','來源類型':'人工校讀','紅框圖':image,'原圖SHA256':digest,'舊全文':old.decode(),'舊SHA256':hashlib.sha256(old).hexdigest(),'新全文':new.decode(),'新SHA256':hashlib.sha256(new).hexdigest(),'處理':'使用規則欄只插入新引文，原文未替換','插入位置':point,'插入位元組數':len(addition),'移除本批插入即與舊全文逐位元組相同':True})
assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==v for n,v in before.items() if n!=name)
archive=ROOT/'docs/勘校修訂'/stem;archive.mkdir();report={'日期':'2026-11-25','基準提交':base,'新增卡數':5,'既有卡追加':1,'原有字值覆寫':0,'其他舊卡異動':0,'卡片總數':len(before)+5,'明細':rows}
(archive/'舊新全文與SHA256.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 綱目76–77頁細字續核','','新增5卡，原卡1張只插入一段新引文；現有原字覆寫0，其他卡異動0。四欄及出處完整，無新空殼。','','|頁|圈字|照錄原字|處理|紅框|','|---|---|---|---|---|']
for r in rows:md.append(f'|{r["原頁"]}|{r["圖中圈字"]}|{r["原字"].replace(chr(10)," ")}|{r["處理"]}|[原圖](../{r["紅框圖"].removeprefix("docs/")})|')
md+=['','卷舌下方小字原圖右壁、左十，依右至左存「壁十」，未改讀為「十壁」，不補單位、不解釋取法。','貫索亢字只續錄至同一張卡的使用規則欄；移除本批插入的位元組後，整張卡與舊全文完全相同，不替換舊值。[舊新全文與SHA256](../勘校修訂/'+stem+'/舊新全文與SHA256.json)。','第76頁太歲、第77頁中央寅等字位已有卡，未重建、不回頭改值；邊緣殘字及無法確定的細註仍保留。','下一步第78–80頁細字；不宣稱這兩頁全部圖字已驗收。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
(D/(stem+'.json')).write_text(json.dumps({k:v for k,v in report.items() if k!='明細'}|{'明細':[{k:v for k,v in r.items() if k not in ('舊全文','新全文')} for r in rows]},ensure_ascii=False,indent=2)+'\n')
with (ROOT/'docs/勘校修訂紀錄.md').open('a') as f:f.write('\n## 2026-11-25【原文續錄】綱目第76–77頁細字\n\n5張新卡、貫索原卡插入亢字新引文1段，既有文字全數保留；移除插入位元組即還原舊全文。卷舌壁十按原圖右至左照錄，不加單位或取法。[逐項原圖](檢查/'+stem+'.md)；[舊新全文與SHA256](勘校修訂/'+stem+'/舊新全文與SHA256.json)。\n')
with (ROOT/'docs/catalog/星學綱目正傳.md').open('a') as f:f.write('\n### 2026-11-25：第76–77頁細字續核\n\n76頁天戟／巳、黃旛／丑，77頁拔鞍／未、黃旛／戌、卷舌壁十／亥，新補5卡；76頁貫索亢字追加原卡，不改舊字。太歲與中央年字已有卡，不重建。[原字、雙紅框與全文留存](../檢查/'+stem+'.md)。未明細註不推讀，未宣告整頁完成。\n')
p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('|星學綱目正傳|'):
        c=line.strip('|').split('|');c[5]=c[5].replace('5720','5725');c[6]+='；同日第76–77頁天戟、黃旛兩處、拔鞍及卷舌壁十新增5卡，貫索亢字插入原卡，舊字不改，細註仍待核';c[7]='2026-11-25';lines[i]='|'+'|'.join(c)+'|'
p.write_text('\n'.join(lines)+'\n')
p=ROOT/'docs/狀態.md';s=p.read_text().replace('共20,284張；綱目5,720張','共20,289張；綱目5,725張');s=re.sub(r'復工位置：[^\n]+','復工位置：《綱目》第76–77頁細字新增5卡、貫索原卡只插入亢字引文，舊字不改；卷舌壁十按圖中字位照錄。下一個第一動作：第78–80頁未收細字，先對照既有卡避免重建，未知字不依常見神煞名代填。',s,1);p.write_text(s)
for relative in ['docs/階段1.5目前檢查摘要.md','docs/檢查/階段1.5完成條件核對-2026-11-18.md','docs/檢查/階段1.5待校與待裁決分界.md']:
    p=ROOT/relative;s=p.read_text().replace('20,284','20,289').replace('20284','20289').replace('6,452','6,457').replace('6452','6457');p.write_text(s)
p=D/'階段1.5待校與待裁決分界.json';j=json.loads(p.read_text());j['卡片數']=len(before)+5
for r in j['明細']:
    if r['書名']=='星學綱目正傳' and r['頁碼'] in (76,77):r['最新續核']='2026-11-25部分細字新核，見'+stem+'.md；其餘未清字保留，不標全頁完成。'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='明細'},ensure_ascii=False))
