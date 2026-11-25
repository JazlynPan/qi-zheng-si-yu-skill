"""執行：逐段列出原37頁OCR候選與同頁卡片文字的位置線索；不判字、不改卡。"""
from pathlib import Path
from collections import defaultdict,Counter
import json,re,hashlib
from stage2_preflight import CITE

R=Path(__file__).resolve().parents[1]
D=R/'docs/檢查'
def compact(s):
    return re.sub(r'[\s，。、；：「」《》〈〉（）(),.:;!?！？]','',s)

def main():
    manifest=json.loads((R/'docs/ocr/機器候選/剩餘圖頁批次清單.json').read_text())
    keys={(x['書名'],x['PDF實際頁碼']) for x in manifest}
    texts=defaultdict(list)
    for path in sorted((R/'qi-zheng-si-yu/knowledge').glob('*.md')):
        raw=path.read_text()
        cites=list(CITE.finditer(raw))
        for i,cite in enumerate(cites):
            if cite['unit']!='頁':
                continue
            nums=[int(n) for n in re.findall(r'\d+',cite['loc'])]
            for book,page in keys:
                if cite['book']==book and nums[0]<=page<=nums[-1]:
                    body=raw[cite.end():cites[i+1].start() if i+1<len(cites) else len(raw)]
                    texts[(book,page)].append((path.name,compact(body)))
    rows=[];pages=[]
    for item in manifest:
        book,page=item['書名'],item['PDF實際頁碼']
        p=R/'docs/ocr/機器候選/剩餘圖頁'/(Path(item['原圖檔名']).stem+'-PaddleOCRv5.json')
        raw=json.loads(p.read_text())
        current=[]
        for ri,result in enumerate(raw['結果']):
            result=result.get('res',result)
            for n,(candidate,poly) in enumerate(zip(result['rec_texts'],result['dt_polys']),1):
                needle=compact(candidate)
                found=[name for name,body in texts[(book,page)] if len(needle)>=2 and needle in body]
                status='同頁卡片有相同文字（僅線索）' if found else '單字／符號須原圖定位' if len(needle)<2 else '未逐字命中，須看原圖'
                row={'書名':book,'PDF實際頁碼':page,'原圖檔名':item['原圖檔名'],'結果序號':ri,'框序號':n,'OCR候選':candidate,'原框':poly,'機器對照':status,'同頁卡片檔名':found,'人工核字狀態':'本表未作人工裁決','候選來源':str(p.relative_to(R))}
                rows.append(row);current.append(row)
        pages.append({'書名':book,'頁碼':page,'候選數':len(current),'分流':dict(Counter(x['機器對照'] for x in current))})
    assert len(manifest)==37 and len(rows)==1358
    report={'日期':'2026-11-25','證據等級':'E0，文字比對，不是原圖核字驗收','限制':'僅原37頁批次的1358個框，不含其後其他方向或原圖1新增候選；同頁文字命中不證明字位、歸屬或原字正確，未命中不等於缺卡。不做異體字或簡繁轉換，不採OCR作答案。','總頁數':37,'總段數':len(rows),'分類':dict(Counter(x['機器對照'] for x in rows)),'逐頁':pages,'逐段':rows}
    stem='階段1.5原37頁1358段文字線索-2026-11-25'
    (D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    md=['# 原37頁1358段OCR文字線索','','本表為E0機械比對，不是人工驗收；不據命中數計算完成率。不改卡、不增卡、不刪卡。',report['限制'],'',str(report['分類'])+'。','','|書名|PDF頁|原候選段數|同頁文字線索|未命中待看原圖|單字／符號待定位|','|---|---|---|---|---|---|']
    for p in pages:
        c=p['分流'];md.append(f'|{p["書名"]}|{p["頁碼"]}|{p["候選數"]}|{c.get("同頁卡片有相同文字（僅線索）",0)}|{c.get("未逐字命中，須看原圖",0)}|{c.get("單字／符號須原圖定位",0)}|')
    md+=['','[1358段逐筆定位與同頁卡片清單]('+stem+'.json)。保留原OCR值供定位，人工讀值必須另據原圖記錄；不能把此表當1358段已核畢。']
    (D/(stem+'.md')).write_text('\n'.join(md)+'\n')
    print(json.dumps(report['分類'],ensure_ascii=False))

if __name__=='__main__':main()
