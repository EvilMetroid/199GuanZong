#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从答案解析 Markdown 题库生成 RAG 切分库(JSONL)。

与 build_rag_chunks_from_md.py(真题卷)配对:真题库给出题干/选项/切片图,
本库给出同年份同题号的答案与解析,消费方可按 (year, question_no) 关联,
同题多条切分按 part 升序拼接即得解析全文。答案解析 md 由 build_answer_md.py
生成且逐年结构统一(2026 年为人工整理),以 md 为唯一内容源。

用法(仓库根目录执行,脚本自身按 __file__ 定位仓库根,任意目录亦可):
    python3 scripts/build_answer_rag_chunks.py            # 全量重建
    python3 scripts/build_answer_rag_chunks.py 2013 2018  # 只重建指定年份

指定年份时,汇总库仍覆盖全部年份:指定年份从 md 重建,其余年份从各自
的逐年 jsonl 合并,不会因局部重建而丢失其他年份。指定的年份在题库中
不存在(或含非数字参数)时直接报错退出,不写任何文件。合并的逐年 jsonl
若比其 md 旧(改过 md 忘了重建),同样报错退出,防止汇总库混入过期内容。

输出:
    199管综答案_Markdown题库/{year}年/{year}年199真题解析_chunks.jsonl   (每年)
    199管综答案_Markdown题库/199管综历年真题_全量RAG切分库_答案.jsonl    (汇总)
    ./199管综历年真题_全量RAG切分库_答案.jsonl                            (仓库根目录镜像)

chunk 字段:year / question_no / category / answer / part / parts / part_label / explanation
    category 与真题库一致:1-15 问题求解、16-25 条件充分性判断、
    26-55 逻辑推理、56 论证有效性分析、57 论说文;
    answer 为 1-55 题的 A-E 字母,写作题为 null;
    1-55 题每题 1 条切分(part=parts=1,part_label 为空串);
    写作题按板块细分为多条切分:以"参考范文"行和独占一行的【…】标题
    (【谬误分析】【参考立意】【参考范文】【高分范文 N】等)为分界,
    2025 写作题中穿插原文的【谬误 N】类标注不算分界;
    分界前的引导段(如 2026 的材料概述)label 为空串;
    explanation 为该板块内容;md 中"（内容缺失,见原 PDF）"占位行转为空串。

校验:每年 57 个题目块齐整、1-55 题必须有 A-E 答案字母(缺失则非 0 退出);
汇总库必须覆盖题库内全部年份,缺年份非 0 退出;解析为空仅告警
(2022 精简版原书个别题目仅给答案,属真实状态)。
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # 仓库根目录
OUTPUT_ROOT = ROOT / "199管综答案_Markdown题库"
TOTAL_JSONL_NAME = "199管综历年真题_全量RAG切分库_答案.jsonl"

Q_HEAD = re.compile(r"^### 第 (\d+) 题")
ANSWER = re.compile(r"^\*\*答案\*\*\s*[:：]\s*([A-Ea-e])\b")
MISSING_PLACEHOLDER = "（内容缺失,见原 PDF）"

# 写作题分块边界:独占一行的【…】标题,或"参考范文"开头行(标题可能同行为内)
ESSAY_BOUNDARY = re.compile(r"^(?:【[^】]{1,20}】|参考范文)")
# 2025 写作题把【谬误 N】整行标注穿插在材料引用之间(行尾常带整句批评),
# 属行内标注而非板块起点,前缀匹配不算分界
ESSAY_BOUNDARY_SKIP = re.compile(r"^【(?:谬误|缺陷|漏洞|点评)\s*\d+】")

CATEGORY = {
    15: "问题求解", 25: "条件充分性判断", 55: "逻辑推理",
    56: "论证有效性分析", 57: "论说文",
}


def category_of(q: int) -> str:
    for upper, cat in CATEGORY.items():
        if q <= upper:
            return cat
    return ""


def atomic_write(path: Path, text: str):
    """先写临时文件再原子替换,避免中途失败留下半截 jsonl/md。"""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def parse_year_args(available):
    """命令行年份参数:非数字或题库中不存在的年份直接报错退出。"""
    args = sys.argv[1:]
    bad = [a for a in args if not a.isdigit()]
    if bad:
        print(f"[✘] 非法年份参数: {bad}(应为 4 位年份数字)")
        sys.exit(1)
    only = [int(a) for a in args]
    unknown = [y for y in only if y not in available]
    if unknown:
        print(f"[✘] 指定的年份在题库中不存在: {unknown}")
        print(f"    题库现有年份: {sorted(available)}")
        sys.exit(1)
    return only


def split_essay_parts(expl_lines):
    """写作题解析 -> [(label, [行])]:分界行开启新板块,分界前行归 label 为空的引导段。"""
    parts, label, cur = [], "", []
    for ln in expl_lines:
        t = ln.strip()
        if t and ESSAY_BOUNDARY.match(t) and not ESSAY_BOUNDARY_SKIP.match(t):
            if parts or cur:
                parts.append((label, cur))
            label = t if t.startswith("【") else "参考范文"
            cur = []
        else:
            cur.append(ln)
    parts.append((label, cur))
    # 去掉内容为空的板块(整块仅标题且无正文时保留最后一条,由上层告警)
    parts = [(lb, ls) for lb, ls in parts if any(l.strip() for l in ls)] \
        or parts[-1:]
    return parts


