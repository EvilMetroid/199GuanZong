import json, fitz, re

doc = fitz.open("真题部分/2010年199管综真题.pdf")
with open("199管综真题_Markdown题库/2010年/ocr_cache.json") as f:
    cache = json.load(f)

q_starts = {}

# Match from OCR lines
for p in range(1, 13):
    lines = cache[str(p)]
    for l_idx, l in enumerate(lines):
        txt = l['text']
        m = re.match(r'^(\d{1,2})[\.、．\s]', txt)
        if m:
            qn = int(m.group(1))
            if 1 <= qn <= 57 and qn not in q_starts:
                q_starts[qn] = (p, l['bbox'][1], txt)

# Fix Q10
if 10 not in q_starts:
    # Page 2, starts around y=118
    q_starts[10] = (2, 118.0, "10. 已知直线 ax - by + 3 = 0...")

# Missing images previously: 14, 19, 49, 50
print("Mapped 2010 questions:", len(q_starts))
for q in range(1, 58):
    if q in q_starts:
        p, y0, txt = q_starts[q]
        print(f"Q{q:02d}: p{p}, y0={y0:.1f}, {txt[:30]}")
    else:
        print(f"Q{q:02d}: MISSING")
