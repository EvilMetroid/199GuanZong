import json, os, re

YEAR = 2025
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

math_q_2025 = [
    {
        "question_no": 1,
        "category": "问题求解",
        "stem": "两瓶酒精溶液体积相同，酒精与水的体积之比分别为 $1:2$ 和 $2:3$，将这两瓶酒精溶液混合，混合后酒精与水的体积之比为（ ）。",
        "options": {
            "A": "7:13",
            "B": "11:19",
            "C": "23:37",
            "D": "3:5",
            "E": "5:7"
        }
    },
    {
        "question_no": 2,
        "category": "问题求解",
        "stem": "已知圆、正方形、等边三角形的周长分别为 $a, b, c$，若它们的面积相等，则（ ）。",
        "options": {
            "A": "$a < b < c$",
            "B": "$a < c < b$",
            "C": "$b < a < c$",
            "D": "$b < c < a$",
            "E": "$c < b < a$"
        }
    },
    {
        "question_no": 3,
        "category": "问题求解",
        "stem": "某人骑车从甲地前往到乙地，前三分之一路程的平均速度是 $12\\text{km/h}$，中间三分之一路程的平均速度为 $18\\text{km/h}$，后三分之一路程的平均速度为 $12\\text{km/h}$，此人全程的平均速度是（ ）。",
        "options": {
            "A": "$12.5\\text{km/h}$",
            "B": "$13\\text{km/h}$",
            "C": "$13.5\\text{km/h}$",
            "D": "$14\\text{km/h}$",
            "E": "$14.5\\text{km/h}$"
        }
    },
    {
        "question_no": 4,
        "category": "问题求解",
        "stem": "一项任务，甲单独完成需要 15 天，甲、乙两人共同完成需要 6 天，甲、乙、丙三人共同完成需要 4 天。现在乙单独工作 1 天后，余下工作由甲、丙两人共同完成，还需要（ ）。",
        "options": {
            "A": "4 天",
            "B": "5 天",
            "C": "6 天",
            "D": "7 天",
            "E": "8 天"
        }
    },
    {
        "question_no": 5,
        "category": "问题求解",
        "stem": "如图，圆的半径为 2，圆心角 $\\angle AOB = 120^\\circ$，点 $C$ 是劣弧 $AB$ 上的动点，则四边形 $AOBC$ 面积的最大值为（ ）。",
        "options": {
            "A": "$\\sqrt{3}$",
            "B": "$2\\sqrt{3}$",
            "C": "4",
            "D": "$3\\sqrt{3}$",
            "E": "$4\\sqrt{3}$"
        }
    },
    {
        "question_no": 6,
        "category": "问题求解",
        "stem": "如图，在大半球中挖去一个同心小半球，小半球直径为大半球直径的一半，若小半球的体积为 $20\\text{cm}^3$，则剩下部分的体积为（ ）。",
        "options": {
            "A": "$160\\text{cm}^3$",
            "B": "$140\\text{cm}^3$",
            "C": "$100\\text{cm}^3$",
            "D": "$80\\text{cm}^3$",
            "E": "$60\\text{cm}^3$"
        }
    },
    {
        "question_no": 7,
        "category": "问题求解",
        "stem": "某单位举行田径赛，参加田赛项目有 50 人，参加径赛项目有 45 人。已知该单位有 90 名员工，其中 18 人未参加比赛。若两类项目均参加的女员工有 5 名，则两类项目均参加的男员工有（ ）。",
        "options": {
            "A": "10 人",
            "B": "12 人",
            "C": "14 人",
            "D": "16 人",
            "E": "18 人"
        }
    },
    {
        "question_no": 8,
        "category": "问题求解",
        "stem": "已知点 $A$ 是圆 $x^2 + y^2 - 16x - 12y + 75 = 0$ 的圆心，过原点 $O$ 作该圆的一条切线，切点为 $B$，则三角形 $AOB$ 的面积为（ ）。",
        "options": {
            "A": "$\\frac{15}{2}\\sqrt{5}$",
            "B": "$15\\sqrt{5}$",
            "C": "25",
            "D": "$25\\sqrt{3}$",
            "E": "$\\frac{25}{2}\\sqrt{3}$"
        }
    },
    {
        "question_no": 9,
        "category": "问题求解",
        "stem": "$1+2-3+4+5-6+7+8-9+10+\\cdots+97+98-99=$（ ）。",
        "options": {
            "A": "1536",
            "B": "1551",
            "C": "1568",
            "D": "1584",
            "E": "1617"
        }
    },
    {
        "question_no": 10,
        "category": "问题求解",
        "stem": "如图，在边长为 1 的正方形 $ABCD$ 中，$E, F$ 分别为 $AB, AD$ 的中点，$DE, BF$ 交于点 $O$，四边形 $BCDO$ 的面积为（ ）。",
        "options": {
            "A": "$\\frac{2}{3}$",
            "B": "$\\frac{3}{4}$",
            "C": "$\\frac{5}{9}$",
            "D": "$\\frac{7}{12}$",
            "E": "$\\frac{11}{18}$"
        }
    },
    {
        "question_no": 11,
        "category": "问题求解",
        "stem": "100 件商品中 2 件次品，将其分成 10 箱，每箱 10 件，则 2 件次品在同一箱的概率为（ ）。",
        "options": {
            "A": "$\\frac{1}{5}$",
            "B": "$\\frac{2}{11}$",
            "C": "$\\frac{1}{10}$",
            "D": "$\\frac{1}{11}$",
            "E": "$\\frac{9}{100}$"
        }
    },
    {
        "question_no": 12,
        "category": "问题求解",
        "stem": "甲乙丙三股东，甲股份是丙的 2.4 倍，乙是丙 3 倍，年底分红，20% 红利 3 人均分，剩余按持有比例分，丙分 460 万元，则年底红利为（ ）。",
        "options": {
            "A": "2400 万",
            "B": "2100 万",
            "C": "1800 万",
            "D": "1200 万",
            "E": "1000 万"
        }
    },
    {
        "question_no": 13,
        "category": "问题求解",
        "stem": "袋中两个红球，三个白球，四个黑球，随机摸两个，两个同色的概率为（ ）。",
        "options": {
            "A": "$\\frac{1}{6}$",
            "B": "$\\frac{1}{4}$",
            "C": "$\\frac{7}{36}$",
            "D": "$\\frac{5}{18}$",
            "E": "$\\frac{1}{3}$"
        }
    },
    {
        "question_no": 14,
        "category": "问题求解",
        "stem": "设 $a, b, c, d$ 为正整数，若 $\\frac{27}{35} = \\frac{b}{a} + \\frac{d}{c}$，则 $a+b+c+d$ 的最小值为（ ）。",
        "options": {
            "A": "15",
            "B": "16",
            "C": "17",
            "D": "18",
            "E": "24"
        }
    },
    {
        "question_no": 15,
        "category": "问题求解",
        "stem": "$ABCDE$ 五个集装箱堆放成两组，每次运走每组最上面一堆，将 5 个集装箱全部运走不同搬运顺序为（ ）。",
        "options": {
            "A": "5 种",
            "B": "6 种",
            "C": "10 种",
            "D": "12 种",
            "E": "15 种"
        }
    },
    {
        "question_no": 16,
        "category": "条件充分性判断",
        "stem": "甲、乙、丙三人共同完成了一批零件的加工，三人的工作效率互不相同，已知他们的工作效率之比，则能确定这批零件的数量。\n(1) 已知甲、乙两人加工零件数量之差。\n(2) 已知甲、丙两人加工零件数量之和。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 17,
        "category": "条件充分性判断",
        "stem": "设 $m, n$ 为正整数，能确定 $m, n$ 的乘积。\n(1) 已知 $m, n$ 的最大公约数。\n(2) 已知 $m, n$ 的最小公倍数。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 18,
        "category": "条件充分性判断",
        "stem": "甲班 34 人，乙班 36 人，在满分 100 分的考试中，甲班总分数与乙班总分数相等，则可知两班的平均分之差。\n(1) 两班的平均分都是整数。\n(2) 乙班的平均分不低于 65。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 19,
        "category": "条件充分性判断",
        "stem": "如图，在菱形 $ABCD$ 中，$M, N$ 分别为 $AD$ 和 $CD$ 的中点，$P$ 是 $AC$ 上的动点，则能确定 $PM+PN$ 的最小值。\n(1) 已知 $AC$。\n(2) 已知 $AB$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 20,
        "category": "条件充分性判断",
        "stem": "在分别标记了数字 1，2，3，4，5，$a$ 的 6 张卡片中，随机抽取 2 张，则这两张卡片上的数字之和为奇数的概率大于 $\\frac{1}{2}$。\n(1) $a = 7$。\n(2) $a = 8$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 21,
        "category": "条件充分性判断",
        "stem": "设 $a, b$ 为实数，则 $(a+b\\sqrt{2})^\\frac{1}{2} = 1+\\sqrt{2}$。\n(1) $a=3, b=2$。\n(2) $(a-b\\sqrt{2})(3+2\\sqrt{2}) = 1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 22,
        "category": "条件充分性判断",
        "stem": "设 $p, q$ 为常数，一个等腰三角形的腰和底分别是方程 $x^2 - 3px + q = 0$ 的两个根，则能确定这个三角形。\n(1) $q \\le 2p^2$。\n(2) $p \\ge 2$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 23,
        "category": "条件充分性判断",
        "stem": "$x, y$ 是实数，则 $\\sqrt{2x^2+2y^2} - |x| - y^2 \\ge 0$。\n(1) $|x| \\le 1$。\n(2) $|y| \\le 1$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 24,
        "category": "条件充分性判断",
        "stem": "已知数列 $\{a_n\}$，则能确定 $a_1, a_2, a_3, a_4, a_5$ 成等差。\n(1) 已知 $a_1 + a_5 = a_2 + a_4$。\n(2) 已知 $a_1 + a_5 = 2a_3$。",
        "options": COND_OPTIONS
    },
    {
        "question_no": 25,
        "category": "条件充分性判断",
        "stem": "已知曲线 $L: y = a(x-1)(x-7)$，则能确定 $a$ 的值。\n(1) 曲线与圆 $(x-4)^2 + (y+1)^2 = 10$ 恰有 3 个交点。\n(2) 曲线与圆 $(x-4)^2 + (y-4)^2 = 25$ 恰有 4 个交点。",
        "options": COND_OPTIONS
    }
]

