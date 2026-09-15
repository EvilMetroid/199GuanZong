import json, os, re, fitz

YEAR = 2013
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

math_q_2013 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "某工厂生产一批零件，计划 10 天完成任务，实际提前 2 天完成，则每天的产量比计划平均提高了（ ）。",
        "options": {
            "A": "15%",
            "B": "20%",
            "C": "25%",
            "D": "30%",
            "E": "35%"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "甲、乙两人同时从 A 点出发，沿 400 米跑道同向匀速行走，25 分钟后乙比甲少走了一圈，若乙行走一圈需要 8 分钟，则甲的速度是（ ）（单位：米/分钟）。",
        "options": {
            "A": "62",
            "B": "65",
            "C": "66",
            "D": "67",
            "E": "69"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "甲班共有 30 名学生，在一次满分为 100 分的考试中，全班的平均成绩为 90 分，则成绩低于 60 分的学生至多有（ ）名。",
        "options": {
            "A": "8",
            "B": "7",
            "C": "6",
            "D": "5",
            "E": "4"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "某工程由甲公司承包需要 60 天完成，由甲、乙两公司共同承包需要 28 天完成，由乙、丙两公司共同承包需要 35 天完成，则由丙公司承包完成该工程需要的天数为（ ）天。",
        "options": {
            "A": "85",
            "B": "90",
            "C": "95",
            "D": "100",
            "E": "105"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "已知 $f(x) = \\frac{1}{(x+1)(x+2)} + \\frac{1}{(x+2)(x+3)} + \\dots + \\frac{1}{(x+9)(x+10)}$，则 $f(8) = $（ ）。",
        "options": {
            "A": "1/9",
            "B": "1/10",
            "C": "5/72",
            "D": "1/16",
            "E": "5/144"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "甲、乙两商店同时购进了一批某品牌电视机，当甲店售出 15 台时乙店售出 10 台，此时两店的库存比为 $8:7$；当甲店售出 130 台时乙店售出 140 台，此时两店的库存比为 $1:3$，那么甲、乙两商店购进电视机的数量比是（ ）。",
        "options": {
            "A": "3:2",
            "B": "5:4",
            "C": "4:3",
            "D": "5:3",
            "E": "7:5"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "如图1所示，在直角三角形 $ABC$ 中，$AC = 4, BC = 3, DE$ 垂直平分 $AB$，则 $\\triangle CDE$ 的面积为（ ）。",
        "options": {
            "A": "25/32",
            "B": "25/24",
            "C": "35/32",
            "D": "35/24",
            "E": "7/4"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "点 $(0, 4)$ 关于直线 $2x + y + 1 = 0$ 的对称点为（ ）。",
        "options": {
            "A": "(-4, 2)",
            "B": "(-4, -2)",
            "C": "(4, -2)",
            "D": "(4, 2)",
            "E": "(-2, 4)"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "在 $(x^2 + 3x + 1)^5$ 的展开式中，$x^2$ 的系数为（ ）。",
        "options": {
            "A": "5",
            "B": "10",
            "C": "45",
            "D": "90",
            "E": "95"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "将体积为 $4\\pi$ 立方厘米和 $32\\pi$ 立方厘米的两个实心金属球熔化后铸成一个实心大球，则大球的表面积为（ ）平方厘米。",
        "options": {
            "A": "$32\\pi$",
            "B": "$36\\pi$",
            "C": "$38\\pi$",
            "D": "$40\\pi$",
            "E": "$42\\pi$"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "有一批水果要装箱，一名熟练工单独装箱需要 10 天，每天报酬为 200 元；一名普通工单独装箱需要 15 天，每天报酬为 120 元。由于场地限制，最多可同时安排 12 人装箱，若要求在一天内完成装箱任务，则支付的最少报酬为（ ）元。",
        "options": {
            "A": "1800",
            "B": "1840",
            "C": "1920",
            "D": "1960",
            "E": "2000"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "已知抛物线 $y = x^2 + bx + c$ 的对称轴为 $x = 1$，且过点 $(-1, 1)$，则（ ）。",
        "options": {
            "A": "$b = -2, c = -2$",
            "B": "$b = 2, c = 2$",
            "C": "$b = -2, c = 2$",
            "D": "$b = -1, c = -1$",
            "E": "$b = 1, c = 1$"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "已知 $\{a_n\}$ 为等差数列，若 $a_2$ 和 $a_{10}$ 是方程 $x^2 - 10x - 9 = 0$ 的两个根，则 $a_5 + a_7 = $（ ）。",
        "options": {
            "A": "-10",
            "B": "-9",
            "C": "9",
            "D": "10",
            "E": "12"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "已知 10 件产品中有 4 件一等品，从中任取 2 件，则至少有 1 件一等品的概率为（ ）。",
        "options": {
            "A": "1/3",
            "B": "2/3",
            "C": "2/15",
            "D": "8/15",
            "E": "13/15"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "确定两人从 $A$ 地出发经过 $B, C$，沿逆时针方向行走一圈回到 $A$ 地。已知 $A, B$ 相距 40 千米，$B, C$ 相距 30 千米，$C, A$ 相距 50 千米。甲的速度是 6 千米/小时，乙的速度是 4 千米/小时，则两人出发后相遇的时间是（ ）小时。",
        "options": {
            "A": "12",
            "B": "15",
            "C": "16",
            "D": "20",
            "E": "24"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "已知平面区域 $D_1 = \\{(x, y) \\mid x^2 + y^2 \\le 9\\}, D_2 = \\{(x, y) \\mid (x-a)^2 + (y-b)^2 \\le 4\\}$，则 $D_1$ 与 $D_2$ 的公共区域的面积不小于 $\\pi$。\n(1) $a^2 + b^2 \\le 4$。\n(2) $a^2 + b^2 = 1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "$p = mq + 1$ 为质数。\n(1) $m$ 为正整数，$q$ 为质数。\n(2) $m, q$ 均为质数。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "$\\triangle ABC$ 的边长分别为 $a, b, c$，则 $\\triangle ABC$ 为直角三角形。\n(1) $(c^2 - a^2 - b^2)(a^2 - b^2) = 0$。\n(2) $\\triangle ABC$ 的面积为 $\\frac{1}{2}ab$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "已知二次函数 $f(x) = ax^2 + bx + c$，则方程 $f(x) = 0$ 有两个不同实根。\n(1) $a + c = 0$。\n(2) $a + b + c = 0$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "档案馆在一个库房中安装了 $n$ 个烟火感应报警器，每个报警器遇到烟火成功报警的概率为 $p$。该库房遇烟火发出警报的概率达到 0.999。\n(1) $n = 3, p = 0.9$。\n(2) $n = 2, p = 0.97$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "已知 $a, b$ 是实数，则 $|a| \\le 1, |b| \\le 1$。\n(1) $|a+b| \\le 1$。\n(2) $|a-b| \\le 1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "设 $x, y, z$ 为非零实数，则 $\\frac{2x+3y-4z}{x+y-2z} = 1$。\n(1) $3x - 2y = 0$。\n(2) $2y - z = 0$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "某单位年终共发了 100 万元奖金，奖金金额分别是一等奖 1.5 万元、二等奖 1 万元、三等奖 0.5 万元，则该单位至少有 100 人。\n(1) 得二等奖的人数最多。\n(2) 得三等奖的人数最多。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "三个科室的人数分别为 6、3 和 2，因工作需要，每晚需要排 3 人值班，则在两个月中可使每晚的值班人员不完全相同。\n(1) 值班人员不能来自同一科室。\n(2) 值班人员来自三个不同科室。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "设 $a_1 = 1, a_2 = k, \\dots, a_{n+1} = |a_n - a_{n-1}|$ ($n \\ge 2$)，则 $a_{100} + a_{101} + a_{102} = 2$。\n(1) $k = 2$。\n(2) $k$ 为整数。",
        "options": COND_OPTIONS
    }
]

# Read PDF text for Q26-57
doc = fitz.open(f"真题部分/{YEAR}年199管综真题.pdf")
pages_text = [doc[p].get_text() for p in range(3, 13)]
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
all_questions = list(math_q_2013)

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
