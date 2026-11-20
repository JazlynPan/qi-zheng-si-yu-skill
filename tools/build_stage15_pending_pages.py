"""執行：彙整三本待核來源的逐頁分界，只產報告，不改卡或宣告完成。"""
from pathlib import Path
import json,collections
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs/檢查'
def main():
 manifest=json.loads((ROOT/'docs/ocr/機器候選/剩餘圖頁批次清單.json').read_text());rows={}
 for x in manifest:
  book,page=x['書名'],x['PDF實際頁碼'];stem=Path(x['原圖檔名']).stem
  p=ROOT/'docs/ocr/機器候選/剩餘圖頁'/(stem+'-PaddleOCRv5.json');o=json.loads(p.read_text());n=sum(len(r.get('res',r).get('rec_texts',[]))for r in o['結果'])
  rows[(book,page)]={'書名':book,'頁碼':page,'原機器候選段數':n,'候選檔':str(p.relative_to(ROOT)),'已提報條數':0}
 for file,book in [('T15逐條紅框對照.json','星平總會命海'),('T17逐條紅框對照.json','河洛五星合參案例抄本')]:
  data=json.loads((D/file).read_text());counts=collections.Counter(x['原圖頁碼']for x in data['明細'])
  for page,n in counts.items():
   row=rows.setdefault((book,page),{'書名':book,'頁碼':page,'原機器候選段數':None,'候選檔':None});row['已提報條數']=n
 for page in [40,41,99,100,101]:rows.setdefault(('星學綱目正傳',page),{'書名':'星學綱目正傳','頁碼':page,'原機器候選段數':None,'候選檔':None,'已提報條數':0})
 rows.setdefault(('星平總會命海',16),{'書名':'星平總會命海','頁碼':16,'原機器候選段數':None,'候選檔':None,'已提報條數':27})
 for (book,page),r in rows.items():
  if book=='河洛五星合參案例抄本':scope='環排、紅批、卦畫及數字；可定位候選已提報，未辨範圍仍存在';action='等待已提報字值裁決；未覆蓋處須繼續按原圖分區核對，不能以172筆代表全頁。';ref='T17逐條紅框對照.md'
  elif book=='星平總會命海':scope='第16頁變曜27題與淂字部件待裁決'if page==16 else'盤內字列、數字及四方向可定位機器候選，尚未全核';action='不改原卡；逐條看圖後才錄原字，不能把86筆候選當成全頁已讀完。';ref='命海16_T14本輪逐筆複核.md'if page==16 else'T15逐條紅框對照.md'
  elif 73<=page<=96:scope='跨頁年組、科甲五題、其餘窄欄及下表；五題報告不覆蓋全頁所有字';action='保留已提報修訂；其餘尚未校清小字另按原圖定位，不以既有卡數或機器成功數結案。';ref='科甲欄全組重核.md'
  elif page==97:scope='玉堂第2–10列已存9列；首列未／木、題字細點與天嗣下注後段未校清';action='先核首列與天嗣下注的原字；不以OCR王、已等替原刻。';ref='綱目97至98頁續核紀錄.md'
  elif page==98:scope='右列36格已收；T21婁水、會已記使用者讀值，簊金仍候選；其他左旁與歸屬未清';action='不再重問已回覆兩字；其他小字按行位核對，不自補歸屬取法。';ref='綱目98_T21本輪字形複核.md'
  elif page==40:scope='正月至六月已收可辨字列，剩餘未明字及外圍格位';action='只核未收格，不重讀已核字列，不以月份規律補字。';ref=None
  elif page==41:scope='七八月可辨字已收；九至十二月淡損圈支與同名異位置';action='原內嵌圖仍不清的部分保持無法判斷，不依其他月圖補值。';ref='綱目41月份OCR與結構檢查.json'
  elif page==99:scope='大字與勾絞字列、可核圖註已收；下註接行及細字仍須確認覆蓋';action='已收同頁引文不重建卡；只檢尚未確認的列末與接行。';ref=None
  elif page==100:scope='伏尸、闌干整欄已提報；T22四格與貫索仍依使用者指令暫停';action='等待整欄確認，不繼續T22四格或貫索。';ref='綱目100伏尸闌干整欄對照.md'
  else:scope='餘四物理欄8圈題已收39項，血支與浮沉下注另2卡；年在未第4項末字未定';action='只核未收的辰／戌字形及細字接行；不改已存卡片。';ref='綱目101餘四欄續核.md'
  r.update({'未完成範圍':scope,'下一動作':action,'報告入口':ref})
 data={'日期':'2026-11-19','卡片數':len(list((ROOT/'qi-zheng-si-yu/knowledge').glob('*.md'))),'列記圖頁數':len(rows),'逐書圖頁數':dict(collections.Counter(b for b,p in rows)),'原37圖頁候選數':sum(r['原機器候選段數']or 0 for r in rows.values()),'限制':'只建立待核分界，不代表所有未核字已切分；機器候選與已提報候選不可相減當未完成字數。沒有將未逐字校完的1358段標成完成。','階段1.5完成':False,'明細':[rows[k]for k in sorted(rows)]}
 (D/'階段1.5待校與待裁決分界.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 lines=['# 階段1.5待校與待裁決分界','','## 統計口徑','',f'目前{data["卡片數"]:,}張卡，來源30份：29本PDF共3,430頁及1份Word。正文帳本27份已整理、3份進行中。','本表列記'+str(len(rows))+'個圖頁位置；不是43頁都未讀，也不是這些頁全已讀完。原37圖頁共'+str(data['原37圖頁候選數'])+'段機器候選，仍未有完整逐段人工驗收表，不把產出OCR當完成。','已提報數是T14／T15／T17篩選後的問題數，和原OCR段數不是同一單位，不能相減算進度百分比。','','## 逐頁範圍','','|書名／PDF頁|原OCR段數／已提報條數|未完成範圍|下一個動作／入口|','|---|---|---|---|']
 for r in data['明細']:
  link=f'[報告]({r["報告入口"]})'if r['報告入口']else'[逐書紀錄](../catalog/星學綱目正傳.md)'
  lines.append(f'|{r["書名"]} {r["頁碼"]}|{r["原機器候選段數"]if r["原機器候選段數"]is not None else"本表不重算"}／{r["已提報條數"]}|{r["未完成範圍"]}|{r["下一動作"]} {link}|')
 lines+=['','## 結論','','本批第101頁血支、浮沉下注新增2卡，原有19,778卡未改；機械檢查以最新階段1.5目前覆蓋與R1檢查.json為準，不在本表固定空殼數。','尚有未校清原字與未完成的逐段核對工作；此外使用者正分批裁決，不能把兩者合稱已完成。階段1.5維持進行中，不進階段2。','復工先核97頁天嗣下注未收文字及玉堂首格，再處理98頁其他左旁未定字；不可續核100頁暫停項。']
 (D/'階段1.5待校與待裁決分界.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:v for k,v in data.items()if k!='明細'},ensure_ascii=False))
if __name__=='__main__':main()
