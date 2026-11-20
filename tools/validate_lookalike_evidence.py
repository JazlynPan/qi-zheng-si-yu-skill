"""執行：檢查登籍31組圖檔、入口與全庫本機連結；不判定原字、不改卡。"""
from pathlib import Path
from urllib.parse import unquote
import json,re,subprocess
from validate_suidian_entry_20261120 import anchors
R=Path(__file__).resolve().parents[1];D=R/'docs'
def main():
 obj=json.loads((D/'檢查/登籍31組原圖待確認.json').read_text());rows=obj['明細'];assert len(rows)==31
 assert all((R/x['原圖']).is_file() for x in rows)
 changes=subprocess.check_output(['git','diff','HEAD','--name-only','--','qi-zheng-si-yu/knowledge'],cwd=R).decode();assert not changes
 assert not subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','qi-zheng-si-yu/knowledge'],cwd=R).decode()
 errors=[];links=0;cache={}
 for p in R.rglob('*.md'):
  if '.git' in p.parts:continue
  for m in re.finditer(r'!?\[[^\]\n]*\]\((<[^>\n]+>|[^)\n]+)\)',p.read_text()):
   t=re.sub(r'\s+"[^"]*"$','',m[1].strip().strip('<>'))
   if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',t)or t.startswith('//'):continue
   links+=1;parts=t.split('#',1);q=(p.parent/unquote(parts[0])).resolve()if parts[0]else p
   if not q.exists():errors.append([str(p.relative_to(R)),t,'檔案不存在']);continue
   if len(parts)==2 and parts[1] and q.suffix=='.md':
    if q not in cache:cache[q]=anchors(q)
    if unquote(parts[1])not in cache[q]:errors.append([str(p.relative_to(R)),t,'錨點不存在'])
 entry=(D/'待你處理.md').read_text();groups={}
 for sec in re.split(r'^## ',entry,flags=re.M)[1:]:groups[sec.splitlines()[0]]=len(re.findall(r'^- ',sec,re.M))
 assert list(groups.values())==[77,3,19],groups
 report={'日期':'2026-11-20','證據等級':'E0：圖檔與文件檢查，非原字核定','原圖組數':31,'原圖檔數':31,'跨頁組數':sum(x['是否跨頁']for x in rows),'卡片總數':len(list((R/'qi-zheng-si-yu/knowledge').glob('*.md'))),'卡片修改新增刪除':0,'形近字補定位數':18,'形近字仍未定位數':19,'待決入口各組數':groups,'本機連結檢查數':links,'失效數':len(errors),'失效清單':errors,'限制':'原字尚待使用者逐圖確認；不從歲殿推填登籍。'}
 (D/'檢查/形近字18筆補定位驗收.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False));assert not errors
if __name__=='__main__':main()
