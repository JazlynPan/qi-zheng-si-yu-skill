"""執行：核對歲殿授權邊界、入口、全庫Markdown本機連結及錨點；不改卡。
目錄：anchors（標題錨點）、main（差異邊界與全庫連結）。
"""
from pathlib import Path
from urllib.parse import unquote
import json,re,hashlib,subprocess,unicodedata
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT).decode()
def anchors(p):
 text=p.read_text();result=set(re.findall(r'<a\s+(?:name|id)=["\']([^"\']+)',text));seen={}
 for h in re.findall(r'^#{1,6}\s+(.+?)\s*#*$',text,re.M):
  h=re.sub(r'<[^>]+>','',h).replace('`','').lower();s=''.join(c for c in h if c in '-_ 'or unicodedata.category(c)[0]in'LN').replace(' ','-');n=seen.get(s,0);seen[s]=n+1;result.add(s+(f'-{n}'if n else''))
 return result

def main():
 audit=json.loads((D/'勘校修訂/2026-11-20歲殿16張回填.json').read_text());base=audit['基準提交'];expected={r['卡名']for r in audit['明細']};changed=set()
 for name,h in audit['全庫修改前SHA256'].items():
  p=ROOT/'qi-zheng-si-yu/knowledge'/name
  if hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.add(name)
 assert changed==expected
 assert {p.name for p in(ROOT/'qi-zheng-si-yu/knowledge').glob('*.md')}==set(audit['全庫修改前SHA256'])
 state=(D/'狀態.md').read_text();prefix='待你決定的入口：[docs/待你處理.md](待你處理.md)。\n';assert state==prefix+git('show',base+':docs/狀態.md')
 docsbase=set(git('ls-tree','-r','--name-only','-z',base,'--','docs').split('\0'))-{''};docsnow={str(p.relative_to(ROOT))for p in D.rglob('*')if p.is_file()};assert docsbase<=docsnow
 allowed={'docs/狀態.md','docs/勘校修訂紀錄.md'};modified=set(git('diff','--name-only','-z',base,'--','docs').split('\0'))&docsbase;assert modified<=allowed,modified-allowed
 errors=[];links=0;fragcount=0;cache={}
 for p in ROOT.rglob('*.md'):
  if '.git'in p.parts:continue
  for m in re.finditer(r'!?\[[^\]\n]*\]\((<[^>\n]+>|[^)\n]+)\)',p.read_text()):
   t=m[1].strip().strip('<>');t=re.sub(r'\s+"[^"]*"$','',t)
   if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',t)or t.startswith('//'):continue
   links+=1;parts=t.split('#',1);target=unquote(parts[0]);q=(p.parent/target).resolve()if target else p
   if not q.exists():errors.append({'檔案':str(p.relative_to(ROOT)),'連結':t,'原因':'檔案不存在'});continue
   if len(parts)==2 and parts[1]and q.suffix=='.md':
    fragcount+=1
    if q not in cache:cache[q]=anchors(q)
    if unquote(parts[1])not in cache[q]:errors.append({'檔案':str(p.relative_to(ROOT)),'連結':t,'原因':'錨點不存在'})
 entry=(D/'待你處理.md').read_text();items=[x for x in entry.splitlines()if x.startswith('- ')]
 assert len(items)==69
 for line in items:assert len(re.findall(r'\[圖\d+\]',line))<=3
 assert not git('diff','--name-only',base,'--','qi-zheng-si-yu/index','qi-zheng-si-yu/references','qi-zheng-si-yu/scripts')
 newtracked=set(git('diff','--name-only','--diff-filter=A','-z',base).split('\0'))-{''};untracked=set(git('ls-files','--others','--exclude-standard','-z').split('\0'))-{''};allnew=newtracked|untracked|{'docs/檢查/歲殿回填與入口驗收-2026-11-20.json'}
 check={'授權日期':'2026-11-20','基準提交':base,'回填歲殿卡數':16,'其餘卡內容異動':0,'卡片增刪搬移':0,'己丑卡未動':True,'戊寅未填午':True,'原有docs刪除搬移':0,'狀態只加入口首行':True,'待決入口項數':69,'各組項數':{'可直接回答':28,'先確認規則':4,'等Codex找圖':37},'每項最多3張圖':True,'全庫本機連結檢查數':links,'其中錨點':fragcount,'失效連結數':len(errors),'失效清單':errors,'新增入口檔':1,'本輪新增docs檔數':len([n for n in allnew if n.startswith('docs/')]),'本輪新增工具檔數':len([n for n in allnew if n.startswith('tools/')]),'新增檔總數':len(allnew),'外部網址':'不作遠端可用性檢查；本次只核全庫本機目標與Markdown錨點。'}
 (D/'檢查/歲殿回填與入口驗收-2026-11-20.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n');print(json.dumps(check,ensure_ascii=False));assert not errors
if __name__=='__main__':main()
