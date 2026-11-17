#!/usr/bin/env python3
"""執行：只清理指定清單內、位於出處引文之前的欄位占位；可先檢查，再以--apply寫入。"""
import argparse, hashlib, json, re, subprocess
from pathlib import Path


def digest(data): return hashlib.sha256(data).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--list',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--apply',action='store_true')
    args=ap.parse_args()
    manifest=json.loads(args.list.read_text())
    rows=manifest['明細'];assert len(rows)==manifest['卡片數']==266
    paths=[Path(r['卡片路徑'])for r in rows];assert len(set(paths))==266
    base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    root=Path('qi-zheng-si-yu/knowledge')
    all_before={p:digest(p.read_bytes())for p in root.rglob('*')if p.is_file()}
    planned=[];report=[]
    for row,path in zip(rows,paths):
        assert path.parent==root and path.is_file()
        old=path.read_text();pieces=re.split(r'(\n## [^\n]+\n)',old);new=list(pieces);fields=[]
        for i in range(1,len(pieces),2):
            heading=pieces[i].strip()[3:]
            if heading not in row['欄位']:continue
            body=pieces[i+1]
            m=re.match(r'\n(原文未提及|無)\n\n(?=《[^》]+》第\d)',body)
            if not m:continue
            payload=body[m.end():]
            # There must be actual text after the first source line, not a figure/absence marker alone.
            content=payload.split('\n',1)[1].strip()
            assert content and content not in ('原文未提及','原文以圖表呈現','無')
            new[i+1]='\n'+payload
            assert new[i+1][1:].encode()==body[m.end():].encode()
            fields.append({'欄位':heading,'移除占位':m[1],'出處及引文SHA256':digest(payload.encode())})
        result=''.join(new)
        # The only removed lines are the listed leading markers and their following blank lines.
        assert result.startswith('#七政四餘\n') and old.splitlines()[0]==result.splitlines()[0]
        for i in range(1,len(pieces),2):
            if pieces[i+1]!=new[i+1]:assert pieces[i].strip()[3:]in row['欄位']
        if fields:planned.append((path,result))
        report.append({'卡片路徑':str(path),'處理欄位':fields,'修改前SHA256':digest(old.encode()),'修改後SHA256':digest(result.encode())})
    assert len(planned)in (0,266),'只允許整份已授權清單，或完成後重跑無變更'
    if args.apply:
        for path,data in planned:path.write_text(data)
    changed={p for p,h in all_before.items()if digest(p.read_bytes())!=h}
    assert changed==({p for p,_ in planned}if args.apply else set())
    assert set(all_before)=={p for p in root.rglob('*')if p.is_file()}
    result={'基準提交':base,'授權範圍卡片數':266,'模式':'已套用'if args.apply else'僅檢查','待修改卡片數':len(planned),'已修改卡片數':len(changed),'移除占位數':sum(len(r['處理欄位'])for r in report),'出處及引文異動數':0,'清單外卡片異動數':0,'新增或刪除卡片數':0,'明細':report}
    args.report.parent.mkdir(exist_ok=True,parents=True)
    args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k!='明細'},ensure_ascii=False))

if __name__=='__main__':main()
