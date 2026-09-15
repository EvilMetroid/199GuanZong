import json, re

with open("199管综真题_Markdown题库/2010年/ocr_cache.json") as f:
    cache = json.load(f)

from build_2010_flawless import exact_crops_2010

q_lines = {q: [] for q in range(1, 58)}

for p in range(1, 13):
    lines = cache[str(p)]
    for l in lines:
        txt = l['text']
        if "2010年真题" in txt or "绝密" in txt: continue
        ymid = (l['bbox'][1] + l['bbox'][3]) / 2.0
        for q, slices in exact_crops_2010.items():
            matched = False
            for (sp, sy0, sy1) in slices:
                if sp == p and sy0 <= ymid <= sy1:
                    q_lines[q].append(txt)
                    matched = True
                    break
            if matched:
                break

for q in range(1, 58):
    print(f"Q{q:02d}: {len(q_lines[q]):2d} lines | {q_lines[q][0] if q_lines[q] else 'EMPTY'}")
