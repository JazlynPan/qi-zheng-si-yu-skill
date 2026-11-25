"""執行：保存河洛第2頁14處四方向人工覆核、已確認原字及全文雜湊。"""
from review_helpers import *
import subprocess

DATE='2026-11-25'
stem='河洛第2頁斜排續核-'+DATE
source=Path('/workspace/review/ocr/河洛-2-原圖0.png')
image=Image.open(source).convert('RGB')
previous=json.loads((D/'河洛第2頁原圖0之39框位置對照-2026-11-21.json').read_text())
rows=[x for x in previous['明細'] if x.get('人工接續結果')=='旋斜／紅筆重疊，未確認']
assert len(rows)==14
# 人工逐張看過四向圖；本表不是OCR輸出，也不推算任何宮位或取法。
readings={11:'角',16:'卯',21:'婁',25:'金',29:'壁',32:'室',35:'危',36:'虛',37:'田'}
folder=PIC/stem
folder.mkdir(exist_ok=True)
details=[]
for row in rows:
    number=int(row['編號'].split('-')[-1])
    x0,y0,x1,y1=map(int,row['原框'])
    cut=(max(0,x0-25),max(0,y0-25),min(image.width,x1+25),min(image.height,y1+25))
    tile=image.crop(cut).resize(((cut[2]-cut[0])*4,(cut[3]-cut[1])*4))
    ImageDraw.Draw(tile).rectangle(((x0-cut[0])*4,(y0-cut[1])*4,(x1-cut[0])*4,(y1-cut[1])*4),outline='red',width=3)
    panel=Image.new('RGB',(1100,1120),'white')
    draw=ImageDraw.Draw(panel)
    draw.text((8,8),row['編號']+'／河洛PDF第2頁原圖0：只旋轉、放大，不補畫',font=FONT,fill='black')
    for i,angle in enumerate((0,90,180,270)):
        rotated=tile.rotate(angle,expand=True)
        rotated.thumbnail((520,480))
        xx=10+(i%2)*550; yy=60+(i//2)*530
        draw.text((xx,yy),f'逆時針{angle}度',font=FONT,fill='black')
        panel.paste(rotated,(xx,yy+30))
    output=folder/(row['編號']+'-四方向.png')
    panel.save(output)
    details.append({'編號':row['編號'],'原頁':2,'原圖序號':0,'原框':row['原框'],'來源類型':'人工校讀','讀值':readings.get(number,''),'結果':'原字可辨，僅收字面' if number in readings else '紅筆重疊／旋斜，仍未確認','紅框圖':str(output.relative_to(ROOT))})

name='首例星盤邊欄文字（河洛五星合參案例抄本）.md'
p=K/name
old=p.read_bytes()
before={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in K.glob('*.md')}
archive=ROOT/'docs/勘校修訂'/stem
assert not archive.exists(), '已執行過，勿重複追加'
archive.mkdir()
new=old+('\n《河洛五星合參案例抄本》第2頁：\n\n原文以圖表呈現\n\n'+'\n\n'.join(readings.values())+'\n').encode()
p.write_bytes(new)
assert new.startswith(old)
assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==digest for n,digest in before.items() if n!=name)
assert all(new.decode().count('## '+field)==1 for field in ('核心概念','使用規則','操作步驟','原文例子'))
record={'日期':DATE,'基準提交':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'卡片':name,'原頁':2,'來源類型':'人工校讀','原圖SHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'舊全文':old.decode(),'新全文':new.decode(),'舊SHA256':hashlib.sha256(old).hexdigest(),'新SHA256':hashlib.sha256(new).hexdigest(),'原有全文完整前綴':True,'新增片段':list(readings.values()),'新增卡數':0,'其餘卡片異動':0}
(archive/'舊新全文與SHA256.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
report={'日期':DATE,'範圍':'原圖0之14處先前未確認框；不代表全頁覆蓋','人工看圖角度':[0,90,180,270],'可辨字位':9,'仍未確認框':5,'修改既有卡數':1,'新增卡數':0,'卡片總數':len(before),'明細':details}
(D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 河洛第2頁斜排續核（2026-11-25）','','## 完成範圍','','原圖0先前14處未確認框，逐張查看0、90、180、270度圖。9處可辨的獨立原字追加到同一命例卡，5框仍未確認。不把字面串成句、不判星宮歸屬、不推算取法；框外字仍不算已核。','新增卡0，追加既有卡1，其餘卡異動0，全庫20,278卡。放大不增加來源細節，不補畫。','','|編號|原字|結果|原圖|','|---|---|---|---|']
for r in details:
    md.append(f'|{r["編號"]}|{r["讀值"] or "未確認"}|{r["結果"]}|[四方向紅框](../{r["紅框圖"].removeprefix("docs/")})|')
md+=['','## 留存與後續','','[舊新全文與SHA256](../勘校修訂/'+stem+'/舊新全文與SHA256.json)。原有卡片全文逐位元組保留為新卡前綴；只追加9個原字。','HL2-0-12、14、22、38、39仍未確認，未將候選當原字；原圖1尚未完成候選覆蓋對照。不宣稱第2頁、全書或階段1.5完成。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
with (ROOT/'docs/勘校修訂紀錄.md').open('a') as f:
    f.write('\n## 2026-11-25【原文續錄】河洛第2頁斜排字位\n\n只追加角、卯、婁、金、壁、室、危、虛、田9個可辨原字，不串句、不補取法；原全文逐位元組完整保留。[逐框原圖與結果](檢查/'+stem+'.md)；[舊新全文與SHA256](勘校修訂/'+stem+'/舊新全文與SHA256.json)。\n')
with (ROOT/'docs/catalog/河洛五星合參案例抄本.md').open('a') as f:
    f.write('\n### 2026-11-25：第2頁14處四方向續核\n\n9處可辨獨立原字追加原命例；5處仍未確認。不刪改上次紀錄，其14處為當時狀態；本次續核結果見[逐框報告](../檢查/'+stem+'.md)。仍61卡，未驗收整頁。\n\n|概念名稱／定位編號|書名|PDF頁碼|原因|\n|---|---|---|---|\n|HL2-0-12、14、22、38、39|河洛五星合參案例抄本|2（原圖0）|四方向查看後，紅筆重疊或旋斜字形仍不足以確認，未入卡；原圖1覆蓋另待續核。|\n')
p=ROOT/'docs/來源清單.md'
lines=p.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('|河洛五星合參案例抄本|'):
        cols=line.strip('|').split('|')
        cols[6]+='；2026-11-25第2頁原圖0之14處四方向續核，9處可辨原字追加原命例，5框仍未確認，原圖1覆蓋未完'
        cols[7]=DATE
        lines[i]='|'+'|'.join(cols)+'|'
p.write_text('\n'.join(lines)+'\n')
p=ROOT/'docs/狀態.md'
s=p.read_text().replace('統計日期2026-11-21','統計日期2026-11-25',1)
s=re.sub(r'復工位置：[^\n]+','復工位置：《河洛五星合參案例抄本》第2頁原圖0之14處四方向續核，9處原字已追加原命例，5框仍未確認（HL2-0-12、14、22、38、39）。下一個第一動作：原圖1之0度OCR框與既有T17框作位置對照，只處理未覆蓋字位；原圖0未確認5框保留，整頁尚未驗收。',s,1)
p.write_text(s)
print(json.dumps({k:v for k,v in report.items() if k!='明細'},ensure_ascii=False))
