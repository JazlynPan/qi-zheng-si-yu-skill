"""執行：核對歲殿／登籍檔案覆蓋，僅出缺口清單；不推填、不建卡。"""
from pathlib import Path
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1];K=ROOT/'qi-zheng-si-yu/knowledge';D=ROOT/'docs'
def main():
 groups={'兩種卡都有':[],'只有歲殿卡，缺登籍卡':[],'只有登籍卡，缺歲殿卡':[],'兩種卡都缺':[]}
 for i in range(60):
  y='甲乙丙丁戊己庚辛壬癸'[i%10]+'子丑寅卯辰巳午未申酉戌亥'[i%12];a=K/f'歲殿圖列·{y}（星學綱目圖說下）.md';b=K/f'登籍圖列·{y}（星學綱目圖說下）.md'
  label='兩種卡都有'if a.exists()and b.exists()else'只有歲殿卡，缺登籍卡'if a.exists()else'只有登籍卡，缺歲殿卡'if b.exists()else'兩種卡都缺'
  groups[label].append({'年份':y,'歲殿卡':a.name if a.exists()else None,'登籍卡':b.name if b.exists()else None,'處理':'等待逐組原圖證據及使用者確認，不自動補卡'})
 report={'統計日期':'2026-11-20','口徑':'按六十組干支及實際歲殿／登籍檔名，不把歲駕卡當歲殿卡；存在檔案不代表有可用字值。','分布':{k:len(v)for k,v in groups.items()},'僅歲殿缺登籍組數':len(groups['只有歲殿卡，缺登籍卡']),'新增或修改卡片':0,'使用者決定':'覆蓋缺口，不當作值錯；原圖證據逐組確認後才補，不能從歲殿值自行推填登籍。','明細':groups}
 (D/'檢查/登籍覆蓋缺口31組-2026-11-20.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 lines=['# 登籍覆蓋缺口核對（2026-11-20）','','## 統計口徑','','以目前實際檔案為準：有歲殿卡、沒有登籍卡31組；與外部所述約33組不同，不推測其計數方式。另有10組兩種卡都缺。缺卡是覆蓋缺口，不是字值錯誤。','歲駕不是歲殿：丁丑、己丑現有歲駕檔不自動算成歲殿。兩種卡都有17組也不代表17組都有可用字值，其中戊寅已如實標缺載。','','|檔案覆蓋情形|組數|','|---|---|']
 for label,rows in groups.items():lines.append(f'|{label}|{len(rows)}|')
 lines+=['','## 只有歲殿、缺登籍的31組','','|年份|現有歲殿卡|登籍狀態|','|---|---|---|']
 for r in groups['只有歲殿卡，缺登籍卡']:lines.append(f'|{r["年份"]}|{r["歲殿卡"]}|缺卡；待逐組原圖與使用者確認|')
 lines+=['','## 其餘缺口','','兩種卡都缺：'+'、'.join(r['年份']for r in groups['兩種卡都缺'])+'。','只有登籍、缺歲殿：'+'、'.join(r['年份']for r in groups['只有登籍卡，缺歲殿卡'])+'。','','## 補卡條件與本次處理','','原圖是否有登籍題字、是否與歲殿共用字值，都須在各組原圖上確認；不把一般聯列說法擴大為60組均可直接複製。尤其戊寅與己丑已有特殊限制，不能靠公式或鄰欄補出。','目前不新增任何卡片，先整理逐組原圖證據，再交使用者確認；本次未授權補卡。丙子先前不新增的決定亦不因本缺口清單而解除。','[60組值與缺載檢查](歲殿登籍60組一致性-2026-11-20.md)仍保留；本表另將「缺檔」與「值錯」分開，不將42組缺卡統稱為42組錯字。']
 (D/'檢查/登籍覆蓋缺口31組-2026-11-20.md').write_text('\n'.join(lines)+'\n');print(json.dumps(report['分布'],ensure_ascii=False))
if __name__=='__main__':main()
