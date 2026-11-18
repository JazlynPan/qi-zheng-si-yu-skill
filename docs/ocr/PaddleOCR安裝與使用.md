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

套件安裝完成、pip check通過。命海16酉宮與綱目101頁兩張原圖均成功輸出文字、框位與分數（2/2可執行測試通過）；這不是辨識準確率。

命海酉宮出現串欄、漏字與錯字，不能用來裁決主未好；整頁結果也未逐字驗收。後續應按實際欄位裁切後再辨識、對原圖校讀，不把整頁輸出當作已提煉完成。

原始候選與檢查：[命海酉宮](機器候選/命海16酉-PaddleOCRv5.json)、[綱目101頁](機器候選/綱目101-PaddleOCRv5.json)、[試跑檢查](機器候選/PaddleOCR首次試跑檢查.json)。

模型下載時預設快取指向唯讀目錄，工具已改用呼叫者指定的模型快取目錄；再次試跑成功使用已下載模型。
