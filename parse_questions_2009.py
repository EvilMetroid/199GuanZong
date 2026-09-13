import fitz, json, re

doc = fitz.open("真题部分/2009-2024年199管综真题合集.pdf")
with open("199管综真题_Markdown题库/2009年/ocr_cache.json") as f:
    cache = json.load(f)

# Flatten OCR lines with page numbers
all_ocr_lines = []
for p in range(1, 13):
    lines = cache[str(p)]
    for l in lines:
        all_ocr_lines.append((p, l['text'], l['bbox']))

print(f"Total OCR lines: {len(all_ocr_lines)}")
