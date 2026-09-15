import json, os, re, fitz

YEAR = 2017
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

math_q_2017 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "甲从 1、2、3 中抽取一个数，记为 $a$；乙从 1、2、3、4 中抽取一个数，记为 $b$。若规定当 $a > b$ 或 $a+1 < b$ 时甲获胜，则甲获胜的概率为（ ）。",
        "options": {
            "A": "1/6",
            "B": "1/4",
            "C": "1/3",
            "D": "5/12",
            "E": "1/2"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "已知 $\\triangle ABC$ 和 $\\triangle A'B'C'$ 满足 $AB : A'B' = AC : A'C' = 2 : 3, \\angle A + \\angle A' = \\pi$，则 $\\triangle ABC$ 和 $\\triangle A'B'C'$ 的面积之比为（ ）。",
        "options": {
            "A": "$\\sqrt{2} : \\sqrt{3}$",
            "B": "$\\sqrt{3} : \\sqrt{5}$",
            "C": "$2 : 3$",
            "D": "$2 : 5$",
            "E": "$4 : 9$"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "将 6 人分成 3 组，每组 2 人，则不同的分组方式共有（ ）种。",
        "options": {
            "A": "12",
            "B": "15",
            "C": "30",
            "D": "45",
            "E": "90"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "甲、乙、丙三人每轮各投篮 10 次，投了三轮。投中数如表1所示：\n\n| | 第一轮 | 第二轮 | 第三轮 |\n| :--- | :--- | :--- | :--- |\n| **甲** | 2 | 5 | 8 |\n| **乙** | 5 | 2 | 5 |\n| **丙** | 8 | 4 | 9 |\n\n设 $\\sigma_1, \\sigma_2, \\sigma_3$ 分别为甲、乙、丙投中数的方差，则（ ）。",
        "options": {
            "A": "$\\sigma_1 > \\sigma_2 > \\sigma_3$",
            "B": "$\\sigma_1 > \\sigma_3 > \\sigma_2$",
            "C": "$\\sigma_2 > \\sigma_1 > \\sigma_3$",
            "D": "$\\sigma_2 > \\sigma_3 > \\sigma_1$",
            "E": "$\\sigma_3 > \\sigma_2 > \\sigma_1$"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "将长、宽、高分别是 12、9 和 6 的长方体切割成正方体，且切割后无剩余，则能切割成相同正方体的最少个数为（ ）。",
        "options": {
            "A": "3",
            "B": "6",
            "C": "24",
            "D": "96",
            "E": "648"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "某品牌电冰箱连续两次降价 $10\\%$ 后的售价是降价前的（ ）。",
        "options": {
            "A": "80%",
            "B": "81%",
            "C": "82%",
            "D": "83%",
            "E": "85%"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "甲、乙、丙三种货车的载重量成等差数列。2 辆甲种车和 1 辆乙种车的载重量为 95 吨，1 辆甲种车和 3 辆丙种车的载重量为 150 吨，则甲、乙、丙分别各一辆车一次最多运送货物为（ ）吨。",
        "options": {
            "A": "125",
            "B": "120",
            "C": "115",
            "D": "110",
            "E": "105"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "张老师到一所中学进行招生咨询，上午接受了 45 名同学的咨询，其中的 9 名同学下午又咨询了张老师，占张老师下午咨询学生的 $10\\%$。一天中向张老师咨询的学生人数为（ ）人。",
        "options": {
            "A": "81",
            "B": "90",
            "C": "115",
            "D": "126",
            "E": "135"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "某种机器人可搜索到的区域是半径为 1 米的圆，若该机器人沿直线行走 10 米，则其搜索过的区域的面积为（ ）（单位：平方米）。",
        "options": {
            "A": "$10 + \\frac{\\pi}{2}$",
            "B": "$10 + \\pi$",
            "C": "$20 + \\frac{\\pi}{2}$",
            "D": "$20 + \\pi$",
            "E": "$10\\pi$"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "不等式 $|x-1| + x \\le 2$ 的解集为（ ）。",
        "options": {
            "A": "$(-\\infty, 1]$",
            "B": "$(-\\infty, \\frac{3}{2}]$",
            "C": "$[1, \\frac{3}{2}]$",
            "D": "$[1, +\\infty)$",
            "E": "$[\\frac{3}{2}, +\\infty)$"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "在 1 到 100 之间，能被 9 整除的整数的平均值是（ ）。",
        "options": {
            "A": "27",
            "B": "36",
            "C": "45",
            "D": "54",
            "E": "63"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "某试卷由 15 道选择题组成，每道题有 4 个选项，只有一项是符合试题要求的。甲有 6 道题能确定正确选项，有 5 道题能排除 2 个错误选项，有 4 道题能排除 1 个错误选项。若从每题排除后剩余的选项中选 1 个作为答案，则甲得满分的概率为（ ）。",
        "options": {
            "A": "$\\frac{1}{2^4} \\times \\frac{1}{3^5}$",
            "B": "$\\frac{1}{2^5} \\times \\frac{1}{3^4}$",
            "C": "$\\frac{1}{2^5} + \\frac{1}{3^4}$",
            "D": "$\\frac{1}{2^4} \\times (\\frac{3}{4})^5$",
            "E": "$\\frac{1}{2^4} + (\\frac{3}{4})^5$"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "某公司用 1 万元购买了价格分别为 1750 元和 950 元的甲、乙两种办公设备，则购买的甲、乙办公设备的件数分别为（ ）。",
        "options": {
            "A": "3, 5",
            "B": "5, 3",
            "C": "4, 4",
            "D": "2, 6",
            "E": "6, 2"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "如图1所示，在扇形 $AOB$ 中，$\\angle AOB = \\frac{\\pi}{4}, OA = 1, AC \\perp OB$，则阴影部分的面积为（ ）。",
        "options": {
            "A": "$\\frac{\\pi}{8} - \\frac{1}{4}$",
            "B": "$\\frac{\\pi}{8} - \\frac{1}{8}$",
            "C": "$\\frac{\\pi}{4} - \\frac{1}{2}$",
            "D": "$\\frac{\\pi}{4} - \\frac{1}{4}$",
            "E": "$\\frac{\\pi}{4} - \\frac{1}{8}$"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "老师问班上 50 名同学周末复习的情况，结果有 20 人复习过数学、30 人复习过语文、6 人复习过英语，且同时复习了数学和语文的有 10 人、语文和英语的有 2 人、英语和数学的有 3 人。若同时复习过这三门课的人数为 0，则没复习过这三门课程的学生人数为（ ）人。",
        "options": {
            "A": "7",
            "B": "8",
            "C": "9",
            "D": "10",
            "E": "11"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "某人需要处理若干份文件，第一小时处理了全部文件的 $\\frac{1}{5}$，第二小时处理了剩余文件的 $\\frac{1}{4}$，则此人需要处理的文件数为 25 份。\n(1) 前两个小时处理了 10 份文件。\n(2) 第二小时处理了 5 份文件。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "能确定某企业产值的月平均增长率。\n(1) 已知一月份的产值。\n(2) 已知全年的总产值。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "圆 $x^2 + y^2 - ax - by + c = 0$ 与 $x$ 轴相切，则能确定 $c$ 的值。\n(1) 已知 $a$ 的值。\n(2) 已知 $b$ 的值。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "某人从 A 地出发，先乘时速为 220 千米的动车，后转乘时速为 100 千米的汽车到达 B 地，则 A、B 两地的距离为 960 千米。\n(1) 乘动车时间与乘汽车的时间相等。\n(2) 乘动车时间与乘汽车的时间之和为 6 小时。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "直线 $y = ax + b$ 与抛物线 $y = x^2$ 有两个交点。\n(1) $a^2 > 4b$。\n(2) $b > 0$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "如图2所示，一个铁球沉入水池中，则能确定铁球的体积。\n(1) 已知铁球露出水面的高度。\n(2) 已知水深及铁球与水面交线的周长。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "已知 $a, b, c$ 为三个实数，则 $\\min\\{|a-b|, |b-c|, |a-c|\\} \\le 5$。\n(1) $|a| \\le 5, |b| \\le 5, |c| \\le 5$。\n(2) $a + b + c = 15$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "某机构向 12 位教师征题，共征集到 5 种题型的试题 52 道，则能确定供题教师的人数。\n(1) 每位供题教师提供的试题数相同。\n(2) 每位供题教师提供的题型不超过 2 种。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "某人参加资格考试，有 A 类和 B 类选择，A 类的合格标准是抽 3 道题至少会做 2 道，B 类的合格标准是抽 2 道题需都会做，则此人参加 A 类考试合格的机会大。\n(1) 此人 A 类题中有 $60\\%$ 会做。\n(2) 此人 B 类题中有 $80\\%$ 会做。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "设 $a, b$ 是两个不相等的实数，则函数 $f(x) = x^2 + 2ax + b$ 的最小值小于零。\n(1) $1, a, b$ 成等差数列。\n(2) $1, a, b$ 成等比数列。",
        "options": COND_OPTIONS
    }
]

# Read PDF text for Q26-57
doc = fitz.open(f"真题部分/{YEAR}年199管综真题.pdf")
pages_text = [doc[p].get_text() for p in range(5, 15)]
raw_all = "\n".join(pages_text)
raw_all = re.sub(rf'{YEAR}\s*年真题[^\n]*\n', '', raw_all)
all_text = raw_all[raw_all.find("三、逻辑推理"):]

special_opts_2017 = {
    37: {
        "A": "1/3 以上的硕士生不能将该书中的名句与诗名或作者对应起来。",
        "B": "大部分硕士生能将该书中的名句与诗名及其作者对应起来。",
        "C": "1/3 以上的一、二年级学生不能把该书中的名句与作者对应起来。",
        "D": "2/3 以上的一、二年级学生不能把该书中的名句与诗名对应起来。",
        "E": "2/3 以上的一、三年级学生能把该书中的名句与诗名对应起来。"
    },
    48: {
        "A": "我是这个团队的灵魂，一旦我离开了这个团队，他们将一事无成。",
        "B": "他有什么资格批评我？大家看看，他的能力连我的一半都不到。",
        "C": "我的家庭条件不好，但不愿意被别人看不起，所以我借钱买了一部智能手机。",
        "D": "这么重要的活动竟然没有邀请我参加，组织者的人品肯定有问题，不值得跟这样的人交往。",
        "E": "我刚接手别人很多年没有做成的事情，我跟他们完全不在一个层次，相信很快就会将事情搞定。"
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
all_questions = list(math_q_2017)

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
        
    if q in special_opts_2017:
        opts = special_opts_2017[q]
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
