#!/usr/bin/env python3
"""執行：批次產生待核OCR候選；每張即存檔，可續跑，完全不寫卡片。"""
import argparse
import hashlib
import json
import os
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest', type=Path)
    p.add_argument('--image-dir', required=True, type=Path)
    p.add_argument('--output-dir', required=True, type=Path)
    p.add_argument('--model-cache', required=True, type=Path)
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    for key, suffix in [('PADDLE_PDX_CACHE_HOME',''), ('PADDLE_HOME',''),
                        ('HF_HOME','huggingface'), ('MODELSCOPE_CACHE','modelscope')]:
        os.environ[key] = str((a.model_cache / suffix).resolve())
    os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
    from paddleocr import PaddleOCR
    engine = PaddleOCR(text_detection_model_name='PP-OCRv5_mobile_det',
                       text_recognition_model_name='PP-OCRv5_server_rec',
                       use_doc_orientation_classify=False, use_doc_unwarping=False,
                       use_textline_orientation=False, device='cpu',
                       cpu_threads=2, enable_mkldnn=False)
    report = []
    for item in json.loads(a.manifest.read_text()):
        src = a.image_dir / item['原圖檔名']
        out = a.output_dir / (src.stem + '-PaddleOCRv5.json')
        sha = hashlib.sha256(src.read_bytes()).hexdigest()
        try:
            if out.exists():
                result = json.loads(out.read_text())
                assert result['原圖SHA256'] == sha
            else:
                rows = []
                for value in engine.predict(str(src)):
                    value = value.json
                    rows.append(json.loads(value) if isinstance(value, str) else value)
                result = dict(item, 原圖SHA256=sha, 狀態='機器候選，未校讀，不得直接入卡',
                              結果=rows, 模型='PP-OCRv5_mobile_det + PP-OCRv5_server_rec')
                out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
            count = sum(len(x['res']['rec_texts']) for x in result['結果'])
            record = dict(item, 輸出檔名=out.name, 候選文字段數=count, 狀態='已存機器候選')
        except Exception as error:
            record = dict(item, 狀態='失敗', 原因=str(error))
        report.append(record)
        (a.output_dir/'批次進度.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps(record, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
