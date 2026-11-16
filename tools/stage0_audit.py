#!/usr/bin/env python3
"""執行階段 0 基準與目錄稽核；不改動卡片、不進行提煉或去重。"""
from pathlib import Path
import argparse,datetime,hashlib,json,re,subprocess
BASE='e8dd54784770396f8521a9bdf373787a822e0c29'
OLD='七政四余-skill/knowledge/'
NEW='qi-zheng-si-yu/knowledge/'
ROOT=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def sha(b):return hashlib.sha256(b).hexdigest()
def audit(expected):
 entries=git('ls-tree','-r','--name-only','-z',BASE).decode().split('\0')
 old=[x for x in entries if x.startswith(OLD)and x.endswith('.md')]
 now={p.name:p for p in(ROOT/NEW).glob('*.md')};errors=[];unchanged=0;only_tag=0
 for path in old:
  name=Path(path).name;p=now.get(name)
  if p is None:errors.append('缺少卡片：'+name);continue
  b=git('show',BASE+':'+path);c=p.read_bytes();before,sep,body=b.partition(b'\n');after,sep2,body2=c.partition(b'\n')
  want='#七政四余'if expected=='old'else'#七政四餘'
  if after.decode()!=want:errors.append('標籤不符：'+name)
  if sep!=sep2 or body!=body2:errors.append('第一行以外異動：'+name)
  if b==c:unchanged+=1
  elif sep==sep2 and body==body2:only_tag+=1
 for name in now:
  if OLD+name not in old:errors.append('新增卡片：'+name)
 local_links=0;badlinks=[]
 for p in [ROOT/'README.md',*list((ROOT/'docs').rglob('*.md'))]:
  for u in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if '://'in u or u.startswith('#'):continue
   path=u.split('#')[0].strip('<>');local_links+=1
   if path and not(p.parent/path).exists():badlinks.append(str(p.relative_to(ROOT))+' → '+u)
 result={'基準提交':BASE,'基準卡片數':len(old),'目前卡片數':len(now),'逐字相同':unchanged,'僅首行不同':only_tag,'卡片異常數':len(errors),'連結檢查數':local_links,'失效連結數':len(badlinks),'卡片異常':errors,'失效連結':badlinks,'PDF追蹤數':sum(x.lower().endswith('.pdf')for x in git('ls-files','-z').decode().split('\0'))}
 return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--expected-tag',choices=['old','new'],default='new');ap.add_argument('--report',default='docs/階段0標籤驗證.md');args=ap.parse_args();r=audit(args.expected_tag)
 out=['# 階段 0 首行標籤與基準驗證','','執行方式：`python tools/stage0_audit.py --expected-tag '+args.expected_tag+'`。以下為本機工作樹檢查，不代表遠端已發佈；遠端首行更新遭自動審核拒絕。此檢查不代表原文內容、去重或檢索已通過。','','|檢查|結果|','|---|---|']
 for k,v in r.items():
  if not isinstance(v,list):out.append(f'|{k}|{v}|')
 for k in ['卡片異常','失效連結']:out+=['','## '+k,'']+(r[k]or['無。'])
 (ROOT/args.report).write_text('\n'.join(out)+'\n');print(json.dumps({k:v for k,v in r.items()if not isinstance(v,list)},ensure_ascii=False));raise SystemExit(bool(r['卡片異常數']or r['失效連結數']or r['PDF追蹤數']))
if __name__=='__main__':main()
