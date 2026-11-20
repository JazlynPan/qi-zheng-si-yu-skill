"""執行：將本輪所有既有文字檔的完整舊新版本與SHA256再集中保存；不改卡。
新檔本身已由git保留全文；本工具針對相對本輪基準有變動的既有檔，不刪任何舊版本。
"""
from pathlib import Path
import subprocess,json,hashlib
R=Path(__file__).resolve().parents[1];F=R/'docs/勘校修訂/2026-11-20完整裁決'
def main():
 out=F/'既有全部檔案舊新全文與SHA256.json';assert not out.exists()
 base=json.loads((F/'定字與既有核對.json').read_text())['基準提交']
 assert not subprocess.check_output(['git','diff','--name-only','--diff-filter=D',base],cwd=R)
 names=subprocess.check_output(['git','diff','--name-only','--diff-filter=M','-z',base],cwd=R).decode().strip('\0').split('\0');rows=[]
 for n in names:
  if not n:continue
  old=subprocess.check_output(['git','show',base+':'+n],cwd=R);new=(R/n).read_bytes()
  rows.append({'檔案':n,'舊全文':old.decode(),'新全文':new.decode(),'舊SHA256':hashlib.sha256(old).hexdigest(),'新SHA256':hashlib.sha256(new).hexdigest()})
 out.write_text(json.dumps({'日期':'2026-11-20','基準提交':base,'既有文字檔修改數':len(rows),'包含':'18張舊卡及本輪變動的帳本、抽查紀錄、狀態、索引入口與開發工具；不刪舊檔','明細':rows},ensure_ascii=False,indent=2)+'\n')
 diff=subprocess.check_output(['git','diff','--binary',base,'--']+names,cwd=R);(F/'既有全部檔案差異.patch').write_bytes(diff);print('集中保存既有檔',len(rows))
if __name__=='__main__':main()
