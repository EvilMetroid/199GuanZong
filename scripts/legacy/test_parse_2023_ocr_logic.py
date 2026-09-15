import json, re

with open('199管综真题_Markdown题库/2023年/ocr_cache.json') as f:
    cache = json.load(f)

all_lines = []
for p in range(5, 16):
    for l in cache[str(p)]:
        t = l['text'].strip()
        # Clean footer
        if '2023年真题一第' in t:
            continue
        all_lines.append(t)

full_text = "\n".join(all_lines)
full_text = re.sub(r'三、逻辑推理：第26～55小题.*?请在答题卡上将所选项的字母涂黑。', '', full_text, flags=re.S)

writing_pos = full_text.find('四、写作')
if writing_pos != -1:
    logic_text = full_text[:writing_pos]
else:
    logic_text = full_text

# Handle shared stems
shared_stems = {
    (31, 32): r'31～32题基于以下题干：.*?(?=31[\.、．])',
    (37, 38): r'37～38题基于以下题干：.*?(?=37[\.、．])',
    (46, 47): r'46～47题基于以下题干：.*?(?=46[\.、．])',
    (54, 55): r'54～55题基于以下题干：.*?(?=54[\.、．])'
}

stem_texts = {}
for (q1, q2), pat in shared_stems.items():
    m = re.search(pat, logic_text, flags=re.S)
    if m:
        stem_texts[(q1, q2)] = m.group(0).strip()
        print(f"Found shared stem for Q{q1}~Q{q2}: length {len(stem_texts[(q1, q2)])}")
    else:
        print(f"MISSING shared stem for Q{q1}~Q{q2}")

q_found = {}
for qn in range(26, 56):
    # Match patterns like 26. 26． 26。
    m = re.search(rf'(?:^|\n)\s*{qn}\s*[\.、．。]', logic_text)
    if m:
        q_found[qn] = m.start()
    else:
        print(f"Missing anchor for Q{qn}")

print(f"Found {len(q_found)} / 30 logic questions in 2023!")

sorted_q = sorted(q_found.items(), key=lambda x: x[1])
logic_q_raw = {}
for idx, (qn, pos) in enumerate(sorted_q):
    next_pos = sorted_q[idx+1][1] if idx + 1 < len(sorted_q) else len(logic_text)
    raw = logic_text[pos:next_pos].strip()
    logic_q_raw[qn] = raw

# Test parsing options for each question
bad = 0
for qn in range(26, 56):
    txt = logic_q_raw[qn]
    opts = list(re.finditer(r'(?:^|\n|\s|\()[A-E][\.\)、．]', txt))
    labels = [re.sub(r'[^A-E]', '', m.group(0)) for m in opts]
    if len(labels) >= 5 and set(labels[-5:]) == {'A', 'B', 'C', 'D', 'E'}:
        pass
    else:
        print(f"Q{qn} options parsed: {labels}")
        bad += 1

print(f"Bad options count: {bad}")
