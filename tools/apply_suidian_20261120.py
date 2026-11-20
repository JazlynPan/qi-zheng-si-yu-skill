"""執行：本次16張歲殿授權的預覽、限定回填與60組一致性報告。
目錄：prepare（舊全文與預覽）、compare（含缺卡全表）、apply（限定差異與保存）。
"""
from pathlib import Path
import json,re,hashlib,subprocess,difflib,argparse
ROOT=Path(__file__).resolve().parents[1];K=ROOT/'qi-zheng-si-yu/knowledge';D=ROOT/'docs';OUT=D/'勘校修訂/2026-11-20歲殿16張回填.json'
VALUES=dict(zip('丙午 丙寅 丙戌 丙申 丙辰 丁亥 丁卯 丁巳 丁未 丁酉 戊寅 戊戌 戊申 己卯 己未 己酉'.split(),'申 辰 子 戌 午 寅 午 申 戌 子 原文未提及 寅 子 申 子 寅'.split()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def prepare():
 assert not OUT.exists(),'不得覆寫已保存的修訂全文'
 prior=json.loads((D/'待裁決/T07修訂預覽與舊全文.json').read_text())['明細'];maps={r['卡片']:r for r in prior};frames={r['卡名']:r['原圖']for r in json.loads((D/'檢查/科甲欄全組重核.json').read_text())['明細']};rows=[]
 snapshot={p.name:sha(p)for p in K.glob('*.md')}
 for year,value in VALUES.items():
  name=f'歲殿圖列·{year}（星學綱目圖說下）.md';old=(K/name).read_text();r=maps[name];assert old==r['舊全文'],'T07舊全文已變，需核對：'+name
  page=r['擬列來源頁碼'];orig=re.search(r'第([^頁]+)頁',old)[1]
  if year=='戊寅':
   # 第3條優先：與已修登籍相同處理；不保留不存在的配值及共值註。
   new=(K/'登籍圖列·戊寅（星學綱目圖說下）.md').read_text();assert '第77–78頁'in new and '原文未提及'in new;why='第3條優先：p78右緣值字被切，沒有可用原字；不填午，按已修登籍撤除錯配並標缺載。'
  else:
   needle='\n歲殿\n\n'+r['現值']+'\n';assert old.count(needle)==1
   new=old.replace(needle,'\n歲殿\n\n'+value+'\n');new=new.replace('第'+orig+'頁','第'+page+'頁',1);why='只改使用者指定值與T07已定位的必要來源頁碼；其他位元組保留。'
   back=new.replace('第'+page+'頁','第'+orig+'頁',1).replace('\n歲殿\n\n'+value+'\n',needle,1);assert back==old
  frame=frames[name];assert (ROOT/frame).is_file()
  rows.append({'卡名':name,'年份':year,'舊值':r['現值'],'新值':value,'原標頁碼':orig,'修訂後頁碼':page,'年欄頁碼':r['年欄頁碼'],'值欄頁碼':r['科甲共值頁碼'],'紅框圖路徑':frame,'理由':why,'舊全文':old,'新全文':new,'舊SHA256':snapshot[name],'新SHA256':hashlib.sha256(new.encode()).hexdigest()})
 base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();dump(OUT,{'標記':'【勘校修正】','授權日期':'2026-11-20','基準提交':base,'狀態':'提交前逐張預覽，未套用','授權範圍':'歲殿16張；第3條戊寅優先，不改午；己丑兩卡及其他項目不動；不補卡不刪檔。','回填數':16,'明細':rows,'全庫修改前SHA256':snapshot})
 lines=['# 歲殿16張提交前逐張清單（2026-11-20）','','戊寅第3條優先，不改午，按已修登籍撤除錯配內容並標原文未提及；其餘15張只改指定值及必要來源頁碼，其他位元組保留。己丑兩卡不動。','','|卡名|舊值|新值|原標頁／年欄＋值欄／新列頁|紅框圖路徑|','|---|---|---|---|---|']
 for r in rows:lines.append(f'|{r["卡名"]}|{r["舊值"]}|{r["新值"]}|{r["原標頁碼"]}／{r["年欄頁碼"]}＋{r["值欄頁碼"]}／{r["修訂後頁碼"]}|[原圖](../{r["紅框圖路徑"].removeprefix("docs/")})|')
 (D/'檢查/歲殿16張提交前清單-2026-11-20.md').write_text('\n'.join(lines)+'\n');print('16張提交前清單與舊／新全文已保存，卡片未改')
def get(year,topic):
 p=K/f'{topic}圖列·{year}（星學綱目圖說下）.md'
 if not p.exists():return '缺卡',None
 t=p.read_text();m=re.search(r'\n'+topic+r'\n\n([^\n]+)',t)
 return (m[1]if m else'缺載／原文未提及'),p.name

def compare():
 rows=[]
 for i in range(60):
  y='甲乙丙丁戊己庚辛壬癸'[i%10]+'子丑寅卯辰巳午未申酉戌亥'[i%12];a,af=get(y,'歲殿');b,bf=get(y,'登籍')
  status='缺卡'if None in [af,bf]else'雙方缺載，無字值可比'if a==b=='缺載／原文未提及'else'一方缺載'if '缺載' in a+b else'值不同'if a!=b else'值相同'
  if y=='己丑':status='未確認（按本次指示不動）'
  rows.append({'年份':y,'歲殿值':a,'登籍值':b,'歲殿卡':af,'登籍卡':bf,'結果':status})
 pending=[r for r in rows if r['結果']!='值相同'];dump(D/'檢查/歲殿登籍60組一致性-2026-11-20.json',{'檢查組數':60,'相同且有實字組數':60-len(pending),'需保留或處理組數':len(pending),'口徑':'按六十年完整列，歲駕不當作歲殿；缺卡雙方皆缺也列。缺載相同不冒充有值相同。只檢查，不自補或改登籍。','明細':rows})
 lines=['# 歲殿／登籍60組回填後一致性','','## 口徑','','依六十年完整對照；歲駕不代歲殿。缺卡（含兩者皆缺）、一方缺載、值不同及己丑未確認全部列出，不自行補卡或改另一側。雙方缺載不視為有字值相同。',f'共60組，{60-len(pending)}組有實字且相同，{len(pending)}組仍需保留或處理。戊寅雙方缺載；己丑依本次指示維持未確認，兩檔未動。','','## 所有不一致或不能判為一致的組','','|年份|歲殿|登籍|狀態|','|---|---|---|---|']
 for r in pending:lines.append(f'|{r["年份"]}|{r["歲殿值"]}|{r["登籍值"]}|{r["結果"]}|')
 (D/'檢查/歲殿登籍60組一致性-2026-11-20.md').write_text('\n'.join(lines)+'\n');return len(pending)
def apply():
 data=json.loads(OUT.read_text());assert data['狀態'].startswith('提交前')
 for name,h in data['全庫修改前SHA256'].items():assert sha(K/name)==h,'預覽後卡片改變：'+name
 for r in data['明細']:(K/r['卡名']).write_text(r['新全文'])
 expected={r['卡名']for r in data['明細']};changed={n for n,h in data['全庫修改前SHA256'].items()if sha(K/n)!=h};assert changed==expected
 assert {p.name for p in K.glob('*.md')}==set(data['全庫修改前SHA256'])
 data['狀態']='已套用，提交與推送狀態以git紀錄為準';dump(OUT,data)
 OUT.with_suffix('.patch').write_text(''.join(''.join(difflib.unified_diff(r['舊全文'].splitlines(True),r['新全文'].splitlines(True),fromfile='a/qi-zheng-si-yu/knowledge/'+r['卡名'],tofile='b/qi-zheng-si-yu/knowledge/'+r['卡名']))for r in data['明細']))
 n=compare();dump(D/'檢查/歲殿16張限定修改驗證.json',{'授權日期':'2026-11-20','修改卡數':16,'其中指定值修正':15,'戊寅缺載撤錯':1,'其他卡異動':0,'卡片新增刪除搬移':0,'其餘15張非指定內容位元組異動':0,'己丑兩卡未動':True,'完整舊／新全文保存':True,'全庫卡數':len(data['全庫修改前SHA256']),'60組需保留或處理數':n})
 with (D/'勘校修訂紀錄.md').open('a')as f:f.write('\n## 2026-11-20　【勘校修正】歲殿16張授權回填\n\n授權日期2026-11-20。15張依指定字值回填並核對必要跨頁來源；其餘位元組不變。戊寅依第3條優先：p78右緣歲殿下方無值，與已修登籍同處理，撤除錯配值及共值註，標原文未提及，沒有填午。己丑兩卡及所有其他卡片均未動；不補卡、不刪檔。\n\n[16張完整舊／新全文](勘校修訂/2026-11-20歲殿16張回填.json)、[完整差異](勘校修訂/2026-11-20歲殿16張回填.patch)、[提交前逐張清單](檢查/歲殿16張提交前清單-2026-11-20.md)、[60組一致性與缺卡](檢查/歲殿登籍60組一致性-2026-11-20.md)。不一致項只列報，不自動改登籍。\n')
 print(f'16張已套用，其餘卡片未動；60組需保留或處理{n}組')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','apply']);args=ap.parse_args();prepare()if args.mode=='prepare'else apply()
