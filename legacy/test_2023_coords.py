import json

with open('199管综真题_Markdown题库/2023年/ocr_cache.json') as f:
    cache = json.load(f)

for p in range(1, 17):
    print(f"--- PAGE {p} ---")
    for item in cache[str(p)]:
        t = item['text']
        y0, y1 = item['bbox'][1], item['bbox'][3]
        print(f"{y0:5.1f} - {y1:5.1f}: {t[:50]}")
