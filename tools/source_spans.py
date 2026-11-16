#!/usr/bin/env python3
"""閱讀用：供提煉開發腳本按已人工確認的原文錨點定位PDF頁碼；不自行判讀概念。"""
import bisect
from pathlib import Path


class Source:
    def __init__(self, path):
        pages = Path(path).read_text().split('\f')
        if not pages[-1].strip(): pages.pop()
        self.pages, self.offsets = [], []
        position = 0
        for page in pages:
            text = ''.join(line.strip() for line in page.splitlines() if line.strip()
                           and not line.strip().isdigit()
                           and not line.strip().startswith(('如果有', '站 id')))
            self.offsets.append(position)
            self.pages.append(text)
            position += len(text)
        self.text = ''.join(self.pages)

    def extract(self, start, end=None, first=1, last=None):
        last = last or len(self.pages)
        left = self.offsets[first-1]
        right = self.offsets[last] if last < len(self.pages) else len(self.text)
        a = self.text.index(start, left, right)
        b = self.text.index(end, a+len(start), right) if end else right
        return self.text[a:b], bisect.bisect_right(self.offsets, a), bisect.bisect_right(self.offsets, b-1)
