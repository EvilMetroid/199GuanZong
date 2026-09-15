import json, os, re, fitz

YEAR = 2022
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

math_q_2022 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "一项工程施工 3 天后，因故障停工 2 天，之后工程队提高工作效率 20%，仍能按原计划完成，则原计划工期为（ ）。",
        "options": {
            "A": "9 天",
            "B": "10 天",
            "C": "12 天",
            "D": "15 天",
            "E": "18 天"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "某商品的成本利润率为 12%，若其成本降低 20% 而售价不变，则利润率为（ ）。",
        "options": {
            "A": "32%",
            "B": "35%",
            "C": "40%",
            "D": "45%",
            "E": "48%"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "设 $x, y$ 为实数，则 $f(x, y) = x^2 + 4xy + 5y^2 - 2y + 2$ 的最小值为（ ）。",
        "options": {
            "A": "1",
            "B": "$\\frac{1}{2}$",
            "C": "2",
            "D": "$\\frac{3}{2}$",
            "E": "3"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "如图，$\\Delta ABC$ 是等腰直角三角形，以 $A$ 为圆心的圆弧交 $AC$ 于 $D$，交 $BC$ 于 $E$，交 $AB$ 的延长线于 $F$。若曲边三角形 $CDE$ 与 $BEF$ 的面积相等，则 $\\frac{AD}{AC} =$（ ）。",
        "options": {
            "A": "$\\frac{\\sqrt{3}}{2}$",
            "B": "$\\frac{2}{\\sqrt{5}}$",
            "C": "$\\sqrt{\\frac{3}{\\pi}}$",
            "D": "$\\frac{\\sqrt{\\pi}}{2}$",
            "E": "$\\sqrt{\\frac{2}{\\pi}}$"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "如图，已知相邻的圆都相切，从这 6 个圆中随机取 2 个，这 2 个圆不相切的概率为（ ）。",
        "options": {
            "A": "$\\frac{8}{15}$",
            "B": "$\\frac{7}{15}$",
            "C": "$\\frac{3}{5}$",
            "D": "$\\frac{2}{5}$",
            "E": "$\\frac{2}{3}$"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "如图，在棱长为 2 的正方体中，$A$、$B$ 是顶点，$C$、$D$ 是所在棱的中点，则四边形 $ABCD$ 的面积为（ ）。",
        "options": {
            "A": "$\\frac{9}{2}$",
            "B": "$\\frac{7}{2}$",
            "C": "$\\frac{3\\sqrt{2}}{2}$",
            "D": "$2\\sqrt{5}$",
            "E": "$3\\sqrt{2}$"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "桌面上方有 8 只杯子，将其中 3 只杯子翻转（杯口朝上与杯口朝下互换）作为一次操作。8 只口朝上的杯子，经 $n$ 次操作后，杯子口全朝下，则 $n$ 的最小值（ ）。",
        "options": {
            "A": "3",
            "B": "4",
            "C": "5",
            "D": "6",
            "E": "8"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "某公司有甲、乙、丙三个部门，若从甲部门调 26 人到丙部门，则丙部门人数是甲部门人数的 6 倍，若从乙部门调 5 人到丙部门，则丙部门人数与乙部门人数相等。甲、乙两部门人数差除以 5 余数为（ ）。",
        "options": {
            "A": "0",
            "B": "1",
            "C": "2",
            "D": "3",
            "E": "4"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "在直角三角形 $ABC$ 中，$D$ 是斜边 $AC$ 的中点，以 $AD$ 为直径的圆交 $AB$ 于 $E$，若三角形 $ABC$ 的面积为 8，则三角形 $AED$ 的面积为（ ）。",
        "options": {
            "A": "1",
            "B": "2",
            "C": "3",
            "D": "4",
            "E": "5"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "一个自然数的各位数字都是 105 的质因数，且每个质因数最多出现一次，这样的自然数有（ ）个。",
        "options": {
            "A": "6",
            "B": "9",
            "C": "12",
            "D": "15",
            "E": "27"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "购买 A 玩具和 B 玩具各一件需花费 1.4 元，购买 200 件 A 玩具和 150 件 B 玩具花费 250 元，A 玩具单价为（ ）元。",
        "options": {
            "A": "0.5",
            "B": "0.6",
            "C": "0.7",
            "D": "0.8",
            "E": "0.9"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "甲乙两支足球队进行比赛，比分为 $4:2$，且在比赛过程中乙队没有领先过，则不同的进球顺序有（ ）种。",
        "options": {
            "A": "6",
            "B": "8",
            "C": "9",
            "D": "10",
            "E": "12"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "4 个男生和 2 个女生站成一排，则女生既不在两边也不相邻的概率为（ ）。",
        "options": {
            "A": "$\\frac{1}{2}$",
            "B": "$\\frac{5}{12}$",
            "C": "$\\frac{3}{8}$",
            "D": "$\\frac{1}{3}$",
            "E": "$\\frac{1}{5}$"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "已知 $A, B$ 两地相距 208 千米，甲、乙从 A 出发，丙从 B 出发，相向而行，甲速度 60 千米/小时，乙速度 80 千米/小时，丙速度 90 千米/小时，则（ ）分钟以后，甲丙距离和乙丙距离相等。",
        "options": {
            "A": "70",
            "B": "75",
            "C": "78",
            "D": "80",
            "E": "86"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "如图，用 4 种颜色对图中五块区域进行涂色，每块区域涂一种颜色，且相邻的两块区域颜色不同，不同的涂色方法有（ ）种？",
        "options": {
            "A": "12",
            "B": "24",
            "C": "32",
            "D": "48",
            "E": "96"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "如图，$AD$ 与圆相切于点 $D$，$AC$ 与圆相交于点 $B$。则能确定 $\\Delta ABD$ 与 $\\Delta BDC$ 的面积之比。\n(1) 已知 $\\frac{AD}{CD}$。\n(2) 已知 $\\frac{BD}{CD}$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "设实数 $x$ 满足 $|x-2| - |x-3| = a$，则能确定 $x$ 的值。\n(1) $0 < a \\le \\frac{1}{2}$。\n(2) $\\frac{1}{2} < a \\le 1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "两个人数不等的班数学测验的平均分不相等，则能确定人数多的班。\n(1) 已知两个班的平均分。\n(2) 已知两个班的总平均分。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "在 $\\Delta ABC$ 中，$D$ 为 $BC$ 边上的点，$BD, AB, BC$ 成等比数列，则 $\\angle BAC = 90^\\circ$。\n(1) $BD = DC$。\n(2) $AD \\perp BC$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "将 75 名学生分成 25 组，每组 3 人，则能确定女生人数。\n(1) 已知全男生的组和全女生的组。\n(2) 只有 1 个男生的组和只有 1 个女生的组数相等。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "某直角三角形的边长 $a, b, c$ 成等比数列，则能确定公比的值。\n(1) $a$ 是直角边长。\n(2) $c$ 是斜边边长。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "已知 $x$ 为正实数，则能确定 $x - \\frac{1}{x}$ 的值。\n(1) 已知 $\\sqrt{x} + \\frac{1}{\\sqrt{x}}$ 的值。\n(2) 已知 $x^2 - \\frac{1}{x^2}$ 的值。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "已知 $a, b$ 为实数，则能确定 $\\frac{a}{b}$ 的值。\n(1) $a, b, (a+b)$ 为等比数列。\n(2) $a(a+b) > 0$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "已知正数列 $\{a_n\}$，则 $\{a_n\}$ 为等差数列。\n(1) $a_{n+1}^2 - a_n^2 = 2n, n = 1, 2, \\cdots$。\n(2) $a_1 + a_3 = 2a_2$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "设实数 $a, b$ 满足 $|a-2b| \\le 1$，则 $|a| > |b|$。\n(1) $|b| > 1$。\n(2) $|b| < 1$。",
        "options": COND_OPTIONS
    }
]

# Logic parsing from OCR cache
with open('199管综真题_Markdown题库/2022年/ocr_cache.json') as f:
    cache = json.load(f)

all_lines = []
for p in range(3, 10):
    for l in cache[str(p)]:
        t = l['text'].strip()
        if '5个节目中选择了3个节目观看' in t and not any('28.退休' in x for x in all_lines):
            all_lines.append('28.退休在家的老王今晚在“焦点访谈”“国家记忆”“自然传奇”“人物故事”“纵横中国”这')
        all_lines.append(t)

full_text = "\n".join(all_lines)
full_text = re.sub(r'三、逻辑推理：第26-55小题.*?只有一项是符合试题要求的。', '', full_text, flags=re.S)
writing_pos = full_text.find('四、写作')
logic_text = full_text[:writing_pos]

q_found = {}
for qn in range(26, 56):
    pattern = rf'(?:^|\n)\s*{qn}\s*[\.、．]'
    m = re.search(pattern, logic_text)
    if m:
        q_found[qn] = m.start()

sorted_q = sorted(q_found.items(), key=lambda x: x[1])
logic_q_raw = {}
for idx, (qn, pos) in enumerate(sorted_q):
    next_pos = sorted_q[idx+1][1] if idx + 1 < len(sorted_q) else len(logic_text)
    logic_q_raw[qn] = logic_text[pos:next_pos].strip()

logic_q_2022 = []
for qn in range(26, 56):
    if qn == 27:
        logic_q_2022.append({
            "question_no": 27,
            "category": "逻辑推理",
            "stem": "“君问归期未有期，巴山夜雨涨秋池。何当共剪西窗烛，却话巴山夜雨时。”这首《夜雨寄北》是晚唐诗人李商隐的名作。一般认为这是一封“家书”，当时诗人身处巴蜀，妻子在长安，所以说“寄北”。但有学者提出，这首诗实际上是寄给友人的。\n以下哪项如果为真，最能支持以上学者的观点？",
            "options": {
                "A": "李商隐之妻王氏卒于大中五年，而该诗作于大中七年。",
                "B": "明清小说戏曲中经常将家庭塾师或官员幕客称为“西席”“西宾”。",
                "C": "唐代温庭筠的《舞衣曲》中有诗句“回颦笑语西窗客，星斗寥寥波脉脉”。",
                "D": "该诗另一题为《夜雨寄内》，“寄内”即寄怀妻子。此说得到了许多人的认同。",
                "E": "“西窗”在古代专指客房、客厅，起自尊客于西的先秦古礼，并被后世习察日用。"
            }
        })
        continue
    if qn == 34:
        logic_q_2022.append({
            "question_no": 34,
            "category": "逻辑推理",
            "stem": "补充胶原蛋白已经成为当下很多女性抗衰老的手段之一。她们认为：吃猪蹄能够补充胶原蛋白，为了美容养颜，最好多吃些猪蹄。近日有些专家对此表示质疑，他们认为多吃猪蹄其实并不能补充胶原蛋白。\n以下哪项如果为真，最能质疑上述专家的观点？",
            "options": {
                "A": "猪蹄中的胶原蛋白会被人体的消化系统分解，不会直接以胶原蛋白的形态补充到皮肤中。",
                "B": "人们在日常生活中摄入的优质蛋白和水果、蔬菜中的营养物质，足以提供人体所需的胶原蛋白。",
                "C": "猪蹄中胶原蛋白的含量并不多，但胆固醇含量高、脂肪多，食用过多会引起肥胖，还会增加患高血压的风险。",
                "D": "猪蹄中的胶原蛋白经过人体消化后会被分解成氨基酸等物质，氨基酸参与人体生理活动，再合成人体必需的胶原蛋白等多种蛋白质。",
                "E": "胶原蛋白是人体皮肤、骨骼和肌腱中的主要结构蛋白，它填充在真皮之间，撑起皮肤组织，增加皮肤紧密度，使皮肤水润而富有弹性。"
            }
        })
        continue
    txt = logic_q_raw[qn]
    txt = re.sub(rf'^\s*{qn}\s*[\.、．]\s*', '', txt)
    
    # Parse options
    opt_matches = list(re.finditer(r'(?:^|\n|\s)([A-E])[\.、．]', txt))
    if len(opt_matches) > 5:
        opt_matches = opt_matches[-5:]
    
    first_opt_idx = opt_matches[0].start()
    stem = txt[:first_opt_idx].strip()
    
    options = {}
    for i in range(len(opt_matches)):
        lbl = opt_matches[i].group(1)
        st = opt_matches[i].end()
        en = opt_matches[i+1].start() if i+1 < len(opt_matches) else len(txt)
        val = txt[st:en].strip()
        val = re.sub(r'\s+', ' ', val)
        options[lbl] = val
    
    stem = re.sub(r'\n+', '\n', stem)
    
    logic_q_2022.append({
        "question_no": qn,
        "category": "逻辑推理",
        "stem": stem,
        "options": options
    })

writing_q_2022 = [
    {
        "question_no": 56,
        "category": "论证有效性分析",
        "stem": "论证有效性分析：分析下述论证中存在的缺陷和漏洞，选择若干要点，写一篇 600 字左右的文章，对该论证的有效性进行分析和评论。（论证有效性分析的一般要点是：概念特别是核心概念的界定和使用是否准确并前后一致，有无各种明显的逻辑错误，论证的论据是否成立并支持结论，结论成立的条件是否充分等。）\n\n默默无闻、无私奉献虽然是人们尊崇的德行，但这种德行其实不可能成为社会的道德精神。\n\n一种德行必须借助大众媒体的传播，让大家受其感染，并化为自觉意识，然后才能成为社会的道德精神。但是，默默无闻、无私奉献的精神所赖以存在的行为特点是不事张扬、不为人知。既然如此，它就得不到传播，也就不可能成为社会的道德精神。\n\n退一步讲，默默无闻、无私奉献的善举经媒体大力宣传以后为更多的人所了解，这就从根本上使这一善举，失去了默默无闻的特性。既然如此，这一命题就无从谈起了。\n\n再者，默默无闻的善举一旦被媒体大力宣传，当事人必然会受到社会的肯定与赞赏，而这就是社会对他的回报，既然他从社会得到了回报，怎么还可以说是无私奉献呢？\n\n由此可见，默默无闻、无私奉献的德行注定不可能成为社会的道德精神。",
        "options": {}
    },
    {
        "question_no": 57,
        "category": "论说文",
        "stem": "论说文：根据下述材料，写一篇 700 字左右的论说文，题目自拟。\n\n鸟类会飞是因为它们在进化中不断优化了其身体结构。飞行是一项特殊的运动，鸟类的躯体进化成了适合飞行的流线型，飞行也是一项需要付出高能量代价的运动，鸟类增强了翅膀、胸肌部位的功能，又改进了呼吸系统，以便给肌肉持续提供氧气，同时，鸟类在进化过程中舍弃了那些沉重的、效率低的身体部位。",
        "options": {}
    }
]

all_questions = math_q_2022 + logic_q_2022 + writing_q_2022
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
