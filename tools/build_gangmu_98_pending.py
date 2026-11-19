#!/usr/bin/env python3
"""執行：產生綱目98頁左旁三字的紅框與待核清單，不改卡片。"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--image',type=Path,required=True)
a=p.parse_args();root=Path(__file__).resolve().parents[1]
out=root/'docs/待裁決/原圖';out.mkdir(exist_ok=True,parents=True)
im=Image.open(a.image).convert('RGB')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
rows=[]
for ident,title,position,candidate,box in [
 ('T21-1','正廟','第三格左旁上字','箕',(431,233,463,282)),
 ('T21-2','正廟','第十一格左旁上字','紫',(431,548,462,592)),
 ('T21-3','垣廟','首格左旁上字','會',(376,160,405,210))]:
    x0,y0,x1,y1=box;cut=(max(0,x0-8),max(0,y0-8),min(im.width,x1+8),min(im.height,y1+8))
    tile=im.crop(cut).resize(((cut[2]-cut[0])*6,(cut[3]-cut[1])*6))
    panel=Image.new('RGB',(max(440,tile.width),tile.height+50),'white');panel.paste(tile,(0,50));d=ImageDraw.Draw(panel)
    d.text((8,8),ident+' 第98頁 '+title,font=font,fill='black')
    d.rectangle(((x0-cut[0])*6,(y0-cut[1])*6+50,(x1-cut[0])*6,(y1-cut[1])*6+50),outline='red',width=3)
    name=f'綱目98左旁-{ident}.png';panel.save(out/name)
    rows.append({'編號':ident,'原題':title,'位置':position,'PDF實際頁碼':98,'現存卡片讀字':'尚未收錄此左旁字，不涉及覆寫','候選讀字':candidate,'狀態':'未確認','問題':f'紅框上方的字可以讀作「{candidate}」嗎？','原圖':'../待裁決/原圖/'+name,'原圖框位':list(box)})
data={'書名':'星學綱目正傳','PDF實際頁碼':98,'原圖SHA256':hashlib.sha256(a.image.read_bytes()).hexdigest(),'明細':rows,'範圍限制':'只列本次具體字形疑點，不代表三欄左旁其他字與對應關係已全部完成；候選不是原文定稿。','卡片異動數':0}
(root/'docs/檢查/綱目98左旁三字待核.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
lines=['# 綱目98頁右列成果與左旁三字待核','','本次新增3張右列字列卡，各12格，共36格。左旁字不因此算已提取，兩列的對應取法也未補造。既有卡片與先前待裁決修訂未動。','','- [逐字核讀紀錄](../ocr/校讀/星學綱目正傳-098三欄右列字列.json)','- [格式與既有卡不變性檢查](綱目98右列字列驗證.json)','','## 左旁字形待核','','下面的字僅為候選，未入卡。原圖只裁切放大與加框，不重畫字形；每條只問一個字。']
for x in rows:
    lines +=['','### '+x['編號'],'',f'《星學綱目正傳》第98頁，{x["原題"]}欄{x["位置"]}。',f'目前：{x["現存卡片讀字"]}；候選：{x["候選讀字"]}。',f'差異：這個小字尚未核定，不能用右列或常見取法代填。',f'![{x["編號"]}紅框原圖]({x["原圖"]})','',x['問題']]
lines+=['','## 還沒完成的範圍','','三欄左旁其他字、同列歸屬及97頁玉堂疑字仍待核；這三條不是全頁的完整問題清單。未核部分記入catalog與待辦，不建占位卡。','下一處續核：100頁宿名欄旁的小字與數字；不重做已確認的98頁右列。仍屬階段1.5，不宣布完成。']
(root/'docs/檢查/綱目98左旁三字待核.md').write_text('\n'.join(lines)+'\n')
assert all(x['問題'].count('？')==1 and (root/'docs/檢查'/x['原圖']).is_file()for x in rows)
print(json.dumps({'紅框數':len(rows),'卡片異動數':0},ensure_ascii=False))
