"""執行：依第99頁原圖補飛廉下注；OCR候選僅留存，不自動採字。"""
from review_helpers import *
import subprocess,shutil

stem='綱目99飛廉下注續核-2026-11-25';name='飛廉圖下注（星學綱目第99頁）.md';p=K/name
assert not p.exists()
quote='此主非災横禍及主惡死'
before={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in K.glob('*.md')}
assert not any(quote in x.read_text() for x in K.glob('*.md'))
src=Path('/workspace/review/ocr/綱目-99-原圖0.png');picture=framed_image(src,[0,666,62,938],PIC/stem/'飛廉下注-兩行紅框.png','綱目PDF第99頁：飛廉下注，先右行再左行',scale=4,margin=16)
body=f'#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n《星學綱目正傳》第99頁：\n\n原文以圖表呈現\n\n{quote}\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n'
p.write_text(body)
assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==v for n,v in before.items())
archive=ROOT/'docs/勘校修訂'/stem;archive.mkdir()
e={'日期':'2026-11-25','基準提交':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'卡片':name,'原頁':99,'來源類型':'人工校讀','原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'紅框圖':picture,'舊全文':None,'舊SHA256':None,'新增全文':body,'新增SHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'新增卡數':1,'既有卡異動':0,'卡片總數':len(before)+1,'說明':'原字横照錄，不改成其他字；不以OCR候選淡或其他書的語句代填。'}
(archive/'新卡全文與SHA256.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n')
shutil.copyfile('/tmp/綱目99飛廉再核.json',D/(stem+'-PaddleOCR候選.json'))
(D/(stem+'.md')).write_text('# 綱目第99頁飛廉下注續核\n\n原圖飛廉欄下注先右行、再左行，照錄「'+quote+'」。保留原刻横字，不改通行字；OCR候選有漏字及誤字，只作定位。\n\n[兩行紅框](../'+picture.removeprefix('docs/')+')；[新卡全文與SHA256](../勘校修訂/'+stem+'/新卡全文與SHA256.json)；[OCR候選]('+stem+'-PaddleOCR候選.json)。\n\n新增有實質規則原文的卡1張，既有卡異動0。全庫20,280張、綱目5,716張。未載操作步驟、原例標原文未提及及無；不解釋或套用斷語。\n\n本次只補未收的下注；第98頁其他欄旁、100頁未授權字與101頁截斷接行仍保留，已裁決值不重問、不覆寫。\n')
with (ROOT/'docs/catalog/星學綱目正傳.md').open('a') as f:f.write('\n### 2026-11-25：第99頁飛廉下注\n\n原圖兩行「'+quote+'」已核字新增1卡，原刻横字保留，既有卡不動。全庫20,280、綱目5,716。[原圖與新卡雜湊](../檢查/'+stem+'.md)。\n')
p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('|星學綱目正傳|'):
        c=line.strip('|').split('|');c[5]=c[5].replace('5715','5716');c[6]+='；同日第99頁飛廉下注原字新增1卡，横字照錄；第98、100、101頁未授權及截斷接行保留';c[7]='2026-11-25';lines[i]='|'+'|'.join(c)+'|'
p.write_text('\n'.join(lines)+'\n')
p=ROOT/'docs/狀態.md';s=p.read_text().replace('共20,279張；綱目5,715張','共20,280張；綱目5,716張');s=re.sub(r'復工位置：[^\n]+','復工位置：《綱目》97頁天嗣下注及99頁飛廉下注各新增1卡，98、100、101頁原圖已接續查看，已授權字保持；未清欄旁與截斷接行待核。下一個第一動作：73–96頁既有逐頁未清細字按原生圖續核，先從73頁開始；原有歲殿登籍及擎遊裁決邊界不擴張。',s,1);p.write_text(s)
for relative in ['docs/階段1.5目前檢查摘要.md','docs/檢查/階段1.5完成條件核對-2026-11-18.md','docs/檢查/階段1.5待校與待裁決分界.md']:
    p=ROOT/relative;s=p.read_text().replace('20,279','20,280').replace('20279','20280').replace('6,447','6,448').replace('6447','6448');p.write_text(s)
p=D/'階段1.5待校與待裁決分界.json';j=json.loads(p.read_text());j['卡片數']=len(before)+1
for r in j['明細']:
    if r['書名']=='星學綱目正傳' and r['頁碼']==99:
        r['未完成範圍']='飛廉下注兩行已核圖新增1卡；其餘已收字不重做，未授權異讀或截斷接行保留。';r['報告入口']=stem+'.md'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:e[k] for k in ['新增卡數','既有卡異動','卡片總數']},ensure_ascii=False))
