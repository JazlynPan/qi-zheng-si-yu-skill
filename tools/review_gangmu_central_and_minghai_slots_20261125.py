"""執行：保存12個中央歲駕原圖覆核及命海132格卡片覆蓋；不改卡。"""
from review_helpers import *
from collections import Counter
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.md')}
stem='綱目十二歲駕字區與命海132格覆蓋-2026-11-25'
values=['木','土','木','火','金','水','日','炁','水','金','火','木'];rows=[]
for i,page in enumerate(range(73,97,2)):
 branch='子丑寅卯辰巳午未申酉戌亥'[i];src=Path(f'/workspace/review/ocr/綱目-{page}-原圖0.png');im=Image.open(src);w,h=im.size
 candidates=list(K.glob(f'歲駕圖列·第{page}頁*（星學綱目圖說下）.md'));assert len(candidates)==1
 card=candidates[0];text=card.read_text();assert values[i] in text
 box=[int(w*.26),int(h*.64),int(w*.54),int(h*.94)]
 image=framed_image(src,box,PIC/stem/f'GM-{page}-中央歲駕.png',f'綱目PDF第{page}頁 中央歲駕原字；不是全頁驗收',scale=3,margin=5)
 rows.append({'PDF實際頁碼':page,'卡名中央字框':branch,'圖上歲駕星字':values[i],'旁註吉':page in [75,77,79],'卡片':str(card.relative_to(ROOT)),'紅框圖':image,'原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'結果':'既有歲駕原文已收，本字區不重建；相鄰外圈細字另列'})
slots=[]
for palace in '子丑寅卯辰巳午未申酉戌亥':
 for star in '日月木火土金水炁孛羅計':
  p=K/f'{palace}宮{star}圖列（星平總會命海）.md';assert p.exists();text=p.read_text();assert '《星平總會命海》第16頁' in text
  slots.append({'宮':palace,'星曜':star,'卡片':str(p.relative_to(ROOT)),'SHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'有原頁引用':True,'結論':'具名卡已存在；不是逐字讀值驗收'})
report={'日期':'2026-11-25','綱目中央歲駕圖區數':12,'中央字區新增卡':0,'命海第16頁應有格數':132,'已有具名卡數':len(slots),'缺具名卡數':0,'卡片異動':0,'綱目中央字區明細':rows,'命海132格明細':slots,'限制':'歲駕區為直接看圖核對既有原字；命海132格是E0存在性檢查，不把132格都說成使用者已逐字確認。不能由這兩種覆蓋檢查宣稱階段1.5完成。'}
(D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 綱目十二歲駕字區與命海132格覆蓋','','## 結果','','《綱目》12個中央歲駕字區再看原圖，星字已有原卡；新增0、改卡0。中央歲駕不是待補卡缺口，相鄰外圈細註仍須分開記。','','|PDF頁|中央字框（沿用卡名）|圖上歲駕星字|旁見吉|圖|','|---|---|---|---|---|']
for r in rows:md.append(f'|{r["PDF實際頁碼"]}|{r["卡名中央字框"]}|{r["圖上歲駕星字"]}|{"有" if r["旁註吉"] else "本區未另記"}|[紅框](../{r["紅框圖"].removeprefix("docs/")})|')
md+=['','## 命海第16頁','','12宮×11曜＝132個應有位置，都有具名卡且各載第16頁出處；缺卡0。這是E0結構覆蓋，不是132格讀值全數驗收。T14已裁決字不重問、不重改；其他需要改字的項目仍須使用者確認。','[逐格卡名、雜湊及圖證據]('+stem+'.json)。','','## 限制','','本報告只能把「中央歲駕未查」與「132格可能缺卡」這兩類籠統敘述換成具體結果。不能把別處淡損宿度、擎遊歸屬、尚未授權的登籍缺卡，當作已結案。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==h for n,h in before.items())
print(json.dumps({'中央歲駕':len(rows),'命海具名卡':len(slots),'卡片異動':0},ensure_ascii=False))
