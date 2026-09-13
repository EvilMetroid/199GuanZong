import json, os, re, fitz

YEAR = 2021
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
MD_PATH = os.path.join(OUT_DIR, f"{YEAR}年199管综真题试卷.md")
JSONL_PATH = os.path.join(OUT_DIR, f"{YEAR}年199真题_chunks.jsonl")

COND_OPTIONS = {
    "A": "条件（1）充分，但条件（2）不充分",
    "B": "条件（2）充分，但条件（1）不充分",
    "C": "条件（1）和条件（2）单独都不充分，但条件（1）和条件（2）联合起来充分",
    "D": "条件（1）充分，条件（2）也充分",
    "E": "条件（1）和条件（2）单独都不充分，条件（1）和条件（2）联合起来也不充分"
}

math_q_2021 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "某便利店第一天售出 50 种商品，第二天售出 45 种商品，第三天售出 60 种商品，前两天售出的商品有 25 种相同，后两天售出的商品有 30 种相同，则这三天售出的商品至少有（ ）种。",
        "options": {
            "A": "20",
            "B": "75",
            "C": "80",
            "D": "85",
            "E": "100"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "三位年轻人的年龄成等差，且最大与最小的两人年龄差的 10 倍是另一人年龄，则三人年龄最大的是（ ）。",
        "options": {
            "A": "19",
            "B": "20",
            "C": "21",
            "D": "22",
            "E": "23"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "$\\frac{1}{1+\\sqrt{2}} + \\frac{1}{\\sqrt{2}+\\sqrt{3}} + \\cdots + \\frac{1}{\\sqrt{99}+\\sqrt{100}} = $（ ）。",
        "options": {
            "A": "9",
            "B": "10",
            "C": "11",
            "D": "$3\\sqrt{11}-1$",
            "E": "$3\\sqrt{11}$"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "设 $p, q$ 是小于 10 的质数，则满足条件 $1 < \\frac{q}{p} < 2$ 的 $p, q$ 有（ ）组。",
        "options": {
            "A": "2",
            "B": "3",
            "C": "4",
            "D": "5",
            "E": "6"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "设二次函数 $f(x) = ax^2 + bx + c$，且 $f(2) = f(0)$，则 $\\frac{f(3) - f(2)}{f(2) - f(1)} = $（ ）。",
        "options": {
            "A": "2",
            "B": "3",
            "C": "4",
            "D": "5",
            "E": "6"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "如图 1 所示，由 $P$ 到 $Q$ 的电路中有三个元件，分别标为 $T_1, T_2, T_3$，电流能通过 $T_1, T_2, T_3$ 的概率分别为 0.9, 0.9, 0.99，假设电流能否通过三个元件相互独立，则电流能在 $P, Q$ 之间通过的概率是（ ）。",
        "options": {
            "A": "0.801 99",
            "B": "0.998 9",
            "C": "0.999",
            "D": "0.999 9",
            "E": "0.999 99"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "甲、乙两组同学中，甲组有 3 男 3 女，乙组有 4 男 2 女，从甲、乙两组中各选出 2 名同学，则这 4 人中恰有 1 名女生的选法有（ ）种。",
        "options": {
            "A": "26",
            "B": "54",
            "C": "70",
            "D": "78",
            "E": "105"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "若球体的内接正方体的体积为 8 立方米，则该球体的表面积为（ ）平方米。",
        "options": {
            "A": "$4\\pi$",
            "B": "$6\\pi$",
            "C": "$8\\pi$",
            "D": "$12\\pi$",
            "E": "$24\\pi$"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "如图 2 所示，已知正六边形边长为 1，分别以正六边形的顶点 $O, P, Q$ 为圆心，以 1 为半径作圆弧，则阴影部分面积为（ ）。",
        "options": {
            "A": "$\\pi - \\frac{3\\sqrt{3}}{2}$",
            "B": "$\\pi - \\frac{3\\sqrt{3}}{4}$",
            "C": "$\\frac{\\pi}{2} - \\frac{3\\sqrt{3}}{4}$",
            "D": "$\\frac{\\pi}{2} - \\frac{3\\sqrt{3}}{8}$",
            "E": "$2\\pi - 3\\sqrt{3}$"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "已知四边形 $ABCD$ 是圆 $x^2 + y^2 = 25$ 的内接四边形，若点 $A, C$ 是直线 $x = 3$ 与圆 $x^2 + y^2 = 25$ 的交点，则四边形 $ABCD$ 的面积的最大值为（ ）。",
        "options": {
            "A": "20",
            "B": "24",
            "C": "40",
            "D": "48",
            "E": "80"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "某商场利用抽奖方式促销，100 个奖券中设有 3 个一等奖、7 个二等奖，则一等奖先于二等奖抽完的概率为（ ）。",
        "options": {
            "A": "0.3",
            "B": "0.5",
            "C": "0.6",
            "D": "0.7",
            "E": "0.73"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "函数 $f(x) = x^2 - 4x - 2|x - 2|$ 的最小值为（ ）。",
        "options": {
            "A": "-4",
            "B": "-5",
            "C": "-6",
            "D": "-7",
            "E": "-8"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "从装有 1 个红球、2 个白球、3 个黑球的袋中随机取出 3 个球，则这 3 个球颜色至多有两种的概率为（ ）。",
        "options": {
            "A": "0.3",
            "B": "0.4",
            "C": "0.5",
            "D": "0.6",
            "E": "0.7"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "现有甲、乙两种浓度酒精，已知用 10 升甲酒精和 12 升乙酒精可以配成浓度为 70% 的酒精，用 20 升甲酒精和 8 升乙酒精可以配成浓度为 80% 的酒精，则甲酒精的浓度为（ ）。",
        "options": {
            "A": "72%",
            "B": "80%",
            "C": "84%",
            "D": "88%",
            "E": "91%"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "甲、乙两人相距 330 千米，他们驾车同时出发，经过 2 小时相遇。甲继续行驶 2 小时 24 分钟后到达乙的出发地，则乙的车速为（ ）千米/小时。",
        "options": {
            "A": "70",
            "B": "75",
            "C": "80",
            "D": "90",
            "E": "96"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "某班增加两名同学，则该班同学的平均身高增加了。\n（1）增加的两名同学的平均身高与原来男同学的平均身高相同。\n（2）原来男同学的平均身高大于女同学的平均身高。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "设 $x, y$ 为实数，则能确定 $x \\le y$。\n（1）$x^2 \\le y - 1$。\n（2）$x^2 + (y - 2)^2 \\le 2$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "清理一块场地，则甲、乙、丙三人能在 2 天内完成。\n（1）甲、乙两人需要 3 天。\n（2）甲、丙两人需要 4 天。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "某单位进行投票表决，已知该单位的男、女员工人数之比为 $3 : 2$，则能确定至少有 50% 的女员工参加了投票。\n（1）投赞成票的人数超过总人数的 40%。\n（2）参加投票的女员工比男员工多。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "设 $a, b$ 为实数，则能确定 $|a| + |b|$ 的值。\n（1）已知 $|a + b|$ 的值。\n（2）已知 $|a - b|$ 的值。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "设 $a$ 为实数，圆 $C: x^2 + y^2 = ax + ay$，则能确定圆 $C$ 的方程。\n（1）直线 $x + y = 1$ 与圆 $C$ 相切。\n（2）直线 $x - y = 1$ 与圆 $C$ 相切。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "某人购买了果汁、牛奶、咖啡三种物品，已知果汁每瓶 12 元，牛奶每盒 15 元，咖啡每盒 35 元，则能确定所买的各种物品的数量。\n（1）总花费为 104 元。\n（2）总花费为 215 元。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "某人开车去上班，有一段路因维修限速通行，则可算出此人上班的距离。\n（1）路上比平时多用了半小时。\n（2）已知维修路段的通行速度。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "已知数列 $\{a_n\}$，则数列 $\{a_n\}$ 为等比数列。\n（1）$a_n a_{n+1} > 0$。\n（2）$a_{n+1}^2 - 2a_n^2 - a_n a_{n+1} = 0$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "给定两个直角三角形，则这两个直角三角形相似。\n（1）每个直角三角形边长成等比数列。\n（2）每个直角三角形边长成等差数列。",
        "options": COND_OPTIONS
    }
]

# Parse logic 26..55
doc = fitz.open('真题部分/2021年199管综真题.pdf')
full_text = ''
for p in range(3, 13):
    full_text += f'\n<<<PAGE_{p}>>>\n' + doc[p].get_text()

full_text = re.sub(r'2021年真题[一－]-第\s*\d+\s*页（共31\s*页）\)?', '', full_text)
full_text = re.sub(r'三、逻辑推理[：∶]第26～55小题.*?请在答题卡上将所选项的字母涂黑。', '', full_text, flags=re.S)

writing_start = full_text.find('四、写作')
logic_text = full_text[:writing_start]

group_data = {
    (40, 41): "40～41 题基于以下题干：\n冬奥组委会官网开通全球招募系统，正式招募冬奥会志愿者。张明、刘伟、庄敏、孙兰、李梅 5 人在一起讨论报名事宜。他们商量的结果如下：\n（1）如果张明报名，则刘伟也报名。\n（2）如果庄敏报名，则孙兰也报名。\n（3）只要刘伟和孙兰两人中至少有 1 人报名，则李梅也报名。\n后来得知，他们 5 人中恰有 3 人报名了。",
    (47, 48): "47～48 题基于以下题干：\n某剧团拟将历史故事“鸿门宴”搬上舞台，该剧有项王、沛公、项伯、张良、项庄、樊哙、范增 7 个主要角色，甲、乙、丙、丁、戊、己、庚 7 名演员每人只能扮演其中一个角色，且每个角色只能由其中一人扮演。根据各演员的特点，角色安排如下：\n（1）如果甲不扮演沛公，则乙扮演项王。\n（2）如果丙或己扮演张良，则丁扮演范增。\n（3）如果乙不扮演项王，则丙扮演张良。\n（4）如果丁不扮演樊哙，则庚或戊扮演沛公。",
    (54, 55): "54～55 题基于以下题干：\n某高铁线路设有“东沟”“西山”“南镇”“北阳”“中丘”5 座高铁站。该线路有甲、乙、丙、丁、戊 5 趟车运行。这 5 座高铁站中，每站恰好有 3 趟车停靠，且甲车和乙车停靠的站均不相同。已知：\n（1）若乙车或丙车至少有一车在“北阳”停靠，则它们均在“东沟”停靠。\n（2）若丁车在“北阳”停靠，则丙、丁和戊车均在“中丘”停靠。\n（3）若甲、乙和丙车中至少有 2 趟车在“东沟”停靠，则这 3 趟车均在“西山”停靠。"
}

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

sorted_q = sorted(q_splits.items(), key=lambda x: x[1])
logic_questions_raw = {}
for idx, (qn, pos) in enumerate(sorted_q):
    next_pos = sorted_q[idx+1][1] if idx + 1 < len(sorted_q) else len(logic_text_cleaned)
    block = logic_text_cleaned[pos:next_pos].strip()
    logic_questions_raw[qn] = block

def clean_text_segment(s):
    s = re.sub(r'<<<PAGE_\d+>>>', '', s)
    s = s.replace('工', '丁') if '甲、乙、丙、工、戊' in s else s
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

# Special table for Q52
table_q52 = "\n\n表 1\n| 除冰剂类型 | 融冰速度 | 破坏道路设施的可能风险 | 污染土壤 | 污染水体 |\n| :---: | :---: | :---: | :---: | :---: |\n| Ⅰ | 快 | 高 | 高 | 高 |\n| Ⅱ | 中等 | 中 | 低 | 中 |\n| Ⅲ | 较慢 | 低 | 低 | 中 |\n| Ⅳ | 快 | 中 | 中 | 低 |\n| Ⅴ | 较慢 | 低 | 低 | 低 |"

logic_q_2021 = []
for qn in range(26, 56):
    raw_block = logic_questions_raw[qn]
    clean = re.sub(r'<<<PAGE_\d+>>>', '', raw_block)
    opt_matches = list(re.finditer(r'[\(（]([A-E])[\)）]', clean))
    last_5 = opt_matches[-5:]
    first_opt_start = last_5[0].start()
    raw_stem = clean[:first_opt_start].strip()
    raw_stem = re.sub(rf'^\s*{qn}\s*[\.、．]\s*', '', raw_stem)
    raw_stem = clean_text_segment(raw_stem)
    
    if qn == 52:
        raw_stem = raw_stem.replace('见表1∶', '见表 1：' + table_q52)
        
    for (g_start, g_end), g_stem in group_data.items():
        if qn == g_start:
            raw_stem = g_stem + "\n\n" + raw_stem
            
    opts = {}
    for i in range(5):
        m = last_5[i]
        label = m.group(1)
        start = m.end()
        end = last_5[i+1].start() if i < 4 else len(clean)
        opt_text = clean_text_segment(clean[start:end])
        opts[label] = opt_text
        
    logic_q_2021.append({
        "question_no": qn,
        "category": "逻辑推理",
        "stem": raw_stem,
        "options": opts
    })

writing_q_2021 = [
    {
        "question_no": 56,
        "category": "写作",
        "stem": "56．论证有效性分析：分析下述论证中存在的缺陷与漏洞，选择若干要点，写一篇 600 字左右的文章，对该论证的有效性进行分析和评论。（论证有效性分析的一般要点是：概念特别是核心概念的界定和使用是否准确并前后一致，有无各种明显的逻辑错误，论证的论据是否成立并支持结论，结论成立的条件是否充分等。）\n\n常言道：“耳听为虚，眼见为实。”但实际“眼见未必为实”。从哲学上讲，事物表相不等于事物真相。我们亲眼看到的显然不是事物真相。只有将表相加以分析，透过现象看本质才能看到真相。换言之，我们看到的未必是真实情况，即“所见未必为实”。\n\n举例来说，人们都看到了旭日东升、夕阳西下，也就是说，太阳绕地球转，但是，这只是人们站在地球上看到的表象而已，其实这是地球自转造成的。由此可见，眼见者未必实。\n\n我国古代哲学家老子早就看到了这一点。他说过，人们只看到了房子的“有”（有形的结构），但人们没有看到“无”（房子中无形的空间）才有实际效用。这也说明眼所见者未必实，未见者为实。\n\n老子还说，讲究表面的礼节是“忠信之薄”的表现。韩非解释时举例说，父母和子女因为感情深厚而不讲究礼节，可见讲究礼节是感情不深的表现。现在人们把那种客气的行为称作“见外”，也是这个道理。这其实也是一种“眼所见者未必实”的现象。因此，如果你看到有人对你很客气，就认为他对你好，那就错了。",
        "options": {}
    },
    {
        "question_no": 57,
        "category": "写作",
        "stem": "57．论说文：根据下述材料，写一篇 700 字左右的论说文，题目自拟。\n\n我国著名实业家穆藕初在《实业与教育之关系》中指出，教育之重点在道德教育（如责任心和公共心之养成、机械心之拔除）和科学教育（如观察力、推论力、判断力之养成）。完全受此两种教育，实业界中坚人物可成。",
        "options": {}
    }
]

all_questions = math_q_2021 + logic_q_2021 + writing_q_2021
print(f"Total questions compiled: {len(all_questions)}")

with open(JSONL_PATH, "w", encoding="utf-8") as f:
    for q in all_questions:
        chunk = {
            "year": YEAR,
            "category": q["category"],
            "question_no": q["question_no"],
            "stem": q["stem"],
            "options": q["options"],
            "image": f"images/{YEAR}_q{q['question_no']:02d}.png"
        }
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

md_lines = [
    f"# {YEAR}年全国硕士研究生招生考试管理类专业学位联考综合能力试题 (科目代码: 199)\n",
    "## 一、问题求解：第1～15小题，每小题3分，共45分。下列每题给出的A、B、C、D、E五个选项中，只有一项是符合试题要求的。\n"
]

for q in all_questions:
    qn = q["question_no"]
    if qn == 16:
        md_lines.append("\n## 二、条件充分性判断：第16～25小题，每小题3分，共30分。要求判断每题给出的条件（1）和条件（2）能否充分支持题干所陈述的结论。A、B、C、D、E五个选项为判断结果，请选择一项符合试题要求的判断。\n")
        md_lines.append("> **A**．条件（1）充分，但条件（2）不充分\n> **B**．条件（2）充分，但条件（1）不充分\n> **C**．条件（1）和条件（2）单独都不充分，但条件（1）和条件（2）联合起来充分\n> **D**．条件（1）充分，条件（2）也充分\n> **E**．条件（1）和条件（2）单独都不充分，条件（1）和条件（2）联合起来也不充分\n")
    elif qn == 26:
        md_lines.append("\n## 三、逻辑推理：第26～55小题，每小题2分，共60分。下列每题给出的A、B、C、D、E五个选项中，只有一项是符合试题要求的。\n")
    elif qn == 56:
        md_lines.append("\n## 四、写作：第56～57小题，共65分。其中论证有效性分析30分，论说文35分。\n")
        
    md_lines.append(f"\n### 第{qn}题\n")
    md_lines.append(f"![{YEAR}_q{qn:02d}](images/{YEAR}_q{qn:02d}.png)\n")
    md_lines.append(f"{q['stem']}\n")
    
    if q["options"]:
        for opt_key in ["A", "B", "C", "D", "E"]:
            if opt_key in q["options"]:
                md_lines.append(f"- **{opt_key}**．{q['options'][opt_key]}")

with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines) + "\n")

print(f"Generated {MD_PATH}")
print(f"Generated {JSONL_PATH}")
