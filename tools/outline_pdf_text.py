#!/usr/bin/env python3
"""執行：從已核對頁碼的文字抽取卷題與節題候選；不把候選數當章數。"""
import argparse,re
from pathlib import Path
from opencc import OpenCC

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('text',type=Path);ap.add_argument('--title',required=True)
    ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    cc=OpenCC('s2twp');pages=a.text.read_text().split('\f')
    if not pages[-1].strip():pages.pop()
    volumes=[];heads=[]
    for pg,page in enumerate(pages,1):
        for line in page.splitlines():
            t=line.strip();indent=len(line)-len(line.lstrip())
            if re.search('大全卷之[一二三四五六七八九十]+$',t):volumes.append((pg,t))
            if indent>=8 and 2<=len(t)<=28 and not re.search(r'[，。；：、（）()？！“”《》,.;:!?\dA-Za-z]',t) and not t.startswith(('如果','浙江','后学','金陵','热心','逸士','此以','此系','此段','此论','此言','此后')):heads.append((pg,t))
    out=[f'# 《{a.title}》正文結構核對','','## 目錄','','- [卷次](#卷次)','- [節題定位清單](#節題定位清單)','- [核對限制](#核對限制)','','本 PDF 共 '+str(len(pages))+' 頁。未見獨立目錄；卷次依正文卷首題辨識。節題清單由版面縮排抽取供逐節閱讀核對，不把節題或子目數稱作全書章數。','','## 卷次','','|卷首 PDF 頁|正文卷題|','|---|---|']
    out += [f'|{p}|{t}|'for p,t in volumes]
    out += ['','## 節題定位清單','','以下保留重複題名及原文用字，逐節閱讀後再將缺題、異文與誤判列入核對紀錄。','','|PDF頁|題名候選|','|---|---|']+[f'|{p}|{t}|'for p,t in heads]
    out += ['','## 核對限制','','開篇引、序與卷首同在第 3 頁交接；一頁可能同時包含前卷末文及後卷卷首，不將共享頁拆成不存在的頁碼。純敘述、作者署名、詩句及圖中標籤可能與節題縮排相同；此清單只作定位，須按正文確認。','']
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(cc.convert('\n'.join(out)).replace('司檯','司臺'))
    print('卷題',len(volumes),'節題定位',len(heads))
if __name__=='__main__':main()
