import fitz, re

doc = fitz.open("真题部分/2009-2024年199管综真题合集.pdf")

# For each page 1..12, extract lines with (y0, y1, text)
page_lines = {}
for p in range(1, 13):
    page = doc[p]
    lines = []
    # get text as words or lines
    text_page = page.get_text("words")
    # Alternatively get_text("blocks")
    blocks = page.get_text("blocks")
    for b in blocks:
        if b[6] == 0: # text block
            b_text = b[4].strip()
            lines.append({'y0': b[1], 'y1': b[3], 'x0': b[0], 'x1': b[2], 'text': b_text})
    lines.sort(key=lambda x: x['y0'])
    page_lines[p] = lines

print("Pages loaded:", len(page_lines))
for p in range(1, 13):
    print(f"--- Page {p} ---")
    for item in page_lines[p]:
        first_line = item['text'].split('\n')[0]
        if any(c in first_line for c in ['1','2','3','4','5','6','7','8','9','一、','二、','三、','四、']) and len(first_line) < 40:
            print(f"  y0={item['y0']:.1f}, y1={item['y1']:.1f}: {first_line}")

