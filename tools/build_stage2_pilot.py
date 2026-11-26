"""執行：依人工判讀檔產生單本分類及試跑報告，不改卡、不跑全庫分類。

目錄：引用解析／字串對照／單本分類／相似候選群／試跑報告／保全檢查。
原PDF只用來核對三個字形短語；分類依據只有卡名與四欄。
"""
import argparse
import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
import re
import unicodedata
import fitz
from stage2_preflight import parse, FIELDS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/階段2試跑'
K = ROOT / 'qi-zheng-si-yu/knowledge'
BOOK = '五星捷要便覽'
HEAD = re.compile(r'^《([^》]+)》([^\n]*)$', re.M)
CLASSES = ['規則', '命例', '術語', '單句詩訣', '圖表待核對', '其他']
DESTS = ['可搜尋', '圖表待核對', '待我決定']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def blocks(value):
    heads = list(HEAD.finditer(value))
    return [{'書名': m[1], '題頭': m[0], '尾部': m[2],
             '文字': value[m.end():heads[i + 1].start() if i + 1 < len(heads) else len(value)].strip()}
            for i, m in enumerate(heads)]


def payload(value):
    return '\n'.join(line for line in value.splitlines()
                     if line.strip() and not HEAD.fullmatch(line)
                     and line.strip() not in ['原文未提及', '無', '原文以圖表呈現'])


