"""執行：依74、75頁原圖補未收四處題字；不改他卡，不按常見神煞名換字。"""
from review_helpers import *
import subprocess

stem='綱目74至75頁細字續核-2026-11-25'
specs=[(74,'辰','黃旛',[40,501,78,563],[101,515,156,564],[0,491,259,575]),(74,'丑','拔鞍',[300,647,331,718],[356,650,415,716],[260,636,511,755]),(75,'戌','拔鞍',[326,585,355,644],[358,583,418,650],[260,576,516,666]),(75,'子','陌越',[211,675,242,741],[101,680,159,746],[0,665,260,755])]
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.md')}
base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip();rows=[]
folder=PIC/stem;folder.mkdir(exist_ok=True)
for page,circle,word,box,cb,clip in specs:
    name=f'{word}圖列·第{page}頁{circle}字圈（星學綱目圖說下）.md';path=K/name;assert not path.exists()
    src=Path(f'/workspace/review/ocr/綱目-{page}-原圖0.png');im=Image.open(src).convert('RGB');tile=im.crop(clip);tile=tile.resize((tile.width*4,tile.height*4));panel=Image.new('RGB',(max(1050,tile.width),tile.height+70),'white');panel.paste(tile,(0,70));d=ImageDraw.Draw(panel);d.text((8,8),f'綱目PDF第{page}頁／{word}與{circle}字圈：只抄明字，不補取法',font=FONT,fill='black')
    for b in (box,cb):d.rectangle(((b[0]-clip[0])*4,70+(b[1]-clip[1])*4,(b[2]-clip[0])*4,70+(b[3]-clip[1])*4),outline='red',width=3)
    output=folder/f'{page}-{word}-{circle}.png';panel.save(output)
    body=f'#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n《星學綱目正傳》第{page}頁〈六十年甲子圖〉：\n\n原文以圖表呈現\n\n{circle}\n\n{word}\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n'
    assert not any(body==p.read_text() for p in K.glob('*.md'))
    path.write_text(body)
    rows.append({'卡片':name,'原頁':page,'原圖題字':word,'圖中圈字':circle,'來源類型':'人工校讀','原字框':box,'圈字框':cb,'原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'紅框圖':str(output.relative_to(ROOT)),'舊全文':None,'舊SHA256':None,'新全文':body,'新SHA256':hashlib.sha256(path.read_bytes()).hexdigest()})
assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==v for n,v in before.items())
archive=ROOT/'docs/勘校修訂'/stem;archive.mkdir()
report={'日期':'2026-11-25','基準提交':base,'新增卡數':4,'既有卡異動':0,'新增空殼':0,'總卡數':len(before)+4,'說明':'黃旛不換黃幡，拔鞍不換攀鞍，陌越不換陟越；只按本頁可見字形，沒有用他書或星盤規則補字。','明細':rows}
(archive/'新卡全文與SHA256.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(D/(stem+'.json')).write_text(json.dumps({k:v for k,v in report.items() if k!='明細'}|{'明細':[{k:v for k,v in x.items() if k not in ('新全文','舊全文')} for x in rows]},ensure_ascii=False,indent=2)+'\n')
md=['# 綱目74–75頁細字續核','','新增4卡，既有卡異動0，新建空殼0；只抄圈字和題字，不當作年組或起法。',report['說明'],'','','|頁|圈字|原字|新卡|紅框|','|---|---|---|---|---|']
for r in rows:md.append(f'|{r["原頁"]}|{r["圖中圈字"]}|{r["原圖題字"]}|[{r["卡片"]}](../../qi-zheng-si-yu/knowledge/{r["卡片"]})|[雙紅框](../{r["紅框圖"].removeprefix("docs/")})|')
md+=['','[新卡全文與SHA256](../勘校修訂/'+stem+'/新卡全文與SHA256.json)。第74頁辰圈黃旛、丑圈拔鞍，第75頁戌圈拔鞍與子圈陌越，為本輪新辨字；不擴張到其他頁同名候選。','第73頁太歲已有舊卡，不重複建立；其底邊伏尸細字被邊界截去，仍不補全。第74頁寅圈地字後字及闌干宿度旁字、第75頁中央丑年字、未圈邊損字、申圈天官符旁字仍保留待核。','階段1.5仍未驗收；下一步續核第76–80頁，不等同所有圖字均清楚。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
with (ROOT/'docs/catalog/星學綱目正傳.md').open('a') as f:f.write('\n### 2026-11-25：第74–75頁細字續核\n\n第74頁黃旛／辰、拔鞍／丑，第75頁拔鞍／戌、陌越／子，共4處新辨原字新增4卡，其他卡不動。保留旛、拔、陌字，不換他頁通行名。[原圖與逐項清單](../檢查/'+stem+'.md)。其餘細字與邊損字仍待核。\n')
p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('|星學綱目正傳|'):
        c=line.strip('|').split('|');c[5]=c[5].replace('5716','5720');c[6]+='；同日第74–75頁黃旛、拔鞍兩處及陌越，共4卡依原字補錄，不換通行名，餘細字未清';c[7]='2026-11-25';lines[i]='|'+'|'.join(c)+'|'
p.write_text('\n'.join(lines)+'\n')
p=ROOT/'docs/狀態.md';s=p.read_text().replace('共20,280張；綱目5,716張','共20,284張；綱目5,720張');s=re.sub(r'復工位置：[^\n]+','復工位置：《綱目》第74–75頁新核黃旛、拔鞍兩處、陌越，新增4卡；73頁太歲已在舊卡，不重建；邊損細字仍保留。下一個第一動作：第76–80頁既有未清細字按原生圖續核；已裁決歲殿登籍與擎遊邊界不擴張。',s,1);p.write_text(s)
for relative in ['docs/階段1.5目前檢查摘要.md','docs/檢查/階段1.5完成條件核對-2026-11-18.md','docs/檢查/階段1.5待校與待裁決分界.md']:
    p=ROOT/relative;s=p.read_text().replace('20,280','20,284').replace('20280','20284').replace('6,448','6,452').replace('6448','6452');p.write_text(s)
p=D/'階段1.5待校與待裁決分界.json';j=json.loads(p.read_text());j['卡片數']=len(before)+4
for r in j['明細']:
    if r['書名']=='星學綱目正傳' and r['頁碼'] in (74,75):r['最新續核']='2026-11-25部分細字新核，見'+stem+'.md；其餘未清字保留，不標全頁完成。'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='明細'},ensure_ascii=False))
