import json, re

with open('199管综真题_Markdown题库/2025年/ocr_cache.json') as f:
    cache = json.load(f)

for qn in range(1, 58):
    found = []
    for p in range(len(cache)):
        for item in cache[str(p)]:
            txt = item['text'].strip()
            # Match question number start
            if re.match(rf'^{qn}\s*[\.、．]', txt) or re.match(rf'^第?\s*{qn}\s*小?题', txt):
                found.append((p, item['bbox'][1], item['bbox'][3], txt[:30]))
            elif qn in [39, 41, 44, 46, 51, 53] and f'{qn}～' in txt:
                found.append((p, item['bbox'][1], item['bbox'][3], txt[:30]))
    print(f"Q{qn:02d}: {found}")
