"""執行：保存97頁天嗣下注機器分歧、玉堂首格紅框；不改卡、不定字。"""
from review_helpers import *
import shutil

def main():
 src=Path('/workspace/review/ocr/綱目-97-原圖0.png');im=Image.open(src);outdir=PIC/'綱目97續核';outdir.mkdir(parents=True,exist_ok=True)
 cases=[{'編號':'GM97-01','概念':'天嗣下注','box':[23,867,53,899],'問題':'紅框內的原字能辨認嗎？','選項':'能（請填原字）／無法判斷','原因':'整格OCR候選他、單列候選的，放大原圖未可靠確認；兩者不是已核定字值。'}, {'編號':'GM97-02','概念':'玉堂首格左字','box':[434,157,455,192],'問題':'紅框內是未還是木？','選項':'未／木／兩者皆非／看不清','原因':'字上方另見短橫，但本次仍不以機器候選或常見星曜名定字。'}]
 rows=[]
 for c in cases:
  dest=outdir/(c['編號']+'.png');path=framed_image(src,c['box'],dest,c['編號']+' PDF第97頁：'+c['問題'],scale=6,margin=28);rows.append({**c,'書名':'星學綱目正傳','頁碼':97,'原圖':path,'來源SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'狀態':'待核，未改卡、未補卡'})
 source=Path('/workspace/review/ocr/綱目97天嗣下注續核-PaddleOCRv5.json');target=ROOT/'docs/ocr/機器候選/綱目97天嗣下注續核-PaddleOCRv5.json';shutil.copyfile(source,target)
 machine=json.loads(source.read_text());rec=[r.get('res',r).get('rec_texts',[])for r in machine['結果']]
 obj={'日期':'2026-11-20','書名':'星學綱目正傳','PDF頁碼':97,'原圖尺寸':list(im.size),'OCR工具':'本機PP-OCRv5 mobile det + server rec，既有快取模型，無網路查字','執行範圍':'只重核尚未收錄的天嗣下注，整格與左右單列共3裁切','機器候選':rec,'人工結果':'未確認右列生之後的字；不得採他、的替代。左列可見但要生復生之為主也，不單獨截成缺上下文的規則卡。','新增卡':0,'既有卡異動':0,'明細':rows};save('綱目97天嗣下注與玉堂首格續核-2026-11-20.json',obj)
 md=['# 綱目97頁剩餘下注與首格續核','','## 結果','','只核尚未收錄的天嗣下注及玉堂首格，不重建既有字列卡。新卡0、既有卡異動0。','天嗣下注3個裁切均已用既有本機PP-OCRv5執行；[原始機器輸出](../ocr/機器候選/綱目97天嗣下注續核-PaddleOCRv5.json)保留框位、分數與裁切設定，分數不等於原字正確率。','','## 機器分歧','','整格：'+repr(rec[0]),'右單列：'+repr(rec[1]),'左單列：'+repr(rec[2]),'同一字被讀成他／的；人工放大仍無可靠讀值，不拿語義補出完整句。左列可見「但要生復生之為主也」，但不把缺右列關鍵字的片段單獨立成規則卡。','','## 待核原字','','|編號|位置|原圖|請回答|','|---|---|---|---|']
 for c in rows:md.append(f'|{c["編號"]}|{c["概念"]}|[紅框圖](../{c["原圖"].removeprefix("docs/")})|{c["問題"]} {c["選項"]}|')
 md+=['','這兩處不因OCR已跑完而視為已完成提煉；仍記入逐書圖表與待核對頁。']
 (D/'綱目97天嗣下注與玉堂首格續核-2026-11-20.md').write_text('\n'.join(md)+'\n')
 cat=ROOT/'docs/catalog/星學綱目正傳.md'
 with cat.open('a')as f:f.write('\n2026-11-20｜圖表與待核對頁：天嗣下注、玉堂首格左字｜《星學綱目正傳》PDF第97頁｜整格／單列OCR分歧，原圖仍未能定字；[兩處紅框與機器候選](../檢查/綱目97天嗣下注與玉堂首格續核-2026-11-20.md)。未建空殼卡。\n')
 p=ROOT/'docs/待你處理.md';s=p.read_text();items=[]
 for c in rows:items.append(f'- {c["編號"]}｜{c["概念"]}：{c["問題"]}｜[報告](檢查/綱目97天嗣下注與玉堂首格續核-2026-11-20.md)｜[圖1]({c["原圖"].removeprefix("docs/")})｜選項：{c["選項"]}')
 s=s.replace('## 可直接回答（有圖）\n','## 可直接回答（有圖）\n\n'+'\n'.join(items)+'\n',1).replace('待處理共99項（有圖96','待處理共101項（有圖98');p.write_text(s)
 p=ROOT/'docs/狀態.md';s=p.read_text().replace('下一個第一動作：續核97頁天嗣下注未收原字；','97頁天嗣下注3裁切OCR分歧及玉堂首格已留2張紅框待核。下一個第一動作：依逐頁清單續核其他未收圖註；');p.write_text(s)
 print(json.dumps({'新增卡':0,'卡異動':0,'原圖':2,'OCR裁切':3},ensure_ascii=False))
if __name__=='__main__':main()
