import json, os, re, fitz

YEAR = 2018
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

math_q_2018 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "学科竞赛设一等奖、二等奖和三等奖，比例为 $1:3:8$，获奖率为 $30\\%$。已知 10 人获得一等奖，则参加竞赛的人数为（ ）人。",
        "options": {
            "A": "300",
            "B": "400",
            "C": "500",
            "D": "550",
            "E": "600"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "为了解某公司员工的年龄结构，按男、女人数的比例进行了随机抽样，结果如表1所示：\n\n| | | | | | | | | | |\n| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n| **男员工年龄（岁）** | 23 | 26 | 28 | 30 | 32 | 34 | 36 | 38 | 41 |\n| **女员工年龄（岁）** | 23 | 25 | 27 | 27 | 29 | 31 | | | |\n\n根据表中数据统计，该公司男员工的平均年龄与全体员工的平均年龄分别是（ ）（单位：岁）。",
        "options": {
            "A": "32, 30",
            "B": "32, 29.5",
            "C": "32, 27",
            "D": "30, 27",
            "E": "29.5, 27"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "某单位采取分段收费的方式收取网络流量（单位：GB）费用：每月流量 20（含）以内免费，流量 20 到 30（含）的每 GB 收费 1 元，流量 30 到 40（含）的每 GB 收费 3 元，流量 40 以上的每 GB 收费 5 元。小王这个月用了 45GB 的流量，则他应该交费（ ）元。",
        "options": {
            "A": "45",
            "B": "65",
            "C": "75",
            "D": "85",
            "E": "135"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "如图1所示，圆 $O$ 是 $\\triangle ABC$ 的内切圆，若 $\\triangle ABC$ 的面积与周长的大小之比为 $1:2$，则圆 $O$ 的面积为（ ）。",
        "options": {
            "A": "$\\pi$",
            "B": "$2\\pi$",
            "C": "$3\\pi$",
            "D": "$4\\pi$",
            "E": "$5\\pi$"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "设实数 $a, b$ 满足 $|a - b| = 2, |a^3 - b^3| = 26$，则 $a^2 + b^2 = $（ ）。",
        "options": {
            "A": "30",
            "B": "22",
            "C": "15",
            "D": "13",
            "E": "10"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "有 96 位顾客至少购买了甲、乙、丙三种商品中的一种，经调查：同时购买了甲、乙两种商品的有 8 位，同时购买了甲、丙两种商品的有 12 位，同时购买了乙、丙两种商品的有 6 位，同时购买了三种商品的有 2 位。则仅购买一种商品的顾客有（ ）位。",
        "options": {
            "A": "70",
            "B": "72",
            "C": "74",
            "D": "76",
            "E": "82"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "如图2所示，四边形 $A_1 B_1 C_1 D_1$ 是平行四边形，$A_2, B_2, C_2, D_2$ 分别是 $A_1 B_1 C_1 D_1$ 四边的中点，$A_3, B_3, C_3, D_3$ 分别是四边形 $A_2 B_2 C_2 D_2$ 四边的中点，依次下去，得到四边形序列 $A_n B_n C_n D_n (n=1,2,3,\\dots)$。设 $A_n B_n C_n D_n$ 的面积为 $S_n$，且 $S_1 = 12$，则 $S_1 + S_2 + S_3 + \\dots = $（ ）。",
        "options": {
            "A": "16",
            "B": "20",
            "C": "24",
            "D": "28",
            "E": "30"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "将 6 张不同的卡片 2 张一组分别装入甲、乙、丙 3 个袋中，若指定的两张卡片要在同一组，则不同的装法有（ ）种。",
        "options": {
            "A": "12",
            "B": "18",
            "C": "24",
            "D": "30",
            "E": "36"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "甲、乙两人进行围棋比赛，约定先胜 2 盘者赢得比赛。已知每盘棋甲获胜的概率是 0.6，乙获胜的概率是 0.4。若乙在第一盘获胜，则甲赢得比赛的概率为（ ）。",
        "options": {
            "A": "0.144",
            "B": "0.288",
            "C": "0.36",
            "D": "0.4",
            "E": "0.6"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "已知圆 $C: x^2 + (y-a)^2 = b$，若圆 $C$ 在点 $(1,2)$ 处的切线与 $y$ 轴的交点为 $(0,3)$，则 $ab = $（ ）。",
        "options": {
            "A": "-2",
            "B": "-1",
            "C": "0",
            "D": "1",
            "E": "2"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "羽毛球队有 4 名男运动员和 3 名女运动员，从中选出两对参加混双比赛，则不同的选派方式有（ ）种。",
        "options": {
            "A": "9",
            "B": "18",
            "C": "24",
            "D": "36",
            "E": "72"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "从标号为 1 到 10 的 10 张卡片中随机抽取 2 张，它们的标号之和能被 5 整除的概率为（ ）。",
        "options": {
            "A": "1/5",
            "B": "1/9",
            "C": "2/9",
            "D": "2/15",
            "E": "7/45"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "某单位为检查 3 个部门的工作，由这 3 个部门的主任和外聘的 3 名人员组成检查组，分 2 人一组检查工作，每组有 1 名外聘成员。规定本部门主任不能检查本部门，则不同的安排方式有（ ）种。",
        "options": {
            "A": "6",
            "B": "8",
            "C": "12",
            "D": "18",
            "E": "36"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "如图3所示，圆柱体的底面半径为 2，高为 3，垂直于底面的平面截圆柱体所得截面为矩形 $ABCD$。若弦 $AB$ 所对的圆心角是 $\\frac{\\pi}{3}$，则截掉部分（较小部分）的体积为（ ）。",
        "options": {
            "A": "$\\pi - 3$",
            "B": "$2\\pi - 6$",
            "C": "$\\pi - \\frac{3\\sqrt{3}}{2}$",
            "D": "$2\\pi - 3\\sqrt{3}$",
            "E": "$\\pi - \\sqrt{3}$"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "函数 $f(x) = \\max\\{x^2, -x^2 + 8\\}$ 的最小值为（ ）。",
        "options": {
            "A": "8",
            "B": "7",
            "C": "6",
            "D": "5",
            "E": "4"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "设 $x, y$ 为实数，则 $|x+y| \\le 2$。\n(1) $x^2 + y^2 \\le 2$。\n(2) $xy \\le 1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "设 $\{a_n\}$ 为等差数列，则能确定 $a_1 + a_2 + \\dots + a_9$ 的值。\n(1) 已知 $a_1$ 的值。\n(2) 已知 $a_5$ 的值。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "设 $m, n$ 是正整数，则能确定 $m+n$ 的值。\n(1) $\\frac{1}{m} + \\frac{3}{n} = 1$。\n(2) $\\frac{1}{m} + \\frac{2}{n} = 1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "甲、乙、丙三人的年收入成等比数列，则能确定乙的年收入的最大值。\n(1) 已知甲、丙两人的年收入之和。\n(2) 已知甲、丙两人的年收入之积。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "如图4所示，在矩形 $ABCD$ 中，$AE = FC$，则三角形 $AED$ 与四边形 $BCFE$ 能拼接成一个直角三角形。\n(1) $EB = 2FC$。\n(2) $ED = EF$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "甲购买了若干件 A 玩具、乙购买了若干件 B 玩具送给幼儿园，甲比乙少花了 100 元。则能确定甲购买的玩具件数。\n(1) 甲与乙共购买了 50 件玩具。\n(2) A 玩具的价格是 B 玩具的 2 倍。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "已知点 $P(m, 0), A(1, 3), B(2, 1)$，点 $(x, y)$ 在三角形 $PAB$ 上，则 $x-y$ 的最小值与最大值分别为 -2 和 1。\n(1) $m \\le 1$。\n(2) $m \\ge -2$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "如果甲公司的年终奖总额增加 $25\\%$，乙公司的年终奖总额减少 $10\\%$，两者相等，则能确定两公司的员工人数之比。\n(1) 甲公司的人均年终奖与乙公司的相同。\n(2) 两公司的员工人数之比与两公司的年终奖总额之比相等。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "设 $a, b$ 为实数，则圆 $x^2 + y^2 = 2y$ 与直线 $x + ay = b$ 不相交。\n(1) $|a-b| > \\sqrt{1+a^2}$。\n(2) $|a+b| > \\sqrt{1+a^2}$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "设函数 $f(x) = x^2 + ax$，则 $f(x)$ 的最小值与 $f[f(x)]$ 的最小值相等。\n(1) $a \\ge 2$。\n(2) $a \\le 0$。",
        "options": COND_OPTIONS
    }
]

# Read PDF text for Q26-57
doc = fitz.open(f"真题部分/{YEAR}年199管综真题.pdf")
pages_text = [doc[p].get_text() for p in range(5, 15)]
raw_all = "\n".join(pages_text)
raw_all = re.sub(rf'{YEAR}\s*年真题[^\n]*\n', '', raw_all)
raw_all = re.sub(r'[5sS][0oO]\s*[\.、．]\s*最终审定', '50．最终审定', raw_all)
all_text = raw_all[raw_all.find("三、逻辑推理"):]

special_opts_2018 = {
    30: {
        "A": "甲周日值日。",
        "B": "乙周六值日。",
        "C": "丁周二值日。",
        "D": "戊周二值日。",
        "E": "己周五值日。"
    },
    31: {
        "A": "甲周一值日。",
        "B": "乙周六值日。",
        "C": "丙周三值日。",
        "D": "戊周日值日。",
        "E": "己周二值日。"
    },
    40: {
        "A": "乙。",
        "B": "丙。",
        "C": "丁。",
        "D": "戊。",
        "E": "庚。"
    },
    41: {
        "A": "甲在第一编队。",
        "B": "乙在第一编队。",
        "C": "丙在第一编队。",
        "D": "戊在第二编队。",
        "E": "庚在第二编队。"
    },
    42: {
        "A": "甲：文学创作最重要的是阅读优秀文学作品。乙：你只见现象，不见本质，文学创作最重要的是观察生活、体验生活。任何优秀的文学作品都来源于火热的社会生活。",
        "B": "甲：做人最重要的是要讲信用。乙：你说得不全面，做人最重要的是要遵纪守法。如果不遵纪守法，就没法讲信用。",
        "C": "甲：作为一部优秀的电视剧，最重要的是能得到广大观众的喜爱。乙：你只见其表，不见其里，作为一部优秀的电视剧最重要的是具有深刻寓意与艺术魅力。没有深刻寓意与艺术魅力，就不能成为优秀的电视剧。",
        "D": "甲：科学研究最重要的是研究内容的创新。乙：你只见内容，不见方法，科学研究最重要的是研究方法的创新。只有实现研究方法的创新，才能真正实现研究内容的创新。",
        "E": "甲：一年中最重要的季节是收获的秋天。乙：你只看结果，不问原因，一年中最重要的季节是播种的春天。没有春天的播种，哪来秋天的收获？"
    },
    43: {
        "A": "若己不言，则人不闻。",
        "B": "若己为，则人会知；若己言，则人会闻。",
        "C": "若能做到盗钟而掩耳，则可言之而人不闻。",
        "D": "若己不为，则人不知。",
        "E": "若能做到捕雀而掩目，则可为之而人不知。"
    },
    44: {
        "A": "2015 年发达国家卷烟消费量同比下降比率高于发展中国家。",
        "B": "2015 年世界其他国家卷烟消费量同比下降比率低于中国。",
        "C": "2015 年世界其他国家卷烟消费量同比下降比率高于中国。",
        "D": "2015 年中国卷烟消费量大于 2013 年。",
        "E": "2015 年中国卷烟消费量恰好等于 2013 年。"
    },
    47: {
        "A": "兰园不在园林的中心。",
        "B": "菊园不在园林的中心。",
        "C": "兰园在园林的中心。",
        "D": "菊园在园林的中心。",
        "E": "梅园不在园林的中心。"
    },
    48: {
        "A": "南门位于菊园。",
        "B": "东门位于竹园。",
        "C": "东门位于梅园。",
        "D": "东门位于松园。",
        "E": "南门位于梅园。"
    },
    52: {
        "A": "有些创新者可能受到惩罚。",
        "B": "有些值得拥有专利的创新产品并没有申请专利。",
        "C": "有些值得拥有专利的产品是模仿。",
        "D": "没有模仿值得拥有专利。",
        "E": "所有的模仿者都受到了惩罚。"
    },
    53: {
        "A": "甲、乙、丙。",
        "B": "乙、丙、丁。",
        "C": "甲、戊、己。",
        "D": "甲、丁、己。",
        "E": "丙、戊、己。"
    },
    55: {
        "A": "施琳。",
        "B": "杨虹。",
        "C": "张芳。",
        "D": "范勇。",
        "E": "王玉。"
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
all_questions = list(math_q_2018)

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
        
    if q in special_opts_2018:
        opts = special_opts_2018[q]
        idx = raw.find("(A)")
        if idx == -1:
            idx = raw.find("CA)")
        stem_part = raw[:idx].strip() if idx != -1 else raw.strip()
    else:
        norm_text = normalize_options(raw)
        opt_parts = list(re.finditer(r'(?:^|\n)\s*([A-E])\.\s*(.*?)(?=(?:\n\s*[A-E]\.|\Z))', norm_text, re.DOTALL))
        stem_part = norm_text[:opt_parts[0].start()].strip() if opt_parts else ""
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
