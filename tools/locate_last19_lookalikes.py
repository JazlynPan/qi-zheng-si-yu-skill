"""執行：用原頁已找到的完整語境補19筆字位圖；不改卡，不以術數推字。"""
from review_helpers import *
from locate_pending_lookalikes import folded
CASES={
'XJ-0028':(87,'夭命之圖解〔〕未癸丑丙戌庚子'),
'XJ-0033':(10,'寅申有曜亥宮恩〔〕丑卯宮亥未酉'),
'XJ-0077':(22,'申酉十死一生〔〕酉日提到寅宮'),
'XJ-0084':(5,'金星為命主〔〕申二宮安命水星'),
'XJ-0089':(72,'金〔〕宮咸池星又名天沒星'),
'XJ-0090':(72,'金〔〕宮咸池星又名天沒星'),
'XJ-0128':(102,'格高官貴仕路軒〔〕命主卑微留滯'),
'XJ-0132':(20,'知不知立春後〔〕時天度午入地'),
'XJ-0173':(12,'酉上見卯即金〔〕宮坐命'),
'XJ-0270':(12,'木躔〔〕金躔胃名木打大梁'),
'XJ-0279':(69,'已酉壬子庚午〔〕丑'),
'XJ-0311':(68,'丁卯甲戌已巳〔〕丑'),
'XJ-0384':(197,'丙子丁丑戊子〔〕丑詩例'),
'XJ-0406':(20,'計泊卯〔〕宮卯泄計且羅'),
'XJ-0443':(7,'炁星在垣眉宇軒〔〕精神清秀壽永')}
def main():
 out=D/'形近字剩餘19筆字位核對-2026-11-20.json';assert not out.exists()
 old=json.loads((D/'形近字批量修訂清單.json').read_text())['明細'];prior=json.loads((D/'形近字37筆補定位-2026-11-20.json').read_text());rows=[]
 for prev in prior['明細']:
  if prev['原圖']:continue
  ident=prev['編號'];r=next(a for a in old if a['編號']==ident);book=r['書名'];notes=[]
  if ident=='XJ-0443':book='五星捷要便覽';notes.append('舊檢查腳本漏認卡片第25行無頁碼的書名，錯承前段琴堂來源；卡片原段明列五星捷要便覽。不是琴堂原文，也不能把錯誤歸於卡片。')
  pgno=CASES[ident][0]if ident in CASES else r['起頁'];doc=pdf(book);pg=doc[pgno-1]
  if ident in CASES:
   b,a=CASES[ident][1].split('〔〕');b=folded(b).replace('洩','泄').replace('鹹','咸');a=folded(a).replace('洩','泄').replace('鹹','咸');raw,boxes=pagechars(book,pgno);s=folded(raw).replace('洩','泄').replace('鹹','咸');positions=[i for i in range(len(s))if s[max(0,i-len(b)):i]==b and s[i+1:i+1+len(a)]==a];assert len(positions)==1,(ident,positions)
   i=positions[0];bb=boxes[i];cl=(bb+(-110,-45,110,45))&pg.rect;pix=pg.get_pixmap(matrix=fitz.Matrix(3,3),clip=cl);image=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);scale=3;local=(bb.x0-cl.x0,bb.y0-cl.y0,bb.x1-cl.x0,bb.y1-cl.y0);context=raw[max(0,i-15):i]+'〔'+raw[i]+'〕'+raw[i+1:i+16];glyph=raw[i];method='原頁完整雙側語境唯一定位；目標字不作搜尋條件'
  else:
   # 人工查看整欄後，依本張卡的列序定位；不推算宮位。
   # 100頁只取孤寡欄，不續核暫停中的伏尸、闌干、貫索。
   source=Path('/workspace/review/ocr')/f'綱目-{pgno}-原圖0.png';im=Image.open(source).convert('RGB')
   if ident in ['XJ-0164','XJ-0165','XJ-0166']:
    ordinal={'XJ-0164':3,'XJ-0165':4,'XJ-0166':5}[ident];cy={3:250,4:287,5:323}[ordinal];bb=(81,cy-15,102,cy+15);clip=(49,max(0,cy-45),111,cy+45);notes.append(f'孤寡欄第{ordinal}列右字；同圖另一字僅供定位，不改讀值。')
   else:
    ordinal=6;cy=374;bb=(83,cy-17,104,cy+17);clip=(49,cy-50,113,cy+50);notes.append('解神欄第6列右字；依原刻列序定位，不按干支規律代填。')
   image=im.crop(clip).resize(((clip[2]-clip[0])*6,(clip[3]-clip[1])*6));local=(bb[0]-clip[0],bb[1]-clip[1],bb[2]-clip[0],bb[3]-clip[1]);scale=6;context='按卡片既有字列與原圖欄題、列序定位，待核字形';glyph='未用OCR代讀';method='人工查看原圖孤寡／解神欄，依卡片列序框字';notes.append('框位座標為原始內嵌PNG像素，非PDF點數。')
  dest=PIC/'形近字剩餘19筆'/f'{ident}.png';dest.parent.mkdir(parents=True,exist_ok=True);pan=Image.new('RGB',(max(900,image.width),image.height+110),'white');pan.paste(image,(0,110));dr=ImageDraw.Draw(pan);dr.text((8,5),ident+f' 《{book}》PDF第{pgno}頁',font=FONT,fill='black');dr.text((8,35),f'紅框內是「{r["現字"]}」還是「{r["候選字"]}」？亦可答兩者皆非／看不清',font=FONT,fill='black');dr.text((8,65),'只補字位圖，未修改卡片；文字層讀字不等於裁決',font=FONT,fill='red');dr.rectangle((local[0]*scale,110+local[1]*scale,local[2]*scale,110+local[3]*scale),outline='red',width=3);pan.save(dest)
  mismatch=book!=r['書名']or not r['起頁']<=pgno<=r['迄頁']
  if mismatch and ident!='XJ-0443':notes.append('找到的原頁不在卡片現標範圍，須另核來源頁碼；本輪不改卡。')
  rows.append({'編號':ident,'卡名':r['卡名'],'原報告書名':r['書名'],'卡片現標頁碼':[r['起頁'],r['迄頁']],'實際來源書名':book,'原圖實際頁碼':pgno,'現字':r['現字'],'候選字':r['候選字'],'定位方法':method,'定位語境':context,'文字層讀字':glyph,'來源類型':'人工校讀'if ident not in CASES else'文字層','原圖':str(dest.relative_to(ROOT)),'原圖框位':list(bb),'來源需再核':mismatch,'說明':notes,'狀態':'已補字位圖，待使用者確認；未改卡'})
 obj={'日期':'2026-11-20','本批筆數':19,'原圖數':19,'累計37筆已補字位圖':37,'來源頁碼不在卡片範圍':sum(x['來源需再核']and x['編號']!='XJ-0443'for x in rows),'舊檢查來源誤承':1,'卡片修改':0,'明細':rows};save(out.name,obj)
 md=['# 形近字剩餘19筆字位核對','','## 結果','','共19筆19圖；與上一批18筆合計37筆字位圖。這只表示找到字位，不表示已裁決原字。','5筆原頁超出卡片現標範圍，另1筆是舊檢查腳本誤承前段書名；均未改卡。','綱目100頁只取孤寡欄，不續核仍暫停的伏尸、闌干與貫索。','','|編號|卡名|原報告書名／頁碼|本次來源／實際頁碼|紅框圖|說明|','|---|---|---|---|---|---|']
 for x in rows:md.append(f'|{x["編號"]}|{x["卡名"]}|{x["原報告書名"]} {x["卡片現標頁碼"]}|{x["實際來源書名"]} {x["原圖實際頁碼"]}|[原圖](../{x["原圖"].removeprefix("docs/")})|'+('；'.join(x['說明'])or'字形待確認')+'|')
 md+=['','## 來源差異的處理','','XJ-0443卡片第25行本來就列《五星捷要便覽》，但未列PDF頁碼；舊檢查器只認有頁碼的出處，錯誤延用前段《歷學會通·琴堂五星》第2–4頁。本次找到《五星捷要便覽》第7頁同句，這是報告來源辨識錯誤，不是兩書異文。其「軒昂」屬合法詞，仍以原頁圖保留供核。','其餘5筆頁碼差異僅提報，未擅自回填。所有字值等使用者確認；看不清時保留未確認。']
 (D/'形近字剩餘19筆字位核對-2026-11-20.md').write_text('\n'.join(md)+'\n');print({k:v for k,v in obj.items()if k!='明細'})
if __name__=='__main__':main()
