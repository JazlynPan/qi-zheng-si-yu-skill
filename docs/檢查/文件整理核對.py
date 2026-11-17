#!/usr/bin/env python3
"""執行：唯讀卡片與Git歷史，僅產生本次文件核對報告，不修改卡片。
目錄：基準與帳本；R1新增卡；頁碼與待核紀錄；JSON及回報草稿。
"""
from pathlib import Path
import sys,json,re,subprocess,hashlib,unicodedata
from collections import Counter
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from stage2_preflight import parse,substantive

def git(*args):return subprocess.check_output(['git','-c','core.quotepath=false',*args],cwd=ROOT,text=True)
def compact(nums):
 nums=sorted(set(nums));out=[]
 for n in nums:
  if out and n==out[-1][1]+1:out[-1][1]=n
  else:out.append([n,n])
 return '、'.join(str(a)if a==b else f'{a}–{b}'for a,b in out)or'無'
config=json.loads((ROOT/'docs/檢查/文件整理卡片基準.json').read_text());base={'head':config['基準提交']};cards={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in (ROOT/'qi-zheng-si-yu/knowledge').glob('*.md')}
current_digest=hashlib.sha256(json.dumps(cards,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert len(cards)==config['卡片數']and current_digest in [config['開工工作區卡片集合SHA256'],config['基準提交卡片集合SHA256']],'卡片已不同於本次開工或已提交基準；不要以本報告宣稱無異動'
rows=[]
for line in (ROOT/'docs/來源清單.md').read_text().splitlines():
 if line.startswith('|')and'https://'in line:
  c=line.strip('|').split('|');status=c[5]
  if re.search(r'首輪.*(?:完成|通過)',status)or'完成首輪提煉'in status:kind='完成'
  elif any(k in status for k in ['已整理','已逐節整理']):kind='進行中'
  elif any(k in status for k in ['未處理','待提煉']):kind='未處理'
  else:raise ValueError('未分類帳本狀態：'+c[0])
  span=c[6];limit=int(c[3])if c[3].isdigit()else None
  if limit is None:
   m=re.search(r'第1[–—-](\d+)段',span);assert m;word_paragraphs=int(m[1]);missing=[]
  else:
   covered=set()
   for m in re.finditer(r'(\d+)\s*[–—-]\s*(\d+)',span):covered.update(range(int(m[1]),int(m[2])+1))
   if c[0]=='河洛五星合參案例抄本':
    assert '1、11敘事跳過'in span and'14正文空白'in span;covered.update([1,11,14,15])
   if c[0]=='星學綱目正傳':
    assert'103、156空白'in span;covered.update([103,156])
   missing=sorted(set(range(1,limit+1))-covered)
  rows.append({'書名':c[0],'狀態分類':kind,'帳本原狀態':status,'頁數':limit,'已處理範圍原文':span,'帳本數字範圍未明列':compact(missing),'未明列頁數':len(missing)})
counts=dict(Counter(r['狀態分類']for r in rows));counts.setdefault('未處理',0)
r1=git('log','--reverse','--format=%H','--','docs/規則補充.md').splitlines()[0]
assert'R1'in git('show',r1+':docs/規則補充.md')
added=set(p for p in git('diff','--name-only','--diff-filter=A','-z',r1,'HEAD','--','qi-zheng-si-yu/knowledge').split('\0')if p)
added_history=set(p for p in git('log',r1+'..HEAD','--diff-filter=A','--format=','--name-only','--','qi-zheng-si-yu/knowledge').splitlines()if p)
removed=set(p for p in git('log',r1+'..HEAD','--diff-filter=D','--format=','--name-only','--','qi-zheng-si-yu/knowledge').splitlines()if p)
assert added_history==added and not removed
empty=[]
for path in sorted(added):
 fields,sources,_=parse((ROOT/path).read_text());assert len(fields)==4
 rest=''.join(substantive(v)for v in fields.values())
 for marker in ['原文以圖表呈現','原文以图表呈现','原文未提及','無','无']:rest=rest.replace(marker,'')
 rest=''.join(c for c in rest if not c.isspace()and not unicodedata.category(c).startswith('P'))
 if not rest:empty.append({'檔名':Path(path).name,'所屬書':sorted({x[0]for x in sources}),'路徑':path})
suspects=[ROOT/'docs/歷史/階段1.5檢查/命海卷一疑字候選待核對.json',ROOT/'docs/歷史/階段1.5檢查/命海卷二躔宿疑字待核對.json',*sorted((ROOT/'docs/檢查').glob('命海*待核對.json'))]
records=[];page_counter=Counter();source_counts=[]
for path in suspects:
 items=json.loads(path.read_text());source_counts.append({'檔案':str(path.relative_to(ROOT)),'筆數':len(items)})
 for item in items:
  loc=item.get('頁碼',item.get('出處',''));s=str(loc)
  if '第'in s:s=s.split('第',1)[1].split('頁',1)[0]
  ns=[int(x)for x in re.findall(r'\d+',s)];assert ns
  pages=list(range(ns[0],ns[-1]+1));page_counter.update(pages)
  records.append({'頁碼':compact(pages),'原記錄':item})
assert len(records)==89
gangmu_pages=set();gangmu_count=0
for gp in sorted((ROOT/'docs/檢查').glob('綱目*待核對.json')):
 for item in json.loads(gp.read_text()):
  loc=str(item.get('頁碼',item.get('出處','')))
  if '第'in loc:loc=loc.split('第',1)[1].split('頁',1)[0].split('页',1)[0]
  ns=[int(x)for x in re.findall(r'\d+',loc)];assert ns
  gangmu_pages.update(range(ns[0],ns[-1]+1));gangmu_count+=1
pending=[
 {'書名':'河洛五星合參案例抄本','頁碼':'2–3、12–13、15','數量':'5頁','待核內容':'環排、紅批、未確認字與卦畫；已補邊欄文字，不等於全圖完成。'},
 {'書名':'星平總會命海','頁碼':'16','數量':'1頁：14組文字註、19組曜名','待核內容':'逐格清單已有，132格均有局部文字卡，但仍未全圖轉錄。'},
 {'書名':'星平總會命海','頁碼':'331–336','數量':'6頁盤圖','待核內容':'可讀命例文字已處理，盤圖仍待核對。'},
 {'書名':'星平總會命海','頁碼':compact(page_counter),'數量':f'89筆，涉及{len(page_counter)}個不同頁碼','待核內容':'原字、缺字及主詞不明；須對原頁核字，不用他書補；原頁也缺字時仍不能補造。'},
 {'書名':'星學綱目正傳','頁碼':'40–41、73–101','數量':'31頁圖表','待核內容':'已有28張圖中文字卡，外圍格位、細字及未錄欄尚待核；103、156空白不列待核圖。'},
 {'書名':'星學綱目正傳','頁碼':'297–312','數量':'1篇：篇名120、識別118，差2','待核內容':'候選引文覆蓋抽取文字9,314字，仍須原頁確認題數與抽取是否漏字，不能補造2題。'},
 {'書名':'星學綱目正傳','頁碼':compact(gangmu_pages),'數量':f'{gangmu_count}筆待核記錄，涉及{len(gangmu_pages)}頁','待核內容':'依7份既有待核JSON彙整；須對原頁核字，不等同14個獨立概念。'},
 {'書名':'星學綱目正傳','頁碼':'423–424','數量':'1段，跨2頁','待核內容':'亡劫問答續文殘缺，待原頁核字。'}]
result={'檢查基準提交':base['head'],'本次卡片變更數':0,'核對卡片集合SHA256':current_digest,'卡片數':len(cards),'R1生效提交':r1,'R1後歷史新增數':len(added_history),'R1後目前新增檔數':len(added),'R1後新增又刪除數':len(removed),'R1後新增空殼數':len(empty),'空殼前10張':empty[:10],'全部新增空殼':empty,'來源份數':len(rows),'PDF本數':sum(r['頁數']is not None for r in rows),'PDF總頁數':sum(r['頁數']or 0 for r in rows),'Word份數':sum(r['頁數']is None for r in rows),'Word原始段落數':word_paragraphs,'帳本狀態統計':counts,'逐書狀態與頁碼':rows,'命海疑字來源':source_counts,'命海疑字筆數':len(records),'命海疑字頁碼':compact(page_counter),'命海疑字涉及頁數':len(page_counter),'只能對原頁核對的已登記項目':pending,'階段1.5是否宣告完成':False,'限制':'完成統計沿用帳本正文整理狀態，非全部圖像或最終品質檢查完成；頁碼列記覆蓋與內容核對完成分開計，不以新增0份推論提煉完成。'}
(ROOT/'docs/檢查/文件整理與階段1.5核對.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
complete=[r['書名']for r in rows if r['狀態分類']=='完成'];ongoing=[r['書名']for r in rows if r['狀態分類']=='進行中'];gaps=[r for r in rows if r['未明列頁數']]
lines=['# 文件整理與階段1.5核對報告','','## 目錄','','- 文件修正與統計口徑','- R1唯讀檢查','- 逐書頁碼覆蓋','- 仍須對原頁核對的項目','- 階段1.5結束回報草稿','- 範圍與暫存內容','','## 文件修正與統計口徑','','決定紀錄的取代註記已移到舊OCR待確認紀錄下一行，其餘行維持原字與順序。README及工作階段不再沿用「8/11」「其餘3份待處理」，改說河洛、命海、綱目仍核對中。','','盤點：雲端30份、帳本30份、新增0份，代表沒有帳本外新檔，不代表整理已完成。',f'正文整理：完成{counts["完成"]}份（26本PDF、1份Word）、進行中{counts["進行中"]}本PDF、未處理0份。完成沿用帳本已列提煉及來源檢查完成的狀態，並非圖像、疑字、去重及Skill最終檢查完成。','','完成清單：'+'、'.join(complete)+'。','','進行中清單：'+'、'.join(ongoing)+'。未處理清單：無。','','## R1唯讀檢查','',f'R1首次寫入規則補充的提交：`{r1}`。以其後新增提交追查：歷史新增{len(added_history):,}張，目前仍在庫{len(added):,}張，期間新增又刪除0張；既有卡片的追加不算新卡。',f'新增空殼{len(empty)}張；前10張清單：'+('無（查無符合條件者）。'if not empty else'見JSON報告。'),'','判讀方式：只檢查四欄，移除書名頁碼題頭、缺載標記、圖表標記、空白及標點，剩下沒有實質文字才列空殼；不是只因含有圖表標記就列空殼。本次新增卡皆有剩餘文字。','','本次沒有可歸因的新增空殼，故沒有「為何仍建立」的違規案例。原有R1繼續適用：只有圖表指標、沒有實質文字者記入該書catalog，不建立卡；既有空殼不改、不刪，留到階段2。','','## 逐書頁碼覆蓋','','下表檢查帳本已處理範圍的數字列記；列全不等於圖表與疑字已核完，序目及空白不要求製卡。Word以原始段落計，不虛構頁數。','','|書名|帳本正文整理狀態|頁／段範圍未明列部分|','|---|---|---|']
for r in rows:lines.append('|'+r['書名']+'|'+r['狀態分類']+'|'+r['帳本數字範圍未明列']+'|')
lines+=['','數字範圍未明列：綱目1–6、104–114，共17頁；該書結構核對已標為序目與卷題，不足以認定漏讀正文。本次只回報，沒有代補帳本頁碼。其餘28本PDF及Word253段的範圍均已列記。','','內容未完整核對：河洛2–3、12–13、15頁；命海16、331–336頁及疑字所在頁；綱目40–41、73–101頁圖表、靈臺題數與殘文。這些不是尚未接觸的全書空白頁段，而是局部內容尚未核完。','','命海323頁之後：第324–337頁可讀正文已處理；331–336頁盤圖仍待核對。已明寫入狀態.md。','','## 仍須對原頁核對的項目','','|書名|PDF頁碼|數量|待核內容|','|---|---|---|---|']
for r in pending:lines.append('|'+r['書名']+'|'+r['頁碼']+'|'+r['數量']+'|'+r['待核內容']+'|')
lines+=['','上表只彙整已有明確頁碼及筆數的主要待核紀錄；沒有把原書缺字改正，也沒有把所有含圖表標記的卡片一律判為空殼。命海89筆來自6份既有待核紀錄，來源與筆數見JSON。','','其他已登記但尚無完整逐圖清單：欽定第30頁點陣圖（至少1頁；其他課式圖未列全）；渾天24–69頁格局圖例（所在區間46頁，非已確認46張圖）；說證275–276頁圖像（2頁）；星平大成卷七95–118頁五運六氣圖文（區間24頁，細頁與圖數未列）。不能據此宣稱全庫的圖像待核數已統計完。','','Word第18–47段比較表是30個原始段落，可直接回原Word表格核對，不屬只能靠PDF圖像；璇璣第6、9頁編者明示省略的原表，不是本版可補回的漏讀頁。本次只登記這些限制，不改卡、不補表。','','## 階段1.5結束回報草稿','','**這是草稿；階段1.5仍進行中，未宣告完成，未進入階段2。**','',f'- 書籍／來源：{len(rows)}份，29本PDF＋1份Word。',f'- 篇幅：PDF合計{result["PDF總頁數"]:,}頁；Word為{word_paragraphs}個原始段落，不併入PDF頁數。',f'- 卡片：{len(cards):,}張；本次卡片異動0。','- 已完成正文整理清單：'+ '、'.join(complete)+'。','- 未完成清單：河洛五星合參案例抄本、星平總會命海、星學綱目正傳；具體圖頁、疑字與題數見上表。','- 尚未處理的新來源：0份；不代表已可結束本階段。','- 結束條件：目前未通過。仍有3份核對中、帳本頁碼明列缺口、其他圖像待核細頁未列全；待核項尚未由使用者確認接受，不能自行宣布完成。','','## 範圍與暫存內容','','本次只改文件；knowledge/以開工時逐檔SHA256比對，新增、修改、刪除、搬移均0。工作區原先已有前輪2張卡片的暫存變更，本次保留原樣，不加入文件提交。相關短批證據與檢查暫存亦不併入本次提交；暫存存在不等於已推送。','','檢查明細：[文件整理與階段1.5核對.json](檢查/文件整理與階段1.5核對.json)。帳本：[來源清單.md](來源清單.md)；目前位置：[狀態.md](狀態.md)。']
lines+=['','本次報告可重跑：`python docs/檢查/文件整理核對.py`。程式只讀卡片與Git歷史，僅寫本報告及JSON；基準保存於「檢查/文件整理卡片基準.json」，保留開工既有暫存與已提交版本兩組卡片集合雜湊，不保存或覆寫卡片正文。']
(ROOT/'docs/文件整理與階段1.5核對報告.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:result[k]for k in ['卡片數','R1後歷史新增數','R1後新增空殼數','來源份數','PDF總頁數','Word原始段落數','帳本狀態統計','命海疑字筆數','命海疑字頁碼','命海疑字涉及頁數']},ensure_ascii=False))
print('報告行數',len(lines),'未明列',[(r['書名'],r['帳本數字範圍未明列'])for r in gaps])
