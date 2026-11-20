"""執行：核對本輪17卡限定修訂、全庫格式與其他卡的相關讀字；只出報告。
目錄：授權邊界與四欄（main前段）；全量詞表（中段）；來源查核與結論（末段）。
"""
from review_helpers import *
from stage1_audit import sections,FIELDS
from collections import Counter
import subprocess,csv
TERMS=['玉璽','天纛','天縻','天娼','天暉','天臂','長生星','天聰','天旺','天濕星','天溫星','天漫星','天琮','天宗','閑宮星','困苦星','天垣','天空','玉垣','天姬','天坎','天災','天亢','天元','天酷','天醜','主清高','主清貴','主清廟','華蓋','天慘','天條','天祿','相火同','拍火同','柏火同','絕根星','絕祿星','天桑','天柔']
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT).decode()
def main():
 records=[json.loads((ROOT/'docs/勘校修訂'/f'2026-11-20-T14伏尸使用者授權-{s}.json').read_text())for s in ['T14','伏尸']];base=records[0]['基準提交'];expected={r['卡名']:r for rec in records for r in rec['明細']};actual=set(git('-c','core.quotePath=false','diff','--name-only',base,'--','qi-zheng-si-yu/knowledge').splitlines());assert actual=={'qi-zheng-si-yu/knowledge/'+n for n in expected}
 original=set(git('ls-tree','-r','--name-only',base,'--','qi-zheng-si-yu/knowledge').splitlines()) # 此處以數量核對，中文路徑另由diff精確核對。
 files=sorted(K.glob('*.md'));assert len(files)==len(original)==19796
 for n,r in expected.items():assert (K/n).read_bytes()==r['新全文'].encode()
 assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==h for n,h in records[0]['禁止修改卡'].items());assert '\n\n主阻滯\n\n'in (K/'子宮火圖列（星平總會命海）.md').read_text()
 problems=[];hits=[];term_files={t:set()for t in TERMS};term_counts=Counter();regex=re.compile('|'.join(re.escape(t)for t in sorted(TERMS,key=len,reverse=True)))
 for p in files:
  text=p.read_text();fields=sections(text);bad=[]
  if text.splitlines()[0]!='#七政四餘':bad.append('首行標籤')
  for f in FIELDS:
   if not fields.get(f):bad.append('四欄缺載或空白：'+f)
  if not re.search(r'《[^》]+》',text):bad.append('缺書名')
  if not(re.search(r'第\s*\d+[^\n]*頁',text)or re.search(r'《楊國正七政四餘彙編》第\d+(?:[—–-]\d+)?段',text)):bad.append('缺PDF頁碼／授權Word段落')
  if bad:problems.append({'卡名':p.name,'問題':bad})
  if p.name in expected:continue
  refs=[]
  for line_no,line in enumerate(text.splitlines(),1):
   refs+=re.findall(r'《[^》]+》[^\n]{0,55}',line)
   for m in regex.finditer(line):
    term=m[0];term_counts[term]+=1;term_files[term].add(p.name);hits.append({'卡名':p.name,'行號':line_no,'命中字':term,'前後文':line[max(0,m.start()-20):m.end()+20],'最近出處':refs[-1]if refs else'本行之前無出處，請讀完整卡片','處理':'僅列報，未改此卡；同詞不代表錯字'})
 tsv=D/'T14相關讀字其他卡片全量清單-2026-11-20.tsv'
 with tsv.open('w')as f:
  wr=csv.DictWriter(f,fieldnames=['卡名','行號','命中字','前後文','最近出處','處理'],delimiter='\t');wr.writeheader();wr.writerows(hits)
 fs=(K/'伏尸已核並列字列（星學綱目第100頁續表）.md').read_text();values=re.findall(r'^[子丑寅卯辰巳午未申酉戌亥][虛女尾角軫星柳井畢婁壁][一二三四五十]+$',fs,re.M);assert set(values)==set(records[1]['使用者十二值'])and len(values)==12
 fire=[p for p in files if '火' in p.name and '角' in p.name and '天娼'in p.read_text()];assert len(fire)>=3;assert all(p.name not in expected for p in fire)
 result={'日期':'2026-11-20','基準提交':base,'全庫卡數':len(files),'修訂卡數':17,'T14卡數':16,'T14替換欄值':19,'伏尸卡數':1,'伏尸改值':4,'其餘卡異動':0,'卡片增刪':0,'禁止修改9題保持原值':True,'T14-15只保護旁註而同卡曜名已授權修訂':True,'伏尸12支無重複且與授權一致':True,'闌干與ETHICS未動':not bool(git('diff','--name-only',base,'--','qi-zheng-si-yu/ETHICS.md')),'格式問題數':len(problems),'格式問題':problems,'其他卡命中數':len({r['卡名']for r in hits}),'其他卡逐筆出現次數':len(hits),'各詞':{t:{'卡數':len(term_files[t]),'出現次數':term_counts[t]}for t in TERMS},'火躔角宿天娼保留卡':[p.name for p in fire],'限制':'E0限定替換與格式檢查；使用者裁字不是由腳本重裁。其他卡同詞一律不判錯、不替換。'};save('T14與伏尸修訂後全庫檢查-2026-11-20.json',result)
 md=['# T14與伏尸修訂後全庫檢查','','## 目錄','','- [修訂邊界](#修訂邊界)','- [其他卡片逐筆清單](#其他卡片逐筆清單)','- [天桑與天娼文獻查核](#天桑與天娼文獻查核)','- [需要使用者決定](#需要使用者決定)','','## 修訂邊界','',f'全庫{len(files):,}張；T14修16卡19值，伏尸修1卡4值，共17卡；其餘卡異動0、增刪0。首行、四欄、書名與PDF頁碼／授權Word段落檢查：{len(problems)}問題。','亥宮孛旁註現有享福，原字保留；卯宮月喜宮依使用者明確授權改入廟。T14-15旁註主阻滯保持原樣，僅同卡T14-14曜名天災改天坎。其餘8張禁改卡全文雜湊一致。','伏尸實際只有一檔、兩段引文，沒有第二個相反版本的獨立卡；保留兩段，只改尾十四→尾四十、角二→角一、星三→星二、井二→井一，合計十二支各一次，與授權十二值完全相同。闌干與貫索未改。','[T14逐格舊新與原圖](T14授權修訂前清單-2026-11-20.md)、[伏尸十二格舊新與原圖](伏尸授權修訂前清單-2026-11-20.md)。完整舊新全文保存於docs/勘校修訂/，修訂紀錄已追加。','天濕星、主清廟、拍火同均與前輪候選不同，已在T14清單單獨標示並附放大原圖，依本輪使用者授權套用。','','## 其他卡片逐筆清單','',f'排除本輪17張已改卡，其餘卡中命中{result["其他卡命中數"]}張、{len(hits)}處；[全量逐筆TSV](T14相關讀字其他卡片全量清單-2026-11-20.tsv)。逐筆列卡名、行號、前後文與最近出處，保留重複欄位中的每次出現，不自行去重或批量替換。','同字可能是不同宮位、星宿或不同書的正常用字，表中每一筆都僅供核對，不能當作錯字清單。','','|詞|其他卡數|出現次數|','|---|---|---|']
 for t in TERMS:md.append(f'|{t}|{len(term_files[t])}|{term_counts[t]}|')
 url580='https://zh.wikisource.org/zh-hant/欽定古今圖書集成/博物彙編/藝術典/第580卷';url578='https://zh.wikisource.org/zh-hant/欽定古今圖書集成/博物彙編/藝術典/第578卷'
 md+=['','## 天桑與天娼文獻查核','','查核日期2026-11-20。以下是網路文字轉錄旁證，不是《命海》第16頁底本字形證據，也不以其他術數網頁作判定。',f'- [《古今圖書集成》藝術典第580卷]({url580})〈太陽入宮〉〈日寅〉（網頁第228行）記「日居人馬號天桑」。提供天桑線索；寅宮日卡現天柔仍未改，T14-18保持未確認。',f'- [《古今圖書集成》藝術典第578卷]({url578})〈熒惑躔度〉〈火角〉（網頁第574行）記「火躔角宿號天娼」。本庫《星平總會命海》PDF第189頁文字層也找到同句；這個天娼與子宮月格不同，保留。','本庫保留的火躔角宿卡：']
 for p in fire:md.append(f'- [{p.name}](../../qi-zheng-si-yu/knowledge/{p.name})：未修改。')
 md+=['','## 需要使用者決定','','1. T14-18天柔／天桑仍須以《命海》第16頁原圖裁決；外文獻天桑不直接回填。','2. T14-03、13、15、18、19、20、21、24、27保持本輪禁改範圍；三處不淂地為使用者指出的候選，因明列不得動，現卡不淨地仍未改。','3. 闌干整欄仍待原圖確認；本輪伏尸授權不視為解除闌干、T22或貫索的暫停條件。','4. 其他卡片全量詞表只供逐筆確認，尚未授權修訂。']
 (D/'T14與伏尸修訂後全庫檢查-2026-11-20.md').write_text('\n'.join(md)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['各詞','格式問題','火躔角宿天娼保留卡']},ensure_ascii=False))
if __name__=='__main__':main()