def parse_year_md(md_path: Path):
    """解析单年答案解析 md,返回 (chunks, problems, warnings)。"""
    year = int(md_path.parent.name.replace("年", ""))
    lines = md_path.read_text(encoding="utf-8").split("\n")

    # 定位题目块:### 第 N 题 到下一个题号锚点或 ## 板块标题。
    # 2026 写作题块内的"### 范文标题"行属 Q56/57 内容,不是块边界。
    q_blocks = {}
    spans = []
    for i, ln in enumerate(lines):
        m = Q_HEAD.match(ln)
        if m:
            spans.append((int(m.group(1)), i))
    for k, (qnum, i) in enumerate(spans):
        end = spans[k + 1][1] if k + 1 < len(spans) else len(lines)
        for j in range(i + 1, end):
            if lines[j].startswith("## "):
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
        if q <= 55 and not answer:
            problems.append(f"Q{q} 缺少答案字母")
        if not expl_lines:
            warnings.append(f"Q{q} 解析为空(2022 精简版原书个别题目仅给答案)")

        if q >= 56:
            parts = split_essay_parts(expl_lines)
            for idx, (label, part_lines) in enumerate(parts, 1):
                chunks.append({
                    "year": year, "question_no": q,
                    "category": category_of(q),
                    "answer": answer,
                    "part": idx, "parts": len(parts),
                    "part_label": label,
                    "explanation": "\n".join(part_lines).strip(),
                })
        else:
            chunks.append({
                "year": year, "question_no": q,
                "category": category_of(q),
                "answer": answer,
                "part": 1, "parts": 1, "part_label": "",
                "explanation": "\n".join(expl_lines).strip(),
            })
    return chunks, problems, warnings


def main():
    year_dirs = sorted(OUTPUT_ROOT.glob("[0-9][0-9][0-9][0-9]年"))
    if not year_dirs:
        print(f"[✘] {OUTPUT_ROOT} 下没有任何年份目录,拒绝写入汇总库")
        sys.exit(1)
    available = {int(d.name.replace("年", "")) for d in year_dirs}
    only = parse_year_args(available)

    all_chunks, n_problems = [], 0
    for d in year_dirs:
        year = int(d.name.replace("年", ""))
        per_year = d / f"{year}年199真题解析_chunks.jsonl"
        if year in (only or available):
            md_path = d / f"{year}年199管综真题解析.md"
            if not md_path.exists():
                print(f"[✘] {year} 年缺少 {md_path.name},跳过")
                n_problems += 1
                continue
            chunks, problems, warnings = parse_year_md(md_path)
            atomic_write(per_year, "".join(
                json.dumps(c, ensure_ascii=False) + "\n" for c in chunks))
            all_chunks.extend(chunks)
            essay = sum(1 for c in chunks if c["question_no"] >= 56)
            status = "OK " if not problems else "WARN"
            print(f"[{status}] {year}: 55 主切分 + {essay} 条写作子切分"
                  f" -> {per_year.name}")
            for w in warnings:
                print(f"       ! {w}")
            for p in problems:
                print(f"       ✘ {p}")
                n_problems += 1
        else:
            if not per_year.exists():
                print(f"[✘] {year}: 缺 {per_year.name},无法并入汇总库")
                n_problems += 1
                continue
            md_path = d / f"{year}年199管综真题解析.md"
            if md_path.exists() and md_path.stat().st_mtime > per_year.stat().st_mtime:
                print(f"[✘] {year}: {md_path.name} 比 {per_year.name} 新,"
                      f"切分库可能过期,请先重建该年")
                n_problems += 1
                continue
            chunks = [json.loads(l) for l in
                      per_year.read_text(encoding="utf-8").splitlines()
                      if l.strip()]
            all_chunks.extend(chunks)

    # 汇总库必须覆盖题库内全部年份(局部重建不得缩小汇总范围)
    got_years = sorted({c["year"] for c in all_chunks})
    if got_years != sorted(available):
        missing_years = sorted(available - set(got_years))
        print(f"[✘] 汇总库缺少年份: {missing_years}")
        n_problems += 1

    if not n_problems:
        total_path = OUTPUT_ROOT / TOTAL_JSONL_NAME
        text = "".join(json.dumps(c, ensure_ascii=False) + "\n"
                       for c in all_chunks)
        atomic_write(total_path, text)
        mirror = ROOT / TOTAL_JSONL_NAME
        atomic_write(mirror, text)

    print(f"\n共 {len(all_chunks)} 条切分({len(got_years)} 个年份)")
    if not n_problems:
        print(f"汇总库: {total_path}")
        print(f"根目录镜像: {mirror}")
    if n_problems:
        print(f"⚠ 有 {n_problems} 处问题,见上方明细,请人工复核对应题目")
        sys.exit(1)
    print("全部年份 57 题齐整,校验通过")


if __name__ == "__main__":
    main()
