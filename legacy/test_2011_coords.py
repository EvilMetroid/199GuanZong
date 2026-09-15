import json, fitz, re

with open("199管综真题_Markdown题库/2011年/ocr_cache.json") as f:
    cache = json.load(f)

# Find questions start y
q_starts = {}
for p in range(1, 14):
    lines = cache[str(p)]
    for l in lines:
        txt = l['text']
        m = re.match(r'^(\d{1,2})[\.、．\s]', txt)
        if m:
            qn = int(m.group(1))
            if 1 <= qn <= 57 and qn not in q_starts:
                q_starts[qn] = (p, l['bbox'][1])

# Fix manually located Q8 and Q23
q_starts[8] = (1, 545.0)
q_starts[23] = (3, 275.0)

print(f"2011 mapped questions: {len(q_starts)} / 57")
