from review_helpers import *
from collections import Counter
stem='綱目41九至十二月圈支續核-2026-11-25';rows=[]
for month in range(9,13):
 src=Path(f'/workspace/review/ocr/綱目41月{month}外圍放大.png')
 im=Image.open(src)
 image=framed_image(src,[40,175,715,1040],PIC/stem/f'GM41-{month:02d}-外圍圈支.png',f'綱目PDF第41頁 {month}月：淡損圈支不按規律補字',scale=1,margin=0)
 rows.append({'編號':f'GM41-{month:02d}','月份':month,'來源類型':'人工校讀原圖；OCR只提供定位線索','原圖檔名':src.name,'原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'紅框圖':image,'看圖結論':'外圍神煞名稱多可辨，圈支淡損，仍無法可靠逐格配對；未借別月值補字','是否改卡':False,'已收卡':['天德月別圖列（星學綱目圖說）.md','月德月別圖列（星學綱目圖說）.md']})
report={'日期':'2026-11-25','PDF頁碼':41,'月份數':4,'已可靠補出圈支數':0,'新增卡數':0,'既有卡異動數':0,'明細':rows,'限制':'放大不增加原始像素；原生內嵌圖已於既有報告記尺寸與SHA。沒有使用生成式補筆、他書或取法推測。不是全部圈支驗收通過。'}
(D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 綱目第41頁九至十二月圈支續核','','四個月份外圍圖已再看原圖。可讀名稱不能代替同格圈支；已有天德、月德月別卡不重建。新增卡0、既有卡異動0。','原生圖尺寸與限制見[既有原生圖核對](綱目41月份OCR與結構檢查.json)。','','|編號|PDF頁／月份|本次結果|原圖|','|---|---|---|---|']
for r in rows:md.append(f'|{r["編號"]}|41／{r["月份"]}月|圈支淡損，無法可靠逐格配對|[紅框圖](../{r["紅框圖"].removeprefix("docs/")})|')
md+=['','## 需要使用者決定','','每題：請看紅框圈內的小字，能逐格辨讀嗎？選項：能（請寫神煞名與圈字）／無法判斷（保留缺值）。看不清就保留缺值，不依月份規律補字。','本報告只記本次核圖；不得把神煞名稱照錄另建成沒有可用字值的空殼卡。','[逐項證據]('+stem+'.json)。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
p=ROOT/'docs/待你處理.md';s=p.read_text();marker='## 需要先確認規則'
entries=[]
for r in rows:entries.append(f'- {r["編號"]}｜第41頁{r["月份"]}月紅框圈內小字能逐格辨讀嗎？｜[報告](檢查/{stem}.md)｜[圖1]({r["紅框圖"].removeprefix("docs/")})｜選項：能（請填神煞名與圈字）／無法判斷（保留缺值）')
assert all(r['編號'] not in s for r in rows)
s=s.replace(marker,'\n'.join(entries)+'\n\n'+marker)
s=s.replace('待處理共81項（有圖77、規則4','待處理共85項（有圖81、規則4');p.write_text(s)
p=ROOT/'docs/catalog/星學綱目正傳.md'
with p.open('a') as f:f.write('\n### 2026-11-25：第41頁九至十二月剩餘圈支\n\n四月圖再核仍無法可靠逐格配對，不由他月推字；天德、月德已有原文，不重建卡。新增0、改卡0。[四張原圖與待決問題](../檢查/'+stem+'.md)。\n')
p=ROOT/'docs/狀態.md';s=p.read_text().replace('下一個第一動作：續核第40–41頁九至十二月外圍圖，與已有月德天德卡分開，不重建已收原文；隨後整合未核與待決清單，不因走到末頁宣稱完成。','第41頁九至十二月外圍圈支再核仍無法可靠配對，已附四張紅框，未造空殼。下一個第一動作：核對剩餘圖頁的逐頁分區紀錄與已收片段，移除復工清單中已完成的工作敘述，保留真正模糊字與待決項。')
s=s.replace('1. 新增HL15-候卦','1. 第41頁四個月份圈支淡損（GM41-09至12）已附圖；新增HL15-候卦');p.write_text(s)
print(json.dumps({'月份圖':4,'新增卡':0,'待處理':85},ensure_ascii=False))
