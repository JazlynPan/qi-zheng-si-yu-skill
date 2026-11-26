"""執行：檢查65張試跑的六欄、一卡一去向、全庫不改卡，以及報告重跑一致性。"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/階段2試跑'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pdf', type=Path, required=True)
    args = ap.parse_args()
    paths = ['docs/卡片分類.tsv', 'qi-zheng-si-yu/references/variants.md',
             'docs/階段2試跑/字形對照證據.json', 'docs/階段2試跑/去重試跑.json',
             'docs/去重報告.md', 'docs/衝突清單.md', 'docs/階段2試跑/待核對明細.json',
             'docs/待人工核對清單.md', 'docs/階段2試跑/分類與保全檢查.json',
             'docs/階段2試跑/五星捷要便覽-試跑報告.md']
    before = {name: sha(ROOT/name) for name in paths}
    result = subprocess.run([sys.executable, 'tools/build_stage2_pilot.py', '--pdf', str(args.pdf)],
                            cwd=ROOT, check=True, text=True, capture_output=True)
    repeated = json.loads(result.stdout)
    after = {name: sha(ROOT/name) for name in paths}
    differences = [name for name in paths if before[name] != after[name]]
    assert not differences, differences
    with (ROOT/'docs/卡片分類.tsv').open(newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        assert reader.fieldnames == ['卡片檔名', '書名', '篇名', '類別', '去向', '重複於']
        rows = list(reader)
    assert len(rows) == len({r['卡片檔名'] for r in rows}) == 65
    assert all(r['去向'] in ['可搜尋', '圖表待核對', '待我決定'] for r in rows)
    assert all(r['類別'] in ['規則', '命例', '術語', '單句詩訣', '圖表待核對', '其他'] for r in rows)
    assert len((ROOT/'docs/卡片分類.tsv').read_text().splitlines()) == 66
    assert all(r['重複於'] == '' for r in rows)
    snapshot = json.loads((OUT/'基準快照.json').read_text())
    manifest = [{'卡片檔名': p.name, 'SHA256': sha(p)}
                for p in sorted((ROOT/'qi-zheng-si-yu/knowledge').glob('*.md'))]
    digest = hashlib.sha256(json.dumps(manifest, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    assert digest == snapshot['全庫檔名與SHA256彙總']
    assert len(manifest) == snapshot['全庫卡數'] == 20391
    assert repeated['原卡修改刪除新增'] == 0
    report = {'日期': snapshot['日期'], '證據等級': 'E0，分類格式、保全與重跑檢查',
              '試跑卡數': 65, '逐卡列數檢查通過': 65, '單一去向檢查通過': 65,
              '全庫卡數': len(manifest), '全庫卡片位元組異動': 0,
              '連跑兩次逐位元組相同輸出數': len(paths), '輸出差異': differences,
              '限制': '不等於所有類別已具代表性，不是全庫分類、原文語義驗收或E2盲評。'}
    (OUT/'試跑驗證.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