# Parse logic from OCR cache
with open('199管综真题_Markdown题库/2025年/ocr_cache.json') as f:
    cache = json.load(f)

all_lines = []
for p in range(4, 19):
    for l in cache[str(p)]:
        t = l['text'].strip()
        if '2025考研199管综真题' in t: continue
        all_lines.append(t)

full_text = '\n'.join(all_lines)
full_text = re.sub(r'三、逻辑推理：第 26～55 小题.*?请在答题卡上将所选项的字母涂黑。', '', full_text, flags=re.S)

writing_pos = full_text.find('四、写作')
logic_text = full_text[:writing_pos] if writing_pos != -1 else full_text

# Shared stems definition
stems_map = {
    (39, 40): "39～40 题基于以下题干：\n全球气候正在变暖。权威科学报告显示，最近 50 年的全球气候变暖主要是人类燃烧化石燃料导致的。全球气候变暖已经给人类的生存和发展带来巨大危害。当前，人类的生产生活排放正在逼近多个气候临界点，一旦突破这些临界点，人类的未来将面临巨大风险。如何应对这样的气候风险？以下几位专家相继提出不同看法：\n甲：各国应当尽快停止依赖化石燃料，转向开发风能、水能、太阳能等清洁能源。\n乙：有些发展中国家由于经济、技术等条件的限制，目前还无法很快实现能源转型。\n丙：当前气候风险巨大，不能尽快实现能源转型的国家就是在破坏人类的共同家园。\n丁：全球气候变暖主要是发达国家 200 多年的工业排放导致的，他们更应对此负责。\n戊：若要求发展中国家尽快实现能源转型，发达国家就必须向他们提供资金和技术。\n己：所谓气候风险目前还存在不确定性，在此情况下花费巨大代价去应对并不明智。",
    (50, 51): "50～51 题基于以下题干：\n在欣赏一幅古代山水画时，某人发现在一片山水屋舍之间，有主人、童子、访客和垂钓 4 种人物共 6 人点缀其中。3 名访客正走在门外的小桥上高声呼喊，画中的主人正要打开院门迎客，童子正在院中煮茶，1 名钓者正在远离人群的一条小溪旁安静垂钓。赏画人将这 6 人当作甲、乙、丙、丁、戊、己，并且设想：\n(1) 如果甲是主人，则乙和丙均是访客；\n(2) 如果丙是访客，则己在院外且甲是童子；\n(3) 如果丙和丁至多有一人是访客，则甲是主人且戊在院内。",
    (52, 53): "52～53 题基于以下题干：\n某次考试有 10 道选择题，小李、小王、小文 3 人均只答对其中 6 道题。已知：\n(1) 没有人连续答对 3 道题；\n(2) 小李第 2、4、9 题答错了，小王第 1、5、8 题答错了，小文第 3、6、9 题答错了。",
    (54, 55): "54～55 题基于以下题干：\n某学院尚余 9 个考场的监考任务供甲、乙、丙、丁、戊 5 位老师选择。已知，每场考试 2 小时，每位老师均需监考 2～3 个考场；有 2 个考场要求其中 2 人共同监考；其余 7 个考场要求单独监考，各需 1 名监考人员。这 9 个考场的时间安排详见题图。\n对于监考安排，丙、丁没有任何要求，但其他 3 位老师有如下要求：\n甲：我的监考需安排在晚上，但不要连续两个晚上都安排监考；\n乙：若我的监考没有都安排在前三天，则有一场需安排我和丙在同一天同一时间监考；\n戊：我想监考三场，但都不要安排在上午。\n事后得知，这 3 位老师的要求均得到了满足。"
}

