"""執行：保存原圖1之22處四方向人工判讀、原文追加與復工位置。"""
from review_helpers import *
from collections import Counter
import subprocess

stem='河洛第2頁原圖1之50框位置對照-2026-11-25'
path=D/(stem+'.json')
j=json.loads(path.read_text())
existing={1:'偏財弦照',2:'財官拱命',3:'文星登駕',27:'角',42:'陰陽差錯'}
fresh={9:'鬼',11:'柳',15:'張',18:'翼',29:'正印',30:'亢',36:'木',38:'天哭',40:'心',46:'尾'}
name='首例星盤邊欄文字（河洛五星合參案例抄本）.md'
p=K/name
old=p.read_bytes()
before={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in K.glob('*.md')}
for r in j['明細']:
    if not r['紅框圖']:
        continue
    n=int(r['編號'].split('-')[-1])
    r['來源類型']='人工校讀'
    r['人工查看角度']=[0,90,180,270]
    r['人工原字']=existing.get(n,fresh.get(n,''))
    r['人工結果']='既有原字已收' if n in existing else '可辨原字追加' if n in fresh else '仍未確認，不採機器候選'
    if n in existing:
        assert existing[n] in old.decode()
j['人工結果統計']=dict(Counter(r['人工結果'] for r in j['明細'] if r['紅框圖']))
j['限制']='位置交疊28框未逐框重核；另22框看四方向，5框字面已收、10框新補原字、7框未確認；不是整頁驗收。'
path.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
archive=ROOT/'docs/勘校修訂/河洛第2頁原圖1續核-2026-11-25'
assert not archive.exists()
archive.mkdir()
new=old+('\n《河洛五星合參案例抄本》第2頁：\n\n原文以圖表呈現\n\n'+'\n\n'.join(fresh.values())+'\n').encode()
p.write_bytes(new)
assert new.startswith(old)
assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==v for n,v in before.items() if n!=name)
assert all(new.decode().count('## '+field)==1 for field in ('核心概念','使用規則','操作步驟','原文例子'))
record={'日期':'2026-11-25','基準提交':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'卡片':name,'原頁':2,'來源類型':'人工校讀','原圖SHA256':hashlib.sha256(Path('/workspace/review/ocr/河洛-2-原圖1.png').read_bytes()).hexdigest(),'舊全文':old.decode(),'新全文':new.decode(),'舊SHA256':hashlib.sha256(old).hexdigest(),'新SHA256':hashlib.sha256(new).hexdigest(),'原有全文完整前綴':True,'新增片段':list(fresh.values()),'新增卡數':0,'其餘卡片異動':0}
(archive/'舊新全文與SHA256.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
p=D/(stem+'.md')
s=p.read_text()+'\n## 22框人工四方向續核\n\n'+str(j['人工結果統計'])+'。只記原字，不把獨立字位串成句、不賦予盤面含義；5框已有原字不重複追加。\n\n|編號|人工原字|結果|\n|---|---|---|\n'
for r in j['明細']:
    if r['紅框圖']:
        s+=f'|{r["編號"]}|{r["人工原字"] or "未確認"}|{r["人工結果"]}|\n'
s+='\n[舊新全文與SHA256](../勘校修訂/河洛第2頁原圖1續核-2026-11-25/舊新全文與SHA256.json)。修改既有卡1，新增卡0，總卡數20,278。\n\n仍未確認HL2-1-10、14、41、47、48、49、50；其中14框包含已收福德，但其餘重疊字未全核，不算全框完成。原圖0另有5框待核，兩圖框外環排未全部核銷。下一步轉第3頁原圖的候選覆蓋對照；這12框保留待看原圖，不靠上下文補字。\n'
p.write_text(s)
with (ROOT/'docs/勘校修訂紀錄.md').open('a') as f:
    f.write('\n## 2026-11-25【原文續錄】河洛第2頁原圖1\n\n原圖1之22框四方向查看，10處可辨原字追加原命例；5處已收不重複追加，7框未確認。原全文完整前綴保留。[逐框結果及紅框](檢查/'+stem+'.md)；[舊新全文與SHA256](勘校修訂/河洛第2頁原圖1續核-2026-11-25/舊新全文與SHA256.json)。\n')
with (ROOT/'docs/catalog/河洛五星合參案例抄本.md').open('a') as f:
    f.write('\n### 2026-11-25：第2頁原圖1續核\n\n50框先作位置對照，其中22框未充分交疊既有框，再看四方向：5處字面已收、10處原字追加原命例、7框未確認。不把框位交疊當作原字正確或全頁完成。[逐框結果與紅框](../檢查/'+stem+'.md)。\n\n|概念名稱／定位編號|書名|PDF頁碼|原因|\n|---|---|---|---|\n|HL2-1-10、14、41、47、48、49、50|河洛五星合參案例抄本|2（原圖1）|旋斜小字、紅筆重疊或候選為局部切片，四向看圖仍未全框確認；未填猜測字。|\n')
p=ROOT/'docs/來源清單.md'
lines=p.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('|河洛五星合參案例抄本|'):
        c=line.strip('|').split('|');c[6]+='；同日原圖1之50框完成位置對照，22框人工四向續核：5已收、10原字追加、7待核；原圖0另5框待核，兩圖未驗收全頁';c[7]='2026-11-25';lines[i]='|'+'|'.join(c)+'|'
p.write_text('\n'.join(lines)+'\n')
p=ROOT/'docs/狀態.md';s=p.read_text()
s=re.sub(r'復工位置：[^\n]+','復工位置：《河洛五星合參案例抄本》第2頁兩原圖本輪共追加19處原字至原命例（原圖0九處、原圖1十處），卡數不增；原圖0五框、原圖1七框仍未確認，不算全頁完成。下一個第一動作：第3頁原圖0之0度OCR候選與既有T17框作位置對照，核未覆蓋字位；第2頁12框保留待核，不靠上下文補字。',s,1)
p.write_text(s)
print(json.dumps(j['人工結果統計'],ensure_ascii=False))
