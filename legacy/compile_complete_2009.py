import json, os, re, fitz

YEAR = 2009
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

from make_2009_data import math_q

doc = fitz.open("真题部分/2009-2024年199管综真题合集.pdf")
pages_text = [doc[p].get_text() for p in range(4, 13)]
all_text = "\n".join(pages_text)
all_text = re.sub(r'2009\s*年真题[^\n]*\n', '', all_text)

q_positions = {}
for q in range(26, 58):
    m = re.search(rf'(?:^|\n)\s*{q}[\.、．]', all_text)
    if m:
        q_positions[q] = m.start()

sorted_qs = sorted(q_positions.keys())
all_questions = list(math_q)

def normalize_options(raw):
    t = re.sub(r'(?:^|\n|\s|[。？?；;∶:])[（\(]+([A-E])[）\)\>、．]?', r'\n\1. ', raw)
    t = re.sub(r'(?:^|\n|\s|[。？?；;∶:])([A-E])[）\)\>、．]\s*', r'\n\1. ', t)
    return t

for i, q in enumerate(sorted_qs):
    start = q_positions[q]
    end = q_positions[sorted_qs[i+1]] if i+1 < len(sorted_qs) else len(all_text)
    raw = all_text[start:end].strip()
    raw = re.sub(r'^\d{1,2}[\.、．]\s*', '', raw)
    
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
