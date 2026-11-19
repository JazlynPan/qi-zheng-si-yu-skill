#!/usr/bin/env python3
"""執行：產生階段1.5核對與結束草稿，不改帳本狀態、不宣告完成。"""
import collections
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'docs/檢查'
coverage=json.loads((D/'階段1.5目前覆蓋與R1檢查.json').read_text())
cloud=json.loads((D/'雲端盤點2026-11-19帳本比對.json').read_text())
kept=json.loads((D/'綱目100餘格續核原文保留.json').read_text())
ledger=[]
for line in (ROOT/'docs/來源清單.md').read_text().splitlines():
    if not line.startswith('|') or 'https://'not in line:continue
    c=line.strip('|').split('|');ledger.append(c)
status={x['書名']:x['正文帳本分類'] for x in coverage['逐書列記覆蓋']}
unfinished={'河洛五星合參案例抄本':'2、3、12、13、15頁環排、紅批、卦畫與未確認字；7張原圖的172筆可定位機器候選仍不是核定原文。','星平總會命海':'16頁27筆候選待裁決；331–336頁盤字未全核，86筆機器候選不等於正確原文；原89筆均已回原頁，未明者仍保留。','星學綱目正傳':'40–41頁圖格與淡損圈支、73–96頁跨欄與待確認修訂、97頁玉堂、98頁左旁字、100頁剩4格、101頁其餘圈字與列序仍未核清。'}
lines=['# 階段1.5核對與結束回報草稿（2026-11-19）','','## 目錄','','- [結論](#結論)','- [已完成與檢查](#已完成與檢查)','- [逐書帳本狀態](#逐書帳本狀態)','- [未完成清單](#未完成清單)','- [待確認的決定](#待確認的決定)','','## 結論','','**目前未通過階段1.5完成條件。** 本檔是核對及結束回報草稿，不是完成宣告，沒有進入階段2。','仍有可讀字未完整校清的圖像、無法可靠辨讀的字形，以及使用者指定確認前不得套用的修訂；不能把三者合稱為已完成。','','## 已完成與檢查','',f'- 來源{coverage["來源數"]}份：29本PDF共{coverage["PDF總頁數"]:,}頁，另1份Word依節題與原始段落定位。',f'- 全庫{coverage["卡片數"]:,}張卡；帳本27份已整理所列正文，3份仍核對中，0份完全未處理。',f'- R1生效後新增{coverage["R1後目前新增卡片數"]:,}張，新增空殼{coverage["R1後新增空殼數"]}張；既有空殼不刪、不改。','- 帳本列記沒有未明列的PDF頁段；這不是逐字核完或圖像完成的證明。',f'- 2026-11-19重新盤點雲端{cloud["雲端份數"]}份，新增{len(cloud["新增來源ID"])}、缺少{len(cloud["帳本缺少於雲端ID"])}、檔名不符{cloud["檔名不符數"]}；無子資料夾。',f'- 本機{cloud["本機雜湊已核對數"]}份SHA256符合帳本，29本PDF頁數符合；未重新下載全部遠端內容，不能等同重驗遠端雜湊。',f'- 以a3cbfc6e為基準核對原有{kept["既有卡片數"]:,}張：原文保留問題{kept["原文保留問題數"]}、目前全庫結構問題{kept["結構問題數"]}。僅E0檔案檢查，不代替原圖字讀或獨立盲評。','- 靈臺118題與題稱120差2已由使用者接受為原書結構差異，結案，不補造。','- T04登籍戊子與辛巳／辛亥決定已處理；T09原PDF184／188頁已核，184頁未載天魔名，不擴張出處。','','## 逐書帳本狀態','','此表只反映帳本與原有處理紀錄；「已整理正文」不代表後續跨書檢查、評測或Skill可用。','','|書名|PDF頁數或其他定位|帳本狀態|','|---|---|---|']
for c in ledger:
    catalog=ROOT/'docs/catalog'/(c[0]+'.md');label=f'[{c[0]}](../catalog/{catalog.name})'if catalog.is_file()else c[0]
    word='仍核對中'if status[c[0]]=='進行中'else'已整理所列正文'
    lines.append(f'|{label}|{c[3]}|{word}|')
lines+=['','## 未完成清單','','|書名|具體剩餘工作|','|---|---|']
for book,remaining in unfinished.items():lines.append(f'|{book}|{remaining}|')
lines+=['','- [待辦事項](../待辦事項.md)：包含T07、T10、T14、T15、T17、T20–T22的具體範圍與原圖入口。','- 先前37張選定圖頁的1,358段OCR候選仍未全量逐字校完；37／37產出成功不能算37頁完成，也不能只因全量格式通過就結案。','- 圖像困難與尚未校完的工作都留在上表，不把未確認字當原文，不用規律、他書或模型記憶補足。','','## 待確認的決定','','1. [T07完整修訂預覽](../待裁決/T07修訂預覽.md)：21筆已有原圖讀值，舊全文與預覽已保存，尚未套用；己丑未確認不動，補卡不做。','2. 其他待裁決與無法可靠辨讀的項目仍保留。若要讓這些項目留待人工或後續處理，必須由使用者明確接受剩餘範圍；本報告沒有自行縮小原定工作。','3. 未完成項未核清、或使用者未接受保留範圍之前，帳本3份進行中及階段1.5狀態都不改為完成。','','## 檢查依據','','[雲端比對](雲端盤點2026-11-19帳本比對.json)｜[帳本頁範圍及R1](階段1.5目前覆蓋與R1檢查.json)｜[原文保留及結構](綱目100餘格續核原文保留.json)']
report=D/'階段1.5核對與結束草稿-2026-11-19.md';report.write_text('\n'.join(lines)+'\n')
errors=[]
for link in re.findall(r'\]\(([^)]+)\)',report.read_text()):
    if link.startswith('#'):continue
    if not(report.parent/link).exists():errors.append(link)
assert not errors,errors
print(json.dumps({'來源數':len(ledger),'正文已整理':27,'仍核對中':3,'卡片數':coverage['卡片數'],'報告失效連結':len(errors),'階段1.5完成':False},ensure_ascii=False))
