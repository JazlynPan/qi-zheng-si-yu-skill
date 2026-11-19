#!/usr/bin/env python3
"""執行：原PDF抽出第16頁原生圖，像素比對舊宮位裁片；只定位，不辨字。"""
import argparse,json,subprocess,tempfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pdf',type=Path,required=True);p.add_argument('--image-dir',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory()as td:
 prefix=Path(td)/'native';subprocess.run(['pdfimages','-f','16','-l','16','-png',str(a.pdf),str(prefix)],check=True,capture_output=True);files=sorted(Path(td).glob('native-*.png'));assert len(files)==1
 im=Image.open(files[0]).convert('RGB');im.save(a.image_dir/'命海16原生.png')
big=np.array(im);rows={}
for g,suffix in [('亥','亥'),('午','午'),('卯','卯宮'),('子','子'),('寅','寅'),('巳','巳宮'),('未','未'),('辰','辰宮'),('酉','酉'),('戌','戌')]:
 z=Image.open(a.image_dir/f'命海-16-{suffix}局部.png').convert('RGB');z=z.resize((round(z.width/3),round(z.height/3)));res=cv2.matchTemplate(big,np.array(z),cv2.TM_CCOEFF_NORMED);_,v,_,loc=cv2.minMaxLoc(res);assert v>.98
 rows[g]={'相似係數':v,'原生左上座標':loc,'原生裁片尺寸':z.size,'舊局部放大倍率':3}
(root/'docs/檢查/命海16原生圖像定位.json').write_text(json.dumps({'原生尺寸':im.size,'說明':'像素模板比對只定位舊裁片在PDF原生圖上的位置，不辨字。','各宮':rows},ensure_ascii=False,indent=2)+'\n')
print('10宮原生圖定位完成，未辨字、未改卡。')
