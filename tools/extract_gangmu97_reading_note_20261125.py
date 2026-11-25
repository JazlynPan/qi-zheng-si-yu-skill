"""執行：照錄第97頁表頭讀圖指示，原卡不動；原圖與新卡全文留存。"""
from review_helpers import *
from stage2_preflight import parse
import subprocess
stem='綱目97表頭讀圖註續錄-2026-11-25'
name='天盤諸吉星例讀圖註（星學綱目第97頁）.md'
p=K/name;assert not p.exists()
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.md')}
assert not any('前有總圖合地支看' in p.read_text() for p in K.glob('*.md'))
src=Path('/workspace/review/ocr/綱目-97-原圖0.png')
picture=framed_image(src,[564,0,654,557],PIC/stem/'天盤表頭與横看原圖.png','綱目PDF第97頁：表頭原文與横看指示',scale=2,margin=0)
body='#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n《星學綱目正傳》第97頁：\n\n原文以圖表呈現\n\n天盤諸吉星例\n\n## 操作步驟\n\n《星學綱目正傳》第97頁：\n\n1. 横看\n2. 前有總圖合地支看\n\n## 原文例子\n\n無\n'
p.write_text(body)
assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==h for n,h in before.items())
total=len(before)+1;bookcount=sum(any(b=='星學綱目正傳' for b,a,z,u in parse(p.read_text())[1]) for p in K.glob('*.md'))
record={'日期':'2026-11-25','基準提交':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'卡片':name,'書名':'星學綱目正傳','PDF實際頁碼':97,'來源類型':'人工校讀原頁圖','原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'紅框圖':picture,'舊全文':None,'舊SHA256':None,'新全文':body,'新SHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'新增卡數':1,'既有卡異動':0,'查重同文數':0,'檢查':{'書名頁碼':True,'四欄':True,'有原文實質指示':True},'限制':'只錄原圖兩句，不解釋總圖範圍、不補表格演算方法。原字横保留，不改橫。'}
a=ROOT/'docs/勘校修訂'/stem;a.mkdir();(a/'新卡全文與SHA256.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
(D/(stem+'.md')).write_text('# 綱目第97頁表頭讀圖註續錄\n\n原圖右側表頭「天盤諸吉星例」；旁見「横看」與「前有總圖合地支看」。只照錄原文指示，不補讀表規則，原字横保留。\n\n新增1卡、既有卡異動0；全庫'+f'{total:,}'+'張，綱目'+f'{bookcount:,}'+'張。\n\n[紅框原圖](../'+picture.removeprefix('docs/')+')；[新卡全文與SHA256](../勘校修訂/'+stem+'/新卡全文與SHA256.json)。\n\n頁邊其他小註未全部辨清，不把這兩條指示視為全頁驗收。\n')
with (ROOT/'docs/catalog/星學綱目正傳.md').open('a') as f:f.write('\n### 2026-11-25：第97頁表頭讀圖註\n\n只照錄横看、前有總圖合地支看，新增1卡，原卡不改。[原圖與全文](../檢查/'+stem+'.md)。\n')
p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
for i,line in enumerate(lines):
 if line.startswith('|星學綱目正傳|'):
  c=line.strip('|').split('|');c[5]=re.sub(r'累計\d+張',f'累計{bookcount}張',c[5]);c[6]+='；2026-11-25第97頁表頭兩條讀圖原文新增1卡，不補取法';c[7]='2026-11-25';lines[i]='|'+'|'.join(c)+'|'
p.write_text('\n'.join(lines)+'\n')
p=ROOT/'docs/狀態.md';s=p.read_text();s=re.sub(r'共[\d,]+張；綱目[\d,]+張',f'共{total:,}張；綱目{bookcount:,}張',s);s=re.sub('復工位置：[^\n]+','復工位置：《綱目》第97頁表頭兩條讀圖原文已新增1卡，第98頁三欄下注已續錄，第84頁伏尸旁軫九已續錄。下一個第一動作：更新43個圖頁的實際剩餘範圍，分開已收、模糊與待授權項，不以卡數代表完成。',s,1);p.write_text(s)
for fn in ['docs/階段1.5目前檢查摘要.md','docs/檢查/階段1.5完成條件核對-2026-11-18.md','docs/檢查/階段1.5待校與待裁決分界.md']:
 p=ROOT/fn;s=p.read_text().replace('20,339','20,340').replace('20339','20340').replace('6,507','6,508').replace('6507','6508');p.write_text(s)
p=D/'階段1.5待校與待裁決分界.json';j=json.loads(p.read_text());j['卡片數']=total;p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['python','tools/check_stage15_progress.py','--output','docs/檢查/'+stem+'-檢查.json','--expected-items','85','--expected-new-card',name],check=True,cwd=ROOT)
