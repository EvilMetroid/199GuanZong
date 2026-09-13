import fitz, re, json

doc = fitz.open('真题部分/2020年199管综真题.pdf')
full_text = ''
for p in range(4, 13):
    full_text += f'\n<<<PAGE_{p}>>>\n' + doc[p].get_text()

full_text = re.sub(r'2020年真题－第\d+页（共31\s*页）', '', full_text)
full_text = re.sub(r'三、逻辑推理：第26~55小题.*?请在答庭卡上将所选项的字母涂黑。', '', full_text, flags=re.S)

# Normalize typos
full_text = re.sub(r'S4\s*[\.、．]', '54．', full_text)
full_text = re.sub(r'so\s*移动互联网时代', '50．移动互联网时代', full_text)
full_text = re.sub(r'48\.1818', '48．1818', full_text)

# Ensure dots after question numbers
for qn in [30, 34, 35, 38, 41, 55]:
    full_text = re.sub(rf'(?:^|\n)\s*{qn}(?=[^\d\.\、\．])', f'\n{qn}．', full_text)

# Also fix the multi-question group markers
full_text = full_text.replace('31-32题基千以下题干：', '31～32题基于以下题干：\n')
full_text = full_text.replace('37-38题基于以下题干：', '37～38题基于以下题干：\n')
full_text = full_text.replace('46-47题基于以下题干：', '46～47题基于以下题干：\n')
full_text = full_text.replace('54-55题基千以下题干：', '54～55题基于以下题干：\n')

# Split by questions 26..55
writing_start = full_text.find('四、写作')
logic_text = full_text[:writing_start]

q_splits = {}
for qn in range(26, 56):
    pattern = rf'(?:^|\n)\s*{qn}．'
    m = re.search(pattern, logic_text)
    if m:
        q_splits[qn] = m.start()
    else:
        print(f"Failed to find Q{qn}")

print(f"Mapped {len(q_splits)} logic questions")

sorted_q = sorted(q_splits.items(), key=lambda x: x[1])
logic_questions = {}

for idx, (qn, pos) in enumerate(sorted_q):
    next_pos = sorted_q[idx+1][1] if idx + 1 < len(sorted_q) else len(logic_text)
    block = logic_text[pos:next_pos].strip()
    logic_questions[qn] = block

def extract_opts(txt):
    clean = re.sub(r'<<<PAGE_\d+>>>', '', txt)
    opt_matches = list(re.finditer(r'[\(（]([A-E])[\)）]', clean))
    opts = {}
    if len(opt_matches) >= 5:
        # Check the last 5 matches
        last_5 = opt_matches[-5:]
        labels = [m.group(1) for m in last_5]
        if set(labels) == {'A', 'B', 'C', 'D', 'E'}:
            first_opt_start = last_5[0].start()
            stem = clean[:first_opt_start].strip().replace('\n', ' ')
            for i in range(5):
                start = last_5[i].end()
                end = last_5[i+1].start() if i < 4 else len(clean)
                opts[last_5[i].group(1)] = clean[start:end].strip().replace('\n', ' ')
            return stem, opts
    return clean, {}

all_good = True
for qn in range(26, 56):
    stem, opts = extract_opts(logic_questions[qn])
    if len(opts) != 5:
        print(f"Q{qn} bad options count: {len(opts)}")
        print(logic_questions[qn][:200])
        all_good = False
    else:
        # print first option and last option
        print(f"Q{qn}: OK! stem len={len(stem)}, A={opts['A'][:20]}..., E={opts['E'][:20]}...")

if all_good:
    print("\nSUCCESS: ALL 30 logic questions (Q26-Q55) have exactly 5 options!")
