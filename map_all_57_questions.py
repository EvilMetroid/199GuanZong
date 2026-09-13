import json, re

with open("199管综真题_Markdown题库/2009年/ocr_cache.json") as f:
    cache = json.load(f)

# Let's define the question start points explicitly:
# Each question has (page, start_line_idx, text_hint)
q_starts = {}

# Scan all lines
for p_idx in range(1, 13):
    lines = cache[str(p_idx)]
    for l_idx, l in enumerate(lines):
        txt = l['text']
        # check question pattern
        m = re.match(r'^(\d{1,2})[\.、．]', txt)
        if m:
            q_num = int(m.group(1))
            if 1 <= q_num <= 57 and q_num not in q_starts:
                q_starts[q_num] = (p_idx, l_idx, l['bbox'][1], txt)

# Missing questions manually located from inspection:
# Q16: p3, line 8 ("16.ai +a2+a+…. +a =↓")
if 16 not in q_starts:
    q_starts[16] = (3, 8, cache['3'][8]['bbox'][1], cache['3'][8]['text'])

# Q19: p3, line 18 ("有意义的一切的值,这个分式为一个定值.")
# Actually in p3, line 18 is Q19 stem
if 19 not in q_starts:
    q_starts[19] = (3, 18, cache['3'][18]['bbox'][1], "19.对于使分式有意义...")

# Q20: p3, line 22 ("a²-b2") -> stem of Q20
if 20 not in q_starts:
    q_starts[20] = (3, 22, cache['3'][22]['bbox'][1], "20.19a^2+9b^2=134")

# Q49: p9, between line 29 and line 30
# line 29 is Q48 (E) at y=484.56. Q49 stem begins around y=500.
if 49 not in q_starts:
    # We can set start y ~ 500 on p9
    q_starts[49] = (9, 30, 500.0, "49.张珊：不同于“刀”“枪”“箭”...")

print(f"Mapped {len(q_starts)} questions!")
for q in sorted(q_starts.keys()):
    p, l_idx, y0, txt = q_starts[q]
    print(f"Q{q:02d}: p{p}, y0={y0:.1f}, {txt[:30]}")
