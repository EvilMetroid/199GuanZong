import json, os, re, fitz

YEAR = 2012
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

math_q_2012 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "某商品的定价为 200 元，受金融危机的影响，连续两次降价 20% 后的售价为（ ）。",
        "options": {
            "A": "114 元",
            "B": "120 元",
            "C": "128 元",
            "D": "144 元",
            "E": "160 元"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "如图1所示，$\\triangle ABC$ 是直角三角形，$S_1, S_2, S_3$ 为正方形，已知 $a, b, c$ 分别是 $S_1, S_2, S_3$ 的边长，则（ ）。",
        "options": {
            "A": "$a = b + c$",
            "B": "$a^2 = b^2 + c^2$",
            "C": "$a^2 = 2b^2 + 2c^2$",
            "D": "$a^3 = b^3 + c^3$",
            "E": "$a^3 = 2b^3 + 2c^3$"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "如图2所示，一个储物罐的下半部分是底面直径与高均为 20 米的圆柱形，上半部分（顶部）是半球形，已知底面与顶部的造价是 400 元/平方米，侧面的造价是 300 元/平方米，该储物罐的造价是（ ）（$\\pi \\approx 3.14$）。",
        "options": {
            "A": "56.52 万元",
            "B": "62.8 万元",
            "C": "75.36 万元",
            "D": "87.92 万元",
            "E": "100.48 万元"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "在一次商品促销活动中，主持人出示一个 9 位数，让顾客猜测商品的价格，商品的价格是该 9 位数中从左到右相邻的 3 个数字组成的 3 位数。若顾客一次猜中价格的概率不低于 1/3，则该 9 位数中的数字最多有（ ）个相同。",
        "options": {
            "A": "5",
            "B": "6",
            "C": "7",
            "D": "8",
            "E": "9"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "某商店经营 15 种商品，每次在橱窗内陈列 5 种，若每两次陈列的商品不完全相同，则最多可陈列（ ）次。",
        "options": {
            "A": "3000",
            "B": "3003",
            "C": "4000",
            "D": "4003",
            "E": "4300"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "甲、乙、丙三个地区的公务员参加一次测评，其人数和考分情况如表1所示，三个地区按平均分由高到低的排名顺序为（ ）。",
        "options": {
            "A": "乙、丙、甲",
            "B": "乙、甲、丙",
            "C": "甲、丙、乙",
            "D": "丙、甲、乙",
            "E": "丙、乙、甲"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "经统计，某机场的一个安检口每天中午办理安检手续的乘客人数及相应的概率如表2所示，该安检口 2 天中至少有 1 天中午办理安检手续的乘客人数超过 15 的概率是（ ）。",
        "options": {
            "A": "0.2",
            "B": "0.25",
            "C": "0.4",
            "D": "0.5",
            "E": "0.75"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "某人在保险柜中存放了 $M$ 元现金，第一天取出它的 $\\frac{2}{3}$，以后每天取出前一天所取的 $\\frac{1}{3}$，共取了 7 天，保险柜中剩余的现金为（ ）。",
        "options": {
            "A": "$\\frac{M}{3^7}$ 元",
            "B": "$\\frac{M}{3^6}$ 元",
            "C": "$\\frac{2M}{3^6}$ 元",
            "D": "$[1 - (\\frac{2}{3})^7]M$ 元",
            "E": "$[1 - 7 \\times (\\frac{2}{3})^7]M$ 元"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "在直角坐标系中，若平面区域 $D$ 中所有点的坐标 $(x, y)$ 均满足：$0 \\le x \\le 6, 0 \\le y \\le 6, |y-x| \\le 3, |y+x| \\ge 3$，则平面区域 $D$ 的面积为（ ）。",
        "options": {
            "A": "18",
            "B": "22.5",
            "C": "27",
            "D": "31.5",
            "E": "36"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "某单位春季植树 100 棵，前 2 天安排乙组植树，其余任务由甲、乙两组合作 4 天完成，已知乙组每天比甲组少植树 2 棵，则甲组每天植树（ ）棵。",
        "options": {
            "A": "11",
            "B": "12",
            "C": "13",
            "D": "14",
            "E": "15"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "在两队进行的羽毛球对抗赛中，每队派出 3 男、2 女共 5 名运动员进行 5 场单打比赛，如果女子比赛安排在第二和第四场进行，则比赛双方的出场顺序共有（ ）种。",
        "options": {
            "A": "48",
            "B": "72",
            "C": "144",
            "D": "576",
            "E": "1440"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "若 $x^3 + 3x^2 + ax + b$ 能被 $x^2 - 3x + 2$ 整除，则（ ）。",
        "options": {
            "A": "$a = -4, b = 4$",
            "B": "$a = -4, b = -4$",
            "C": "$a = 10, b = -8$",
            "D": "$a = -10, b = 8$",
            "E": "$a = -2, b = 0$"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "某公司计划运送 180 台电视机和 110 台洗衣机下乡，现有两种货车，甲种货车每辆最多可载 40 台电视机和 10 台洗衣机，乙种货车每辆最多可载 20 台电视机和 20 台洗衣机，已知甲、乙两种货车的租金分别是每辆 400 元和 360 元，则最少的运费是（ ）元。",
        "options": {
            "A": "2560",
            "B": "2600",
            "C": "2640",
            "D": "2680",
            "E": "2720"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "如图3所示，三个边长为 1 的正方形重叠放置，则覆盖区域（实线所围）的面积为（ ）。",
        "options": {
            "A": "$3 - \\sqrt{2}$",
            "B": "$3 - \\frac{3\\sqrt{2}}{4}$",
            "C": "$3 - \\sqrt{3}$",
            "D": "$3 - \\frac{\\sqrt{3}}{2}$",
            "E": "$3 - \\frac{3\\sqrt{3}}{4}$"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "在一次捐赠活动中，某市将捐赠的物品打包成件，其中帐篷和食品共 320 件，帐篷比食品多 80 件，则帐篷的件数是（ ）。",
        "options": {
            "A": "180",
            "B": "200",
            "C": "220",
            "D": "240",
            "E": "260"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "一元二次方程 $ax^2 + bx + 1 = 0$ 有两个不同实根。\n(1) $a < \\frac{b^2}{4}$。\n(2) $a < 0$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "已知 $\{a_n\}, \{b_n\}$ 分别为等比数列与等差数列，$a_1 = b_1 = 1$，则 $b_2 \\ge a_2$。\n(1) $a_2 > 0$。\n(2) $a_{10} = b_{10}$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "直线 $y = ax + b$ 过第二象限。\n(1) $a = -1, b = 1$。\n(2) $a = 1, b = -1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "某产品由两道独立工序加工完成。则该产品是合格品的概率大于 0.8。\n(1) 第一道工序的合格率为 0.9。\n(2) 第二道工序的合格率为 0.9。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "已知 $m, n$ 是正整数，则 $m$ 是偶数。\n(1) $3m + 2n$ 是偶数。\n(2) $3m^2 + 2n$ 是偶数。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "已知 $a, b$ 是实数，则 $a > b$。\n(1) $a^2 > b^2$。\n(2) $a^2 > b$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "在某次考试中，3 道题中答对 2 道题即为及格。假设某人答对各题的概率相同，则此人及格的概率是 $\\frac{20}{27}$。\n(1) 答对各题的概率为 $\\frac{2}{3}$。\n(2) 3 道题全部答错的概率为 $\\frac{1}{27}$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "已知三种水果的平均价格为 10 元/千克，则每种水果的价格均不超过 18 元/千克。\n(1) 三种水果中价格最低的为 6 元/千克。\n(2) 购买重量分别是 1 千克、1 千克和 2 千克的三种水果共用了 46 元。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "某户要建一个长方形的羊栏，则羊栏的面积大于 500 平方米。\n(1) 羊栏的周长为 120 米。\n(2) 羊栏对角线的长不超过 50 米。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "直线 $y = x + b$ 是抛物线 $y = x^2 + a$ 的切线。\n(1) $y = x + b$ 与 $y = x^2 + a$ 有且仅有一个交点。\n(2) $x^2 - x \\ge b - a$ ($x \\in \\mathbb{R}$)。",
        "options": COND_OPTIONS
    }
]

# Read PDF text for Q26-57
doc = fitz.open(f"真题部分/{YEAR}年199管综真题.pdf")
pages_text = [doc[p].get_text() for p in range(4, 14)]
raw_all = "\n".join(pages_text)
raw_all = re.sub(rf'{YEAR}\s*年真题[^\n]*\n', '', raw_all)

# Limit to logic text starting from header
all_text = raw_all[raw_all.find("三、逻辑推理"):]

# Q26 to Q57 positions
q_positions = {}
for q in range(26, 58):
    q_pat = r'(?:^|\n)\s*' + r'\s*'.join(str(q)) + r'[\.、．\s]'
    m = re.search(q_pat, all_text)
    if m:
        q_positions[q] = m.start()
    else:
        print(f"Missing position for Q{q}!")

sorted_qs = sorted(q_positions.keys())
all_questions = list(math_q_2012)

def normalize_options(raw):
    t = re.sub(r'(?:^|\n|\s|[。？?；;∶:,，、])[（\(C]?([A-E])[）\)\>、．]?\s*', r'\n\1. ', raw)
    t = re.sub(r'(?:^|\n|\s|[。？?；;∶:,，、])([A-E])[）\)\>、．]\s*', r'\n\1. ', t)
    return t

for i, q in enumerate(sorted_qs):
    start = q_positions[q]
    end = q_positions[sorted_qs[i+1]] if i+1 < len(sorted_qs) else len(all_text)
    raw = all_text[start:end].strip()
    raw = re.sub(r'^(?:\d\s*\d)[\.、．\s]\s*', '', raw)
    
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
        if q == 29 and "E" not in opts:
            opts["E"] = "仅I、Ⅲ和IV。"
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
