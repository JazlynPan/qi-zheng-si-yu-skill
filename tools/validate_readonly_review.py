"""執行：核驗本輪卡片保護、報告連結、圖檔存在及統計；不改卡片。"""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs/檢查'
def main():
 baseline=json.loads((D/'全庫複核唯讀基準.json').read_text());changed=[n for n,h in baseline['雜湊'].items()if not(ROOT/n).exists()or hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h]
 expected={n for n in baseline['雜湊']if '/knowledge/'in n};actual={str(p.relative_to(ROOT))for p in(ROOT/'qi-zheng-si-yu/knowledge').glob('*.md')}
 names=subprocess.check_output(['git','diff','--name-only',baseline['基準提交']],cwd=ROOT).decode().splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT).decode().splitlines();missing=[];reviewed=0
 # 檔名有臺灣文字，git輸出可能引號跳脫，改以-z取原始路徑。
 names=subprocess.check_output(['git','diff','--name-only','-z',baseline['基準提交']],cwd=ROOT).decode().split('\0')+subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
 for n in set(names):
  p=ROOT/n
  if not n or not p.is_file()or p.suffix!='.md':continue
  reviewed+=1
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if target.startswith(('https:','http:','#')):continue
   if not(p.parent/target.split('#')[0]).exists():missing.append({'檔案':n,'連結':target})
 data=json.loads((D/'形近字批量修訂清單.json').read_text());imgmissing=[r['編號']for r in data['明細']if not r.get('原圖')or not(ROOT/r['原圖']).is_file()]
 result={'日期':'2026-11-19','卡片總數':len(actual),'保護檔案內容異動':len(changed),'卡片路徑增刪':len(actual^expected),'檢查報告數':reviewed,'失效連結數':len(missing),'失效連結':missing,'形近字候選':len(data['明細']),'缺圖筆數':len(imgmissing),'仍未精確定位':sum(r['定位']=='僅附引用頁紅框；未定位字位'for r in data['明細']),'非古籍文字截錄':sum(r['單位']=='段'for r in data['明細']),'尚未建立提醒仍存在':'尚未建立的檔案不代表已可用'in(ROOT/'AGENTS.md').read_text(),'技能空目錄僅gitkeep':{x:[p.name for p in(ROOT/'qi-zheng-si-yu'/x).iterdir()]for x in['index','scripts','references']}}
 (D/'全庫複核驗證結果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False));assert not changed and actual==expected and not missing and not imgmissing
if __name__=='__main__':main()
