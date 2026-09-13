import json
from fix_all_crops_2009 import exact_crops

with open("199管综真题_Markdown题库/2009年/ocr_cache.json") as f:
    cache = json.load(f)

q_lines = {q: [] for q in range(1, 58)}

for p in range(1, 13):
    lines = cache[str(p)]
    for l in lines:
        txt = l['text']
        # skip page headers / footers
        if "2009年真题" in txt or "绝密" in txt:
            continue
        ymid = (l['bbox'][1] + l['bbox'][3]) / 2.0
        
        # find which question contains this line
        matched = False
        for q, slices in exact_crops.items():
            for (sp, sy0, sy1) in slices:
                if sp == p and sy0 <= ymid <= sy1:
                    q_lines[q].append(txt)
                    matched = True
                    break
            if matched:
                break

for q in range(1, 58):
    print(f"Q{q:02d}: {len(q_lines[q])} lines | First: {q_lines[q][0] if q_lines[q] else 'EMPTY'}")
