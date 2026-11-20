"""執行：只新增待你處理入口，從現有證據連到待決項；不改卡或重寫舊報告。
目錄：main（分組、待決項、排除已決項、入口文字）。
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs'
def clean(s):return str(s).replace('\n',' ').replace('|','／')
def report(path,anchor=''):
 p=ROOT/path;assert p.exists(),path
 return '[報告]('+str(p.relative_to(D))+anchor+')'
def pics(paths):
 assert len(paths)<=3
 out=[]
 for i,p in enumerate(paths,1):
  assert (ROOT/p).is_file(),p
  out.append(f'[圖{i}]('+str((ROOT/p).relative_to(D))+')')
 return ' '.join(out)
def row(ident,q,path,images,options,anchor=''):
 return '- '+ident+'｜'+clean(q)+'｜'+report(path,anchor)+'｜'+pics(images)+'｜選項：'+options

def main():
 dest=D/'待你處理.md';assert not dest.exists(),'只新增，不覆寫入口'
 t14=json.loads((D/'檢查/命海16_T14本輪逐筆複核.json').read_text())['明細'];shape=json.loads((D/'檢查/形近字批量修訂清單.json').read_text())['明細'];pairs=json.loads((D/'檢查/擎遊44筆成對原圖重核.json').read_text())['明細']
 sections={'可直接回答（有圖）':[],'需要先確認規則':[],'等 Codex 先找圖':[]};direct=sections['可直接回答（有圖）'];rules=sections['需要先確認規則'];waiting=sections['等 Codex 先找圖']
 for r in t14:
  # 三處淂字合成一題；27號主喜怒已有使用者明確確認，現卡本來一致，不再問。
  if r['編號']in['T14-13','T14-19','T14-24','T14-27']:continue
  label=r['卡片'].split('圖列')[0]
  direct.append(row(r['編號'],f'{label}紅框內是「{r["現存讀字"]}」還是「{r["候選修訂字"]}」？','docs/檢查/命海16_T14本輪逐筆複核.md',[r['原圖']],f'{r["現存讀字"]}／{r["候選修訂字"]}／看不清','#'+r['編號'].lower()))
 direct.append(row('T14-13／19／24','這三格中間的字是否相同，應讀淂、得還是淨？','docs/檢查/命海16_淂字三處部件複核.md',['docs/待裁決/原圖/命海T14/三處淂字原生並排.png'],'淂／得／淨／三處不同（逐格填）／看不清'))
 direct.append(row('T21-1','正廟第三格左旁是否確為你提出的「簊金」？','docs/檢查/綱目98_T21本輪字形複核.md',['docs/待裁決/原圖/綱目T21/T21-1.png'],'確認簊金／另寫讀值／看不清'))
 direct.append(row('綱目100-伏尸','伏尸整欄12格的宿名與數字是否與目前收錄一致？','docs/檢查/綱目100伏尸闌干整欄對照.md',['docs/待裁決/原圖/綱目100整欄/伏尸-整欄紅框.png','docs/待裁決/原圖/綱目100整欄/FS-02.png','docs/待裁決/原圖/綱目100整欄/FS-08.png'],'12格一致／逐格更正／看不清'))
 direct.append(row('綱目100-闌干','闌干整欄目前收錄的11格是否一致（未收卯格仍暫停）？','docs/檢查/綱目100伏尸闌干整欄對照.md',['docs/待裁決/原圖/綱目100整欄/闌干-整欄紅框.png','docs/待裁決/原圖/綱目100整欄/LG-08.png'],'11格一致／逐格更正／看不清'))
 direct.append(row('己丑共值','己丑這格能讀出歲殿與登籍的值嗎（現仍未確認，兩卡不動）？','docs/檢查/歲殿登籍60組一致性-2026-11-20.md',['docs/待裁決/原圖/科甲欄/KJ-020.png'],'填可辨原字／圖上無值／看不清'))
 def byyear(y):return next(r['原圖']for r in pairs if r['年字']==y)
 rules.append(row('擎遊記法','原圖未分擎天、游奕的組，是否只按左右成對記錄而不替它選邊？','docs/檢查/科甲欄全組重核.md',[byyear('庚子'),byyear('辛巳'),byyear('辛亥')],'成對記錄並註未分／先保留不改'))
 rules.append(row('擎遊分類','前組比對有三種定義，分類要採原圖前組右字，還是三種方法各列？','docs/檢查/科甲欄全組重核.md',[byyear('丁丑')],'原圖前組右字／三種方法各列／另指定定義','#分類獨立重算'))
 rules.append(row('丙辰分題例外','丙辰原圖分別印擎天、游奕，是否按各自題字記錄，不套用未分記法？','docs/檢查/科甲欄全組重核.md',[byyear('丙辰')],'分題照錄／暫不改'))
 rules.append(row('缺卡補建','未來是否只補已確認有實字、且未被禁止新增的缺卡（丙子及未確認己丑不自補）？','docs/檢查/歲殿登籍60組一致性-2026-11-20.md',['docs/待裁決/原圖/科甲欄/KJ-014.png'],'符合條件者另批補／暫不補'))
 unresolved=[r for r in shape if r['定位']=='僅附引用頁紅框；未定位字位'];assert len(unresolved)==37
 for r in unresolved:
  # 現有圖片只圈引用頁範圍，不謊稱已圈到目標字；不要求使用者現在猜字。
  q=f'《{r["書名"]}》第{r["起頁"]}頁「{r["前文"]}〔{r["現字"]}〕{r["後文"]}」尚未圈到字，等補字位圖後再判。'
  waiting.append(row(r['編號'],q,'docs/檢查/形近字批量修訂清單.md',[r['原圖']],'等補字位圖後再判'))
 lines=['# 待你處理','','只列尚未決定的項目；每項最多3張圖。第三組目前只有引用頁範圍框，尚未圈到目標字，不用現在猜。']
 for title,items in sections.items():lines+=['','## '+title,'']+items
 lines+=['',f'待處理共{sum(map(len,sections.values()))}項（有圖{len(direct)}、規則{len(rules)}、等補圖{len(waiting)}）；本輪與上一輪已回填28張卡（22修訂、6新增，不重複計檔）；[完整歷次勘校修訂紀錄](勘校修訂紀錄.md)。']
 dest.write_text('\n'.join(lines)+'\n')
 state=D/'狀態.md';old=state.read_text();prefix='待你決定的入口：[docs/待你處理.md](待你處理.md)。\n';state.write_text(prefix+old);assert state.read_text()[len(prefix):]==old
 print(json.dumps({'入口待處理項':sum(map(len,sections.values())),'各組':{k:len(v)for k,v in sections.items()},'狀態僅新增首行':True,'排除已決T14_27':True},ensure_ascii=False))
if __name__=='__main__':main()
