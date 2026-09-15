import json, re

with open('199管综真题_Markdown题库/2022年/ocr_cache.json') as f:
    cache = json.load(f)

# Combine OCR lines from page 3 to 9
all_lines = []
for p in range(3, 10):
    for l in cache[str(p)]:
        t = l['text'].strip()
        # Fix missing Q28 line in OCR
        if '5个节目中选择了3个节目观看' in t and not any('28.退休' in x for x in all_lines):
            all_lines.append('28.退休在家的老王今晚在“焦点访谈”“国家记忆”“自然传奇”“人物故事”“纵横中国”这')
        all_lines.append(t)

full_text = "\n".join(all_lines)
full_text = re.sub(r'三、逻辑推理：第26-55小题.*?只有一项是符合试题要求的。', '', full_text, flags=re.S)

writing_pos = full_text.find('四、写作')
logic_text = full_text[:writing_pos]

q_found = {}
for qn in range(26, 56):
    pattern = rf'(?:^|\n)\s*{qn}\s*[\.、．]'
    m = re.search(pattern, logic_text)
    if m:
        q_found[qn] = m.start()
    else:
        print(f"Missing Q{qn}")

print(f"Mapped {len(q_found)} / 30 logic questions in 2022 OCR!")

sorted_q = sorted(q_found.items(), key=lambda x: x[1])
logic_q_raw = {}
for idx, (qn, pos) in enumerate(sorted_q):
    next_pos = sorted_q[idx+1][1] if idx + 1 < len(sorted_q) else len(logic_text)
    logic_q_raw[qn] = logic_text[pos:next_pos].strip()

# Check options
bad = 0
for qn in range(26, 56):
    txt = logic_q_raw[qn]
    # match A. B. C. D. E. or A、 B、
    opts = list(re.finditer(r'(?:^|\n|\s)([A-E])[\.、．]', txt))
    labels = [m.group(1) for m in opts]
    if len(labels) >= 5 and set(labels[-5:]) == {'A', 'B', 'C', 'D', 'E'}:
        pass
    else:
        print(f"Q{qn} options: {labels}")
        bad += 1

if bad == 0:
    print("ALL Q26-Q55 logic options found cleanly!")
