#!/usr/bin/env python3
"""重算已逐頁查看原PDF所記的題目數；不自動判讀題目、不更動卡片。"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COUNTS=[5,7,8,7,8,8,8,8,8,8,8,8,8,7,8,4]
def main():
    names=json.loads((ROOT/'docs/catalog/星學綱目正傳-靈臺星格正文題名.json').read_text())['已核對首句']
    rows=[];offset=0
    for page,count in zip(range(297,313),COUNTS):
        items=names[offset:offset+count]
        assert len(items)==count
        rows.append({'PDF實際頁碼':page,'原頁另起題首數':count,'題序起':offset+1,'題序迄':offset+count,'首題':items[0],'末題':items[-1]})
        offset+=count
    assert offset==len(names)==118
    report={'書名':'星學綱目正傳','來源SHA256':'647dd4a5f503ef69db26a7bc14902a766a94dbec67e1ff09a44a86988139cca6','核對日期':'2026-11-17','核對方式':'人工逐頁查看原PDF第297–312頁，按另起格歌題首計數，跨頁續文不重計；不按粗體辨識，因部分題首不是粗體。程式僅重算人工計數及對應既有題名序列，不聲稱能自動從圖像辨題。','原PDF篇名':'靈臺一百二十格','原頁另起題首總數':offset,'既有題名清單數':len(names),'差額':120-offset,'明細':rows,'結論':'原PDF本篇可辨識的另起題首為118，與原題120相差2；逐頁檢查未發現另外兩個獨立題首。不得將差額補成新題，也不能據此判定更早底本是否缺文。','限制':'本次只核對題目分界及數量，不替代全文逐字校勘，不改既有卡片。'}
    target=ROOT/'docs/檢查/綱目靈臺原PDF逐頁題數核對.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'核對頁數':len(rows),'題首數':offset,'原題差額':120-offset},ensure_ascii=False))
if __name__=='__main__':main()
