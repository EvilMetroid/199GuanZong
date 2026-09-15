import json, os, re, fitz

YEAR = 2011
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

math_q_2011 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "已知船在静水中的速度为 28 千米/小时，河水的流速为 2 千米/小时，则此船在相距 78 千米的两地间往返一次所需时间是（ ）小时。",
        "options": {
            "A": "5.9",
            "B": "5.6",
            "C": "5.4",
            "D": "4.4",
            "E": "4"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "若实数 $a, b, c$ 满足 $|a-3| + \\sqrt{3b+5} + (5c-4)^2 = 0$，则 $abc = $（ ）。",
        "options": {
            "A": "-4",
            "B": "-4/5",
            "C": "-4/3",
            "D": "-4/15",
            "E": "3"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "某年级 60 名学生中，有 30 人参加合唱团，45 人参加运动队，其中参加合唱团而未参加运动队的有 8 人，则参加运动队而未参加合唱团的有（ ）人。",
        "options": {
            "A": "15 人",
            "B": "22 人",
            "C": "23 人",
            "D": "30 人",
            "E": "37 人"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "现有一个半径为 $R$ 的球体，拟用刨床将其加工成正方体，则能加工成的最大正方体的体积是（ ）。",
        "options": {
            "A": "$\\frac{8}{3}R^3$",
            "B": "$\\frac{8\\sqrt{3}}{9}R^3$",
            "C": "$\\frac{4\\sqrt{3}}{9}R^3$",
            "D": "$\\frac{\\sqrt{3}}{3}R^3$",
            "E": "$\\frac{\\sqrt{3}}{9}R^3$"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "2007年，某市的全年研究与试验发展（R&D）经费支出 300 亿元，比 2006 年增长 20%，该市的 GDP 为 10000 亿元，比 2006 年增长 10%。2006 年该市的 R&D 经费支出占当年 GDP 的（ ）。",
        "options": {
            "A": "1.75%",
            "B": "2%",
            "C": "2.5%",
            "D": "2.75%",
            "E": "3%"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "现从 5 名管理专业、4 名经济专业和 1 名财会专业的学生中，随机选出 2 名学生，则这 2 名学生专业不同的概率是（ ）。",
        "options": {
            "A": "1/3",
            "B": "2/5",
            "C": "2/3",
            "D": "13/18",
            "E": "31/45"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "一所四年制大学每年的毕业生 7 月份离校，新生 9 月份入学。该校 2001 年招生 2000 名，之后每年比上一年多招 200 名，则该校 2007 年 9 月底的在校学生有（ ）名。",
        "options": {
            "A": "14000 名",
            "B": "11600 名",
            "C": "9000 名",
            "D": "6200 名",
            "E": "3200 名"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "将 2 个红球与 1 个白球随机地放入甲、乙、丙三个盒子中，则乙盒中至少有 1 个红球的概率为（ ）。",
        "options": {
            "A": "1/9",
            "B": "8/27",
            "C": "4/9",
            "D": "5/9",
            "E": "17/27"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "如图1所示，四边形 $ABCD$ 是边长为 1 的正方形，弧 $AOB$、$BOC$、$COD$、$DOA$ 均为半圆，则阴影部分的面积为（ ）。",
        "options": {
            "A": "$2 - \\frac{\\pi}{2}$",
            "B": "$\\frac{\\pi}{2} - 1$",
            "C": "$1 - \\frac{\\pi}{4}$",
            "D": "$\\frac{\\pi}{4} - \\frac{1}{2}$",
            "E": "$\\frac{\\pi}{8}$"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "3个3口之家一起观看演出，他们购买了同一排的 9 张连座票，则每一家的人都坐在一起的不同坐法有（ ）种。",
        "options": {
            "A": "$(3!)^2$",
            "B": "$(3!)^3$",
            "C": "$3(3!)^3$",
            "D": "$(3!)^4$",
            "E": "$9!$"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "设 $P$ 是圆 $x^2 + y^2 = 2$ 上的一点，该圆在点 $P$ 的切线平行于直线 $x+y+2=0$，则点 $P$ 的坐标为（ ）。",
        "options": {
            "A": "(-1, 1)",
            "B": "(1, -1)",
            "C": "(0, \\sqrt{2})",
            "D": "(\\sqrt{2}, 0)",
            "E": "(1, 1)"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "设 $a, b, c$ 是小于 12 的三个不同的质数（素数），且 $|a-b| + |b-c| + |c-a| = 8$，则 $a+b+c = $（ ）。",
        "options": {
            "A": "10",
            "B": "12",
            "C": "14",
            "D": "15",
            "E": "19"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "在年底的献爱心活动中，某单位共有 100 人参加捐款，经统计，捐款总额是 19000 元，个人捐款数额有 100 元、500 元和 2000 元三种，该单位捐款 500 元的人数为（ ）人。",
        "options": {
            "A": "13",
            "B": "18",
            "C": "25",
            "D": "30",
            "E": "38"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "某施工队承担了开凿一条长为 2400 米隧道的工程，在掘进了 400 米后，由于改进了施工工艺，每天比原计划多掘进 2 米，最后提前 50 天完成了施工任务，原计划施工工期是（ ）天。",
        "options": {
            "A": "200 天",
            "B": "240 天",
            "C": "250 天",
            "D": "300 天",
            "E": "350 天"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "已知 $x^2 + y^2 = 9, xy = 4$，则 $\\frac{x^3 + y^3 + x + y}{x+y} = $（ ）。",
        "options": {
            "A": "1",
            "B": "2",
            "C": "$\\sqrt{17}$",
            "D": "6",
            "E": "10"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "实数 $a, b, c$ 成等差数列。\n(1) $e^a, e^b, e^c$ 成等比数列。\n(2) $\\ln a, \\ln b, \\ln c$ 成等差数列。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "在一次英语考试中，某班的及格率为 80%。\n(1) 男生及格率为 70%，女生及格率为 90%。\n(2) 男生人数与女生人数之比为 $1:1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "如图2所示，等腰梯形的上底与腰均为 $x$，下底为 $x+10$。则 $x = 13$。\n(1) 该梯形的上底与下底之比为 $13:23$。\n(2) 该梯形的面积为 216。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "现有 3 名男生和 2 名女生参加面试，则面试的排序方法有 24 种。\n(1) 第一位面试的是女生。\n(2) 第二位面试的是指定的某位男生。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "已知 $\\triangle ABC$ 的三条边分别为 $a, b, c$，则 $\\triangle ABC$ 是等腰直角三角形。\n(1) $(a-b)(c^2 - a^2 - b^2) = 0$。\n(2) $c = \\sqrt{2}b$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "直线 $ax + by + 3 = 0$ 被圆 $(x-2)^2 + (y-1)^2 = 4$ 截得的线段长度为 $2\\sqrt{3}$。\n(1) $a = 0, b = -1$。\n(2) $a = -1, b = 0$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "已知实数 $a, b, c, d$ 满足 $a^2 + b^2 = 1, c^2 + d^2 = 1$。则 $|ac + bd| < 1$。\n(1) 直线 $ax + by = 1$ 与 $cx + dy = 1$ 仅有一个交点。\n(2) $a \\neq c, b \\neq d$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "某年级共有 8 个班，在一次年级考试中，共有 21 名学生不及格，每班不及格的学生最多有 3 名，则（一）班至少有 1 名学生不及格。\n(1) （二）班的不及格人数多于（三）班。\n(2) （四）班不及格的学生有 2 名。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "现有一批文字材料需要打印，两台新型打印机单独完成此任务分别需要 4 小时与 5 小时，两台旧型打印机单独完成此任务分别需要 9 小时与 11 小时，则能在 2.5 小时内完成任务。\n(1) 安排两台新型打印机同时打印。\n(2) 安排一台新型打印机与两台旧型打印机同时打印。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "已知 $\{a_n\}$ 为等差数列，则该数列的公差为零。\n(1) 对任何正整数 $n$，都有 $a_1 + a_2 + \\dots + a_n \\le n a_n$。\n(2) 对任何正整数 $n$，都有 $a_n \\ge a_{n-1}$。",
        "options": COND_OPTIONS
    }
]

# Read PDF text for Q26-57
doc = fitz.open(f"真题部分/{YEAR}年199管综真题.pdf")
pages_text = [doc[p].get_text() for p in range(3, 14)]
all_text = "\n".join(pages_text)
all_text = re.sub(rf'{YEAR}\s*年真题[^\n]*\n', '', all_text)

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
all_questions = list(math_q_2011)

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
