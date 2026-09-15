import json, os, re, fitz

YEAR = 2020
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

math_q_2020 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "某产品去年涨价 10%，今年涨价 20%，则该产品两年涨价为（ ）。",
        "options": {
            "A": "15%",
            "B": "16%",
            "C": "30%",
            "D": "32%",
            "E": "33%"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "设 $A = \\{x \\mid |x - a| < 1, x \\in \\mathbf{R}\\}, B = \\{x \\mid |x - b| < 2, x \\in \\mathbf{R}\\}$，则 $A \\subset B$ 的充分必要条件是（ ）。",
        "options": {
            "A": "$|a - b| \\le 1$",
            "B": "$|a - b| \\ge 1$",
            "C": "$|a - b| < 1$",
            "D": "$|a - b| > 1$",
            "E": "$|a - b| = 1$"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "一项考试的总成绩由甲、乙、丙三部分组成：总成绩 = 甲成绩 $\\times 30\\%$ + 乙成绩 $\\times 20\\%$ + 丙成绩 $\\times 50\\%$。考试通过的标准是每部分 $\\ge 50$ 分，且总成绩 $\\ge 60$ 分。已知某人甲成绩 70 分，乙成绩 75 分，且通过这项考试，则此人丙成绩分数至少是（ ）分。",
        "options": {
            "A": "48",
            "B": "50",
            "C": "55",
            "D": "60",
            "E": "62"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "从 1 至 10 这 10 个整数中任取三个数，恰有一个质数的概率是（ ）。",
        "options": {
            "A": "$\\frac{2}{3}$",
            "B": "$\\frac{1}{2}$",
            "C": "$\\frac{5}{12}$",
            "D": "$\\frac{2}{5}$",
            "E": "$\\frac{1}{120}$"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "若等差数列 $\{a_n\}$ 满足 $a_1 = 8$，且 $a_2 + a_4 = a_1$，则 $\{a_n\}$ 前 $n$ 项和的最大值为（ ）。",
        "options": {
            "A": "16",
            "B": "17",
            "C": "18",
            "D": "19",
            "E": "20"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "已知实数 $x$ 满足 $x^2 + \\frac{1}{x^2} - 3x - \\frac{3}{x} + 2 = 0$，则 $x^3 + \\frac{1}{x^3} = $（ ）。",
        "options": {
            "A": "12",
            "B": "15",
            "C": "18",
            "D": "24",
            "E": "27"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "设实数 $x, y$ 满足 $|x - 2| + |y - 2| \\le 2$，则 $x^2 + y^2$ 的取值范围是（ ）。",
        "options": {
            "A": "$[2, 18]$",
            "B": "$[2, 20]$",
            "C": "$[2, 36]$",
            "D": "$[4, 18]$",
            "E": "$[4, 20]$"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "某网店对单价为 55 元、75 元、80 元的三种商品进行促销，促销策略是：每单满 200 元减 $m$ 元，如果每单减 $m$ 元的实际售价均不低于原价的 8 折，那么 $m$ 的最大值为（ ）。",
        "options": {
            "A": "40",
            "B": "41",
            "C": "43",
            "D": "44",
            "E": "48"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "某人在同一观众群体中调查了对五部电影的看法，得到数据如表 1 所示：\n\n| 电影 | 第一部 | 第二部 | 第三部 | 第四部 | 第五部 |\n| :--- | :---: | :---: | :---: | :---: | :---: |\n| 好评率 | 0.25 | 0.5 | 0.3 | 0.8 | 0.4 |\n| 差评率 | 0.75 | 0.5 | 0.7 | 0.2 | 0.6 |\n\n则观众意见分歧最大的两部电影依次是（ ）。",
        "options": {
            "A": "第一部和第三部",
            "B": "第二部和第三部",
            "C": "第二部和第五部",
            "D": "第四部和第一部",
            "E": "第四部和第二部"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "如图 1 所示，在 $\\triangle ABC$ 中，$\\angle ABC = 30^\\circ$，将线段 $AB$ 绕点 $B$ 旋转至 $DB$，使 $\\angle DBC = 60^\\circ$，则 $\\triangle DBC$ 与 $\\triangle ABC$ 的面积之比为（ ）。",
        "options": {
            "A": "1",
            "B": "$\\sqrt{2}$",
            "C": "2",
            "D": "$\\frac{\\sqrt{3}}{2}$",
            "E": "$\\sqrt{3}$"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "已知数列 $\{a_n\}$ 满足 $a_1 = 1, a_2 = 2$，且 $a_{n+2} = a_{n+1} - a_n (n = 1, 2, 3, \\cdots)$，则 $a_{100} = $（ ）。",
        "options": {
            "A": "1",
            "B": "-1",
            "C": "2",
            "D": "-2",
            "E": "0"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "如图 2 所示，圆 $O$ 的内接 $\\triangle ABC$ 是等腰三角形，底边 $BC = 6$，顶角为 $\\frac{\\pi}{4}$，则圆 $O$ 的面积为（ ）。",
        "options": {
            "A": "$12\\pi$",
            "B": "$16\\pi$",
            "C": "$18\\pi$",
            "D": "$32\\pi$",
            "E": "$36\\pi$"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "甲、乙两人从一条长为 1800 米道路的两端同时出发，往返行走。已知甲每分钟行走 100 米，乙每分钟行走 80 米，则两人第三次相遇时，甲距其出发点（ ）米。",
        "options": {
            "A": "600",
            "B": "900",
            "C": "1000",
            "D": "1400",
            "E": "1600"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "如图 3 所示，$A, B, C, D$ 两两相连，从一个节点沿线段到另一个节点当作 1 步，若机器人从节点 $A$ 出发，随机走了 3 步，则机器人未到达节点 $C$ 的概率为（ ）。",
        "options": {
            "A": "$\\frac{4}{9}$",
            "B": "$\\frac{11}{27}$",
            "C": "$\\frac{10}{27}$",
            "D": "$\\frac{19}{27}$",
            "E": "$\\frac{8}{27}$"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "某科室有 4 名男职员，2 名女职员，若将这 6 名职员分为 3 组，每组 2 人且女职员不同组，则有（ ）种不同的分组方式。",
        "options": {
            "A": "4",
            "B": "6",
            "C": "9",
            "D": "12",
            "E": "15"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "在 $\\triangle ABC$ 中，$\\angle B = 60^\\circ$，则 $\\frac{c}{a} > 2$。\n（1）$\\angle C < 90^\\circ$。\n（2）$\\angle C > 90^\\circ$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "圆 $x^2 + y^2 = 2x + 2y$ 上的点到 $ax + by + \\sqrt{2} = 0$ 距离的最小值大于 1。\n（1）$a^2 + b^2 = 1$。\n（2）$a > 0, b > 0$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "设 $a, b, c$ 是实数，则能确定 $a, b, c$ 的最大值。\n（1）已知 $a, b, c$ 的平均值。\n（2）已知 $a, b, c$ 的最小值。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "甲、乙两种品牌的手机 20 部，任取 2 部，恰有 1 部甲品牌的概率为 $P$，则 $P > \\frac{1}{2}$。\n（1）甲品牌手机不少于 8 部。\n（2）乙品牌手机多于 7 部。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "某单位计划租 $n$ 辆车出游，则能确定出游人数。\n（1）若租用 20 座的车辆，只有 1 辆车没坐满。\n（2）若租用 12 座的车辆，还缺 10 个座位。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "在长方体中，能确定长方体对角线的长度。\n（1）已知共顶点的三个面的面积。\n（2）已知共顶点的三个面的对角线长度。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "已知甲、乙、丙三人共捐款 3500 元，则能确定每人的捐款金额。\n（1）三人的捐款金额各不相同。\n（2）三人的捐款金额都是 500 的倍数。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "设函数 $f(x) = (ax - 1)(x - 4)$，则在 $x = 4$ 左侧附近有 $f(x) < 0$。\n（1）$a > \\frac{1}{4}$。\n（2）$a < 4$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "设 $a, b$ 是正实数，则 $\\frac{1}{a} + \\frac{1}{b}$ 存在最小值。\n（1）已知 $ab$ 的值。\n（2）已知 $a, b$ 是方程 $x^2 - (a+b)x + 2 = 0$ 的不同实根。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "设 $a, b, c, d$ 是正实数，则 $\\sqrt{a} + \\sqrt{d} \\le \\sqrt{2(b+c)}$。\n（1）$a + d = b + c$。\n（2）$ad = bc$。",
        "options": COND_OPTIONS
    }
]

# Parse Logic Questions 26..55
doc = fitz.open('真题部分/2020年199管综真题.pdf')
full_text = ''
for p in range(4, 13):
    full_text += f'\n<<<PAGE_{p}>>>\n' + doc[p].get_text()

full_text = re.sub(r'2020年真题－第\d+页（共31\s*页）', '', full_text)
full_text = re.sub(r'三、逻辑推理：第26~55小题.*?请在答庭卡上将所选项的字母涂黑。', '', full_text, flags=re.S)

full_text = re.sub(r'S4\s*[\.、．]', '54．', full_text)
full_text = re.sub(r'so\s*移动互联网时代', '50．移动互联网时代', full_text)
full_text = re.sub(r'48\.1818', '48．1818', full_text)

for qn in [30, 34, 35, 38, 41, 55]:
    full_text = re.sub(rf'(?:^|\n)\s*{qn}(?=[^\d\.\、\．])', f'\n{qn}．', full_text)

writing_start = full_text.find('四、写作')
logic_text = full_text[:writing_start]

# Extract group headers
# 31-32, 37-38, 46-47, 54-55
group_data = {
    (31, 32): "31～32 题基于以下题干：\n“立春”“春分”“立夏”“夏至”“立秋”“秋分”“立冬”“冬至”是我国二十四节气中的八个节气。凉风、广莫风、条风、明庶风、清明风、景风、阊阖风、不周风是八种节风。上述八个节气与八种节风之间一一对应。已知：\n（1）“立秋”对应“凉风”。\n（2）“冬至”对应“不周风”，或者“立春”对应“条风”。\n（3）若“凉风”对应“立秋”或者“立冬”，则“明庶风”对应“春分”。",
    (37, 38): "37～38 题基于以下题干：\n放假 3 天，小李夫妇除安排 1 天休息之外，其他 2 天准备做 6 件事：①购物；②看望双方父母；③郊游；④带孩子去游乐场；⑤去市内公园；⑥去电影院看电影。他们商定：\n（1）每件事均做一次，且在 1 天内做完，每天至少做 2 件事。\n（2）④和⑥安排在同一天完成。\n（3）②在③之前 1 天完成。",
    (46, 47): "46～47 题基于以下题干：\n某公司甲、乙、丙、丁、戊 5 人爱好出国旅游。去年，在日本、德国、英国、法国、美国 5 个国家中，他们每人都去了其中的两个国家旅游，且每个国家总有他们中的 2～3 人去旅游。已知：\n（1）如果甲去德国，则乙不去；\n（2）如果某人去了日本，则他不能去德国和法国；\n（3）只有丁去了英国，乙才去美国；\n（4）若丁没去法国，则丙去了美国；\n（5）戊去了德国，且甲去了法国。",
    (54, 55): "54～55 题基于以下题干：\n某项测试共有 4 道题，每道题给出 A、B、C、D 四个选项，其中只有一项是正确答案。现有张、王、赵、李 4 人参加了测试，他们的答题情况和测试结果如表 3 所示：\n\n表 3\n| 答题者 | 第一题 | 第二题 | 第三题 | 第四题 | 测试结果 |\n| :--- | :---: | :---: | :---: | :---: | :--- |\n| 张 | A | B | A | B | 均不正确 |\n| 王 | B | D | B | C | 只答对 1 题 |\n| 赵 | D | A | A | B | 均不正确 |\n| 李 | C | C | B | D | 只答对 1 题 |"
}

# Remove group header text from raw logic_text so it doesn't pollute previous question options
logic_text_cleaned = logic_text
logic_text_cleaned = re.sub(r'31[-～]32题基[于千]以下题干：[\s\S]*?(?=31．)', '', logic_text_cleaned)
logic_text_cleaned = re.sub(r'37[-～]38题基[于千]以下题干：[\s\S]*?(?=37．)', '', logic_text_cleaned)
logic_text_cleaned = re.sub(r'46[-～]47题基[于千]以下题干：[\s\S]*?(?=46．)', '', logic_text_cleaned)
logic_text_cleaned = re.sub(r'54[-～]55题基[于千]以下题干：[\s\S]*?(?=54．)', '', logic_text_cleaned)

q_splits = {}
for qn in range(26, 56):
    pattern = rf'(?:^|\n)\s*{qn}．'
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
    s = s.replace('“', '“').replace('”', '”').replace('‘', '‘').replace('’', '’')
    s = s.replace('千', '于')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

logic_q_2020 = []

for qn in range(26, 56):
    raw_block = logic_questions_raw[qn]
    clean = re.sub(r'<<<PAGE_\d+>>>', '', raw_block)
    # find options
    opt_matches = list(re.finditer(r'[\(（]([A-E])[\)）]', clean))
    last_5 = opt_matches[-5:]
    first_opt_start = last_5[0].start()
    raw_stem = clean[:first_opt_start].strip()
    # remove question number prefix
    raw_stem = re.sub(rf'^\s*{qn}．\s*', '', raw_stem)
    raw_stem = clean_text_segment(raw_stem)
    
    # Prepend group stem if Q31, Q37, Q46, Q54
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
        
    logic_q_2020.append({
        "question_no": qn,
        "category": "逻辑推理",
        "stem": raw_stem,
        "options": opts
    })

# Writing section
writing_q_2020 = [
    {
        "question_no": 56,
        "category": "写作",
        "stem": "56．论证有效性分析：分析下述论证中存在的缺陷与漏洞，选择若干要点，写一篇 600 字左右的文章，对该论证的有效性进行分析和评论。（论证有效性分析的一般要点是：概念特别是核心概念的界定和使用是否准确并前后一致，有无各种明显的逻辑错误，论证的论据是否成立并支持结论，结论成立的条件是否充分等。）\n\n北京将联手张家口共同举办 2022 年冬季奥运会，中国南方的一家公司决定在本地投资建立一家商业性的冰雪运动中心。这家公司认为，该中心一旦投入运营，将获得可观的经济收益，这是因为：\n\n北京与张家口共同举办冬奥会，必然会在中国掀起一股冰雪运动热潮。中国南方许多人从未有过冰雪运动的经历，会出于好奇心而投身于冰雪运动，这正是一个千载难逢的绝好商机，不能轻易错过。\n\n而且，冰雪运动与广场舞、跑步等不一样，需要一定的运动用品，例如冰鞋、滑雪板与运动服装，等等。这些运动用品价格不菲而具有较高的商业利润。如果在开展商业性冰雪运动的同时也经营冬季运动用品，则公司可以获得更多的利润。\n\n另外，目前中国网络购物已经成为人们的生活习惯，但相对于网络商业，人们更青睐直接体验式的商业模态，而商业性冰雪运动正是直接体验式的商业模态，无疑具有光明的前景。",
        "options": {}
    },
    {
        "question_no": 57,
        "category": "写作",
        "stem": "57．论说文：根据下述材料，写一篇 700 字左右的论说文，题目自拟。\n\n据报道，美国航天飞机“挑战者”号采用了斯沃克公司的零配件，该公司的密封圈技术专家博易斯乔利多次向公司高层提醒：低温会导致橡胶密封圈脆裂而引发重大事故。但是，这一意见一直没有受到重视。1986 年 1 月 27 日，佛罗里达州卡纳维拉尔角发射场的气温降到零度以下，美国宇航局再次打电话给斯沃克公司，询问其对航天飞机的发射还有没有疑虑之处。为此，斯沃克公司召开会议，博易斯乔利坚持认为不能发射，但公司高层认为他所持理由不够充分，于是同意宇航局发射。1 月 28 日上午，航天飞机离开发射平台，仅过了 73 秒，悲剧就发生了。",
        "options": {}
    }
]

all_questions = math_q_2020 + logic_q_2020 + writing_q_2020
print(f"Total questions compiled: {len(all_questions)}")

# Write to JSONL
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

# Write to Markdown
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
