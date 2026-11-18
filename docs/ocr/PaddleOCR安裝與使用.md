# PaddleOCR安裝與使用

## 選擇

2026-11-18依使用者要求，安裝[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)本機OCR工具，採PP-OCRv5；不是把資料集當成Agent Skill安裝。
[官方PP-OCRv5說明](https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/algorithm/PP-OCRv5/PP-OCRv5.en.md)列有繁體、直排、手寫與生僻字支援；這不保證本庫古籍辨識正確。
[MTHv2](https://github.com/HCIILAB/MTHv2_Datasets_Release)是標註資料集，本次未下載訓練；CASIA-HWDB亦未安裝。
SikuBERT等語義修字不採用，避免將底本改成較通順的字。
[官方Agent Skills](https://www.paddleocr.ai/main/en/version3.x/integrations/skills.html)另需PaddleOCR 3.7+與雲端權杖；本次選本機套件，不宣稱已安裝或啟用該雲端Skill。

## 安裝與執行

版本見[requirements-ocr.txt](../../tools/requirements-ocr.txt)。以獨立Python虛擬環境安裝，無修改原提煉工具相依。

```bash
python -m venv /tmp/qz-ocr-env
/tmp/qz-ocr-env/bin/python -m pip install -r tools/requirements-ocr.txt
/tmp/qz-ocr-env/bin/python -m pip check
/tmp/qz-ocr-env/bin/python tools/paddle_ocr_candidates.py 待核圖.png --output /tmp/OCR候選.json --model-cache /tmp/qz-ocr-models
```

首次執行須下載官方模型；圖像辨識在本機執行，不需雲端辨識權杖。模型、虛擬環境、PDF不入git。
工具直接存文字、框位與分數，不轉繁簡、不做語義糾錯、不寫knowledge/。
只產生候選；仍須對圖核字、頁碼與欄位，分數不是原文正確率。
目前未訓練／微調任何模型，亦未改字典；不能宣稱對古籍已有專門訓練。

## 本次驗證

套件安裝完成、pip check通過。模型試跑結果將另存機器候選，未產出前不算可用驗證通過。
