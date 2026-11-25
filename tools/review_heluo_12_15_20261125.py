"""執行：河洛12及15頁可辨完整字列續錄；疑似既有誤讀僅提案。"""
from review_helpers import *
import subprocess

stem='河洛12與15頁續核-2026-11-25'
archive=ROOT/'docs/勘校修訂'/stem
assert not archive.exists()
archive.mkdir()
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.md')}
base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
groups=[('次例四柱附文圖中文字（河洛五星合參案例抄本）.md',12,[('丙辰入巳相品',[420,795,483,1025]),('丙寅入午福德',[373,795,429,1026]),('丁丑入未官祿',[322,795,380,1028])]),('次例河洛數圖中文字（河洛五星合參案例抄本）.md',15,[('天元坤先後天全見',[201,840,268,1040])])]
rows=[];records=[]
for name,page,phrases in groups:
    p=K/name;old=p.read_bytes();src=Path(f'/workspace/review/ocr/河洛-{page}-原圖0.png')
    for n,(text,box) in enumerate(phrases,1):
        assert text not in ''.join(old.decode().split())
        image=framed_image(src,box,PIC/stem/f'HL{page}-{n:02}.png',f'河洛PDF第{page}頁：{text}',scale=4,margin=15)
        rows.append({'卡片':name,'原頁':page,'原文':text,'來源類型':'人工校讀','原框':box,'紅框圖':image})
    new=old+(f'\n《河洛五星合參案例抄本》第{page}頁：\n\n原文以圖表呈現\n\n'+'\n\n'.join(t for t,b in phrases)+'\n').encode()
    assert new.startswith(old)
    p.write_bytes(new)
    assert all(new.decode().count('## '+f)==1 for f in ('核心概念','使用規則','操作步驟','原文例子'))
    records.append({'卡片':name,'原頁':page,'基準提交':base,'舊全文':old.decode(),'新全文':new.decode(),'舊SHA256':hashlib.sha256(old).hexdigest(),'新SHA256':hashlib.sha256(new).hexdigest(),'原全文完整前綴':True,'原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest()})
changed={n for n,p,phrases in groups}
assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==v for n,v in before.items() if n not in changed)
(archive/'舊新全文與SHA256.json').write_text(json.dumps({'日期':'2026-11-25','明細':records},ensure_ascii=False,indent=2)+'\n')
suspect=framed_image(Path('/workspace/review/ocr/河洛-15-原圖0.png'),[263,842,326,1027],PIC/stem/'HL15-候卦-待確認.png','河洛PDF第15頁：現卡未濟／原圖候選未逢，待使用者裁決',scale=4,margin=20)
report={'日期':'2026-11-25','既有卡追加數':2,'新增卡數':0,'新增完整字列':4,'其他卡片異動':0,'卡片總數':len(before),'明細':rows,'待裁決':[{'編號':'HL15-候卦','卡片':groups[1][0],'原頁':15,'現值':'候卦未濟','原圖候選':'候卦未逢','問題':'請看紅框內的最後一字，是「逢」還是「濟」？','紅框圖':suspect,'處理':'只出提案，不覆寫原卡'}]}
(D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 河洛第12、15頁續核','','## 原文續錄','','既有卡2張各追加原圖可辨完整字列，共4條；新增卡0，其他卡不動。舊全文逐位元組保留，未重新計算或推論運程。第12頁原卡已有丙辰、入、相品等片段，本次補齊同欄明寫的字列；不將其他欄位接在一起。','','|卡片|原頁|原文字列|紅框|','|---|---|---|---|']
for r in rows:
    md.append(f'|{r["卡片"]}|{r["原頁"]}|{r["原文"]}|[原圖](../{r["紅框圖"].removeprefix("docs/")})|')
md+=['','[舊新全文與SHA256](../勘校修訂/'+stem+'/舊新全文與SHA256.json)。','','## 需要使用者確認','','HL15-候卦：現卡「候卦未濟」；本輪原圖末字看作「逢」，但不據此覆寫已存引文。請看紅框內的最後一字，是「逢」還是「濟」？[紅框](../'+suspect.removeprefix('docs/')+')。','本項原先「未濟」來自2026-11-18代理校讀記錄，並非本輪使用者新增裁決。不把其後文字沿用誤當使用者已確認。','T17-082邊欄末字仍依原待決保留。第13頁仍有紅批重疊、底色淡字及T17-119圖糊，本批不改。第12頁紅筆數字與第15頁卦畫爻旁記號不由已知術數補讀，未宣告整頁或階段完成。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
with (ROOT/'docs/勘校修訂紀錄.md').open('a') as f:
    f.write('\n## 2026-11-25【原文續錄】河洛12與15頁\n\n追加丙辰入巳相品、丙寅入午福德、丁丑入未官祿、天元坤先後天全見4條原文至兩張既有命例；舊全文保留。[原圖及逐條結果](檢查/'+stem+'.md)；[舊新全文與SHA256](勘校修訂/'+stem+'/舊新全文與SHA256.json)。候卦未濟／未逢僅提案，未覆寫。\n')
with (ROOT/'docs/catalog/河洛五星合參案例抄本.md').open('a') as f:
    f.write('\n### 2026-11-25：第12、15頁完整字列續核\n\n第12頁補3條完整命例字列、第15頁補天元坤先後天全見，原卡舊文全部保留。[逐條原圖及待確認一字](../檢查/'+stem+'.md)。卡數仍61；第13頁未明環排與紅批繼續保留。\n\n|概念名稱／定位編號|書名|PDF頁碼|原因|\n|---|---|---|---|\n|HL15-候卦|河洛五星合參案例抄本|15|原卡未濟，本輪原圖候選未逢；紅框提報，未授權前不覆寫。|\n|紅筆數字、格外淡字及卦畫爻記|河洛五星合參案例抄本|12、13、15|部分細字、圖形記號仍無法確認完整讀序，不由術數推算、不建空殼卡。|\n')
p=ROOT/'docs/待你處理.md';s=p.read_text();marker='## 需要先確認規則'
line='- HL15-候卦｜請看紅框內最後一字，是「逢」還是「濟」？｜[報告](檢查/'+stem+'.md)｜[紅框]('+suspect.removeprefix('docs/')+')｜選項：逢／濟／看不清\n\n'
assert 'HL15-候卦' not in s
s=s.replace(marker,line+marker,1)
p.write_text(s)
p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('|河洛五星合參案例抄本|'):
        c=line.strip('|').split('|');c[6]+='；同日第12頁3條完整入宮字列及第15頁天元坤先後天全見追加既有命例；第15頁候卦末字未濟／未逢另提案，未覆寫';c[7]='2026-11-25';lines[i]='|'+'|'.join(c)+'|'
p.write_text('\n'.join(lines)+'\n')
p=ROOT/'docs/狀態.md';s=p.read_text();s=re.sub(r'復工位置：[^\n]+','復工位置：《河洛》第12頁三條入宮字列、第15頁天元坤先後天全見已補至既有命例；候卦未濟／未逢只出紅框提案。第2頁12框及第13頁未明環排仍保留。下一個第一動作：《命海》第331頁原圖，對照現有命例卡逐區核未收盤字；不等裁決才處理其他頁。',s,1)
s=s.replace('1. 目前4處字疑：','1. 新增HL15-候卦（未濟／未逢）待看原圖；原4處字疑：',1)
p.write_text(s)
print(json.dumps({k:v for k,v in report.items() if k not in ('明細','待裁決')},ensure_ascii=False))
