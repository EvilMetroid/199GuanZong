import fitz, re, json

doc = fitz.open("真题部分/2009-2024年199管综真题合集.pdf")
pages_text = [doc[p].get_text() for p in range(4, 13)]
all_text = "\n".join(pages_text)

# Clean out footers
all_text = re.sub(r'2009\s*年真题[^\n]*\n', '', all_text)

# Locate question start positions
q_positions = {}
for q in range(26, 58):
    m = re.search(rf'(?:^|\n)\s*{q}[\.、．]', all_text)
    if m:
        q_positions[q] = m.start()

sorted_qs = sorted(q_positions.keys())
parsed_logic = {}

for i, q in enumerate(sorted_qs):
    start = q_positions[q]
    end = q_positions[sorted_qs[i+1]] if i+1 < len(sorted_qs) else len(all_text)
    raw = all_text[start:end].strip()
    
    # Remove leading question number like "26."
    raw = re.sub(r'^\d{1,2}[\.、．]\s*', '', raw)
    
    if q in [56, 57]:
        parsed_logic[q] = {"stem": raw, "options": {}}
        continue
        
    # Find options A-E
    # Options can be: （A） (A) A. A) A． etc
    opt_matches = list(re.finditer(r'(?:^|\n|\s)[（\(（]?([A-E])[）\)\.、．]\s*', raw))
    
    # If found at least 4 options
    if len(opt_matches) >= 4:
        # Sort matches by position
        stem = raw[:opt_matches[0].start()].strip()
        opts = {}
        for j, om in enumerate(opt_matches):
            letter = om.group(1).upper()
            opt_start = om.end()
            opt_end = opt_matches[j+1].start() if j+1 < len(opt_matches) else len(raw)
            opt_val = raw[opt_start:opt_end].strip()
            # clean newlines inside option
            opt_val = re.sub(r'\s*\n\s*', '', opt_val)
            opts[letter] = opt_val
        parsed_logic[q] = {"stem": stem, "options": opts}
    else:
        parsed_logic[q] = {"stem": raw, "options": {}}

for q in range(26, 58):
    data = parsed_logic[q]
    opt_keys = list(data["options"].keys())
    print(f"Q{q:02d}: stem_len={len(data['stem']):3d}, opts={opt_keys}")
