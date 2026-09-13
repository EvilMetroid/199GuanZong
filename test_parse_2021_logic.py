import fitz, re

doc = fitz.open('真题部分/2021年199管综真题.pdf')
full_text = ''
for p in range(3, 13):
    full_text += f'\n<<<PAGE_{p}>>>\n' + doc[p].get_text()

full_text = re.sub(r'2021年真题[一－]-第\s*\d+\s*页（共31\s*页）\)?', '', full_text)
full_text = re.sub(r'三、逻辑推理[：∶]第26～55小题.*?请在答题卡上将所选项的字母涂黑。', '', full_text, flags=re.S)

writing_start = full_text.find('四、写作')
logic_text = full_text[:writing_start]

# Group questions:
# 40-41, 47-48, 54-55
group_data = {
    (40, 41): "40～41 题基于以下题干：\n冬奥组委会官网开通全球招募系统，正式招募冬奥会志愿者。张明、刘伟、庄敏、孙兰、李梅 5 人在一起讨论报名事宜。他们商量的结果如下：\n（1）如果张明报名，则刘伟也报名。\n（2）如果庄敏报名，则孙兰也报名。\n（3）只要刘伟和孙兰两人中至少有 1 人报名，则李梅也报名。\n后来得知，他们 5 人中恰有 3 人报名了。",
    (47, 48): "47～48 题基于以下题干：\n某剧团拟将历史故事“鸿门宴”搬上舞台，该剧有项王、沛公、项伯、张良、项庄、樊哙、范增 7 个主要角色，甲、乙、丙、丁、戊、己、庚 7 名演员每人只能扮演其中一个角色，且每个角色只能由其中一人扮演。根据各演员的特点，角色安排如下：\n（1）如果甲不扮演沛公，则乙扮演项王。\n（2）如果丙或己扮演张良，则丁扮演范增。\n（3）如果乙不扮演项王，则丙扮演张良。\n（4）如果丁不扮演樊哙，则庚或戊扮演沛公。",
    (54, 55): "54～55 题基于以下题干：\n某高铁线路设有“东沟”“西山”“南镇”“北阳”“中丘”5 座高铁站。该线路有甲、乙、丙、丁、戊 5 趟车运行。这 5 座高铁站中，每站恰好有 3 趟车停靠，且甲车和乙车停靠的站均不相同。已知：\n（1）若乙车或丙车至少有一车在“北阳”停靠，则它们均在“东沟”停靠。\n（2）若丁车在“北阳”停靠，则丙、丁和戊车均在“中丘”停靠。\n（3）若甲、乙和丙车中至少有 2 趟车在“东沟”停靠，则这 3 趟车均在“西山”停靠。"
}

# Remove group headers from logic_text
logic_text_cleaned = logic_text
logic_text_cleaned = re.sub(r'40～41题基于以下题干[：;；][\s\S]*?(?=40\.)', '', logic_text_cleaned)
logic_text_cleaned = re.sub(r'47[～~]48题基于以下题干[：;；∶][\s\S]*?(?=47\.)', '', logic_text_cleaned)
logic_text_cleaned = re.sub(r'54[～~]55题基于以下题干[：;；∶][\s\S]*?(?=54\.)', '', logic_text_cleaned)

q_splits = {}
for qn in range(26, 56):
    pattern = rf'(?:^|\n)\s*{qn}\s*[\.、．]'
    m = re.search(pattern, logic_text_cleaned)
    if m:
        q_splits[qn] = m.start()
    else:
        print(f"Missing Q{qn}")

print(f"Mapped {len(q_splits)} logic questions")

sorted_q = sorted(q_splits.items(), key=lambda x: x[1])
logic_questions_raw = {}
for idx, (qn, pos) in enumerate(sorted_q):
    next_pos = sorted_q[idx+1][1] if idx + 1 < len(sorted_q) else len(logic_text_cleaned)
    block = logic_text_cleaned[pos:next_pos].strip()
    logic_questions_raw[qn] = block

def clean_text_segment(s):
    s = re.sub(r'<<<PAGE_\d+>>>', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

all_good = True
for qn in range(26, 56):
    raw_block = logic_questions_raw[qn]
    clean = re.sub(r'<<<PAGE_\d+>>>', '', raw_block)
    opt_matches = list(re.finditer(r'[\(（]([A-E])[\)）]', clean))
    last_5 = opt_matches[-5:]
    labels = [m.group(1) for m in last_5]
    if set(labels) != {'A', 'B', 'C', 'D', 'E'}:
        print(f"Q{qn} bad options: {labels}")
        all_good = False
    else:
        print(f"Q{qn}: OK")

if all_good:
    print("ALL Q26-Q55 logic questions parsed perfectly!")
