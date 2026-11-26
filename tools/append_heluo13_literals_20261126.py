"""執行：將第13頁確定可見的比肩、木胃續錄至原命例；舊全文保留。"""
from review_helpers import *
import subprocess
stem='河洛13頁比肩木胃續錄-2026-11-26';name='次例星盤邊欄文字（河洛五星合參案例抄本）.md';p=K/name;old=p.read_bytes();before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.md')}
assert '比肩' not in old.decode() and '木胃' not in old.decode()
addition='\n《河洛五星合參案例抄本》第13頁：\n\n原文以圖表呈現\n\n比肩\n\n木胃\n';new=old+addition.encode();assert new[:len(old)]==old;p.write_bytes(new)
folder=PIC/stem;folder.mkdir();images=[]
for index in [19,16]:
 src=Image.open(PIC/'河洛195段逐框覆核-2026-11-26'/f'HL13-{index:02d}.png');tile=src.crop((0,55,src.width,src.height)).rotate(90,expand=True);panel=Image.new('RGB',(max(550,tile.width),tile.height+55),'white');panel.paste(tile,(0,55));ImageDraw.Draw(panel).text((8,8),f'河洛第13頁 HL13-{index:02d}；原框旋轉90度，不改筆畫',font=FONT,fill='black');dest=folder/f'HL13-{index:02d}-旋轉90.png';panel.save(dest);images.append(str(dest.relative_to(ROOT)))
assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==h for n,h in before.items() if n!=name)
a=ROOT/'docs/勘校修訂'/stem;a.mkdir()
record={'日期':'2026-11-26','基準提交':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'書名':'河洛五星合參案例抄本','PDF實際頁碼':13,'卡片':name,'來源類型':'人工看原圖，旋轉僅協助讀序','舊全文':old.decode(),'舊SHA256':hashlib.sha256(old).hexdigest(),'新全文':new.decode(),'新SHA256':hashlib.sha256(new).hexdigest(),'只追加原文':addition,'舊位元組前綴完整':True,'既有原字覆寫':0,'新增卡數':0,'既有卡追加數':1,'圖':images,'限制':'木胃後的小字未取定，不補成十一或其他度數；比肩、木胃是此命例原圖的文字，未改作通用取法。'}
(a/'舊新全文與SHA256.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
(D/(stem+'.md')).write_text('# 河洛第13頁比肩、木胃續錄\n\n第13頁原圖0，HL13-19旋轉後可辨比肩，HL13-16可辨木胃。兩片段原例尚未收，現在只續錄原字；木胃後數字未取定，沒有填度數。\n\n原卡只追加1張，舊字覆寫0、新增卡0；全庫20,387張。\n\n'+ '\n'.join('[紅框旋轉圖](../'+x.removeprefix('docs/')+')。' for x in images)+'\n\n[完整舊新全文與SHA256](../勘校修訂/'+stem+'/舊新全文與SHA256.json)。\n')
with (ROOT/'docs/勘校修訂紀錄.md').open('a') as f:f.write('\n## 2026-11-26【原文續錄】河洛第13頁比肩、木胃\n\n只續錄此命例兩片段，不補度數，不改原字。[原圖](檢查/'+stem+'.md)；[舊新全文與SHA256](勘校修訂/'+stem+'/舊新全文與SHA256.json)。\n')
with (ROOT/'docs/catalog/河洛五星合參案例抄本.md').open('a') as f:f.write('\n### 2026-11-26：第13頁兩處文字\n\n比肩、木胃續入同一命例，原字不改。木胃後小字不確定，不填度數。[兩框原圖與全文保留](../檢查/'+stem+'.md)。\n')
p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
for i,line in enumerate(lines):
 if line.startswith('|河洛五星合參案例抄本|'):
  c=line.strip('|').split('|');c[6]+='；2026-11-26第13頁比肩、木胃續入原命例，木胃後度數未定，不代填';c[7]='2026-11-26';lines[i]='|'+'|'.join(c)+'|'
p.write_text('\n'.join(lines)+'\n')
p=ROOT/'docs/狀態.md';s=p.read_text();s=s.replace('下一個第一動作：第12、13、15頁逐框記錄已收片段、符號與未辨字；不把機械命中當核字驗收。','第13頁比肩、木胃兩片段已續入原命例，後接度數未補。下一個第一動作：完成第12、13、15頁逐框記錄，與第2、3頁已有結果合成195框明細；未辨字保持待核。');p.write_text(s)
subprocess.run(['python','tools/check_stage15_progress.py','--output','docs/檢查/'+stem+'-檢查.json','--expected-items','90','--expected-changed-card',name],check=True,cwd=ROOT)
