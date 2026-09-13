import fitz, re

doc = fitz.open("真题部分/2009-2024年199管综真题合集.pdf")
pages_text = [doc[p].get_text() for p in range(4, 13)]
all_text = "\n".join(pages_text)

# Split by question numbers
# 26. to 57.
q_texts = {}
for q in range(26, 58):
    pattern = rf'(?:^|\n)\s*{q}[\.、．]'
    m = re.search(pattern, all_text)
    if m:
        q_texts[q] = m.start()
    else:
        print(f"Missing Q{q}")

sorted_qs = sorted(q_texts.keys())
q_chunks = {}
for i, q in enumerate(sorted_qs):
    start = q_texts[q]
    end = q_texts[sorted_qs[i+1]] if i+1 < len(sorted_qs) else len(all_text)
    chunk = all_text[start:end].strip()
    q_chunks[q] = chunk

print(f"Found {len(q_chunks)} logic/writing question chunks from PDF text!")
for q in [26, 27, 28, 49, 50, 56, 57]:
    print(f"=== Q{q} ===")
    print(q_chunks[q][:150])
