"""執行：保存河洛第3頁下欄兩條原字、紅框及舊新全文。"""
from review_helpers import *
import subprocess

stem='河洛第3頁氣值地元續核-2026-11-25'
name='首例河洛數圖中文字（河洛五星合參案例抄本）.md'
src=Path('/workspace/review/ocr/河洛-3-原圖0.png')
rows=[]
for ident,text,box in [('HL3-氣值','氣值一陰',[303,817,364,1000]),('HL3-地元','地元巽',[140,818,200,1008])]:
    picture=framed_image(src,box,PIC/stem/(ident+'.png'),f'河洛PDF第3頁／{ident}：下欄直讀',scale=4,margin=18)
    rows.append({'定位':ident,'原文':text,'原頁':3,'原圖序號':0,'原框':box,'來源類型':'人工校讀','紅框圖':picture})
path=K/name;old=path.read_bytes()
assert all(x['原文'] not in old.decode() for x in rows)
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.md')}
new=old+('\n《河洛五星合參案例抄本》第3頁：\n\n原文以圖表呈現\n\n'+'\n\n'.join(x['原文'] for x in rows)+'\n').encode()
assert new.startswith(old)
archive=ROOT/'docs/勘校修訂'/stem
assert not archive.exists()
archive.mkdir()
path.write_bytes(new)
assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==v for n,v in before.items() if n!=name)
assert all(new.decode().count('## '+f)==1 for f in ('核心概念','使用規則','操作步驟','原文例子'))
evidence={'日期':'2026-11-25','基準提交':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'卡片':name,'舊全文':old.decode(),'新全文':new.decode(),'舊SHA256':hashlib.sha256(old).hexdigest(),'新SHA256':hashlib.sha256(new).hexdigest(),'原有全文完整前綴':True,'原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'明細':rows,'修改卡數':1,'新增卡數':0,'其餘卡異動':0,'卡片總數':len(before)}
(archive/'舊新全文與SHA256.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
md=['# 河洛第3頁氣值、地元續核','','下欄依直行讀序，新補「氣值一陰」「地元巽」至既有命例卡；只抄明寫的文字，不從卦畫推算，不解釋取法。原卡已有的地元、後天全等片段保持不動。','','|原頁|原文|來源類型|原圖|','|---|---|---|---|']
for x in rows:
    md.append(f'|3|{x["原文"]}|人工校讀|[紅框](../{x["紅框圖"].removeprefix("docs/")})|')
md+=['','既有卡追加1、新卡0、其餘卡異動0；總卡數20,278。原卡完整保留為新卡前綴，沒有改寫原文。','[舊新全文與SHA256](../勘校修訂/'+stem+'/舊新全文與SHA256.json)。','第3頁上方數字行、卦畫爻旁散字仍須逐區對照，不由卦形填字。第2頁12框仍未確認；不宣告全頁、全書或階段完成。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
with (ROOT/'docs/勘校修訂紀錄.md').open('a') as f:
    f.write('\n## 2026-11-25【原文續錄】河洛第3頁下欄\n\n追加氣值一陰、地元巽兩條原字，原卡全文逐位元組保留；不由卦畫推算。[原圖及結果](檢查/'+stem+'.md)；[舊新全文與SHA256](勘校修訂/'+stem+'/舊新全文與SHA256.json)。\n')
with (ROOT/'docs/catalog/河洛五星合參案例抄本.md').open('a') as f:
    f.write('\n### 2026-11-25：第3頁下欄續核\n\n下欄原圖明寫「氣值一陰」「地元巽」兩條追加既有命例，原片段全保留。只據明文，不從卦畫推算。[紅框及全文留存](../檢查/'+stem+'.md)。上方數字行及爻旁散字仍未全區核銷，未標全頁完成。\n')
p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('|河洛五星合參案例抄本|'):
        c=line.strip('|').split('|');c[6]+='；同日第3頁下欄氣值一陰、地元巽兩條明文追加既有命例，數字行及爻旁散字未全核';c[7]='2026-11-25';lines[i]='|'+'|'.join(c)+'|'
p.write_text('\n'.join(lines)+'\n')
p=ROOT/'docs/狀態.md';s=p.read_text()
s=re.sub(r'復工位置：[^\n]+','復工位置：《河洛五星合參案例抄本》第2頁本輪補19處原字、第3頁下欄補氣值一陰與地元巽至兩張既有命例；新增卡0。第2頁原圖0五框、原圖1七框仍未確認。下一個第一動作：第3頁上方數字行及卦畫爻旁散字，先對照既有卡與T17框定位未收明文；只抄明字，不從卦畫推算，整頁未驗收。',s,1)
p.write_text(s)
print('第3頁原文追加2條；既有卡追加1、新卡0、其餘卡異動0，舊全文前綴及四欄檢查通過。')
