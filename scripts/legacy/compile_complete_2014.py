import json, os, re, fitz

YEAR = 2014
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

math_q_2014 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "某部门在一次联欢活动中共设了 26 个奖，奖品均价为 280 元，其中一等奖单价为 400 元，其他奖品均价为 270 元，一等奖的个数为（ ）。",
        "options": {
            "A": "6",
            "B": "5",
            "C": "4",
            "D": "3",
            "E": "2"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "某单位进行办公室装修，若甲、乙两个装修公司合作，需 10 周完成，工时费为 100 万元；甲公司单独做 6 周后由乙公司接着做 18 周完成，工时费为 96 万元。甲公司每周的工时费为（ ）。",
        "options": {
            "A": "7.5 万元",
            "B": "7 万元",
            "C": "6.5 万元",
            "D": "6 万元",
            "E": "5.5 万元"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "如图1所示，已知 $AE = 3AB, BF = 2BC$。若 $\\triangle ABC$ 的面积是 2，则 $\\triangle AEF$ 的面积为（ ）。",
        "options": {
            "A": "14",
            "B": "12",
            "C": "10",
            "D": "8",
            "E": "6"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "某公司投资一个项目，已知上半年完成了预算的 $\\frac{1}{3}$，下半年完成了剩余部分的 $\\frac{2}{3}$，此时还有 8 千万元投资未完成，则该项目的预算为（ ）。",
        "options": {
            "A": "3 亿元",
            "B": "3.6 亿元",
            "C": "3.9 亿元",
            "D": "4.5 亿元",
            "E": "5.1 亿元"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "如图2所示，圆 $A$ 和圆 $B$ 的半径均为 1，则阴影部分的面积为（ ）。",
        "options": {
            "A": "$\\frac{2\\pi}{3} - \\frac{\\sqrt{3}}{2}$",
            "B": "$\\frac{\\pi}{3} - \\frac{\\sqrt{3}}{4}$",
            "C": "$\\frac{2\\pi}{3} - \\frac{\\sqrt{3}}{4}$",
            "D": "$\\frac{\\pi}{3} - \\frac{\\sqrt{3}}{2}$",
            "E": "$\\frac{2\\pi}{3} - \\frac{\\sqrt{3}}{8}$"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "某容器中装满了浓度为 90% 的酒精，倒出 1 升后用水将容器注满，搅拌均匀后又倒出 1 升，再用水将容器注满，已知此时酒精浓度为 40%，则该容器的容积是（ ）升。",
        "options": {
            "A": "2.5",
            "B": "3",
            "C": "3.5",
            "D": "4",
            "E": "4.5"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "已知 $\{a_n\}$ 为等差数列，且 $a_2 - a_5 + a_8 = 9$，则 $a_1 + a_2 + \\dots + a_9 = $（ ）。",
        "options": {
            "A": "27",
            "B": "45",
            "C": "54",
            "D": "81",
            "E": "162"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "甲、乙两人上午 8:00 分别自 $A, B$ 出发相向而行，9:00 第一次相遇，9:30 时两人相距 10.5 公里，甲到 $B$、乙到 $A$ 后都立刻沿原路返回。若两人在 10:30 第二次相遇，则 $A, B$ 两地的距离为（ ）。",
        "options": {
            "A": "5.6 公里",
            "B": "7 公里",
            "C": "8 公里",
            "D": "9 公里",
            "E": "9.5 公里"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "掷一枚均匀的硬币若干次，当正面向上次数大于反面向上次数时停止，则在 4 次之内停止的概率为（ ）。",
        "options": {
            "A": "1/8",
            "B": "3/8",
            "C": "5/8",
            "D": "3/16",
            "E": "11/16"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "若几个质数（素数）的乘积为 770，则它们的和为（ ）。",
        "options": {
            "A": "85",
            "B": "84",
            "C": "28",
            "D": "26",
            "E": "25"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "已知直线 $l$ 是圆 $x^2 + y^2 = 5$ 在点 $(1, 2)$ 处的切线，则 $l$ 在 $y$ 轴上的截距为（ ）。",
        "options": {
            "A": "2/5",
            "B": "2/3",
            "C": "3/2",
            "D": "5/2",
            "E": "5"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "如图3所示，正方体 $ABCD-A'B'C'D'$ 的棱长为 2，$F$ 是棱 $C'D'$ 的中点，则 $AF$ 的长为（ ）。",
        "options": {
            "A": "3",
            "B": "5",
            "C": "$\\sqrt{5}$",
            "D": "$2\\sqrt{2}$",
            "E": "$2\\sqrt{3}$"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "在某项活动中，将 3 男 3 女 6 名志愿者随机地分成甲、乙、丙三组，每组 2 人，则每组中均有男有女的概率为（ ）。",
        "options": {
            "A": "1/90",
            "B": "1/15",
            "C": "1/5",
            "D": "2/5",
            "E": "4/5"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "某工厂在半径为 5 厘米的球形工艺品上镀一层装饰金属，厚度为 0.01 厘米，已知该工艺品的表面积为 $S$ 平方厘米，体积为 $V$ 立方厘米，则镀层金属的体积约为（ ）立方厘米。",
        "options": {
            "A": "0.01S",
            "B": "0.02S",
            "C": "0.05S",
            "D": "0.01V",
            "E": "0.02V"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "某单位决定对 4 个部门的经理进行轮岗，要求每位经理必须轮换到 4 个部门中的其他部门任职，则不同的轮岗方案有（ ）种。",
        "options": {
            "A": "3",
            "B": "6",
            "C": "8",
            "D": "9",
            "E": "10"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "已知曲线 $l: y = a + bx - 6x^2 + x^3$，则 $(a+b-5)(a-b-5) = 0$。\n(1) 曲线 $l$ 过点 $(1, 0)$。\n(2) 曲线 $l$ 过点 $(-1, 0)$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "不等式 $|x^2 + 2x + a| \\le 1$ 的解集为空集。\n(1) $a < 0$。\n(2) $a > 2$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "甲、乙、丙三人的年龄相同。\n(1) 甲、乙、丙的年龄成等差数列。\n(2) 甲、乙、丙的年龄成等比数列。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "设 $x$ 是非零实数，则 $\\frac{1}{x^3} + x^3 = 18$。\n(1) $\\frac{1}{x} + x = 3$。\n(2) $\\frac{1}{x^2} + x^2 = 7$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "如图4所示，$O$ 是半圆的圆心，$C$ 是半圆上的一点，$OD \\perp AC$，则能确定 $OD$ 的长。\n(1) 已知 $BC$ 的长。\n(2) 已知 $AO$ 的长。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "方程 $x^2 + 2(a+b)x + c^2 = 0$ 有实根。\n(1) $a, b, c$ 是一个三角形的三边长。\n(2) 实数 $a, c, b$ 成等差数列。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "已知二次函数 $f(x) = ax^2 + bx + c$，则能确定 $a, b, c$ 的值。\n(1) 曲线 $y = f(x)$ 经过点 $(0, 0)$ 和点 $(1, 1)$。\n(2) 曲线 $y = f(x)$ 与直线 $y = -1$ 相切。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "已知袋中装有红、黑、白三种颜色的球若干个，则红球最多。\n(1) 随机取出的一球是白球的概率为 2/5。\n(2) 随机取出的两球中至少有一个黑球的概率小于 1/5。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "已知 $M = \\{a, b, c, d, e\\}$ 是一个整数集合。则能确定集合 $M$。\n(1) $a, b, c, d, e$ 的平均值为 3。\n(2) $a, b, c, d, e$ 任意两个数之和所组成的集合为 $\\{1, 2, 3, 4, 5, 6, 7, 8, 9\\}$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "已知 $x, y$ 为实数。则 $x^2 + y^2 \\ge 1$。\n(1) $4y - 3x \\ge 5$。\n(2) $(x-1)^2 + (y-1)^2 \\ge 5$。",
        "options": COND_OPTIONS
    }
]

# Read PDF text for Q26-57
doc = fitz.open(f"真题部分/{YEAR}年199管综真题.pdf")
pages_text = [doc[p].get_text() for p in range(4, 13)]
raw_all = "\n".join(pages_text)
raw_all = re.sub(rf'{YEAR}\s*年真题[^\n]*\n', '', raw_all)
all_text = raw_all[raw_all.find("三、逻辑推理"):]

q_positions = {}
for q in range(26, 58):
    q_pat = r'(?:^|\n)\s*' + r'\s*'.join(str(q)) + r'[\.、．\s]'
    m = re.search(q_pat, all_text)
    if m:
        q_positions[q] = m.start()
    else:
        print(f"Missing position for Q{q}!")

sorted_qs = sorted(q_positions.keys())
all_questions = list(math_q_2014)

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
        if q == 54:
            opts = {
                "A": "墨灵参加国际象棋比赛。",
                "B": "庄聪参加中国象棋比赛。",
                "C": "孔智参加围棋比赛。",
                "D": "荀慧参加围棋比赛。",
                "E": "韩敏参加中国象棋比赛。"
            }
        elif q == 55:
            opts = {
                "A": "庄聪和韩敏参加中国象棋比赛。",
                "B": "韩敏和荀慧参加中国象棋比赛。",
                "C": "孔智和孟睿参加围棋比赛。",
                "D": "墨灵和孟睿参加围棋比赛。",
                "E": "韩敏和孔智参加围棋比赛。"
            }
        all_questions.append({
            "question_no": q,
            "category": "逻辑推理",
            "stem": stem_part,
            "options": opts
        })
    else:
        if q == 54:
            stem_clean = raw.split("A.")[0].split("(A)")[0].strip()
            all_questions.append({
                "question_no": 54,
                "category": "逻辑推理",
                "stem": stem_clean,
                "options": {
                    "A": "墨灵参加国际象棋比赛。",
                    "B": "庄聪参加中国象棋比赛。",
                    "C": "孔智参加围棋比赛。",
                    "D": "荀慧参加围棋比赛。",
                    "E": "韩敏参加中国象棋比赛。"
                }
            })
        else:
            all_questions.append({
                "question_no": q,
                "category": "逻辑推理",
                "stem": raw,
                "options": {}
            })

print(f"Total questions compiled: {len(all_questions)}")

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
