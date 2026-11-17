#!/usr/bin/env python3
"""執行：僅辨識指定PDF頁面；輸出未校對文字及位置，不將OCR當成原文或自動製卡。"""
import argparse, concurrent.futures, csv, hashlib, io, json, os, subprocess, tempfile
from pathlib import Path
import fitz
import numpy as np
from PIL import Image, ImageFilter

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def recognize(job):
    pdf, title, page, models, output, dpi = job
    with fitz.open(pdf) as doc:
        sheet = doc[page-1]
        # 排除固定頁尾；原頁及原始文字層保持不變。
        clip = fitz.Rect(0, 0, sheet.rect.width, sheet.rect.height*.88)
        pix = sheet.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72), clip=clip)
        image_count = len(sheet.get_images())
    runs=[]
    with tempfile.TemporaryDirectory(prefix='qz-ocr-') as tmp:
        image=Path(tmp)/'page.png';pix.save(str(image))
        variants=[('chi_tra+chi_sim',11),('chi_tra_vert',5)]
        for lang, psm in variants:
            proc=subprocess.run(['tesseract',str(image),'stdout','--tessdata-dir',models,'-l',lang,'--psm',str(psm),'-c','tessedit_create_tsv=1'],capture_output=True,text=True,env={**os.environ,'OMP_THREAD_LIMIT':'1'},check=True)
            if not proc.stdout.startswith('level\t'):
                raise RuntimeError('辨識器未回傳TSV欄位，停止，不產出誤導性的空結果')
            rows=list(csv.DictReader(io.StringIO(proc.stdout),delimiter='\t',quoting=csv.QUOTE_NONE))
            words=[r for r in rows if r.get('text','').strip() and float(r.get('conf','-1'))>=0]
            lines={}
            for r in words:
                key=(r['block_num'],r['par_num'],r['line_num'])
                lines.setdefault(key,[]).append(r['text'])
            runs.append({'前處理':'原頁裁去頁尾','模型':lang,'版面參數':psm,'原始TSV':proc.stdout,'原始辨識文字':'\n'.join(' '.join(v) for v in lines.values()),'引擎平均分數':round(sum(float(r['conf']) for r in words)/len(words),2) if words else None,'字塊':[{k:r[k] for k in ('text','conf','left','top','width','height')} for r in words]})
    # 泛黃底色可能使版面分析把整幅圖視為一塊，僅對無字輸出補做局部底色校正。
    if image_count and not any(r['字塊'] for r in runs):
        with tempfile.TemporaryDirectory(prefix='qz-ocr-background-') as tmp:
            im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples).convert('L')
            gray=np.array(im,dtype='int16');background=np.array(im.filter(ImageFilter.GaussianBlur(20)),dtype='int16')
            image=Path(tmp)/'threshold.png';Image.fromarray(np.where(gray<background-12,0,255).astype('uint8')).save(image)
            for lang,psm in [('chi_tra',11),('chi_tra_vert',5)]:
                proc=subprocess.run(['tesseract',str(image),'stdout','--tessdata-dir',models,'-l',lang,'--psm',str(psm),'-c','tessedit_create_tsv=1'],capture_output=True,text=True,env={**os.environ,'OMP_THREAD_LIMIT':'1'},check=True)
                if not proc.stdout.startswith('level\t'):raise RuntimeError('辨識器沒有回傳TSV')
                words=[r for r in csv.DictReader(io.StringIO(proc.stdout),delimiter='\t',quoting=csv.QUOTE_NONE) if r.get('text','').strip() and float(r.get('conf','-1'))>=0]
                runs.append({'前處理':'灰階局部底色校正：GaussianBlur(20)，差值12；僅供辨識，不改原圖','模型':lang,'版面參數':psm,'原始TSV':proc.stdout,'原始辨識文字':' '.join(r['text'] for r in words),'引擎平均分數':round(sum(float(r['conf']) for r in words)/len(words),2) if words else None,'字塊':[{k:r[k] for k in ('text','conf','left','top','width','height')} for r in words]})
    result={'書名':title,'PDF實際頁碼':page,'來源SHA256':sha(pdf),'狀態':'OCR已執行，文字與欄位待原圖核對','注意':'引擎分數不是正確率；不得直接引用此檔作原文，不以辨識字序推定圖表關係。','解析度DPI':dpi,'原頁圖像物件數':image_count,'模型SHA256':{n:sha(Path(models)/(n+'.traineddata')) for n in ('chi_tra','chi_sim','chi_tra_vert')},'辨識結果':runs}
    target=Path(output)/title/f'{page:03d}.json';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return {'書名':title,'PDF實際頁碼':page,'輸出':str(target),'狀態':result['狀態']}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',required=True);ap.add_argument('--jobs',required=True);ap.add_argument('--models',required=True);ap.add_argument('--output',required=True);ap.add_argument('--dpi',type=int,default=300);ap.add_argument('--workers',type=int,default=3);ap.add_argument('--retry-empty',action='store_true');a=ap.parse_args()
    sources={r['id']:r for r in json.loads(Path(a.manifest).read_text())};jobs=json.loads(Path(a.jobs).read_text());tasks=[]
    for j in jobs:
        for p in j['頁碼']:
            if a.retry_empty:
                previous=json.loads((Path(a.output)/j['書名']/f'{p:03d}.json').read_text())
                if any(r['字塊'] for r in previous['辨識結果']) or not previous['原頁圖像物件數']:continue
            tasks.append((sources[j['id']]['pdf'],j['書名'],p,a.models,a.output,a.dpi))
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as pool:
        for row in pool.map(recognize,tasks):print(json.dumps(row,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