clean_logic_text = logic_text
clean_logic_text = re.sub(r'39~40题基于以下题干.*?(?=39[\.、．。])', '', clean_logic_text, flags=re.S)
clean_logic_text = re.sub(r'50~51\s*题基于以下题干.*?(?=50[\.、．。])', '', clean_logic_text, flags=re.S)
clean_logic_text = re.sub(r'52~53\s*题基于以下题干.*?(?=52[\.、．。])', '', clean_logic_text, flags=re.S)
clean_logic_text = re.sub(r'54～55题基于以下题干.*?(?=54[\.、．。])', '', clean_logic_text, flags=re.S)

pos42 = clean_logic_text.find('42．')
q41_text = '''41. 已知“■■■■”“■■■■”和“■■■■”是三组图形符号，其中有两组分别表示“春花开满园”和“满山梅花开”。\n根据以上信息，可知“■■”中两个相邻图形符号表示的汉字有（详见题图）。\nA. 春山\nB. 梅园\nC. 梅山\nD. 花园\nE. 山花\n'''
clean_logic_text = clean_logic_text[:pos42] + q41_text + clean_logic_text[pos42:]

pos54 = clean_logic_text.find('54．')
q53_text = '''53. 若有一题 3 人均答对了，有一题 3 人均答错了，则以下哪项一定是错误的？\nA. 小李第 3 题答对了。\nB. 小王第 2 题答对了。\nC. 小王第 3 题答错了。\nD. 小文第 2 题答错了。\nE. 小文第 4 题答对了。\n'''
clean_logic_text = clean_logic_text[:pos54] + q53_text + clean_logic_text[pos54:]

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

