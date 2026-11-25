"""執行：原圖核字後新增天嗣下注卡，保留OCR候選與來源證據，不改既有卡。"""
from review_helpers import *
import subprocess,shutil

stem='綱目97天嗣下注續核-2026-11-25'
name='天嗣子孫星圖下注（星學綱目第97頁）.md'
path=K/name
assert not path.exists()
definition='是子孫星以我生物者'
rule='但要生復生之為主也'
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.md')}
assert not any(definition in p.read_text() for p in K.glob('*.md'))
src=Path('/workspace/review/ocr/綱目-97-原圖0.png')
picture=framed_image(src,[0,576,62,933],PIC/stem/'天嗣下注-兩行紅框.png','綱目PDF第97頁：天嗣下注，右行先讀，再左行',scale=4,margin=15)
top=framed_image(src,[395,150,453,213],PIC/stem/'玉堂首格-仍待核.png','綱目PDF第97頁：玉堂首格仍保留字形疑點',scale=4,margin=15)
body=f'#七政四餘\n\n## 核心概念\n\n《星學綱目正傳》第97頁：\n\n原文以圖表呈現\n\n天嗣\n\n{definition}\n\n## 使用規則\n\n《星學綱目正傳》第97頁：\n\n原文以圖表呈現\n\n{rule}\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n'
path.write_text(body)
assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==v for n,v in before.items())
archive=ROOT/'docs/勘校修訂'/stem
archive.mkdir()
evidence={'日期':'2026-11-25','處理':'新增原文卡，既有卡不動','基準提交':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'書名':'星學綱目正傳','PDF實際頁碼':97,'來源類型':'人工校讀；PP-OCRv5僅定位候選','原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'原框':[0,576,62,933],'紅框圖':picture,'卡片':name,'舊全文':None,'舊SHA256':None,'新增全文':body,'新增SHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'新增前同頁完全同文查重':0,'晉升自檢':{'書名頁碼':True,'四欄及缺載標記':True,'同頁原文不重複':True},'新增卡數':1,'既有卡異動':0,'卡片總數':len(before)+1}
(archive/'新卡全文與SHA256.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
ocr=D/(stem+'-PaddleOCR候選.json');shutil.copyfile('/tmp/綱目97天嗣再核.json',ocr)
md=['# 綱目第97頁天嗣下注續核','','## 新補原文','','原圖天嗣欄下注兩行，先右行、再左行；只照錄原字，不依其他書補字、不把復換成其他候選。已對照本機PP-OCRv5候選並直接看原圖；不是獨立代理驗收。','','|原頁|欄位|照錄原文|圖|','|---|---|---|---|',f'|97|核心概念|{definition}|[兩行紅框](../{picture.removeprefix("docs/")})|',f'|97|使用規則|{rule}|同上|','','新增卡1、既有卡異動0；總卡數20,279，綱目5,715。原書未見步驟、例子，分別標原文未提及、無；不建空殼。','[新卡全文與SHA256](../勘校修訂/'+stem+'/新卡全文與SHA256.json)；[OCR候選]('+ocr.name+')。','','## 保留字位','','玉堂首格木／未字形疑點仍保留，不由十干順序推字。[首格紅框](../'+top.removeprefix('docs/')+')。其餘已核九列原卡不改，不把本次補錄當成整頁驗收。','下一個動作：第98–101頁未收欄旁與下注細字，已裁決的簊金、婁水、會及指定宿度值不重問。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
with (ROOT/'docs/catalog/星學綱目正傳.md').open('a') as f:
    f.write('\n### 2026-11-25：第97頁天嗣下注\n\n原圖兩行照錄「是子孫星以我生物者」「但要生復生之為主也」，新增1張有實質原文的卡；全庫20,279、綱目5,715。只採原字，不用OCR取代看圖。[原圖、候選與新卡雜湊](../檢查/'+stem+'.md)。玉堂首格仍未確認，未補造全欄。\n')
p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('|星學綱目正傳|'):
        c=line.strip('|').split('|');c[5]=c[5].replace('5714','5715');c[6]+='；2026-11-25第97頁天嗣下注兩行明文新增1卡，原刻復字保留；玉堂首格仍未核定';c[7]='2026-11-25';lines[i]='|'+'|'.join(c)+'|'
p.write_text('\n'.join(lines)+'\n')
p=ROOT/'docs/狀態.md';s=p.read_text().replace('共20,278張；綱目5,714張','共20,279張；綱目5,715張')
s=re.sub(r'復工位置：[^\n]+','復工位置：《綱目》第97頁天嗣下注兩行已核原圖新增1卡，玉堂首格仍保留木／未疑點；全庫20,279張。下一個第一動作：第98–101頁未收欄旁與下注細字，已裁決簊金、婁水、會及指定宿度不重問；其他待裁決仍留清單，不以OCR候選代填。',s,1);p.write_text(s)
for relative in ['docs/階段1.5目前檢查摘要.md','docs/檢查/階段1.5完成條件核對-2026-11-18.md','docs/檢查/階段1.5待校與待裁決分界.md']:
    p=ROOT/relative;s=p.read_text().replace('20,278','20,279').replace('20278','20279').replace('6,446','6,447').replace('6446','6447').replace('2026-11-21統計','2026-11-25統計').replace('統計更新：2026-11-21','統計更新：2026-11-25')
    s+='\n2026-11-25更新：第97頁天嗣下注新增1卡，現有卡未改；總卡數20,279（knowledge每個Markdown檔計一張）。[原圖與檢查](綱目97天嗣下注續核-2026-11-25.md)。\n' if relative.startswith('docs/檢查/') else '\n2026-11-25更新：第97頁天嗣下注新增1卡；總卡數20,279。[原圖與檢查](檢查/綱目97天嗣下注續核-2026-11-25.md)。\n'
    p.write_text(s)
p=D/'階段1.5待校與待裁決分界.json';j=json.loads(p.read_text());j['日期']='2026-11-25';j['卡片數']=len(before)+1
for r in j['明細']:
    if r['書名']=='星學綱目正傳' and r['頁碼']==97:
        r['未完成範圍']='天嗣下注已核圖新增1卡；玉堂首格仍有木／未疑點。其餘細字及整頁覆蓋未驗收。';r['下一動作']='保留玉堂首格待核，不由干序代填；已收天嗣下注不重做。';r['報告入口']=stem+'.md'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:evidence[k] for k in ['新增卡數','既有卡異動','卡片總數']},ensure_ascii=False))
