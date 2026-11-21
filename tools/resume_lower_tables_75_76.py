"""執行 prepare/apply 頁碼：人工原字、紅框、四欄新卡與舊卡雜湊檢查。"""
from review_helpers import *
import argparse, subprocess, shutil
DATE='2026-11-21'
DATA={75:[('破碎','未',[143,423,178,494]),('大耗','未',[179,422,219,493]),('闌干','未',[34,423,65,493]),('豹尾','未',[67,423,98,493]),('天厄','申',[303,423,332,485]),('天官符','申',[278,421,306,499]),('地解','申',[411,423,441,485]),('紫微','申',[442,423,472,485]),('解神','酉',[433,510,464,575]),('天解','酉',[463,510,495,575]),('將星','酉',[405,510,435,575]),('大殺','酉',[325,510,352,573]),('白虎','酉',[299,510,326,573]),('浮沉','酉',[274,510,301,573]),('血刃','酉',[253,510,276,573]),('福星','戌',[437,592,473,660]),('寡宿','戌',[263,592,298,660]),('吊客','亥',[264,677,298,741]),('病符','子',[163,677,201,741]),('六害','子',[40,677,81,741])]}
DATA[76]=[('飛符','巳',[165,409,199,478]),('官符','巳',[62,409,94,478]),('五鬼','巳',[31,409,62,478]),('年殺','午',[275,408,310,480]),('咸池','午',[310,408,344,480]),('小耗','午',[344,408,375,480]),('勾絞','辰',[162,494,195,561]),('貫索','辰',[55,494,89,569]),('天煞','辰',[0,494,35,561]),('喪門','卯',[157,577,195,644]),('地煞','卯',[55,577,91,644]),('災煞','卯',[0,577,36,648]),('紅鸞','寅',[188,667,221,736]),('玉堂','寅',[144,667,181,736]),('孤辰','寅',[76,667,110,737]),('天空','寅',[34,667,72,737]),('劫殺','寅',[0,667,36,741]),('伏尸','丑',[402,666,440,737]),('劍鋒','丑',[446,666,483,737]),('華蓋','丑',[307,666,344,737])]
CELLS={75:{'未':([0,416,255,508],[101,446,155,503]),'申':([253,416,516,508],[362,446,416,503]),'酉':([253,508,516,590],[362,533,418,583]),'戌':([253,590,516,674],[362,615,418,668]),'亥':([253,674,516,755],[362,694,418,748]),'子':([0,674,255,755],[101,694,154,749])},76:{'巳':([0,402,259,490],[102,427,159,480]),'午':([259,402,520,490],[366,429,416,483]),'辰':([0,490,259,572],[102,515,160,568]),'卯':([0,572,259,661],[102,596,159,654]),'寅':([0,661,259,751],[102,695,161,746]),'丑':([259,661,520,751],[364,692,419,747])}}
PENDING={75:'中央丑字框的年字、未圈左緣殘字、申圈天官符右鄰字、戌圈拔／攀鞍與子圈右側陌／陟越尚未定字',76:'巳圈最左題字、辰圈貫索下方細字、丑圈黃字後字與太歲首字，以及中央神煞細註仍待核'}
DATA[77]=[('小耗','未',[8,418,37,483]),('死符','未',[48,418,80,483]),('天官','未',[188,418,216,483]),('天馬','申',[460,418,491,484]),('解神','申',[430,418,461,484]),('闌干','申',[366,418,391,476]),('破碎','申',[334,418,366,484]),('血刃','申',[311,418,335,484]),('浮沉','申',[286,418,312,484]),('大耗','申',[263,418,288,484]),('紫微','酉',[459,506,489,574]),('地解','酉',[415,506,447,574]),('天厄','酉',[306,506,338,574]),('六害','酉',[273,506,307,574]),('華蓋','戌',[433,591,465,657]),('大殺','戌',[304,591,338,657]),('白虎','戌',[273,591,304,657]),('福星','亥',[434,680,468,744]),('劫煞','亥',[284,680,319,744]),('吊客','子',[88,679,118,746]),('災煞','子',[6,679,36,746])]
CELLS[77]={'未':([0,414,258,501],[108,441,153,496]),'申':([258,414,521,501],[365,445,419,499]),'酉':([258,501,521,588],[365,534,419,585]),'戌':([258,588,521,675],[365,615,419,667]),'亥':([258,675,521,760],[366,704,420,758]),'子':([0,675,258,760],[112,710,161,758])}
PENDING[77]='未圈拔／攀鞍、戌圈黃字後字、亥圈卷舌旁細字與中央年字尚未核清'
def path(n,suffix):return D/f'綱目{n}頁下表續核-{suffix}-{DATE}.json'
def prepare(n):
 assert not path(n,'逐字稿').exists()
 src=Path(f'/workspace/review/ocr/綱目-{n}-原圖0.png');im=Image.open(src).convert('RGB');rows=[]
 folder=PIC/f'綱目{n}頁下表續核';folder.mkdir(parents=True,exist_ok=True)
 for label,circle,box in DATA[n]:
  name=f'{label}圖列·第{n}頁{circle}字圈（星學綱目圖說下）.md';assert not(K/name).exists()
  clip,cb=CELLS[n][circle];tile=im.crop(clip);tile=tile.resize((tile.width*4,tile.height*4));pan=Image.new('RGB',(max(900,tile.width),tile.height+80),'white');pan.paste(tile,(0,80));dr=ImageDraw.Draw(pan)
  dr.text((8,4),f'PDF第{n}頁 {label}／{circle}圈：原字與圈字',font=FONT,fill='black');dr.text((8,34),'只照錄圖字，不推定年份歸屬或取法',font=FONT,fill='red')
  for b in [box,cb]:dr.rectangle(((b[0]-clip[0])*4,80+(b[1]-clip[1])*4,(b[2]-clip[0])*4,80+(b[3]-clip[1])*4),outline='red',width=3)
  dst=folder/f'{label}-{circle}.png';pan.save(dst)
  text=f'#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n《星學綱目正傳》第{n}頁〈六十年甲子圖〉：\n\n原文以圖表呈現\n\n{circle}\n\n{label}\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n'
  rows.append({'題字':label,'圈字':circle,'卡名':name,'PDF頁碼':n,'來源類型':'人工校讀','原圖':str(dst.relative_to(ROOT)),'題字像素框':box,'圈字像素框':cb,'原頁裁切像素':clip,'原頁SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'新卡全文':text,'新卡SHA256':hashlib.sha256(text.encode()).hexdigest()})
 path(n,'逐字稿').write_text(json.dumps({'日期':DATE,'明細':rows},ensure_ascii=False,indent=2)+'\n')
 for off in range(0,len(rows),4):
  canvas=Image.new('RGB',(1200,640),'white')
  for j,r in enumerate(rows[off:off+4]):
   tile=Image.open(ROOT/r['原圖']);tile.thumbnail((595,310));canvas.paste(tile,(j%2*600,j//2*320))
  canvas.save(f'/tmp/綱目{n}本批紅框-{off//4+1}.png')
 print(n,len(rows),'稿與紅框已存')
def apply(n):
 assert not path(n,'驗證').exists();rows=json.loads(path(n,'逐字稿').read_text())['明細'];before={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in K.glob('*.md')};base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
 for r in rows:
  assert not(K/r['卡名']).exists();(K/r['卡名']).write_bytes(r['新卡全文'].encode())
 assert all(hashlib.sha256((K/k).read_bytes()).hexdigest()==v for k,v in before.items())
 ocr=f'綱目{n}下表續核-PaddleOCRv5.json';shutil.copyfile(Path('/workspace/review/ocr')/ocr,ROOT/'docs/ocr/機器候選'/ocr)
 result={'日期':DATE,'基準提交':base,'原有卡數':len(before),'原有卡異動':0,'刪除':0,'新增卡數':len(rows),'全庫卡數':len(before)+len(rows),'明細':rows};path(n,'驗證').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 report=[f'# 綱目第{n}頁下表續核','','本批只照錄題字與圈字；原圖未明文交代的取法、年份歸屬與吉凶均不補入。',f'新增{len(rows)}卡；原有{len(before):,}卡SHA256全部相同；未刪卡。','', '|題字／圈字|新卡|原圖|','|---|---|---|']
 for r in rows:report.append(f'|{r["題字"]}／{r["圈字"]}|[{r["卡名"]}](../../qi-zheng-si-yu/knowledge/{r["卡名"]})|[紅框](../{r["原圖"].removeprefix("docs/")})|')
 report+=['','## 未收範圍','',f'[OCR候選](../ocr/機器候選/{ocr})只作定位輔助，卡片以人工看圖為準。',PENDING[n]+'；不建立空殼卡，不標整頁完成。','既有歲殿、登籍、擎遊與使用者待裁決項均未更動。']
 (D/f'綱目{n}頁下表續核-{DATE}.md').write_text('\n'.join(report)+'\n')
 total=len(before)+len(rows);gm=sum('星學綱目正傳'in p.read_text()for p in K.glob('*.md'));p=ROOT/'docs/狀態.md';s=p.read_text();s=re.sub(r'統計日期\d{4}-\d\d-\d\d',f'統計日期{DATE}',s,1);s=re.sub(r'共[\d,]+張；綱目[\d,]+張',f'共{total:,}張；綱目{gm:,}張',s,1);s=re.sub(r'復工位置：[^\n]+',f'復工位置：《星學綱目正傳》第{n}頁下表本批新增{len(rows)}卡；下一個第一動作：接續第{n+1}頁下表。已收字不重讀，餘字見逐書核對檔；T15-032文室候選仍待確認。',s,1);s=re.sub(r'第73頁下表本輪另收[^\n]+',f'第73–76頁已逐批補錄；第{n}頁本批另收{len(rows)}卡。尚不清楚的細字記入逐書核對檔，不標整頁完成。',s,1);p.write_text(s)
 p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
 for i,line in enumerate(lines):
  if line.startswith('|星學綱目正傳|'):
   c=line.strip('|').split('|');c[5]=re.sub(r'累計\d+張',f'累計{gm}張',c[5]);c[6]+=f'；{DATE}第{n}頁下表另核補{len(rows)}卡，細字待核，不標整頁完成';c[7]=DATE;lines[i]='|'+'|'.join(c)+'|'
 p.write_text('\n'.join(lines)+'\n')
 with(ROOT/'docs/catalog/星學綱目正傳.md').open('a')as f:
  f.write(f'\n### {DATE}：第{n}頁下表續核\n\n新增{len(rows)}卡，只照錄原圖題字與圈字；[逐項紅框與新增卡](../檢查/綱目{n}頁下表續核-{DATE}.md)。已有卡片不變，不標全頁完成。\n\n|概念名稱|書名|PDF頁碼|原因|\n|---|---|---|---|\n|{PENDING[n]}|星學綱目正傳|{n}|殘缺或字形未確認，不建卡，不借他書代填。|\n')
 print(json.dumps({k:v for k,v in result.items()if k!='明細'},ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('mode',choices=['prepare','apply']);ap.add_argument('page',type=int);a=ap.parse_args();prepare(a.page)if a.mode=='prepare'else apply(a.page)