pat = r'(?:^|\n|\s|[（(])([A-E])(?:[）\)\.、．]|\s|(?=[\u4e00-\u9fa5]))'

logic_q_2025 = []
for qn in range(26, 56):
    txt = logic_q_raw[qn]
    txt = re.sub(rf'^\s*{qn}\s*[\.、．。]\s*', '', txt)
    
    matches = list(re.finditer(pat, txt))
    if len(matches) > 5:
        matches = matches[-5:]
    
    first_opt_idx = matches[0].start()
    stem = txt[:first_opt_idx].strip()
    stem = re.sub(r'\n+', '\n', stem)
    
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
        
    logic_q_2025.append({
        "question_no": qn,
        "category": "逻辑推理",
        "stem": stem,
        "options": options
    })

writing_q_2025 = [
    {
        "question_no": 56,
        "category": "论证有效性分析",
        "stem": "论证有效性分析：分析下述论证中存在的缺陷和漏洞，选择若干要点，写一篇 600 字左右的文章，对该论证的有效性进行分析和评论。（论证有效性分析的一般要点是：概念特别是核心概念的界定和使用是否准确并前后一致，有无各种明显的逻辑错误，论证的论据是否成立并支持结论，结论成立的条件是否充分，等等。）\n\n有位西方哲学家曾经指出，一个人在已有的知识体系、价值观念、思维方式等因素的影响下，会形成特定的主观立场，即“前见”。实际上，人们在相互沟通与理解外部世界时无法摆脱这一“前见”。早在先秦时期庄子就说过，人们认为毛嫱是美女，但鱼见到毛嫱只会惊恐游走，这些都表明，人们在相互沟通与理解过程中，主观立场造成了很大障碍。\n\n首先，不同个体交流时无法避免偏见，偏见是每个人都可能拥有的，这一主观立场正是我们沟通与理解的障碍。我们对喜欢的人往往会宽厚包容，对不喜欢的人会吹毛求疵。科学研究表明，别人对我们的实际印象与我们自认为留给别人的印象往往存在差异。\n\n其次，性别不同也会带来主观立场的不同，从而导致沟通障碍。比如，家庭中丈夫和妻子在思维方式上存在不小的差异，丈夫往往偏重理性，而妻子则偏重感性，所以双方从各自的主观立场出发讨论问题时，就会产生分歧与争议。\n\n再次，不同文化之间的交流与理解也存在同样问题。比如不同文化在审美标准上的主观差异通常会导致误解，与中国历史上伟大诗人李白作品相比，唐代僧人寒山的作诗作更受一些美国人的喜爱。白居易的诗篇更受一些日本人青睐，所以不同文化背景下的读者在评判作家作品的高下时经常产生争议。\n\n虽然主观立场造成了沟通与理解的障碍，但这并不意味着人们无法进行理解与沟通，千百年来通过换位思考来克服障碍，摆脱个人主观立场。",
        "options": {}
    },
    {
        "question_no": 57,
        "category": "论说文",
        "stem": "论说文：根据下述材料，写一篇 700 字左右的论说文，题目自拟。\n\n通常情况下，人们都希望被他人认可被社会承认。这种心理会促使他们去接受某种评价标准。因为只有接受了标准并身体力行，他们才能被社会肯定，否则便会被认为不合群。",
        "options": {}
    }
]

all_questions = math_q_2025 + logic_q_2025 + writing_q_2025
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
