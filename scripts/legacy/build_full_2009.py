import json, os, re

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

# Load all questions
with open("questions_2009_data.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

print(f"Loaded {len(questions)} questions.")

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

for q in questions:
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

print(f"Generated {MD_PATH} and {JSONL_PATH} with {len(chunks)} chunks successfully!")
