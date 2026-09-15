import json, re

with open('199管综真题_Markdown题库/2025年/ocr_cache.json') as f:
    cache = json.load(f)

# Combine OCR lines from page 4 to 18
all_lines = []
for p in range(4, 19):
    for l in cache[str(p)]:
        t = l['text'].strip()
        if '2025考研199管综真题' in t: continue
        all_lines.append(t)

full_text = '\n'.join(all_lines)
full_text = re.sub(r'三、逻辑推理：第 26～55 小题.*?请在答题卡上将所选项的字母涂黑。', '', full_text, flags=re.S)

writing_pos = full_text.find('四、写作')
logic_text = full_text[:writing_pos] if writing_pos != -1 else full_text

# Insert Q41 and Q53 anchors if missing
if '41.' not in logic_text and '41．' not in logic_text:
    # insert before 42
    pos42 = logic_text.find('42．')
    q41_text = '''41. 已知“■■■■”“■■■■”和“■■■■”是三组图形符号，其中有两组分别表示“春花开满园”和“满山梅花开”。\n根据以上信息，可知“■■”中两个相邻图形符号表示的汉字有（详见题图）。\nA. 春山\nB. 梅园\nC. 梅山\nD. 花园\nE. 山花\n'''
    logic_text = logic_text[:pos42] + q41_text + logic_text[pos42:]

if '53.' not in logic_text and '53．' not in logic_text:
    pos54 = logic_text.find('54．')
    q53_text = '''53. 若有一题 3 人均答对了，有一题 3 人均答错了，则以下哪项一定是错误的？\nA. 小李第 3 题答对了。\nB. 小王第 2 题答对了。\nC. 小王第 3 题答错了。\nD. 小文第 2 题答错了。\nE. 小文第 4 题答对了。\n'''
    logic_text = logic_text[:pos54] + q53_text + logic_text[pos54:]

q_found = {}
for qn in range(26, 56):
    m = re.search(rf'(?:^|\n)\s*{qn}\s*[\.、．。]', logic_text)
    if m:
        q_found[qn] = m.start()
    else:
        print(f"Missing Q{qn}")

print(f"Mapped {len(q_found)} / 30 questions!")

sorted_q = sorted(q_found.items(), key=lambda x: x[1])
logic_q_raw = {}
for idx, (qn, pos) in enumerate(sorted_q):
    next_pos = sorted_q[idx+1][1] if idx + 1 < len(sorted_q) else len(logic_text)
    logic_q_raw[qn] = logic_text[pos:next_pos].strip()

pat = r'(?:^|\n|\s|[（(])([A-E])(?:[）\)\.、．]|\s)'
bad = 0
for qn in range(26, 56):
    txt = logic_q_raw[qn]
    matches = list(re.finditer(pat, txt))
    labels = [m.group(1) for m in matches]
    if len(labels) >= 5 and set(labels[-5:]) == {'A', 'B', 'C', 'D', 'E'}:
        pass
    else:
        print(f"Q{qn} options parsed: {labels}")
        bad += 1

print(f"Bad options count: {bad}")
