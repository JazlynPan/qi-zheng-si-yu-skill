"""執行：重建97頁天嗣下注兩個待核字位的紅框與證據；不改卡。"""
from review_helpers import *
def main():
 base=PIC/'綱目97天嗣下注';base.mkdir(exist_ok=True);rows=[]
 for ident,box,a,b in [('TS-01',(27,865,55,902),'彼','他'),('TS-02',(0,704,24,746),'復','彼')]:
  dest=base/(ident+'.png');framed_image('/workspace/review/ocr/綱目-97-原圖0.png',box,dest,'PDF97 天嗣下注 '+ident+'：只核字形，不補句義',scale=5,margin=20)
  rows.append({'編號':ident,'原圖':str(dest.relative_to(ROOT)),'原圖框位':list(box),'候選':[a,b],'狀態':'待看原圖／無法判斷','問題':f'請看紅框內的字，是「{a}」還是「{b}」？'})
 save('綱目97天嗣下注待核.json',{'日期':'2026-11-19','PDF實際頁碼':97,'來源類型':'人工校讀','限制':'尚未形成可靠完整引文，不建立卡片；他書語句不代替本圖字形。','明細':rows})
 lines=['# 綱目97頁天嗣下注待核','','總數2個字位疑點，均未定字，未建卡；OCR只作候選，不直接填文。']
 for r in rows:lines+=['','## '+r['編號'],'',f'![原圖](../{r["原圖"].removeprefix("docs/")})','',r['問題']]
 lines+=['','不補出整句取法；此段目前仍未可靠校清，不能列為提煉完成。']
 (D/'綱目97天嗣下注待核.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
