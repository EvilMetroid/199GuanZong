import json, os, re, fitz

YEAR = 2015
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

math_q_2015 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "若实数 $a, b, c$ 满足 $a:b:c = 1:2:5$，且 $a+b+c = 24$，则 $a^2 + b^2 + c^2 = $（ ）。",
        "options": {
            "A": "30",
            "B": "90",
            "C": "120",
            "D": "240",
            "E": "270"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "某公司共有甲、乙两个部门，如果从甲部门调 10 人到乙部门，那么乙部门人数是甲部门的 2 倍；如果把乙部门员工的 $\\frac{1}{5}$ 调到甲部门，那么两个部门的人数相等。该公司的总人数为（ ）。",
        "options": {
            "A": "150",
            "B": "180",
            "C": "200",
            "D": "240",
            "E": "250"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "设 $m, n$ 是小于 20 的质数，满足条件 $|m - n| = 2$ 的 $\{m, n\}$ 共有（ ）。",
        "options": {
            "A": "2 组",
            "B": "3 组",
            "C": "4 组",
            "D": "5 组",
            "E": "6 组"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "如图1所示，$BC$ 是半圆的直径，且 $BC = 4, \\angle ABC = 30^\\circ$，则图中阴影部分的面积为（ ）。",
        "options": {
            "A": "$\\frac{4\\pi}{3} - \\sqrt{3}$",
            "B": "$\\frac{4\\pi}{3} - 2\\sqrt{3}$",
            "C": "$\\frac{2\\pi}{3} + \\sqrt{3}$",
            "D": "$\\frac{2\\pi}{3} + 2\\sqrt{3}$",
            "E": "$2\\pi - 2\\sqrt{3}$"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "有一根圆柱形铁管，管壁厚度为 0.1 米，内径为 1.8 米，长度为 2 米。若将该铁管熔化后浇铸成长方体，则该长方体的体积为（ ）（单位：立方米，$\\pi \\approx 3.14$）。",
        "options": {
            "A": "0.38",
            "B": "0.59",
            "C": "1.19",
            "D": "5.09",
            "E": "6.28"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "某人驾车从 A 地赶往 B 地，前一半路程比计划多用时 45 分钟，平均速度只有计划的 80%；若后一半路程的平均速度为 120 千米/小时，此人还能按原定时间到达 B 地，则 A、B 两地的距离为（ ）千米。",
        "options": {
            "A": "450",
            "B": "480",
            "C": "520",
            "D": "540",
            "E": "600"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "在某次考试中，甲、乙、丙三个班的平均成绩分别为 80、81 和 81.5，三个班的学生得分之和为 6952，则三个班共有学生（ ）人。",
        "options": {
            "A": "85",
            "B": "86",
            "C": "87",
            "D": "88",
            "E": "89"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "如图2所示，梯形 $ABCD$ 的上底与下底分别为 5、7，$E$ 为 $AC$ 和 $BD$ 的交点，$MN$ 过点 $E$ 且平行于 $AD$，则 $MN = $（ ）。",
        "options": {
            "A": "$\\frac{35}{6}$",
            "B": "$\\frac{11}{2}$",
            "C": "$\\frac{26}{5}$",
            "D": "$\\frac{36}{7}$",
            "E": "$\\frac{40}{7}$"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "一项工作，甲、乙合作需要 2 天，人工费 2900 元；乙、丙合作需要 4 天，人工费 2600 元；甲、丙合作 2 天完成了全部工作量的 $\\frac{5}{6}$，人工费 2400 元。甲单独做该工作需要的时间和人工费分别为（ ）。",
        "options": {
            "A": "3 天，3000 元",
            "B": "3 天，2850 元",
            "C": "3 天，2700 元",
            "D": "4 天，3000 元",
            "E": "4 天，2900 元"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "已知 $x_1, x_2$ 是 $x^2 + ax - 1 = 0$ 的两个实根，则 $x_1^2 + x_2^2 = $（ ）。",
        "options": {
            "A": "$a^2 + 2$",
            "B": "$a^2 + 1$",
            "C": "$a^2 - 1$",
            "D": "$a^2 - 2$",
            "E": "$a + 2$"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "某新兴产业在 2005 年年末至 2009 年年末产值的年平均增长率为 $q$，在 2009 年年末至 2013 年年末产值的年平均增长率比前四年下降了 40%，2013 年的产值约为 2005 年产值的 $14.46 (\\approx 1.95^4)$ 倍，则 $q$ 约为（ ）。",
        "options": {
            "A": "30%",
            "B": "35%",
            "C": "40%",
            "D": "45%",
            "E": "50%"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "若直线 $y = ax$ 与圆 $(x-a)^2 + y^2 = 1$ 相切，则 $a^2 = $（ ）。",
        "options": {
            "A": "$\\frac{1+\\sqrt{3}}{2}$",
            "B": "$1 + \\frac{\\sqrt{3}}{2}$",
            "C": "$\\frac{\\sqrt{5}-1}{2}$",
            "D": "$1 + \\frac{\\sqrt{5}}{2}$",
            "E": "$\\frac{1+\\sqrt{5}}{2}$"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "设点 $A(0,2)$ 和 $B(1,0)$，在线段 $AB$ 上取一点 $M(x,y) (0 < x < 1)$，则以 $x, y$ 为两边长的矩形面积的最大值为（ ）。",
        "options": {
            "A": "$\\frac{5}{8}$",
            "B": "$\\frac{1}{2}$",
            "C": "$\\frac{3}{8}$",
            "D": "$\\frac{1}{4}$",
            "E": "$\\frac{1}{8}$"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "某次网球比赛的四强对阵为甲对乙、丙对丁，两场比赛的胜者将争夺冠军，选手之间相互获胜的概率如表1所示：\n\n| | 甲 | 乙 | 丙 | 丁 |\n| :--- | :--- | :--- | :--- | :--- |\n| **甲获胜概率** | \\ | 0.3 | 0.3 | 0.8 |\n| **乙获胜概率** | 0.7 | \\ | 0.6 | 0.3 |\n| **丙获胜概率** | 0.7 | 0.4 | \\ | 0.5 |\n| **丁获胜概率** | 0.2 | 0.7 | 0.5 | \\ |\n\n则甲获得冠军的概率为（ ）。",
        "options": {
            "A": "0.165",
            "B": "0.245",
            "C": "0.275",
            "D": "0.315",
            "E": "0.330"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "平面上有 5 条平行直线与另一组 $n$ 条平行直线垂直，若两组平行直线共构成 280 个矩形，则 $n = $（ ）。",
        "options": {
            "A": "5",
            "B": "6",
            "C": "7",
            "D": "8",
            "E": "9"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "信封中装有 10 张奖券，只有 1 张有奖。从信封中同时抽取 2 张，中奖概率为 $P$；从信封中每次抽取 1 张奖券后放回，如此重复抽取 $n$ 次，中奖概率为 $Q$，则 $P < Q$。\n(1) $n = 2$。\n(2) $n = 3$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "已知 $p, q$ 为非零实数，则能确定 $\\frac{p}{q(p-1)}$ 的值。\n(1) $p + q = 1$。\n(2) $\\frac{1}{p} + \\frac{1}{q} = 1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "已知 $a, b$ 为实数，则 $a \\ge 2$ 或 $b \\ge 2$。\n(1) $a + b \\ge 4$。\n(2) $ab \\ge 4$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "圆盘 $x^2 + y^2 \\le 2(x+y)$ 被直线 $L$ 分成面积相等的两部分。\n(1) $L: x + y = 2$。\n(2) $L: 2x - y = 1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "已知 $\{a_n\}$ 是公差大于零的等差数列，$S_n$ 是 $\{a_n\}$ 的前 $n$ 项和，则 $S_n \\ge S_{10}, n=1, 2, \\dots$。\n(1) $a_{10} = 0$。\n(2) $a_{11} a_{10} < 0$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "几个朋友外出游玩，购买了一些瓶装水，则能确定购买的瓶装水数量。\n(1) 若每人分 3 瓶，则剩余 30 瓶。\n(2) 若每人分 10 瓶，则只有 1 人不够。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "已知 $M = (a_1 + a_2 + \\dots + a_{n-1})(a_2 + a_3 + \\dots + a_n)$，$N = (a_1 + a_2 + \\dots + a_n)(a_2 + a_3 + \\dots + a_{n-1})$，则 $M > N$。\n(1) $a_1 > 0$。\n(2) $a_1 a_n > 0$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "设 $\{a_n\}$ 是等差数列，则能确定数列 $\{a_n\}$。\n(1) $a_1 + a_6 = 0$。\n(2) $a_1 a_6 = -1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "已知 $x_1, x_2, x_3$ 都是实数，$\\bar{x}$ 为 $x_1, x_2, x_3$ 的平均数，则 $|x_k - \\bar{x}| \\le 1, k=1, 2, 3$。\n(1) $|x_k| \\le 1, k=1, 2, 3$。\n(2) $x_1 = 0$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "底面半径为 $r$，高为 $h$ 的圆柱体表面积记为 $S_1$，半径为 $R$ 的球体表面积记为 $S_2$，则 $S_1 \\le S_2$。\n(1) $R \\ge \\frac{r+h}{2}$。\n(2) $R \\le \\frac{2h+r}{3}$。",
        "options": COND_OPTIONS
    }
]

# Read PDF text for Q26-57
doc = fitz.open(f"真题部分/{YEAR}年199管综真题.pdf")
pages_text = [doc[p].get_text() for p in range(4, 13)]
raw_all = "\n".join(pages_text)
raw_all = re.sub(rf'{YEAR}\s*年真题[^\n]*\n', '', raw_all)
# Fix Q50 typo in PDF text
raw_all = re.sub(r'[5sS][0oO]\s*[\.、．]\s*有关数据', '50．有关数据', raw_all)
all_text = raw_all[raw_all.find("三、逻辑推理"):]

q_positions = {}
for q in range(26, 58):
    if q == 40:
        m = re.search(r'(?:^|\n)\s*40\s*[\.、．]\s*有些阔叶树', all_text)
    else:
        q_pat = r'(?:^|\n)\s*' + r'\s*'.join(str(q)) + r'[\.、．\s]'
        m = re.search(q_pat, all_text)
    if m:
        q_positions[q] = m.start()
    else:
        print(f"Missing position for Q{q}!")

sorted_qs = sorted(q_positions.keys())
all_questions = list(math_q_2015)

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
            
        stem_clean = re.sub(r'\n(?![（\(0-9一二三四五六七八九十])', '', stem_part)
        all_questions.append({
            "question_no": q,
            "category": "逻辑推理",
            "stem": stem_clean.strip(),
            "options": opts
        })
    else:
        print(f"Warning: Q{q} options parsed count: {len(opt_parts)}")

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
