import fitz, re

doc = fitz.open('真题部分/2022年199管综真题.pdf')

for pno in range(len(doc)):
    page = doc[pno]
    blocks = page.get_text('blocks')
    blocks.sort(key=lambda b: (b[1], b[0]))
    print(f"=== PAGE {pno} ===")
    for b in blocks:
        t = b[4].strip().replace('\n', ' ')
        m = re.match(r'^([一二三四]、|\d{1,2}|[Ss]4)[\.、．\s]', t)
        if m or '基于以下题干' in t:
            print(f"  [{b[1]:.1f}, {b[3]:.1f}]: {t[:60]}")
