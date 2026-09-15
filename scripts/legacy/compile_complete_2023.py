import json, os, re

YEAR = 2023
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

math_q_2023 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "油价上涨 5% 后，加一箱油比原来多花 20 元；一个月后油价下降 4%，则现在加一箱油需要花（ ）元。",
        "options": {
            "A": "384",
            "B": "401",
            "C": "402.8",
            "D": "403.2",
            "E": "404"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "已知甲、乙两公司的利润之比为 $3:4$，甲、丙两公司的利润之比为 $1:2$。若乙公司的利润为 3000 万元，则丙公司的利润为（ ）万元。",
        "options": {
            "A": "5000",
            "B": "4500",
            "C": "4000",
            "D": "3500",
            "E": "2500"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "一个分数的分母和分子之和为 38，其分子分母都减去 15，约分后得到 $\\frac{1}{3}$，则这个分数的分母与分子之差为（ ）。",
        "options": {
            "A": "1",
            "B": "2",
            "C": "3",
            "D": "4",
            "E": "5"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "$\\sqrt{5+2\\sqrt{6}} - \\sqrt{3} =$（ ）。",
        "options": {
            "A": "$\\sqrt{2}$",
            "B": "$\\sqrt{3}$",
            "C": "$\\sqrt{6}$",
            "D": "$2\\sqrt{2}$",
            "E": "$2\\sqrt{3}$"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "某公司财务部有男员工 2 名，女员工 3 名；销售部有男员工 4 名，女员工 1 名。现要从中选出 2 男 1 女组成工作小组，并要求每个部门至少有 1 名员工入选，则工作小组的不同构成方式有（ ）种。",
        "options": {
            "A": "24",
            "B": "36",
            "C": "50",
            "D": "51",
            "E": "68"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "甲、乙两人从同一地点出发，甲先出发 10 分钟，若乙跑步追赶甲，则 10 分钟可追上；若乙骑车追赶甲，每分钟比跑步多行 100 米，则 5 分钟可追上，那么甲每分钟走的距离为（ ）米。",
        "options": {
            "A": "50",
            "B": "75",
            "C": "100",
            "D": "125",
            "E": "150"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "如右图所示，已知点 $A(-1, 2), B(3, 4)$，若存在点 $P(m, 0)$ 使得 $|PB| - |PA|$ 最大，则（ ）。",
        "options": {
            "A": "$m = -5$",
            "B": "$m = -3$",
            "C": "$m = -1$",
            "D": "$m = 1$",
            "E": "$m = 3$"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "由于疫情防控，电影院要求不同家庭之间至少间隔一个座位，同一家庭的成员座位要相连。两个家庭看电影，一家 3 人，一家 2 人，现有一排 7 个相连的座位，则符合要求的坐法有（ ）种。",
        "options": {
            "A": "36",
            "B": "48",
            "C": "72",
            "D": "144",
            "E": "216"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "方程 $x^2 - 3|x-2| - 4 = 0$ 的所有实根之和为（ ）。",
        "options": {
            "A": "$-4$",
            "B": "$-3$",
            "C": "$-2$",
            "D": "$-1$",
            "E": "0"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "如右图所示，从一个棱长为 6 的正方体中截去两个相同的正三棱锥，若正三棱锥的底面边长 $AB = 4\\sqrt{2}$，则剩余几何体的表面积为（ ）。",
        "options": {
            "A": "168",
            "B": "$168 + 16\\sqrt{3}$",
            "C": "$168 + 32\\sqrt{3}$",
            "D": "$112 + 32\\sqrt{3}$",
            "E": "$124 + 32\\sqrt{3}$"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "如右图所示，在 $\\Delta ABC$ 中，$\\angle BAC = 60^\\circ$，$BD$ 平分 $\\angle ABC$，交 $AC$ 于点 $D$，$CE$ 平分 $\\angle ACB$，交 $AB$ 于点 $E$，$BD$ 和 $CE$ 交于点 $F$，则 $\\angle EFB =$（ ）。",
        "options": {
            "A": "$45^\\circ$",
            "B": "$52.5^\\circ$",
            "C": "$60^\\circ$",
            "D": "$67.5^\\circ$",
            "E": "$75^\\circ$"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "跳水比赛中，裁判给某选手的一个动作打分，其平均值为 8.6，方差为 1.1，若去掉一个最高得分 9.7 和一个最低得分 7.3，则剩余得分的（ ）。",
        "options": {
            "A": "平均值变小，方差变大",
            "B": "平均值变小，方差变小",
            "C": "平均值变小，方差不变",
            "D": "平均值变大，方差变大",
            "E": "平均值变大，方差变小"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "设 $x$ 为正实数，则 $\\frac{x}{8x^3 + 5x + 2}$ 的最大值为（ ）。",
        "options": {
            "A": "$\\frac{1}{15}$",
            "B": "$\\frac{1}{11}$",
            "C": "$\\frac{1}{9}$",
            "D": "$\\frac{1}{6}$",
            "E": "$\\frac{1}{5}$"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "如右图所示，在矩形 $ABCD$ 中，$AD = 2AB$，$E$、$F$ 分别为 $AD$、$BC$ 的中点，从 $A$、$B$、$C$、$D$、$E$、$F$ 中任意取 3 个点，则以这 3 个点为顶点可组成直角三角形的概率为（ ）。",
        "options": {
            "A": "$\\frac{1}{2}$",
            "B": "$\\frac{11}{24}$",
            "C": "$\\frac{3}{5}$",
            "D": "$\\frac{13}{20}$",
            "E": "$\\frac{7}{10}$"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "快递员收到 3 个同城快递任务，取送地点各不相同，取送件可穿插进行，不同的送件方式有（ ）种。",
        "options": {
            "A": "6",
            "B": "27",
            "C": "36",
            "D": "90",
            "E": "360"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "有体育、美术、音乐、舞蹈 4 个兴趣班，每名同学至少参加 2 个，则至少有 12 名同学参加的兴趣班完全相同。\n(1) 参加兴趣班的同学共有 125 人。\n(2) 参加 2 个兴趣班的同学有 70 人。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "关于 $x$ 的方程 $x^2 - px + q = 0$ 有两个实根 $a, b$，则 $p - q > 1$。\n(1) $a > 1$。\n(2) $b < 1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "已知等比数列 $\{a_n\}$ 的公比大于 1，则 $\{a_n\}$ 为递增数列。\n(1) $a_1$ 是方程 $x^2 - x - 2 = 0$ 的根。\n(2) $a_1$ 是方程 $x^2 + x - 6 = 0$ 的根。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "设 $x, y$ 是实数，则 $\\sqrt{x^2 + y^2}$ 有最小值和最大值。\n(1) $(x-1)^2 + (y-1)^2 = 1$。\n(2) $y = x + 1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "设集合 $M = \\{(x, y) \\mid (x-a)^2 + (y-b)^2 \\le 4\}$，$N = \\{(x, y) \\mid x > 0, y > 0\}$，则 $M \\cap N \\neq \\varnothing$。\n(1) $a < -2$。\n(2) $b > 2$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "甲、乙两辆车分别从 $A$、$B$ 两地同时出发，相向而行，1 小时后，甲车到达 $C$ 点，乙车到达 $D$ 点（如右图所示）。则能确定 $A, B$ 两地的距离。\n(1) 已知 $C, D$ 两地的距离。\n(2) 已知甲、乙两车的速度比。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "已知 $m, n, p$ 为 3 个不同的质数，则能确定 $m, n, p$ 的乘积。\n(1) $m + n + p = 16$。\n(2) $m + n + p = 20$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "八个班参加植树活动，共植树 195 棵。则能确定各班植树棵数的最小值。\n(1) 各班植树棵数均不相同。\n(2) 各班植树棵数的最大值是 28。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "设数列 $\{a_n\}$ 的前 $n$ 项和为 $S_n$。则 $a_2, a_3, a_4, \\cdots$ 为等比数列。\n(1) $S_{n+1} > S_n, n = 1, 2, 3, \\cdots$。\n(2) $\{S_n\}$ 是等比数列。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "甲有两张牌 $a, b$，乙有两张牌 $x, y$，甲、乙各自任意取出一张牌。则甲取出的牌不小于乙取出的牌的概率不小于 $\\frac{1}{2}$。\n(1) $a > x$。\n(2) $a + b > x + y$。",
        "options": COND_OPTIONS
    }
]

# Parse logic from OCR cache
with open('199管综真题_Markdown题库/2023年/ocr_cache.json') as f:
    cache = json.load(f)

all_lines = []
for p in range(5, 16):
    for l in cache[str(p)]:
        t = l['text'].strip()
        if '2023年真题一第' in t: continue
        all_lines.append(t)

full_text = '\n'.join(all_lines)
full_text = re.sub(r'三、逻辑推理：第26～55小题.*?请在答题卡上将所选项的字母涂黑。', '', full_text, flags=re.S)

writing_pos = full_text.find('四、写作')
logic_text = full_text[:writing_pos] if writing_pos != -1 else full_text

# Standard shared stems
stems_map = {
    (31, 32): "31～32 题基于以下题干：\n某中学举行田径运动会，高二（3）班甲、乙、丙、丁、戊、己 6 人报名参赛。在跳远、跳高和铅球 3 项比赛中，他们每人都报名 1～2 项。其中 2 人报名跳远，3 人报名跳高，3 人报名铅球。另外，还知道：\n(1) 如果甲、乙至少有 1 人报名铅球，则丙也报名铅球。\n(2) 如果己报名跳高，则乙和己均报名跳远。\n(3) 如果丙、戊至少有 1 人报名铅球，则己报名跳高。",
    (37, 38): "37～38 题基于以下题干：\n某研究所甲、乙、丙、丁、戊 5 人拟定去我国四大佛教名山普陀山、九华山、五台山、峨眉山考察，他们每人去了上述两座名山，且每座名山均有其中的 2～3 人前往，丙与丁结伴考察，已知：\n(1) 如果甲去五台山，则乙和丁都去五台山。\n(2) 如果甲去峨眉山，则丙和戊都去峨眉山。\n(3) 如果甲去九华山，则戊去九华山和普陀山。",
    (46, 47): "46～47 题基于以下题干：\n某单位购买了《尚书》《周易》《诗经》《论语》《老子》《孟子》各 1 本，分发给甲、乙、丙、丁、戊 5 个部门，每个部门至少 1 本。已知：\n(1) 若《周易》《老子》《孟子》至少有 1 本分发给甲或乙部门，则《尚书》分发给丁部门且《论语》分发给戊部门。\n(2) 若《诗经》《论语》至少有 1 本分发给甲或乙部门，则《周易》分发给丙部门且《老子》分发给戊部门。",
    (54, 55): "54～55 题基于以下题干：\n某机关甲、乙、丙、丁 4 人参加本年度综合考评。在德、能、勤、绩、廉 5 个方面的单项考评中，他们之中都恰有 3 人被评为“优秀”，但没有人 5 个单项均被评为“优秀”。已知：\n(1) 若甲和乙在德方面均被评为“优秀”，则他们在廉方面也均被评为“优秀”。\n(2) 若乙和丙在德方面均被评为“优秀”，则他们在绩方面也均被评为“优秀”。\n(3) 若甲在廉方面被评为“优秀”，则甲和丁在绩方面均被评为“优秀”。"
}

# Remove stems from logic_text so anchors are clean
clean_logic_text = logic_text
clean_logic_text = re.sub(r'31～32题基于以下题干：.*?(?=31[\.、．。])', '', clean_logic_text, flags=re.S)
clean_logic_text = re.sub(r'37～38题基于以下题干：.*?(?=37[\.、．。])', '', clean_logic_text, flags=re.S)
clean_logic_text = re.sub(r'46～47题基于以下题干：.*?(?=46[\.、．。])', '', clean_logic_text, flags=re.S)
clean_logic_text = re.sub(r'54～55题基于以下题干：.*?(?=54[\.、．。])', '', clean_logic_text, flags=re.S)

q_found = {}
for qn in range(26, 56):
    m = re.search(rf'(?:^|\n)\s*{qn}\s*[\.、．。]', clean_logic_text)
    if m:
        q_found[qn] = m.start()

sorted_q = sorted(q_found.items(), key=lambda x: x[1])
logic_q_raw = {}
for idx, (qn, pos) in enumerate(sorted_q):
    next_pos = sorted_q[idx+1][1] if idx + 1 < len(sorted_q) else len(clean_logic_text)
    logic_q_raw[qn] = clean_logic_text[pos:next_pos].strip()

pat = r'(?:^|\n|\s|[（(])([A-E])(?:[）\)\.、．]|\s)'

logic_q_2023 = []
for qn in range(26, 56):
    txt = logic_q_raw[qn]
    txt = re.sub(rf'^\s*{qn}\s*[\.、．。]\s*', '', txt)
    
    matches = list(re.finditer(pat, txt))
    if len(matches) > 5:
        matches = matches[-5:]
    
    first_opt_idx = matches[0].start()
    stem = txt[:first_opt_idx].strip()
    stem = re.sub(r'\n+', '\n', stem)
    
    # Prepend shared stem if applicable
    for (q1, q2), stem_prefix in stems_map.items():
        if qn in [q1, q2]:
            stem = f"{stem_prefix}\n\n{stem}"
            break
            
    options = {}
    for i in range(len(matches)):
        lbl = matches[i].group(1)
        st = matches[i].end()
        en = matches[i+1].start() if i+1 < len(matches) else len(txt)
        val = txt[st:en].strip()
        val = re.sub(r'\s+', ' ', val)
        options[lbl] = val
        
    logic_q_2023.append({
        "question_no": qn,
        "category": "逻辑推理",
        "stem": stem,
        "options": options
    })

writing_q_2023 = [
    {
        "question_no": 56,
        "category": "论证有效性分析",
        "stem": "论证有效性分析：分析下述论证中存在的缺陷和漏洞，选择若干要点，写一篇 600 字左右的文章，对该论证的有效性进行分析和评论。（论证有效性分析的一般要点是：概念特别是核心概念的界定和使用是否准确并前后一致，有无各种明显的逻辑错误，论证的论据是否成立并支持结论，结论成立的条件是否充分等。）\n\n随着人口的老龄化，大家都在议论老年人还要不要继续工作的话题。我们认为，老年人应该继续工作。\n\n我国《宪法》规定，“中华人民共和国公民有劳动的权利和义务。”由此可见，老年人继续工作是法律赋予他们的权利。\n\n据统计，我国 2019 年人均预期寿命已经达到 77.3 岁，这说明老年人的健康水平大大提高了，所以老年人完全有能力继续工作。\n\n如果老年人不再继续工作而退出劳动力市场，就势必会打破劳动力市场的原有平衡，从而造成社会劳动力的短缺。如果老年人继续工作，就能有效地避免这一问题。\n\n此外，老年人有权利追求更高质量的生活。他们想增加收入、改善生活，就应该继续工作。再说，有规律的生活方式有益于身体健康，而工作实质上是一种有规律的生活方式，所以老年人继续工作还有益于其身体健康。",
        "options": {}
    },
    {
        "question_no": 57,
        "category": "论说文",
        "stem": "论说文：根据下述材料，写一篇 700 字左右的论说文，题目自拟。\n\n人们常说“领导艺术”，可见领导与艺术之间存在着某种相似点，如领导一个团队完成某项任务和指挥一个乐队演奏某首乐曲一样。",
        "options": {}
    }
]

all_questions = math_q_2023 + logic_q_2023 + writing_q_2023
print(f"Total compiled questions: {len(all_questions)}")

# Write jsonl chunks
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

# Write full markdown
with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write(f"# {YEAR}年全国硕士研究生招生考试管理类综合能力真题（199）\n\n")
    
    current_cat = ""
    for q in all_questions:
        cat = q["category"]
        qn = q["question_no"]
        
        if cat != current_cat:
            current_cat = cat
            if cat == "问题求解":
                f.write("## 一、问题求解：第 1～15 小题，每小题 3 分，共 45 分。下列每题给出的 A、B、C、D、E 五个选项中，只有一项是符合试题要求的。\n\n")
            elif cat == "条件充分性判断":
                f.write("## 二、条件充分性判断：第 16～25 小题，每小题 3 分，共 30 分。要求判断每题给出的条件（1）和条件（2）能否充分支持题干所陈述的结论。\n\n"
                        "A. 条件（1）充分，但条件（2）不充分。\n"
                        "B. 条件（2）充分，但条件（1）不充分。\n"
                        "C. 条件（1）和条件（2）单独都不充分，但条件（1）和条件（2）联合起来充分。\n"
                        "D. 条件（1）充分，条件（2）也充分。\n"
                        "E. 条件（1）和条件（2）单独都不充分，条件（1）和条件（2）联合起来也不充分。\n\n")
            elif cat == "逻辑推理":
                f.write("## 三、逻辑推理：第 26～55 小题，每小题 2 分，共 60 分。下列每题给出的 A、B、C、D、E 五个选项中，只有一项是符合试题要求的。\n\n")
            elif cat in ["论证有效性分析", "论说文"] and qn == 56:
                f.write("## 四、写作：第 56～57 小题，共 65 分。其中论证有效性分析 30 分，论说文 35 分。\n\n")
        
        f.write(f"### 第 {qn} 题\n\n")
        f.write(f"![{YEAR}年第{qn}题](images/{YEAR}_q{qn:02d}.png)\n\n")
        f.write(f"{q['stem']}\n\n")
        
        if q["options"]:
            for opt_key in ["A", "B", "C", "D", "E"]:
                if opt_key in q["options"]:
                    f.write(f"- **{opt_key}**．{q['options'][opt_key]}\n")
            f.write("\n")

print(f"Successfully generated {MD_PATH} and {JSONL_PATH}!")
