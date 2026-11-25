"""執行：依人工定字稿保存圖列原文、紅框、全文雜湊；不自動判字或補字。
用法：python tools/apply_literal_diagram_batch.py docs/檢查/某批人工定字稿.json
"""
from review_helpers import *
from stage2_preflight import parse
import argparse,subprocess

def run(planfile):
    plan=json.loads(planfile.read_text());date=plan['日期'];stem=plan['批名'];book=plan['書名']
    archive=ROOT/'docs/勘校修訂'/stem
    assert not archive.exists() or not any(archive.iterdir()),'本批已有完整留存，禁止重複追加'
    tracked={Path(p.decode()).name for p in subprocess.check_output(['git','ls-files','-z','qi-zheng-si-yu/knowledge'],cwd=ROOT).split(b'\0') if p}
    planned=set()
    for item in plan['明細']:
        if item.get('處理','新增')!='新增':continue
        name=item.get('卡片',f'{item["題字"]}圖列·第{item["頁"]}頁{item["圈"]}字圈（星學綱目圖說下）.md')
        assert name not in tracked,'原有卡不得重建：'+name
        assert name not in planned,'本批名稱重複：'+name
        planned.add(name)
    assert all(p.name in tracked or p.name in planned for p in K.glob('*.md')),'有本批以外未追蹤卡片，先核對來源'
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.md') if p.name in tracked}
    base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    rows=[];newnames=[];changed=[];archive.mkdir(exist_ok=True);folder=PIC/stem;folder.mkdir(exist_ok=True)
    for i,item in enumerate(plan['明細'],1):
        page=item['頁'];circle=item['圈'];label=item['題字'];text=item.get('原文字列',label)
        name=item.get('卡片',f'{label}圖列·第{page}頁{circle}字圈（星學綱目圖說下）.md')
        path=K/name;src=Path('/workspace/review/ocr')/item['原圖檔名'];im=Image.open(src).convert('RGB')
        clip=item['上下文'];tile=im.crop(clip);tile=tile.resize((tile.width*4,tile.height*4));panel=Image.new('RGB',(max(1050,tile.width),tile.height+65),'white');panel.paste(tile,(0,65));draw=ImageDraw.Draw(panel);draw.text((8,8),f'{book} PDF第{page}頁／{label}與{circle}字圈：人工核字',font=FONT,fill='black')
        for b in item['紅框']:
            draw.rectangle(((b[0]-clip[0])*4,65+(b[1]-clip[1])*4,(b[2]-clip[0])*4,65+(b[3]-clip[1])*4),outline='red',width=3)
        image=folder/f'{i:02}-{page}-{label}-{circle}.png';panel.save(image)
        section=item.get('篇名','六十年甲子圖')
        cite=f'《{book}》第{page}頁'+(f'〈{section}〉' if section else '')+'：\n\n原文以圖表呈現\n\n'
        old=None;insertion=None
        if item.get('處理','新增')=='新增':
            body=f'#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n{cite}{circle}\n\n{text}\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n'
            if path.exists():assert path.read_bytes()==body.encode(),'中斷批次的未追蹤卡與定字稿不同：'+name
            assert not any(body==p.read_text() for p in K.glob('*.md') if p.name!=name)
            newnames.append(name)
        else:
            assert item['處理']=='插入原文' and path.exists()
            old=path.read_bytes();assert text not in ''.join(old.decode().split())
            addition=('\n'+cite+text+'\n').encode();point=old.index(b'\n## '+ '操作步驟'.encode()+b'\n');new=old[:point]+addition+old[point:];assert new[:point]+new[point+len(addition):]==old
            body=new.decode();insertion={'位置':point,'位元組數':len(addition),'刪除此插入即還原舊全文':True};changed.append(name)
        assert body.splitlines()[0]=='#七政四餘'
        assert all(body.count('## '+f)==1 for f in ('核心概念','使用規則','操作步驟','原文例子'))
        path.write_bytes(body.encode())
        rows.append({**item,'卡片':name,'來源類型':'人工校讀','原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'紅框圖':str(image.relative_to(ROOT)),'舊全文':old.decode() if old else None,'舊SHA256':hashlib.sha256(old).hexdigest() if old else None,'新全文':body,'新SHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'插入驗證':insertion})
    assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==h for n,h in before.items() if n not in changed)
    total=len(list(K.glob('*.md')));assert total==len(before)+len(newnames)
    bookcount=sum(any(b==book for b,a,z,u in parse(p.read_text())[1]) for p in K.glob('*.md'))
    pending=[]
    for i,item in enumerate(plan.get('待核圖',[]),1):
        src=Path('/workspace/review/ocr')/item['原圖檔名']
        image=framed_image(src,item['原框'],folder/f'待核-{i:02}-{item["頁"]}.png',item['問題'],scale=4,margin=25)
        pending.append({**item,'紅框圖':image,'處理':'僅留圖與候選，不入卡'})
    report={'日期':date,'基準提交':base,'新增卡數':len(newnames),'既有卡只追加引文':len(changed),'既有字值覆寫':0,'其餘舊卡異動':0,'全庫卡數':total,'本書卡數':bookcount,'明細':rows,'保留待核':plan['保留待核'],'待核圖':pending}
    (archive/'舊新全文與SHA256.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (D/(stem+'.json')).write_text(json.dumps({k:v for k,v in report.items() if k!='明細'}|{'明細':[{k:v for k,v in r.items() if k not in ('舊全文','新全文')} for r in rows]},ensure_ascii=False,indent=2)+'\n')
    md=['# '+stem,'',plan['說明'],'',f'新增{len(newnames)}卡、既有卡只插入引文{len(changed)}張；既有原字覆寫0，其他卡異動0。全庫{total:,}張、本書{bookcount:,}張。','','|頁|圈|原字|處理|圖|','|---|---|---|---|---|']
    for r in rows:md.append(f'|{r["頁"]}|{r["圈"]}|{r.get("原文字列",r["題字"]).replace(chr(10)," ")}|{r.get("處理","新增")}|[紅框](../{r["紅框圖"].removeprefix("docs/")})|')
    md+=['','[舊新全文與SHA256](../勘校修訂/'+stem+'/舊新全文與SHA256.json)。新卡四欄、來源及同頁完全同文檢查通過；插入引文可逐位元組移除還原舊卡，不改舊字。','','## 保留待核','']+['- '+t for t in plan['保留待核']]
    md += [f'- {x["問題"]} [紅框](../{x["紅框圖"].removeprefix("docs/")})；未入卡。' for x in pending]
    (D/(stem+'.md')).write_text('\n'.join(md)+'\n')
    if changed:
        with (ROOT/'docs/勘校修訂紀錄.md').open('a') as f:f.write(f'\n## {date}【原文續錄】{stem}\n\n既有卡{len(changed)}張只插入新引文，不替換原字；完整舊新全文與SHA256已留存。[逐項原圖](檢查/{stem}.md)；[全文留存](勘校修訂/{stem}/舊新全文與SHA256.json)。\n')
    with (ROOT/'docs/catalog/星學綱目正傳.md').open('a') as f:f.write(f'\n### {date}：{stem}\n\n新增{len(newnames)}卡，{len(changed)}張原卡只插入原文；原字不改。[原字與紅框](../檢查/{stem}.md)。保留待核：'+ '；'.join(plan['保留待核'])+'。\n')
    p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
    for i,line in enumerate(lines):
        if line.startswith('|'+book+'|'):
            c=line.strip('|').split('|');c[5]=re.sub(r'累計\d+張',f'累計{bookcount}張',c[5]);c[6]+=f'；{date}{stem}新增{len(newnames)}卡、原卡插入引文{len(changed)}張，未清字仍保留';c[7]=date;lines[i]='|'+'|'.join(c)+'|'
    p.write_text('\n'.join(lines)+'\n')
    p=ROOT/'docs/狀態.md';s=p.read_text();s=re.sub(r'共[\d,]+張；綱目[\d,]+張',f'共{total:,}張；綱目{bookcount:,}張',s);s=re.sub(r'復工位置：[^\n]+','復工位置：'+plan['復工位置'],s,1);p.write_text(s)
    for relative in ['docs/階段1.5目前檢查摘要.md','docs/檢查/階段1.5完成條件核對-2026-11-18.md','docs/檢查/階段1.5待校與待裁決分界.md']:
        p=ROOT/relative;s=p.read_text().replace(f'{len(before):,}',f'{total:,}').replace(str(len(before)),str(total))
        s=re.sub(r'(R1(?:生效)?後目前新增)([\d,]+)',lambda m:m[1]+(f'{int(m[2].replace(",",""))+len(newnames):,}' if ',' in m[2] else str(int(m[2])+len(newnames))),s)
        p.write_text(s)
    p=D/'階段1.5待校與待裁決分界.json';j=json.loads(p.read_text());j['卡片數']=total
    for r in j['明細']:
        if r['書名']==book and r['頁碼'] in {x['頁'] for x in rows}:r['最新續核']=date+'部分細字續錄，見'+stem+'.md；未清字保留。'
    p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
    args=['python','tools/check_stage15_progress.py','--output','docs/檢查/'+stem+'-驗證.json','--expected-items',str(plan['待處理項數'])]
    for name in newnames:args+=['--expected-new-card',name]
    for name in changed:args+=['--expected-changed-card',name]
    subprocess.run(args,cwd=ROOT,check=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('plan',type=Path);run(parser.parse_args().plan)
