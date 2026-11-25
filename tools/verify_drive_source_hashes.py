"""執行：串流雲端原檔，核對帳本、PDF頁數與本機SHA256；原檔不入git。
下載設定只放暫存目錄；輸出不含下載網址或短效權杖。
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.request import urlopen
from urllib.error import HTTPError
import argparse,hashlib,json,re,xml.etree.ElementTree as ET,zipfile
import fitz

R=Path(__file__).resolve().parents[1]
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--download-manifest',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--raw-dir',type=Path,required=True);args=ap.parse_args()
    manifest=json.loads(args.download_manifest.read_text());remote={x['id']:x for x in manifest};args.raw_dir.mkdir(exist_ok=True,parents=True)
    ledger=[]
    for line in (R/'docs/來源清單.md').read_text().splitlines():
        if not line.startswith('|') or 'https://' not in line:continue
        c=line.strip('|').split('|');match=re.search(r'/(?:d|folders)/([^/?]+)',c[2]);assert match,c[0]
        ledger.append({'書名':c[0],'檔名':c[1],'ID':match[1],'帳本頁數欄':c[3],'帳本SHA256':c[4]})
    byid={x['ID']:x for x in ledger};assert len(byid)==len(ledger)==30
    local={}
    for filename in ['local-manifest.json','stage15-manifest.json']:
        for x in json.loads((Path('/workspace/sources')/filename).read_text()):
            if x.get('pdf'):local[x.get('name',x.get('title'))]=Path(x['pdf'])
    docx=list(Path('/workspace/attachments').rglob('*.docx'))
    def verify(item):
        ident=item['ID'];f=remote[ident];is_pdf=f['mime_type']=='application/pdf';target=args.raw_dir/(ident+('.pdf' if is_pdf else '.docx'));h=hashlib.sha256();size=0
        try:
            with urlopen(f['download_url'],timeout=45) as response,target.open('wb') as out:
                while True:
                    block=response.read(1024*1024)
                    if not block:break
                    size+=len(block);h.update(block);out.write(block)
        except Exception as exc:
            return {**item,'錯誤類型':type(exc).__name__,'HTTP狀態':getattr(exc,'code',None),'通過':False}
        localfile=local.get(item['檔名']) if is_pdf else next((p for p in docx if p.name==item['檔名']),None)
        assert localfile and localfile.is_file(),item['檔名']
        actual=h.hexdigest();localsha=digest(localfile);pages=None;paragraphs=None;all_paragraphs=None
        if is_pdf:
            with fitz.open(target) as pdf:pages=len(pdf)
        else:
            with zipfile.ZipFile(target) as zipped:
                root=ET.fromstring(zipped.read('word/document.xml'))
                paragraphs=len(root.findall('./{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body/{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'))
                all_paragraphs=len(root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'))
        filename_ok=f['title']==item['檔名'];hash_ok=actual==item['帳本SHA256']==localsha
        page_ok=(str(pages)==item['帳本頁數欄']) if is_pdf else True
        return {**item,'雲端檔名':f['title'],'實際串流位元組數':size,'雲端中繼資料位元組數':int(f['size']),'本機位元組數':localfile.stat().st_size,'本次雲端串流SHA256':actual,'本機SHA256':localsha,'實際PDF頁數':pages,'Word本文直接段落數':paragraphs,'Word含表格原始段落數':all_paragraphs,'檔名一致':filename_ok,'三方雜湊一致':hash_ok,'頁數一致':page_ok,'通過':filename_ok and hash_ok and page_ok and size==int(f['size'])==localfile.stat().st_size}
    rows=[]
    ids_match=set(byid)==set(remote)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(verify,item):item['ID'] for item in ledger if item['ID'] in remote}
        for future in as_completed(futures):
            row=future.result();rows.append(row);print(json.dumps({'已核':len(rows),'檔名':row['檔名'],'通過':row['通過']},ensure_ascii=False),flush=True)
    rows.sort(key=lambda x:x['書名'])
    report={'日期':'2026-11-25','方式':'從Google Drive連接器取得原檔參照，再串流原始位元組重新計算SHA256；沒有把本機雜湊當成本次遠端雜湊','雲端份數':len(remote),'帳本份數':len(ledger),'新增ID':sorted(set(remote)-set(byid)),'帳本缺少ID':sorted(set(byid)-set(remote)),'ID集合一致':ids_match,'通過數':sum(x['通過'] for x in rows),'未通過數':sum(not x['通過'] for x in rows),'PDF份數':sum(x.get('實際PDF頁數') is not None for x in rows),'PDF總頁數':sum(x.get('實際PDF頁數') or 0 for x in rows),'Word份數':sum(x.get('Word本文直接段落數') is not None for x in rows),'明細':rows,'原檔位置':'倉庫外暫存目錄；不提交PDF或Word原檔，也不提交短效下載網址'}
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');assert ids_match and report['通過數']==30 and report['未通過數']==0
    print(json.dumps({k:v for k,v in report.items() if k!='明細'},ensure_ascii=False))

if __name__=='__main__':main()