def norm(value, replacements):
    for a, b in replacements:
        value = value.replace(a, b)
    value = unicodedata.normalize('NFC', value)
    return ''.join(c for c in value if not c.isspace() and not unicodedata.category(c).startswith('P'))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pdf', type=Path, required=True, help='本機原PDF；不會複製到倉庫')
    args = ap.parse_args()
    snapshot = json.loads((OUT / '基準快照.json').read_text())
    plan = json.loads((OUT / '五星捷要便覽-人工判讀.json').read_text())
    raw_pdf = args.pdf.read_bytes()
    expected_pdf = '380da244ad1fdc619a28144557e376f8e9f936329ac9d742bbddd2b9013de09e'
    assert sha(raw_pdf) == expected_pdf, '原PDF與帳本雜湊不同，停止，不套用字形證據'
    pdf = fitz.open(stream=raw_pdf, filetype='pdf')
    assert len(pdf) == 15
    all_manifest, selected = [], {}
    for p in sorted(K.glob('*.md')):
        raw = p.read_bytes()
        all_manifest.append({'卡片檔名': p.name, 'SHA256': sha(raw)})
        text = raw.decode()
        if f'《{BOOK}》' in text:
            fields, sources, repeated = parse(text)
            assert not repeated and all(fields.get(f) for f in FIELDS)
            assert text.splitlines()[0] == '#七政四餘'
            selected[p.name] = {'原文': text, '欄位': fields, '來源': sources, 'SHA256': sha(raw)}
    digest = sha(json.dumps(all_manifest, ensure_ascii=False, separators=(',', ':')).encode())
    assert len(all_manifest) == snapshot['全庫卡數'] and digest == snapshot['全庫檔名與SHA256彙總']
    manual = {r['卡片檔名']: r for r in plan['明細']}
    assert len(manual) == len(plan['明細']) == 65 and set(manual) == set(selected)
    rows, source_issues = [], []
    for name, card in sorted(selected.items()):
        decision = manual[name]
        assert card['SHA256'] == decision['SHA256']
        assert decision['類別'] in CLASSES and decision['去向'] in DESTS
        evidence = decision['依據原文片段']
        assert ''.join(evidence.split()) in ''.join(card['欄位'][decision['判讀依據欄']].split())
        cited = [b for f in FIELDS for b in blocks(card['欄位'][f])]
        books = sorted({b['書名'] for b in cited})
        chapters = sorted({b['書名'] + '：' + m[1] for b in cited
                           if (m := re.search(r'[〈“「]([^〉”」]+)[〉”」]', b['尾部']))})
        own = [b for b in cited if b['書名'] == BOOK]
        paged = any(re.search(r'第\s*\d+[^\n]*頁', b['尾部']) for b in own)
        assert paged == decision['本書頁碼已列']
        rows.append({'卡片檔名': name, '書名': '；'.join(books),
                     '篇名': '；'.join(chapters) or '原卡未標示篇名',
                     '類別': decision['類別'], '去向': decision['去向'], '重複於': ''})
        if not paged:
            source_issues.append({'卡片': name, '問題': '卡有本書引註，但未列本書PDF頁碼',
                                  '本書題頭': list(dict.fromkeys(b['題頭'] for b in own)),
                                  '其他來源已列定位數': sum(s[0] != BOOK for s in card['來源']),
                                  '處理': '暫待決定；不宣稱其他書定位一併失效，不補造頁碼'})
    with (ROOT / 'docs/卡片分類.tsv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['卡片檔名', '書名', '篇名', '類別', '去向', '重複於'], delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

    variants = [
        {'原PDF頁': 10, '原PDF短語': '余仿此', '卡片': '生彼助我.md', '卡片短語': '餘仿此'},
        {'原PDF頁': 12, '原PDF短語': '闲宫', '卡片': '命限政餘吉凶.md', '卡片短語': '閒宮'},
        {'原PDF頁': 11, '原PDF短語': '刑克', '卡片': '孤克淫賤.md', '卡片短語': '刑剋'},
    ]
    for v in variants:
        original = ''.join(pdf[v['原PDF頁'] - 1].get_text().split())
        assert v['原PDF短語'] in original
        assert v['卡片短語'] in selected[v['卡片']]['原文']
    dump(OUT / '字形對照證據.json', {'日期': '2026-11-26', '書名': BOOK, '原PDF_SHA256': expected_pdf, '明細': variants})
    refdir = ROOT / 'qi-zheng-si-yu/references'
    refdir.mkdir(exist_ok=True)
    vmd = ['# 字形對照：單本試跑證據', '',
           '目前只核對《五星捷要便覽》三個同句短語。原PDF為整理版簡體文字層，以下保留文件原字，與既有繁體卡片逐句對照；不宣稱已核原刻版本。', '',
           '|原PDF短語|卡片短語|PDF實際頁|卡片|', '|---|---|---|---|']
    for v in variants:
        vmd.append(f'|{v["原PDF短語"]}|{v["卡片短語"]}|{v["原PDF頁"]}|[卡片](../knowledge/{v["卡片"]})|')
    vmd += ['', '[原PDF雜湊與字位證據](../../docs/階段2試跑/字形對照證據.json)。', '',
            '本次只提供完整短語層級的證據，不把單字一律當成等價字，也不把本表作為全庫簡體字豁免清單。',
            '未收錄財／才、氣／炁等缺乏本輪同句核對證據的組合；分類及候選比較不修改卡片原字。',
            '正式搜尋工具尚未建立；此檔不代表目前Skill已可檢索或回答。']
    (refdir / 'variants.md').write_text('\n'.join(vmd) + '\n')

    replacements = [(v['原PDF短語'], v['卡片短語']) for v in variants]
    texts = {name: norm('\n'.join(payload(c['欄位'][f]) for f in FIELDS), replacements)
             for name, c in selected.items()}
    exact = defaultdict(list)
    for name, c in selected.items():
        if manual[name]['本書頁碼已列']:
            exact[(tuple(c['來源']), texts[name])].append(name)
    agroups = [names for names in exact.values() if len(names) > 1]
    # 本次只列候選，不執行刪除；A組若出現，須重新檢視來源缺載及使用者確認。
    assert not agroups, '本批出現新的完全重複候選，先人工檢視，不自選刪除'
    shingles = {n: {t[i:i + 5] for i in range(max(1, len(t) - 4))} for n, t in texts.items()}
    adjacent = {n: set() for n in selected}
    edges = []
    for a, b in itertools.combinations(sorted(selected), 2):
        union = shingles[a] | shingles[b]
        similarity = len(shingles[a] & shingles[b]) / len(union) if union else 1.0
        if similarity > .85:
            adjacent[a].add(b)
            adjacent[b].add(a)
            edges.append({'卡片1': a, '卡片2': b, '五字片段Jaccard相似度': round(similarity, 6)})
    seen, groups = set(), []
    for n in sorted(selected):
        if n in seen:
            continue
        stack, group = [n], []
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            group.append(node)
            stack.extend(sorted(adjacent[node] - seen))
        if len(group) > 1:
            groups.append(sorted(group))
    b_examples = []
    for name, a, b in [('劫掠陣亡.md', ('張果星宗', '348'), ('增訂天官五星集腋', '290')),
                        ('流落凶死.md', ('張果星宗', '348'), ('增訂天官五星集腋', '289'))]:
        bs = blocks(selected[name]['欄位']['使用規則'])
        ca = next(x for x in bs if x['書名'] == a[0] and a[1] in x['尾部'])
        cb = next(x for x in bs if x['書名'] == b[0] and b[1] in x['尾部'])
        assert norm(ca['文字'], replacements) == norm(cb['文字'], replacements)
        b_examples.append({'卡片': name, '來源1': ca['題頭'], '來源2': cb['題頭'],
                           '原卡引句1': ca['文字'], '原卡引句2': cb['文字'],
                           '限制': '原卡內兩書引文同文的示例，不是兩本原PDF逐字驗收或全庫B類統計'})
    duplicates = {'範圍': '只試跑65張，不是全庫', '節點數': 65, '門檻': .85,
                  '比較方式': '移除來源題頭及缺載標記後，僅套三個已核短語，去標點空白，五字片段Jaccard連邊及相連群；不是語義等同判定',
                  '邊': edges, '候選群': groups, 'A類已發現候選': agroups,
                  'C類純圖表指標': [r['卡片檔名'] for r in rows if r['類別'] == '圖表待核對'],
                  'B類同卡多書同文示例': b_examples, '刪除數': 0}
    dump(OUT / '去重試跑.json', duplicates)
    dmd = ['# 去重報告：單本試跑', '', '範圍：《五星捷要便覽》65張卡，不是全庫結果；本次不刪卡。', '',
           f'- A類完全重複候選：{len(agroups)}組。', f'- 文字相似連邊：{len(edges)}條；相連候選群：{len(groups)}組。',
           '- C類純圖表指標：0張；有文字內容的卡不因核心概念缺載就當空殼。',
           '- D類同名不同義的跨檔候選：本次未確認；不把同卡內用語差異直接算成D類。',
           '- B類：以下只列兩個已核對的同卡多書引句示例，未窮舉整庫；不刪、不合併。', '', '|卡片|兩書出處|', '|---|---|']
    for b in b_examples:
        dmd.append(f'|{b["卡片"]}|{b["來源1"]}／{b["來源2"]}|')
    dmd += ['', '[字串、來源與候選群明細](階段2試跑/去重試跑.json)。原卡內同段重複不符合跨檔刪除定義，仍維持原樣。']
    (ROOT / 'docs/去重報告.md').write_text('\n'.join(dmd) + '\n')

    core = selected['朝君.md']['欄位']['核心概念']
    assert '命主與太陽同垣' in core and '命主星與日月同宮者是' in core and '命主星與日同宮者是' in core
    (ROOT / 'docs/衝突清單.md').write_text('''# 衝突清單：單本試跑候選

本次只有1個待判候選，不宣稱已確認衝突，不替任何書選邊。

## S2-C01：朝君（日／日月）

|來源|卡片所載說法|
|---|---|
|《五星捷要便覽》；原卡未列本書PDF頁碼|朝君：命主與太陽同垣。太陽為君，主星為命主星。|
|《三臺星平命書正宗》第95頁|主星朝君：命主星與日月同宮者是。|
|《司臺曆數袖裡璇璣》第117頁|主星朝君：命主星與日同宮者是。|

來源：[朝君卡](../qi-zheng-si-yu/knowledge/朝君.md)的核心概念欄。
候選類型：取法範圍差異待判。「日／日月」也可能只是傳錄漏字，只有文字小異不算已確認衝突。
需要使用者判斷是否為實質取法不同；本輪不回寫卡片，不自行融合或更正。

反例：[命限政餘吉凶卡](../qi-zheng-si-yu/knowledge/命限政餘吉凶.md)先說日子月午失所，再附躔虛、張升殿的條件。
這是條件不同，不以相反吉凶字句就判為衝突；本輪沒有將其列入衝突項。
''')
    issues = {'本書引用缺頁碼': source_issues,
              '欄內重複提醒': '19張有本書頁碼的卡中，前後原文段落重複屬欄內問題，不當作兩張卡刪除。',
              '例子欄待核': ['生彼助我.md', '財帛田宅入庫.md'],
              '例子欄原因': '與使用規則的文字經過縮接或重整；仍需逐句核原頁是否符合原文照錄，本輪不修卡。',
              '分類代表性': '本次沒有以單一命例、單句詩訣或圖表空殼為主要用途的卡，不能宣稱已測過全部類型。'}
    dump(OUT / '待核對明細.json', issues)
    qmd = ['# 待人工核對清單：單本試跑', '',
           '46張卡的《五星捷要便覽》引用未列本書頁碼；其他書可有有效頁碼，不能說成整卡無出處。',
           '分類表暫列待我決定，讓使用者決定整卡暫緩，或後續按來源段限制引用；不是新增永久排除規則。', '',
           '|卡片|本書題頭|其他書已列定位數|', '|---|---|---|']
    for issue in source_issues:
        qmd.append(f'|{issue["卡片"]}|'+ '；'.join(issue['本書題頭'])+f'|{issue["其他來源已列定位數"]}|')
    qmd += ['', '另有兩張例子欄文字重整待核：生彼助我、財帛田宅入庫；只列問題，不改卡。',
            '本次不把「例子欄有內容」自動當成整張命例；術語卡可含具名例子，如何在後續索引標記另待確認。',
            '[逐卡來源問題](階段2試跑/待核對明細.json)。']
    (ROOT / 'docs/待人工核對清單.md').write_text('\n'.join(qmd) + '\n')

    counts = Counter(r['類別'] for r in rows)
    dests = Counter(r['去向'] for r in rows)
    report = {'日期': snapshot['日期'], '基準提交': snapshot['基準提交'], '試跑書': BOOK,
              '全庫卡片數': len(all_manifest), '試跑卡片數': len(rows), '未做分類的其他卡': len(all_manifest)-len(rows),
              '全部試跑卡恰好一列一去向': len({r['卡片檔名'] for r in rows}) == len(rows),
              '類別數': {c: counts[c] for c in CLASSES}, '去向數': {d: dests[d] for d in DESTS},
              '本書引用缺頁碼數': len(source_issues), '字形同句對照數': len(variants),
              '原PDF頁數與雜湊核對': True, '原卡修改刪除新增': 0, '全庫檔名與SHA256彙總': digest,
              '原文語義驗收': '未執行；不把E0結構及保全檢查說成全庫逐字複核',
              '全庫分類完成': False}
    dump(OUT / '分類與保全檢查.json', report)
    md = ['# 階段2單本試分類：《五星捷要便覽》', '', '## 目錄', '',
          '- [範圍與結果](#範圍與結果)', '- [逐卡分類](#逐卡分類)', '- [需要使用者決定](#需要使用者決定)', '',
          '## 範圍與結果', '',
          '共65張：書名引註有頁碼19張、未列本書頁碼46張。不能只篩有頁碼引用而漏掉46張。',
          '術語38、規則27；可搜尋19、待我決定46。其餘20,326張尚未做本次分類；全庫卡片20,391張完全未動。',
          '機械解析完整四欄；人工依卡名、完整核心定義、規則代表句及例子特徵暫分，未逐字回PDF驗收全部330,593字。',
          '多來源長卡、缺本書頁碼及假設例／具名例混合，是本次試跑的主要問題；不以核心概念原文未提及就當空殼。', '',
          '[六欄TSV](../卡片分類.tsv)；[逐卡人工依據](五星捷要便覽-人工判讀.json)；[保全檢查](分類與保全檢查.json)。', '',
          '## 逐卡分類', '', '|卡片|類別|去向|', '|---|---|---|']
    for row in rows:
        md.append(f'|[ {row["卡片檔名"]} ](../../qi-zheng-si-yu/knowledge/{row["卡片檔名"]})|{row["類別"]}|{row["去向"]}|')
    md += ['', '## 需要使用者決定', '',
           '1. 是否同意先按主要用途分成術語38、規則27？術語內的原例暫不改成單獨命例、不拆卡。',
           '2. 本書頁碼缺載46張：先整卡待決，還是後續只限制缺頁來源、保留其他已載頁碼的來源可搜尋？',
           '3. 本書沒有獨立命例、單句詩訣、圖表空殼的試跑案例，其他類型尚未驗證；不為湊數分類。', '',
           '[去重試跑](../去重報告.md)；[衝突候選](../衝突清單.md)；[待人工核對](../待人工核對清單.md)；[參考專案差異](參考專案核對.md)。',
           '依既有規格先單本試跑，確認後才跑全庫；階段1.5未決項仍保留，不代表已驗收，也未同意104份補卡。']
    (OUT / '五星捷要便覽-試跑報告.md').write_text('\n'.join(md) + '\n')
    # 最後再次核對全庫位元組：分類、圖文及參考檔輸出均不能改卡。
    after = [{'卡片檔名': p.name, 'SHA256': sha(p.read_bytes())} for p in sorted(K.glob('*.md'))]
    assert after == all_manifest
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
