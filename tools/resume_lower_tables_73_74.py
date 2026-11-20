"""執行：prepare73/apply73/prepare74/apply74；原字與圈字照錄，不改舊卡。
目錄：DATA（人工校讀與框位）；prepare（原圖稿）；apply（新卡與雜湊驗證）。
"""
from review_helpers import *
import argparse,subprocess,shutil
DATA={73:[('咸池','酉',[267,504,296,579]),('卷舌','酉',[317,504,354,579]),('天解','戌',[459,594,490,660]),('解神','戌',[434,594,465,660]),('月煞','戌',[392,594,418,656]),('寡宿','戌',[341,594,376,657]),('吊客','戌',[320,594,349,657]),('血刃','戌',[301,594,327,657]),('浮沉','戌',[277,594,304,657]),('豹尾','戌',[251,594,282,658]),('將星','子',[61,679,99,743]),('劍鋒','子',[172,679,212,743]),('伏尸','子',[5,679,49,743])],74:[('破碎','午',[269,413,310,484]),('闌干','午',[328,413,368,473]),('大耗','午',[424,413,455,484]),('天哭','午',[455,413,484,484]),('劫殺','巳',[4,412,48,482]),('小耗','巳',[57,413,97,480]),('死符','巳',[160,413,198,480]),('披頭','辰',[2,501,43,574]),('五鬼','辰',[73,501,107,574]),('官符','辰',[147,501,180,574]),('飛符','辰',[180,501,207,574]),('華蓋','辰',[206,501,234,574]),('勾絞','卯',[60,583,98,650]),('紅鸞','卯',[156,583,195,650]),('喪門','寅',[1,672,36,742]),('孤辰','寅',[40,672,72,742]),('天祿','寅',[156,672,190,742]),('天馬','寅',[216,672,253,742]),('太陽','丑',[474,672,510,740]),('天空','丑',[415,682,448,736])]}
CELLS={73:{'酉':([265,498,530,588],[361,514,411,571]),'戌':([248,588,530,674],[365,603,408,660]),'子':([0,674,265,755],[100,681,159,741])},74:{'午':([261,398,511,493],[358,416,416,480]),'巳':([0,398,261,493],[103,418,158,481]),'辰':([0,493,261,578],[102,507,158,568]),'卯':([0,578,261,665],[101,590,156,650]),'寅':([0,665,261,755],[101,682,158,740]),'丑':([325,665,511,755],[357,680,410,738])}}
def pp(n):return D/f'綱目{n}頁餘下表續核稿-2026-11-20.json'
def prepare(n):
 assert not pp(n).exists();src=Path('/workspace/review/ocr')/f'綱目-{n}-原圖0.png';im=Image.open(src).convert('RGB');folder=PIC/f'綱目{n}頁餘下表';folder.mkdir(parents=True,exist_ok=True);rows=[]
 for title,circle,box in DATA[n]:
  name=f'{title}圖列·第{n}頁{circle}字圈（星學綱目圖說下）.md';assert not(K/name).exists();clip,cb=CELLS[n][circle];t=im.crop(clip);t=t.resize((t.width*3,t.height*3));pan=Image.new('RGB',(max(850,t.width),t.height+85),'white');pan.paste(t,(0,85));dr=ImageDraw.Draw(pan);dr.text((8,5),f'PDF第{n}頁 {title}／{circle}圈：只照錄原圖標示',font=FONT,fill='black');dr.text((8,35),'紅框是題字與圈字；不推定取法或年組',font=FONT,fill='red')
  for b in [box,cb]:dr.rectangle(((b[0]-clip[0])*3,85+(b[1]-clip[1])*3,(b[2]-clip[0])*3,85+(b[3]-clip[1])*3),outline='red',width=3)
  dst=folder/(title+'-'+circle+'.png');pan.save(dst);text=f'#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n《星學綱目正傳》第{n}頁〈六十年甲子圖〉：\n\n原文以圖表呈現\n\n{circle}\n\n{title}\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n';rows.append({'題字':title,'圈字':circle,'卡名':name,'PDF頁碼':n,'原圖':str(dst.relative_to(ROOT)),'題字像素框':box,'圈字像素框':cb,'原頁裁切像素':clip,'來源SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'新卡全文':text,'限制':'人工看圖照錄，不由OCR猜字；不推定原圖取法或年組'})
 pp(n).write_text(json.dumps({'日期':'2026-11-20','明細':rows},ensure_ascii=False,indent=2)+'\n')
 for off in range(0,len(rows),6):
  pan=Image.new('RGB',(1200,840),'white');dr=ImageDraw.Draw(pan)
  for j,r in enumerate(rows[off:off+6]):
   t=Image.open(ROOT/r['原圖']);t.thumbnail((590,235));x=j%2*600;y=j//2*280;pan.paste(t,(x,y+30));dr.text((x+5,y),r['題字']+'／'+r['圈字'],font=FONT,fill='black')
  pan.save(f'/tmp/綱目{n}餘字框位-{off//6+1}.png')
 print('紅框與稿',n,len(rows))
def apply(n):
 target=D/f'綱目{n}頁餘下表新增驗證-2026-11-20.json';assert not target.exists();rows=json.loads(pp(n).read_text())['明細'];before={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in K.glob('*.md')};base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
 for r in rows:
  p=K/r['卡名'];assert not p.exists();t=r['新卡全文'];assert t.splitlines()[0]=='#七政四餘';assert all('## '+x in t for x in ['核心概念','使用規則','操作步驟','原文例子']);p.write_text(t)
 assert all(hashlib.sha256((K/k).read_bytes()).hexdigest()==v for k,v in before.items());assert len(list(K.glob('*.md')))==len(before)+len(rows)
 ocr=f'綱目{n}'+('餘下表續核'if n==73 else'下表續核')+'-PaddleOCRv5.json';shutil.copyfile(Path('/workspace/review/ocr')/ocr,ROOT/'docs/ocr/機器候選'/ocr)
 result={'日期':'2026-11-20','基準提交':base,'PDF頁碼':n,'新增卡數':len(rows),'原有卡核對數':len(before),'原有卡異動':0,'卡片刪除':0,'新增空殼':0,'目前卡數':len(before)+len(rows),'明細':rows};target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 md=[f'# 綱目第{n}頁餘下表續核','','## 新增範圍','',f'本批新增{len(rows)}卡，原有{len(before):,}卡逐檔SHA256不變。只照錄可辨題字與圈字，不推定年組、宮位取法或普遍吉凶。','每張保留四欄、PDF實際頁碼與原圖以圖表呈現標示；無新增空殼。','','|題字／圈字|新卡|原圖|','|---|---|---|']
 for r in rows:md.append(f'|{r["題字"]}／{r["圈字"]}|[{r["卡名"]}](../../qi-zheng-si-yu/knowledge/{r["卡名"]})|[雙紅框](../{r["原圖"].removeprefix("docs/")})|')
 md+=['','## OCR與未收範圍','',f'[本機PP-OCRv5候選](../ocr/機器候選/{ocr})只輔助，不直接入卡。保留原圖吊、卷、劫殺等原字，不自動換成通行異體。','第73頁子圈底部細字、太／大歲首字仍待核；第74頁辰圈黃字下方、寅圈地字下方、中央拔／攀鞍、闌干旁細字與太陽附註尚未核清。按原頁分別記入catalog，不標整頁完成。','本批不續核第100頁暫停項，不拿第100頁伏尸、闌干或他書字值填入本頁。T15-032等待裁決卡不改。'];(D/f'綱目{n}頁餘下表續核-2026-11-20.md').write_text('\n'.join(md)+'\n')
 total=len(before)+len(rows);gangmu=sum('星學綱目正傳'in p.read_text()for p in K.glob('*.md'));p=ROOT/'docs/狀態.md';s=p.read_text();s=re.sub(r'共[\d,]+張；綱目[\d,]+張',f'共{total:,}張；綱目{gangmu:,}張',s,1);s=re.sub(r'復工位置：[^\n]+',f'復工位置：《星學綱目正傳》第{n}頁下表本批新增{len(rows)}卡；已收字不重讀。下一個第一動作：'+('接續第74頁下表。'if n==73 else'接續第75頁下表；73–74頁剩餘細字依catalog待核。')+'T15-032文室候選仍待確認，現卡文星未動。',s,1);p.write_text(s)
 p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
 for i,line in enumerate(lines):
  if line.startswith('|星學綱目正傳|'):
   c=line.strip('|').split('|');c[5]=re.sub(r'累計\d+張',f'累計{gangmu}張',c[5]);c[6]+=f'；2026-11-20第{n}頁下表可辨題字與圈字另收{len(rows)}卡，細字待核，不標全頁完成';lines[i]='|'+'|'.join(c)+'|'
 p.write_text('\n'.join(lines)+'\n')
 with(ROOT/'docs/catalog/星學綱目正傳.md').open('a')as f:f.write(f'\n2026-11-20｜第{n}頁下表新增{len(rows)}卡，只照錄可辨題字與圈字；[逐格原圖與剩餘細字](../檢查/綱目{n}頁餘下表續核-2026-11-20.md)。不標全頁完成，不改已有卡。\n')
 print(json.dumps({k:v for k,v in result.items()if k!='明細'},ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=['prepare73','apply73','prepare74','apply74']);a=ap.parse_args();n=int(a.mode[-2:]);prepare(n)if a.mode.startswith('prepare')else apply(n)
