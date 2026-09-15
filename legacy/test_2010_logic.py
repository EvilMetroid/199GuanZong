import fitz, re, json

doc = fitz.open("真题部分/2010年199管综真题.pdf")
pages_text = [doc[p].get_text() for p in range(4, 13)]
all_text = "\n".join(pages_text)
all_text = re.sub(r'2010\s*年真题[^\n]*\n', '', all_text)

# Q26 to Q57 positions
q_positions = {}
for q in range(26, 58):
    m = re.search(rf'(?:^|\n)\s*{q}[\.、．\s]', all_text)
    if m:
        q_positions[q] = m.start()

sorted_qs = sorted(q_positions.keys())

def normalize_options(raw):
    t = re.sub(r'(?:^|\n|\s|[。？?；;∶:])[（\(]+([A-E])[）\)\>、．]?', r'\n\1. ', raw)
    t = re.sub(r'(?:^|\n|\s|[。？?；;∶:])([A-E])[）\)\>、．]\s*', r'\n\1. ', t)
    return t

parsed_qs = {}
for i, q in enumerate(sorted_qs):
    start = q_positions[q]
    end = q_positions[sorted_qs[i+1]] if i+1 < len(sorted_qs) else len(all_text)
    raw = all_text[start:end].strip()
    raw = re.sub(r'^\d{1,2}[\.、．\s]\s*', '', raw)
    
    if q in [56, 57]:
        parsed_qs[q] = {"stem": raw, "options": {}}
        continue
        
    norm_text = normalize_options(raw)
    opt_parts = list(re.finditer(r'(?:^|\n)\s*([A-E])\.\s*(.*?)(?=(?:\n\s*[A-E]\.|\Z))', norm_text, re.DOTALL))
    if len(opt_parts) >= 4:
        stem_part = norm_text[:opt_parts[0].start()].strip()
        opts = {}
        for m in opt_parts:
            letter = m.group(1).upper()
            val = m.group(2).strip()
            val = re.sub(r'\s*\n\s*', '', val)
            opts[letter] = val
        parsed_qs[q] = {"stem": stem_part, "options": opts}
    else:
        parsed_qs[q] = {"stem": raw, "options": {}}

for q in range(26, 56):
    opts = list(parsed_qs[q]["options"].keys())
    print(f"Q{q:02d}: opts={opts}")

missing = [q for q in range(26, 56) if len(parsed_qs[q]["options"]) < 5]
print("Missing < 5 options:", missing)
