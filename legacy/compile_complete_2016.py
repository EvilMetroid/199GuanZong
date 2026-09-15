import json, os, re, fitz

YEAR = 2016
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

math_q_2016 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "某家庭在一年支出中，子女教育支出与生活资料支出的比为 $3:8$，文化娱乐支出与子女教育支出的比为 $1:2$。已知文化娱乐支出占家庭总支出的 $10.5\\%$，则生活资料支出占家庭总支出的（ ）。",
        "options": {
            "A": "40%",
            "B": "42%",
            "C": "48%",
            "D": "56%",
            "E": "64%"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "有一批同规格的正方形瓷砖，用它们铺满某个正方形区域时剩余 180 块，将此正方形区域的边长增加一块瓷砖的长度时，还需要增加 21 块瓷砖才能铺满。该批瓷砖共有（ ）。",
        "options": {
            "A": "9981 块",
            "B": "10000 块",
            "C": "10180 块",
            "D": "10201 块",
            "E": "10222 块"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "上午 9 时一辆货车从甲地出发前往乙地，同时一辆客车从乙地出发前往甲地，中午 12 时两车相遇。已知货车和客车的速度分别是 90 千米/小时、100 千米/小时，则当客车到达甲地时，货车距乙地的距离为（ ）千米。",
        "options": {
            "A": "30",
            "B": "43",
            "C": "45",
            "D": "50",
            "E": "57"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "在分别标记了数字 1、2、3、4、5、6 的 6 张卡片中随机取 3 张，其上数字之和等于 10 的概率是（ ）。",
        "options": {
            "A": "0.05",
            "B": "0.1",
            "C": "0.15",
            "D": "0.2",
            "E": "0.25"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "某商场将每台进价为 2000 元的冰箱以 2400 元销售时，每天销售 8 台。调研表明，这种冰箱的售价每降低 50 元，每天就能多销售 4 台。若要每天销售利润最大，则该冰箱的定价应为（ ）元。",
        "options": {
            "A": "2200",
            "B": "2250",
            "C": "2300",
            "D": "2350",
            "E": "2400"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "某委员会由三个不同的专业队伍组成，三个专业队伍的人数分别为 2、3、4，从中选派 2 位不同专业的委员外出调研，则不同的选派方式有（ ）种。",
        "options": {
            "A": "36",
            "B": "26",
            "C": "12",
            "D": "8",
            "E": "6"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "从 1 到 100 的整数中任取一个数，则该数能被 5 或 7 整除的概率为（ ）。",
        "options": {
            "A": "0.02",
            "B": "0.14",
            "C": "0.2",
            "D": "0.32",
            "E": "0.34"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "如图1所示，在四边形 $ABCD$ 中，$AB \\parallel CD$，$AB$ 与 $CD$ 的边长分别为 4 和 8，若 $\\triangle ABE$ 的面积为 4，则四边形 $ABCD$ 的面积为（ ）。",
        "options": {
            "A": "24",
            "B": "30",
            "C": "32",
            "D": "36",
            "E": "40"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "现有长方形木板 340 张，正方形木板 160 张（如图2所示），这些木板恰好可以装配成若干竖式和横式的无盖箱子（如图3所示）。装配成的竖式和横式箱子的个数分别为（ ）。",
        "options": {
            "A": "25, 80",
            "B": "60, 50",
            "C": "20, 70",
            "D": "60, 40",
            "E": "40, 60"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "圆 $x^2 + y^2 - 6x + 4y = 0$ 上到原点距离最远的点是（ ）。",
        "options": {
            "A": "(-3, 2)",
            "B": "(3, -2)",
            "C": "(6, 4)",
            "D": "(-6, 4)",
            "E": "(6, -4)"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "如图4所示，点 $A, B, O$ 的坐标分别为 $(4,0), (0,3), (0,0)$，若 $(x,y)$ 是 $\\triangle AOB$ 中的点，则 $2x+3y$ 的最大值为（ ）。",
        "options": {
            "A": "6",
            "B": "7",
            "C": "8",
            "D": "9",
            "E": "12"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "设抛物线 $y = x^2 + 2ax + b$ 与 $x$ 轴相交于 $A, B$ 两点，点 $C$ 坐标为 $(0,2)$，若 $\\triangle ABC$ 的面积等于 6，则（ ）。",
        "options": {
            "A": "$a^2 - b = 9$",
            "B": "$a^2 + b = 9$",
            "C": "$a^2 - b = 36$",
            "D": "$a^2 + b = 36$",
            "E": "$a^2 - 4b = 9$"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "某公司以分期付款方式购买一套定价 1100 万元的设备，首期付款 100 万元，之后每月付款 50 万元，并支付上期余额的利息，月利率 $1\\%$，该公司为此设备支付了（ ）。",
        "options": {
            "A": "1195 万元",
            "B": "1200 万元",
            "C": "1205 万元",
            "D": "1215 万元",
            "E": "1300 万元"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "某学生要在 4 门不同课程中选修 2 门课程，这 4 门课程中的 2 门各开设一个班，另外 2 门各开设两个班，该学生不同的选课方式共有（ ）种。",
        "options": {
            "A": "6",
            "B": "8",
            "C": "10",
            "D": "13",
            "E": "15"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "如图5所示，在半径为 10 厘米的球体上开一个底面半径是 6 厘米的圆柱形洞，则洞的内壁面积为（ ）平方厘米。",
        "options": {
            "A": "$48\\pi$",
            "B": "$288\\pi$",
            "C": "$96\\pi$",
            "D": "$576\\pi$",
            "E": "$192\\pi$"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "已知某公司男员工的平均年龄和女员工的平均年龄，则能确定该公司员工的平均年龄。\n(1) 已知该公司的员工人数。\n(2) 已知该公司男、女员工的人数之比。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "如图6所示，正方形 $ABCD$ 由四个相同的长方形和一个小正方形拼成，则能确定小正方形的面积。\n(1) 已知正方形 $ABCD$ 的面积。\n(2) 已知长方形的长与宽之比。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "利用长度为 $a$ 和 $b$ 的两种管材能连接成长度为 37 的管道（单位：米）。\n(1) $a = 3, b = 5$。\n(2) $a = 4, b = 6$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "设 $x, y$ 是实数，则 $x \\le 6, y \\le 4$。\n(1) $x \\le y + 2$。\n(2) $2y \\le x + 2$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "将 2 升甲酒精和 1 升乙酒精混合得到丙酒精，则能确定甲、乙两种酒精的浓度。\n(1) 1 升甲酒精和 5 升乙酒精混合后的浓度是丙酒精浓度的 $\\frac{1}{2}$ 倍。\n(2) 1 升甲酒精和 2 升乙酒精混合后的浓度是丙酒精浓度的 $\\frac{2}{3}$ 倍。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "设有两组数据 $S_1: 3, 4, 5, 6, 7$ 和 $S_2: 4, 5, 6, 7, a$，则能确定 $a$ 的值。\n(1) $S_1$ 与 $S_2$ 的均值相等。\n(2) $S_1$ 与 $S_2$ 的方差相等。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "已知 $M$ 是一个平面有限点集，则平面上存在到 $M$ 中各点距离相等的点。\n(1) $M$ 中只有三个点。\n(2) $M$ 中的任意三点都不共线。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "设 $x, y$ 是实数，则可以确定 $x^3 + y^3$ 的最小值。\n(1) $xy = 1$。\n(2) $x + y = 2$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "已知数列 $a_1, a_2, a_3, \\dots, a_{10}$，则 $a_1 - a_2 + a_3 - a_4 + \\dots + a_9 - a_{10} \\ge 0$。\n(1) $a_n \\ge a_{n+1}, n=1, 2, 3, \\dots, 9$。\n(2) $a_n^2 \\ge a_{n+1}^2, n=1, 2, 3, \\dots, 9$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "已知 $f(x) = x^2 + ax + b$，则 $0 \\le f(1) \\le 1$。\n(1) $f(x)$ 在区间 $[0,1]$ 中有两个零点。\n(2) $f(x)$ 在区间 $[1,2]$ 中有两个零点。",
        "options": COND_OPTIONS
    }
]

# Read PDF text for Q26-57
doc = fitz.open(f"真题部分/{YEAR}年199管综真题.pdf")
pages_text = [doc[p].get_text() for p in range(4, 14)]
raw_all = "\n".join(pages_text)
raw_all = re.sub(rf'{YEAR}\s*年真题[^\n]*\n', '', raw_all)
all_text = raw_all[raw_all.find("三、逻辑推理"):]

special_opts = {
    38: {
        "A": "有理的让着没理的，只会助长歪风邪气，有悖于社会的法律和道德。",
        "B": "“理性计算”其实就是胆小怕事，总觉得凡事能躲则躲，但有的事很难躲过。",
        "C": "一味退让也会给行车带来极大的危险，不但可能伤及自己，而且也可能伤及无辜。",
        "D": "即使碰上也不可怕，碰上之后如果立即报警，警方一般会有公正的裁决。",
        "E": "如果不让，就会碰上；碰上之后，即使自己有理，也会有许多麻烦。"
    },
    41: {
        "A": "或者光速不变定律已经过时，或者天文学家的观测有误。",
        "B": "如果天文学家的观测没有问题，光速不变定律就需要修改。",
        "C": "要么天文学家的观测有误，要么有人篡改了天文观测数据。",
        "D": "天文观测数据可能存在偏差，毕竟IC310 星系离地球很远。",
        "E": "光速不变定律已历经过去多次实践检验，没有出现反例。"
    },
    43: {
        "A": "第一个庭院。",
        "B": "第二个庭院。",
        "C": "第四个庭院。",
        "D": "第五个庭院。",
        "E": "第六个庭院。"
    },
    44: {
        "A": "第七个庭院是“水”字庭院。",
        "B": "第五个庭院是“木”字庭院。",
        "C": "第四个庭院是“金”字庭院。",
        "D": "第三个庭院是“月”字庭院。",
        "E": "第一个庭院是“火”字庭院。"
    },
    45: {
        "A": "身心健康的人容易和他人相处融洽，而心理有问题的人与他人很难相处。",
        "B": "男性通常比同年龄段的女性对他人有更强的“敌视情绪”，多数国家男性的平均寿命也因此低于女性。",
        "C": "与人为善带来轻松愉悦的情绪，有益身体健康；损人利己则带来紧张的情绪，有损身体健康。",
        "D": "心存善念、思想豁达的人大多精神愉悦、身体健康。",
        "E": "那些自我优越感比较强的人通常“敌视情绪”也比较强，他们长时间处于紧张状态。"
    },
    54: {
        "A": "木心选用水蜜桃、土豆。",
        "B": "水仙选用金针菇、火腿。",
        "C": "土润选用金针菇、水蜜桃。",
        "D": "火珊选用木耳、水蜜桃。",
        "E": "金粲选用木耳、土豆。"
    },
    55: {
        "A": "木心选用金针菇、水蜜桃。",
        "B": "金粲选用木耳、火腿。",
        "C": "火珊选用金针菇、土豆。",
        "D": "水仙选用木耳、土豆。",
        "E": "土润选用水蜜桃、火腿。"
    }
}

q_positions = {}
for q in range(26, 58):
    q_pat = r'(?:^|\n)\s*' + r'\s*'.join(str(q)) + r'[\.、．\s]'
    m = re.search(q_pat, all_text)
    if m:
        q_positions[q] = m.start()
    else:
        print(f"Missing position for Q{q}!")

sorted_qs = sorted(q_positions.keys())
all_questions = list(math_q_2016)

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
        
    if q in special_opts:
        opts = special_opts[q]
        # Get stem part before options
        if q == 38:
            stem_part = raw[:raw.find("(A)")].strip()
        elif q == 41:
            stem_part = raw[:raw.find("(A)")].strip()
        elif q == 43:
            stem_part = raw[:raw.find("(A)")].strip()
        elif q == 44:
            stem_part = raw[:raw.find("(A)")].strip()
        elif q == 45:
            idx = raw.find("CA)") if "CA)" in raw else raw.find("(A)")
            stem_part = raw[:idx].strip()
        elif q in [54, 55]:
            stem_part = raw[:raw.find("(A)")].strip()
    else:
        if q in [33, 40]:
            idx_a = raw.find("(A)")
            stem_part = raw[:idx_a].strip()
            opt_text = raw[idx_a:].strip()
            norm_text = normalize_options(opt_text)
        else:
            norm_text = normalize_options(raw)
            opt_parts = list(re.finditer(r'(?:^|\n)\s*([A-E])\.\s*(.*?)(?=(?:\n\s*[A-E]\.|\Z))', norm_text, re.DOTALL))
            stem_part = norm_text[:opt_parts[0].start()].strip() if opt_parts else ""

        opt_parts = list(re.finditer(r'(?:^|\n)\s*([A-E])\.\s*(.*?)(?=(?:\n\s*[A-E]\.|\Z))', norm_text, re.DOTALL))
        opts = {}
        for m in opt_parts:
            opts[m.group(1).upper()] = re.sub(r'\s*\n\s*', '', m.group(2).strip())

    stem_clean = re.sub(r'\n(?![（\(0-9一二三四五六七八九十])', '', stem_part)
    all_questions.append({
        "question_no": q,
        "category": "逻辑推理",
        "stem": stem_clean.strip(),
        "options": opts
    })

print(f"Total questions compiled: {len(all_questions)}")

# Write chunks.jsonl
with open(JSONL_PATH, "w", encoding="utf-8") as f:
    for item in all_questions:
        chunk = {
            "year": YEAR,
            "category": item["category"],
            "question_no": item["question_no"],
            "stem": item["stem"],
            "options": item["options"],
            "image": f"images/{YEAR}_q{item['question_no']:02d}.png"
        }
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

# Write markdown
with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write(f"# {YEAR}年全国硕士研究生入学统一考试管理类专业学位联考综合能力试卷 (199)\n\n")
    cur_cat = None
    for item in all_questions:
        cat = item["category"]
        q_no = item["question_no"]
        if cat != cur_cat:
            cur_cat = cat
            f.write(f"## {cur_cat}\n\n")
            if cat == "条件充分性判断":
                f.write("> **条件充分性判断说明**：本大题要求判断每题给出的条件 (1) 和条件 (2) 能否充分支持题干所陈述的结论。请在 A、B、C、D、E 五个选项中选择一项。\n")
                f.write("> - **A**：条件（1）充分，但条件（2）不充分\n")
                f.write("> - **B**：条件（2）充分，但条件（1）不充分\n")
                f.write("> - **C**：条件（1）和条件（2）单独都不充分，但条件（1）和条件（2）联合起来充分\n")
                f.write("> - **D**：条件（1）充分，条件（2）也充分\n")
                f.write("> - **E**：条件（1）和条件（2）单独都不充分，条件（1）和条件（2）联合起来也不充分\n\n")
        
        f.write(f"### 第 {q_no} 题\n\n")
        f.write(f"{item['stem']}\n\n")
        
        if item["options"]:
            for opt_k in ["A", "B", "C", "D", "E"]:
                if opt_k in item["options"]:
                    f.write(f"- **{opt_k}**．{item['options'][opt_k]}\n")
            f.write("\n")
        
        img_rel = f"images/{YEAR}_q{q_no:02d}.png"
        f.write(f"![第 {q_no} 题原卷截图]({img_rel})\n\n---\n\n")

print(f"Finished writing {MD_PATH} and {JSONL_PATH}")
