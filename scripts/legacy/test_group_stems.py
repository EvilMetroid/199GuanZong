import fitz, re

doc = fitz.open('真题部分/2020年199管综真题.pdf')
full_text = ''
for p in range(4, 13):
    full_text += f'\n<<<PAGE_{p}>>>\n' + doc[p].get_text()

full_text = re.sub(r'2020年真题－第\d+页（共31\s*页）', '', full_text)
full_text = re.sub(r'三、逻辑推理：第26~55小题.*?请在答庭卡上将所选项的字母涂黑。', '', full_text, flags=re.S)

full_text = re.sub(r'S4\s*[\.、．]', '54．', full_text)
full_text = re.sub(r'so\s*移动互联网时代', '50．移动互联网时代', full_text)
full_text = re.sub(r'48\.1818', '48．1818', full_text)

for qn in [30, 34, 35, 38, 41, 55]:
    full_text = re.sub(rf'(?:^|\n)\s*{qn}(?=[^\d\.\、\．])', f'\n{qn}．', full_text)

# Let's extract group stems
group_stems = {}
# Find all patterns like: (\d+～\d+题基[于千]以下题干：[\s\S]*?)(?=\d+．)
for m in re.finditer(r'((\d+)～(\d+)题基[于千]以下题干：[\s\S]*?)(?=\n\s*\d+．)', full_text):
    g_text = m.group(1).strip()
    q_start = int(m.group(2))
    q_end = int(m.group(3))
    group_stems[(q_start, q_end)] = g_text
    print(f"Group {q_start}-{q_end}: {g_text[:60]}... (len={len(g_text)})")

