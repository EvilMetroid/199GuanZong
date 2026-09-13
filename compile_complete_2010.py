import json, os, re, fitz

YEAR = 2010
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
MD_PATH = os.path.join(OUT_DIR, f"{YEAR}年199管综真题试卷.md")
JSONL_PATH = os.path.join(OUT_DIR, f"{YEAR}年199真题_chunks.jsonl")

# Standard options for 条件充分性判断
COND_OPTIONS = {
    "A": "条件（1）充分，但条件（2）不充分",
    "B": "条件（2）充分，但条件（1）不充分",
    "C": "条件（1）和条件（2）单独都不充分，但条件（1）和条件（2）联合起来充分",
    "D": "条件（1）充分，条件（2）也充分",
    "E": "条件（1）和条件（2）单独都不充分，条件（1）和条件（2）联合起来也不充分"
}

# Math questions 1~25
math_q_2010 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "电影开演时观众中女士与男士人数之比为 $5 : 4$，开演后无观众入场，放映一个小时后，女士的 20%、男士的 15% 离场，则此时在场的女士与男士人数之比为（ ）。",
        "options": {
            "A": "4 : 5",
            "B": "1 : 1",
            "C": "5 : 4",
            "D": "20 : 17",
            "E": "85 : 64"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "某商品的成本为 240 元，若按该商品标价的 8 折出售，利润率是 15%，则该商品的标价为（ ）。",
        "options": {
            "A": "276 元",
            "B": "331 元",
            "C": "345 元",
            "D": "360 元",
            "E": "400 元"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "三名小孩中有一名学龄前儿童（年龄不足 6 岁），他们的年龄都是质数（素数），且依次相差 6 岁，他们的年龄之和为（ ）。",
        "options": {
            "A": "21",
            "B": "27",
            "C": "33",
            "D": "39",
            "E": "51"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "在表1中每行为等差数列，每列为等比数列，$x + y + z = $（ ）。\n\n| | 列1 | 列2 | 列3 |\n| :---: | :---: | :---: | :---: |\n| 行1 | 2 | 2.5 | 3 |\n| 行2 | $x$ | $y$ | $z$ |\n| 行3 | 1/2 | 5/8 | 3/4 |",
        "options": {
            "A": "2",
            "B": "5/2",
            "C": "3",
            "D": "7/2",
            "E": "4"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "如图1所示，在直角三角形 $ABC$ 区域内部有座山，现计划从 $BC$ 边上某点 $D$ 开凿一条隧道到点 $A$，要求隧道长度最短，已知 $AB$ 长为 5 千米，$AC$ 长为 12 千米，则所开凿的隧道 $AD$ 的长度约为（ ）。",
        "options": {
            "A": "4.12 千米",
            "B": "4.22 千米",
            "C": "4.42 千米",
            "D": "4.62 千米",
            "E": "4.92 千米"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "某商店举行店庆活动，顾客消费达到一定数量后，可以在 4 种赠品中随机选取 2 个不同的赠品，任意两位顾客所选赠品中，恰有 1 件品种相同的概率是（ ）。",
        "options": {
            "A": "1/6",
            "B": "1/3",
            "C": "1/2",
            "D": "2/3",
            "E": "5/6"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "多项式 $x^3 + ax^2 + bx - 6$ 的两个因式是 $x-1$ 和 $x-2$，则第三个一次因式为（ ）。",
        "options": {
            "A": "$x - 6$",
            "B": "$x - 3$",
            "C": "$x + 1$",
            "D": "$x + 2$",
            "E": "$x + 3$"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "某公司的员工中，拥有本科毕业证、计算机等级证、汽车驾驶证的人数分别为 130、110、90，又知只有一种证的人数为 140，三证齐全的人数为 30，则恰有双证的人数为（ ）。",
        "options": {
            "A": "45",
            "B": "50",
            "C": "52",
            "D": "65",
            "E": "100"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "甲商店销售某种商品，该商品的进价为每件 90 元，若每件定价 100 元，则一天内能售出 500 件，在此基础上，定价每增 1 元，一天少售出 10 件，若使甲商店获得最大利润，则该商品的定价应为（ ）。",
        "options": {
            "A": "115 元",
            "B": "120 元",
            "C": "125 元",
            "D": "130 元",
            "E": "135 元"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "已知直线 $ax - by + 3 = 0$ ($a>0, b>0$) 过圆 $x^2 + 4x + y^2 - 2y + 1 = 0$ 的圆心，则 $ab$ 的最大值为（ ）。",
        "options": {
            "A": "9/16",
            "B": "11/16",
            "C": "3/4",
            "D": "9/8",
            "E": "9/4"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "某大学派出 5 名志愿者到西部 4 所中学支教，若每所中学至少有一名志愿者，则不同的分配方案共有（ ）种。",
        "options": {
            "A": "240 种",
            "B": "144 种",
            "C": "120 种",
            "D": "60 种",
            "E": "24 种"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "某装置的启动密码是由 0 到 9 中的 3 个不同数字组成，连续 3 次输入错误密码，就会导致该装置永久关闭，一个仅记得密码是由 3 个不同数字组成的人能够启动此装置的概率为（ ）。",
        "options": {
            "A": "1/120",
            "B": "1/168",
            "C": "1/240",
            "D": "1/720",
            "E": "3/1000"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "某居民小区决定投资 15 万元修建停车位，据测算，修建一个室内车位的费用为 5000 元，修建一个室外车位的费用为 1000 元，考虑到实际因素，计划室外车位的数量不少于室内车位的 2 倍，也不多于室内车位的 3 倍，这笔投资最多可建车位的数量为（ ）。",
        "options": {
            "A": "78",
            "B": "74",
            "C": "72",
            "D": "70",
            "E": "66"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "如图2所示，长方形 $ABCD$ 的两条边分别为 8 米和 6 米，四边形 $OEFG$ 的面积是 4 平方米，则阴影部分的面积为（ ）平方米。",
        "options": {
            "A": "32",
            "B": "28",
            "C": "24",
            "D": "20",
            "E": "16"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "在一次竞猜活动中，设有 5 关，如果连续通过 2 关就算闯关成功，小王通过每关的概率都是 1/2，他闯关成功的概率为（ ）。",
        "options": {
            "A": "1/8",
            "B": "1/4",
            "C": "3/8",
            "D": "1/2",
            "E": "19/32"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "$a|a-b| \\ge |a|(a-b)$。\n(1) 实数 $a > 0$。\n(2) 实数 $a, b$ 满足 $a > b$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "有偶数位来宾。\n(1) 聚会时所有来宾都被安排坐在一张圆桌周围，且每位来宾与其邻座性别不同。\n(2) 聚会时男宾人数是女宾人数的两倍。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "售出一件甲商品比售出一件乙商品利润要高。\n(1) 售出 5 件甲商品，4 件乙商品共获利 50 元。\n(2) 售出 4 件甲商品，5 件乙商品共获利 47 元。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "已知数列 $\{a_n\}$ 为等差数列，公差为 $d$，$a_1 + a_2 + a_3 + a_4 = 12$，则 $a_4 = 0$。\n(1) $d = -2$。\n(2) $a_2 + a_4 = 4$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "甲企业今年人均成本是去年的 60%。\n(1) 甲企业今年总成本比去年减少 25%，员工人数增加 25%。\n(2) 甲企业今年总成本比去年减少 28%，员工人数增加 20%。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "该股票涨了。\n(1) 某股票连续三天涨 10% 后，又连续三天跌 10%。\n(2) 某股票连续三天跌 10% 后，又连续三天涨 10%。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "某班有 50 名学生，其中女生 26 名，已知在某次选拔测试中，有 27 名学生未通过，则有 9 名男生通过。\n(1) 在通过的学生中，女生比男生多 5 人。\n(2) 在男生中，未通过的人数比通过的人数多 6 人。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "甲企业一年的总产值为 $\\frac{a}{p}[(1+p)^{12} - 1]$。\n(1) 甲企业一月份的产值为 $a$，以后每月产值的增长率为 $p$。\n(2) 甲企业一月份的产值为 $\\frac{a}{2}$，以后每月产值的增长率为 $2p$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "设 $a, b$ 为非负实数，则 $a+b \\le \\frac{5}{4}$。\n(1) $ab \\le \\frac{9}{16}$。\n(2) $a^2 + b^2 \\le 1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "如图3所示，在三角形 $ABC$ 中，已知 $EF // BC$，则三角形 $AEF$ 的面积等于梯形 $EBCF$ 的面积。\n(1) $|AG| = 2|GD|$。\n(2) $|BC| = \\sqrt{2}|EF|$。",
        "options": COND_OPTIONS
    }
]

# Read PDF text for Q26-57
doc = fitz.open(f"真题部分/{YEAR}年199管综真题.pdf")
pages_text = [doc[p].get_text() for p in range(4, 13)]
all_text = "\n".join(pages_text)
all_text = re.sub(rf'{YEAR}\s*年真题[^\n]*\n', '', all_text)

# Q26 to Q57 positions
q_positions = {}
for q in range(26, 58):
    if q == 49:
        m = re.search(r'(?:^|\n)\s*49[^\d]', all_text)
    elif q == 50:
        m = re.search(r'(?:^|\n)\s*(?:50|so)[\.、．\s]', all_text)
    else:
        m = re.search(rf'(?:^|\n)\s*{q}[\.、．\s]', all_text)
    if m:
        q_positions[q] = m.start()
    else:
        print(f"Missing position for Q{q}!")

sorted_qs = sorted(q_positions.keys())
all_questions = list(math_q_2010)

def normalize_options(raw):
    # Handle C[A-E]) or ([A-E]) or （[A-E]）
    t = re.sub(r'(?:^|\n|\s|[。？?；;∶:])[（\(C]?([A-E])[）\)\>、．]?\s*', r'\n\1. ', raw)
    t = re.sub(r'(?:^|\n|\s|[。？?；;∶:])([A-E])[）\)\>、．]\s*', r'\n\1. ', t)
    return t

for i, q in enumerate(sorted_qs):
    start = q_positions[q]
    end = q_positions[sorted_qs[i+1]] if i+1 < len(sorted_qs) else len(all_text)
    raw = all_text[start:end].strip()
    raw = re.sub(r'^(?:\d{1,2}|so)[\.、．\s]?\s*', '', raw)
    
    if q == 56:
        all_questions.append({
            "question_no": 56,
            "category": "论证有效性分析",
            "stem": raw.strip(),
            "options": {}
        })
        continue
    elif q == 57:
        all_questions.append({
            "question_no": 57,
            "category": "论说文",
            "stem": raw.strip(),
            "options": {}
        })
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
        all_questions.append({
            "question_no": q,
            "category": "逻辑推理",
            "stem": stem_part,
            "options": opts
        })
    else:
        all_questions.append({
            "question_no": q,
            "category": "逻辑推理",
            "stem": raw,
            "options": {}
        })

print(f"Total questions compiled: {len(all_questions)}")

# Validation: check every question
missing_options = []
for q in all_questions:
    qn = q["question_no"]
    if qn <= 55 and len(q["options"]) < 5:
        missing_options.append((qn, list(q["options"].keys())))

if missing_options:
    print("Warning, questions with < 5 options:", missing_options)
else:
    print("SUCCESS: ALL 55 questions (Q1~Q55) have exactly 5 options A~E!")

# Generate Markdown
md_lines = [
    f"# {YEAR} 年全国硕士研究生入学统一考试",
    "# 管理类专业学位联考综合能力试题 (199)",
    "",
    "> **试卷结构**：",
    "> - 一、数学基础（第 1-25 题，共 75 分）",
    "> - 二、逻辑推理（第 26-55 题，共 60 分）",
    "> - 三、中文写作（第 56-57 题，共 65 分）",
    "",
    "---",
    "",
    "## 一、数学基础（第 1-25 题，共 75 分）",
    "",
    "### (一) 问题求解：第 1~15 小题，每小题 3 分，共 45 分。下列每题给出的五个选项中，只有一项是符合试题要求的。",
    ""
]

chunks = []

for q in all_questions:
    q_no = q["question_no"]
    cat = q["category"]
    stem = q["stem"]
    opts = q.get("options", {})
    img_rel = f"images/{YEAR}_q{q_no:02d}.png"
    
    if q_no == 16:
        md_lines.extend([
            "---",
            "",
            "### (二) 条件充分性判断：第 16~25 小题，每小题 3 分，共 30 分。要求判断每题给出的条件（1）和条件（2）能否充分支持题干所陈述的结论。",
            "> **判断标准**：",
            "> - **A**．条件 (1) 充分，但条件 (2) 不充分",
            "> - **B**．条件 (2) 充分，但条件 (1) 不充分",
            "> - **C**．条件 (1) 和条件 (2) 单独都不充分，但条件 (1) 和条件 (2) 联合起来充分",
            "> - **D**．条件 (1) 充分，条件 (2) 也充分",
            "> - **E**．条件 (1) 和条件 (2) 单独都不充分，条件 (1) 和条件 (2) 联合起来也不充分",
            ""
        ])
    elif q_no == 26:
        md_lines.extend([
            "---",
            "",
            "## 二、逻辑推理（第 26-55 题，每小题 2 分，共 60 分）",
            "下列每题给出的五个选项中，只有一项是符合试题要求的。",
            ""
        ])
    elif q_no == 56:
        md_lines.extend([
            "---",
            "",
            "## 三、中文写作（第 56-57 题，共 65 分）",
            ""
        ])
        
    md_lines.append(f"#### 第 {q_no} 题（{cat}）\n")
    md_lines.append(stem)
    md_lines.append("")
    
    if opts:
        for k in ["A", "B", "C", "D", "E"]:
            if k in opts:
                md_lines.append(f"- **{k}**．{opts[k]}")
        md_lines.append("")
        
    md_lines.append(f"![{YEAR}年第{q_no}题原卷切片]({img_rel})")
    md_lines.append("")
    
    chunks.append({
        "year": YEAR,
        "category": cat,
        "question_no": q_no,
        "stem": stem,
        "options": opts,
        "image": img_rel
    })

with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

with open(JSONL_PATH, "w", encoding="utf-8") as f:
    for c in chunks:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

print(f"SUCCESSFULLY wrote {MD_PATH} and {JSONL_PATH}!")
