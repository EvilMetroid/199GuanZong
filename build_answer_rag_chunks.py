#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从答案解析 Markdown 题库生成 RAG 切分库(JSONL)。

与 build_rag_chunks_from_md.py(真题卷)配对:真题库给出题干/选项/切片图,
本库给出同年份同题号的答案与解析,消费方可按 (year, question_no) 关联。
答案解析 md 由 build_answer_md.py 生成且逐年结构统一,以 md 为唯一内容源。

用法:
    python3 build_answer_rag_chunks.py            # 全量重建
    python3 build_answer_rag_chunks.py 2013 2018  # 只重建指定年份

输出:
    199管综答案_Markdown题库/{year}年/{year}年199真题解析_chunks.jsonl   (每年)
    199管综答案_Markdown题库/199管综历年真题_全量RAG切分库_答案.jsonl    (汇总)
    ./199管综历年真题_全量RAG切分库_答案.jsonl                            (仓库根目录镜像)

chunk 字段:year / question_no / category / answer / explanation
    category 与真题库一致:1-15 问题求解、16-25 条件充分性判断、
    26-55 逻辑推理、56 论证有效性分析、57 论说文;
    answer 为 1-55 题的 A-E 字母,写作题为 null;
    explanation 为解析全文(含参考范文);md 中"（内容缺失,见原 PDF）"
    占位行转为空串。

校验:每年必须恰好 57 个 chunk;1-55 题必须有 A-E 答案字母(缺失则非 0 退出);
解析为空仅告警(2022 精简版个别题目原书只给答案,属真实状态)。
"""

import json
import re
import sys
from pathlib import Path

OUTPUT_ROOT = Path("199管综答案_Markdown题库")
TOTAL_JSONL_NAME = "199管综历年真题_全量RAG切分库_答案.jsonl"

Q_HEAD = re.compile(r"^### 第 (\d+) 题")
ANSWER = re.compile(r"^\*\*答案\*\*\s*[:：]\s*([A-Ea-e])\b")
HEADER = re.compile(r"^(## |### )")
MISSING_PLACEHOLDER = "（内容缺失,见原 PDF）"

CATEGORY = {
    15: "问题求解", 25: "条件充分性判断", 55: "逻辑推理",
    56: "论证有效性分析", 57: "论说文",
}


def category_of(q: int) -> str:
    for upper, cat in CATEGORY.items():
        if q <= upper:
            return cat
    return ""


def parse_year_md(md_path: Path):
    """解析单年答案解析 md,返回 (chunks, problems, warnings)。"""
    year = int(md_path.parent.name.replace("年", ""))
    lines = md_path.read_text(encoding="utf-8").split("\n")

    # 定位题目块:### 第 N 题 到下一个任意标题行(## 板块 / ### 下一题)
    q_blocks = {}
    spans = []
    for i, ln in enumerate(lines):
        m = Q_HEAD.match(ln)
        if m:
            spans.append((int(m.group(1)), i))
    for k, (qnum, i) in enumerate(spans):
        end = spans[k + 1][1] if k + 1 < len(spans) else len(lines)
        for j in range(i + 1, end):
            if HEADER.match(lines[j]):
                end = j
                break
        q_blocks[qnum] = lines[i + 1:end]

    problems, warnings = [], []
    if sorted(q_blocks) != list(range(1, 58)):
        missing = [q for q in range(1, 58) if q not in q_blocks]
        problems.append(f"题目块缺失: {missing}")

    chunks = []
    for q in range(1, 58):
        block = q_blocks.get(q, [])
        answer = None
        expl_lines = []
        for ln in block:
            if not ln.strip():
                continue
            ma = ANSWER.match(ln.strip())
            if ma and answer is None:
                answer = ma.group(1).upper()
                continue
            if ln.strip() == MISSING_PLACEHOLDER:
                continue
            expl_lines.append(ln)
        explanation = "\n".join(expl_lines).strip()

        if q <= 55 and not answer:
            problems.append(f"Q{q} 缺少答案字母")
        if not explanation:
            warnings.append(f"Q{q} 解析为空(2022 精简版原书个别题目仅给答案)")

        chunks.append({
            "year": year, "question_no": q,
            "category": category_of(q),
            "answer": answer, "explanation": explanation,
        })
    return chunks, problems, warnings


def main():
    only = [int(x) for x in sys.argv[1:]]
    all_chunks, n_problems = [], 0
    year_dirs = sorted(OUTPUT_ROOT.glob("[0-9][0-9][0-9][0-9]年"))
    if only:
        year_dirs = [d for d in year_dirs if int(d.name.replace("年", "")) in only]
    for d in year_dirs:
        year = int(d.name.replace("年", ""))
        md_path = d / f"{year}年199管综真题解析.md"
        if not md_path.exists():
            print(f"[✘] {year} 年缺少 {md_path.name},跳过")
            n_problems += 1
            continue
        chunks, problems, warnings = parse_year_md(md_path)
        out = d / f"{year}年199真题解析_chunks.jsonl"
        with out.open("w", encoding="utf-8") as f:
            for c in chunks:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        all_chunks.extend(chunks)
        status = "OK " if len(chunks) == 57 and not problems else "WARN"
        print(f"[{status}] {year}: {len(chunks)} chunks -> {out.name}")
        for w in warnings:
            print(f"       ! {w}")
        for p in problems:
            print(f"       ✘ {p}")
            n_problems += 1
        if len(chunks) != 57:
            n_problems += 1

    total_path = OUTPUT_ROOT / TOTAL_JSONL_NAME
    with total_path.open("w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    mirror = Path(TOTAL_JSONL_NAME)
    mirror.write_text(total_path.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"\n共 {len(all_chunks)} 条切分({len(year_dirs)} 个年份)")
    print(f"汇总库: {total_path}")
    print(f"根目录镜像: {mirror}")
    if n_problems:
        print(f"⚠ 有 {n_problems} 处问题,见上方明细,请人工复核对应题目")
        sys.exit(1)
    print("全部年份 57 题齐整,校验通过")


if __name__ == "__main__":
    main()
