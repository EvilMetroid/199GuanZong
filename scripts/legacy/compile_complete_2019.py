import json, os, re, fitz

YEAR = 2019
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

math_q_2019 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "某车间计划 10 天完成一项任务，工作 3 天后因故停工 2 天。若仍要按原计划完成任务，则工作效率需要提高（ ）。",
        "options": {
            "A": "20%",
            "B": "30%",
            "C": "40%",
            "D": "50%",
            "E": "60%"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "设函数 $f(x) = 2x + \\frac{a}{x^2} (a > 0)$ 在 $(0, +\\infty)$ 内的最小值为 $f(x_0) = 12$，则 $x_0 = $（ ）。",
        "options": {
            "A": "5",
            "B": "4",
            "C": "3",
            "D": "2",
            "E": "1"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "某影城统计了一季度的观众人数，如图1所示，则一季度的男、女观众人数之比为（ ）。",
        "options": {
            "A": "3 : 4",
            "B": "5 : 6",
            "C": "12 : 13",
            "D": "13 : 12",
            "E": "4 : 3"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "设实数 $a, b$ 满足 $ab = 6, |a+b| + |a-b| = 6$，则 $a^2 + b^2 = $（ ）。",
        "options": {
            "A": "10",
            "B": "11",
            "C": "12",
            "D": "13",
            "E": "14"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "设圆 $C$ 与圆 $(x-5)^2 + y^2 = 2$ 关于直线 $y = 2x$ 对称，则圆 $C$ 的方程为（ ）。",
        "options": {
            "A": "$(x-3)^2 + (y-4)^2 = 2$",
            "B": "$(x+4)^2 + (y-3)^2 = 2$",
            "C": "$(x-3)^2 + (y+4)^2 = 2$",
            "D": "$(x+3)^2 + (y+4)^2 = 2$",
            "E": "$(x+3)^2 + (y-4)^2 = 2$"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "将一批树苗种在一个正方形花园的边上，四角都种。如果每隔 3 米种一棵，那么剩余 10 棵树苗；如果每隔 2 米种一棵，那么恰好种满正方形的 3 条边，则这批树苗有（ ）棵。",
        "options": {
            "A": "54",
            "B": "60",
            "C": "70",
            "D": "82",
            "E": "94"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "在分别标记了数字 1, 2, 3, 4, 5, 6 的 6 张卡片中，甲随机抽取 1 张后，乙从余下的卡片中再随机抽取 2 张，乙的卡片数字之和大于甲的卡片数字的概率为（ ）。",
        "options": {
            "A": "11/60",
            "B": "13/60",
            "C": "43/60",
            "D": "47/60",
            "E": "49/60"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "10 名同学的语文和数学成绩如表1所示：\n\n| | | | | | | | | | | |\n| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n| **语文成绩** | 90 | 92 | 94 | 88 | 86 | 95 | 87 | 89 | 91 | 93 |\n| **数学成绩** | 94 | 88 | 96 | 93 | 90 | 85 | 84 | 80 | 82 | 98 |\n\n语文和数学成绩的均值分别记为 $E_1$ 和 $E_2$，标准差分别记为 $\\sigma_1$ 和 $\\sigma_2$，则（ ）。",
        "options": {
            "A": "$E_1 > E_2, \\sigma_1 > \\sigma_2$",
            "B": "$E_1 > E_2, \\sigma_1 < \\sigma_2$",
            "C": "$E_1 > E_2, \\sigma_1 = \\sigma_2$",
            "D": "$E_1 < E_2, \\sigma_1 > \\sigma_2$",
            "E": "$E_1 < E_2, \\sigma_1 < \\sigma_2$"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "如图2所示，正方体位于半径为 3 的球内，且一面位于球的大圆上，则正方体表面积最大为（ ）。",
        "options": {
            "A": "12",
            "B": "18",
            "C": "24",
            "D": "30",
            "E": "36"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "在三角形 $ABC$ 中，$AB = 4, AC = 6, BC = 8, D$ 为 $BC$ 的中点，则 $AD = $（ ）。",
        "options": {
            "A": "$\\sqrt{11}$",
            "B": "$\\sqrt{10}$",
            "C": "3",
            "D": "$2\\sqrt{2}$",
            "E": "$\\sqrt{5}$"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "某单位要铺设草坪，若甲、乙两公司合作需要 6 天完成，工时费共计 2.4 万元；若甲公司单独做 4 天后由乙公司接着做 9 天完成，工时费共计 2.35 万元。若由甲公司单独完成该项目，则工时费共计（ ）万元。",
        "options": {
            "A": "2.25",
            "B": "2.35",
            "C": "2.4",
            "D": "2.45",
            "E": "2.5"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "如图3所示，六边形 $ABCDEF$ 是平面与棱长为 2 的正方体所截得到的，若 $A, B, D, E$ 分别为相应棱的中点，则六边形 $ABCDEF$ 的面积为（ ）。",
        "options": {
            "A": "$\\frac{\\sqrt{3}}{2}$",
            "B": "$\\sqrt{3}$",
            "C": "$2\\sqrt{3}$",
            "D": "$3\\sqrt{3}$",
            "E": "$4\\sqrt{3}$"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "货车行驶 72 km 用时 1 h，其速度 $v$ 与行驶时间 $t$ 的关系如图4所示，则 $v_0 = $（ ）。",
        "options": {
            "A": "72",
            "B": "80",
            "C": "90",
            "D": "95",
            "E": "100"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "某中学的 5 个学科各推荐 2 名教师作为支教候选人，若从中选派来自不同学科的 2 人参加支教工作，则不同的选派方式有（ ）种。",
        "options": {
            "A": "20",
            "B": "24",
            "C": "30",
            "D": "40",
            "E": "45"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "设数列 $\{a_n\}$ 满足 $a_1 = 0, a_{n+1} - 2a_n = 1$，则 $a_{100} = $（ ）。",
        "options": {
            "A": "$2^{99} - 1$",
            "B": "$2^{99}$",
            "C": "$2^{99} + 1$",
            "D": "$2^{100} - 1$",
            "E": "$2^{100} + 1$"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "甲、乙、丙三人各自拥有不超过 10 本图书，甲再购入 2 本图书后，他们拥有的图书数量能构成等比数列，则能确定甲拥有图书的数量。\n(1) 已知乙拥有的图书数量。\n(2) 已知丙拥有的图书数量。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "有甲、乙两袋奖券，获奖率分别是 $p$ 和 $q$。某人从两袋中各随机抽取 1 张奖券，则此人获奖的概率不小于 $\\frac{3}{4}$。\n(1) 已知 $p + q = 1$。\n(2) 已知 $pq = \\frac{1}{4}$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "直线 $y = kx$ 与圆 $x^2 + y^2 - 4x + 3 = 0$ 有两个交点。\n(1) $-\\frac{\\sqrt{3}}{3} < k < 0$。\n(2) $0 < k < \\frac{\\sqrt{2}}{2}$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "能确定小明的年龄。\n(1) 小明的年龄是完全平方数。\n(2) 20 年后小明的年龄是完全平方数。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "关于 $x$ 的方程 $x^2 + ax + b - 1 = 0$ 有实根。\n(1) $a + b = 0$。\n(2) $a - b = 0$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "如图5所示，已知正方形 $ABCD$ 的面积，$O$ 为 $BC$ 上一点，$P$ 为 $AO$ 的中点，$Q$ 为 $DO$ 上一点，则能确定三角形 $PQD$ 的面积。\n(1) $O$ 为 $BC$ 的三等分点。\n(2) $Q$ 为 $DO$ 的三等分点。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "设 $n$ 为正整数，则能确定 $n$ 除以 5 的余数。\n(1) 已知 $n$ 除以 2 的余数。\n(2) 已知 $n$ 除以 3 的余数。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "某校理学院五个系每年的录取人数如表2所示：\n\n| 系别 | 数学系 | 物理系 | 化学系 | 生物系 | 地学系 |\n| :--- | :--- | :--- | :--- | :--- | :--- |\n| **录取人数** | 60 | 120 | 90 | 60 | 30 |\n\n今年与去年相比，物理系的录取平均分没变，则理学院的录取平均分升高了。\n(1) 数学系的录取平均分升高了 3 分，生物系的录取平均分降低了 2 分。\n(2) 化学系的录取平均分升高了 1 分，地学系的录取平均分降低了 4 分。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "设三角区域 $D$ 由直线 $x + 8y - 56 = 0, x - 6y + 42 = 0$ 与 $kx - y + 8 - 6k = 0 (k < 0)$ 围成，则对任意的 $(x, y) \\in D$，有 $\\lg(x^2 + y^2) \\le 2$。\n(1) $k \\in (-\\infty, -1]$。\n(2) $k \\in [-1, -\\frac{1}{8})$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "设数列 $\{a_n\}$ 的前 $n$ 项和为 $S_n$，则数列 $\{a_n\}$ 是等差数列。\n(1) $S_n = n^2 + 2n, n=1, 2, 3, \\dots$。\n(2) $S_n = n^2 + 2n + 1, n=1, 2, 3, \\dots$。",
        "options": COND_OPTIONS
    }
]

# Read PDF text for Q26-57
doc = fitz.open(f"真题部分/{YEAR}年199管综真题.pdf")
pages_text = [doc[p].get_text() for p in range(4, 14)]
raw_all = "\n".join(pages_text)
raw_all = re.sub(rf'{YEAR}\s*年真题[^\n]*\n', '', raw_all)
all_text = raw_all[raw_all.find("三、逻辑推理"):]

special_opts_2019 = {
    30: {
        "A": "赵丙、邓丁、刘戊。",
        "B": "陈甲、傅乙、赵丙。",
        "C": "傅乙、邓丁、刘戊。",
        "D": "邓丁、刘戊、张己。",
        "E": "陈甲、赵丙、刘戊。"
    },
    31: {
        "A": "派遣刘戊。",
        "B": "派遣赵丙。",
        "C": "派遣陈甲。",
        "D": "派遣傅乙。",
        "E": "派遣邓丁。"
    },
    33: {
        "A": "结构如图 A 所示（详见试题配图）",
        "B": "结构如图 B 所示（详见试题配图）",
        "C": "结构如图 C 所示（详见试题配图）",
        "D": "结构如图 D 所示（详见试题配图）",
        "E": "结构如图 E 所示（详见试题配图）"
    },
    50: {
        "A": "芹菜、红椒与扁豆在同一组。",
        "B": "菠菜、黄椒与豇豆在同一组。",
        "C": "韭菜、黄瓜与毛豆在同一组。",
        "D": "菠菜、冬瓜与豇豆在同一组。",
        "E": "芹菜、红椒与丝瓜在同一组。"
    }
}

q_positions = {}
for q in range(26, 58):
    if q == 51:
        m = re.search(r'(?:^|\n)\s*51\s*[\.、．]\s*《淮南子', all_text)
    else:
        q_pat = r'(?:^|\n)\s*' + r'\s*'.join(str(q)) + r'[\.、．\s]'
        m = re.search(q_pat, all_text)
    if m:
        q_positions[q] = m.start()
    else:
        print(f"Missing position for Q{q}!")

sorted_qs = sorted(q_positions.keys())
all_questions = list(math_q_2019)

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
        
    if q in special_opts_2019:
        opts = special_opts_2019[q]
        if q == 33:
            stem_part = raw[:raw.find("(A)")].strip()
        elif q in [30, 31, 50]:
            stem_part = raw[:raw.find("(A)")].strip()
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
