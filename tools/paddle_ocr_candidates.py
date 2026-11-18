#!/usr/bin/env python3
"""執行：本機PP-OCRv5產生待核文字、框位與分數；不改知識卡、不做語義修字。"""
import argparse
import hashlib
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--model-cache', required=True, type=Path)
    parser.add_argument('--regions', type=Path, help='JSON陣列，每筆name、box[x0,y0,x1,y1]、scale；只裁切放大，不補字')
    args = parser.parse_args()
    args.model_cache.mkdir(parents=True, exist_ok=True)
    os.environ['PADDLE_PDX_CACHE_HOME'] = str(args.model_cache.resolve())
    os.environ['PADDLE_HOME'] = str(args.model_cache.resolve())
    os.environ.setdefault('HF_HOME', str((args.model_cache / 'huggingface').resolve()))
    os.environ.setdefault('MODELSCOPE_CACHE', str((args.model_cache / 'modelscope').resolve()))
    os.environ.setdefault('PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK', 'True')
    from paddleocr import PaddleOCR
    engine = PaddleOCR(
        text_detection_model_name='PP-OCRv5_mobile_det',
        text_recognition_model_name='PP-OCRv5_server_rec',
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        device='cpu', cpu_threads=2, enable_mkldnn=False,
    )
    regions = json.loads(args.regions.read_text()) if args.regions else None
    inputs = str(args.image)
    if regions:
        import numpy as np
        from PIL import Image
        source = Image.open(args.image).convert('RGB')
        inputs = []
        for region in regions:
            x0, y0, x1, y1 = region['box']
            assert 0 <= x0 < x1 <= source.width and 0 <= y0 < y1 <= source.height
            patch = source.crop((x0, y0, x1, y1))
            scale = region.get('scale', 1)
            assert 1 <= scale <= 4
            patch = patch.resize((patch.width * scale, patch.height * scale))
            inputs.append(np.asarray(patch)[:, :, ::-1].copy())
    rows = []
    for result in engine.predict(inputs):
        value = result.json
        if isinstance(value, str):
            value = json.loads(value)
        rows.append(value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({
        '狀態': 'OCR候選，未校讀，不得直接入卡',
        '原圖SHA256': hashlib.sha256(args.image.read_bytes()).hexdigest(),
        '原圖檔名': args.image.name,
        '說明': '保留模型原字、框位、分數；分數不等於原文正確率；未微調。',
        '裁切設定': regions,
        '框位說明': '裁切模式的框位相對於放大後的局部圖，依裁切設定還原；不是全頁框位。',
        '結果': rows,
    }, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'輸出': str(args.output), '頁結果數': len(rows)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
