import json, re

with open('199管综真题_Markdown题库/2025年/ocr_cache.json') as f:
    cache = json.load(f)

all_lines = []
for p in range(4, 19):
    for l in cache[str(p)]:
        t = l['text'].strip()
        if '2025考研199管综真题' in t: continue
        all_lines.append(t)

full_text = '\n'.join(all_lines)
full_text = re.sub(r'三、逻辑推理：第26～55小题.*?请在答题卡上将所选项的字母涂黑。', '', full_text, flags=re.S)

writing_pos = full_text.find('四、写作')
logic_text = full_text[:writing_pos] if writing_pos != -1 else full_text

# Let's check anchors
q_found = {}
for qn in range(26, 56):
    m = re.search(rf'(?:^|\n)\s*{qn}\s*[\.、．。]', logic_text)
    if m:
        q_found[qn] = m.start()
    else:
        print(f"Missing anchor for Q{qn}")

print(f"Found {len(q_found)} / 30 logic questions in 2025!")
