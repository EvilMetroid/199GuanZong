#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
199 管综真题解析(答案)PDF -> 逐题 Markdown。

答案书共 4 种版式(2009-2021 文都"答案速查+详解"、2022 精简版、
2023/2024/2025 不同排版),本脚本统一处理:
  1. 全量 RapidOCR(150dpi),行框缓存 ocr_cache/{year}_answer_ocr_lines.json;
     各年 PDF 内嵌文本层均为低质 OCR(公式乱码),故不采用。
  2. 页脚页码行剔除("2009年真题-第13页(共30页)"/"— 11 —"/"第 1 页,共 24 页"/裸数字)。
  3. 答案速查区识别(答案速查/【答案快速查询】标记 + "N-M" 字母组),
     解析出 1-55 题答案字母表,与详解逐题字母交叉校验。
  4. 详解逐题切分:题号锚点 "1. (E)" / "1. 【答案】E" / "1. D 【解析】",
     单调递增防误判;56/57 写作题按 "56. 论证有效性分析" 锚点。
  5. 中文断行段落缝合(公式碎片行保持独立),输出统一结构 md。

用法:
    python3 build_answer_md.py            # 2009-2025 全量
    python3 build_answer_md.py 2009 2024  # 指定年份

输出: 199管综答案_Markdown题库/{year}年/{year}年199管综真题解析.md
校验: 每年 57 题锚点缺失 / 答案字母缺失 / 与速查不一致 / 内容过短 均告警,
      有缺失则非 0 退出。公式为 OCR 原文(不做 LaTeX 转换),核对对照原 PDF。
"""

import json
import re
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent
ANSWER_DIR = ROOT / "答案部分"
OUTPUT_ROOT = ROOT / "199管综答案_Markdown题库"
OCR_CACHE = ROOT / "ocr_cache"
DPI = 150

# 题号锚点:"1. (E)" / "1.（E）" / "1. 【答案】E" / "1. D 【解析】"
# 兼容 OCR 变体:行首杂冒号(": 42.(A)")、冒号分隔("42: (A)")、半角括号("28. [答案] A")
Q_START = re.compile(
    r"^\s*[:：]?\s*(\d{1,2})\s*"
    r"(?:[.、．]\s*"
    r"(?:[（(]\s*([A-Ea-e])\s*[)）]"
    r"|[【\[]\s*答案\s*[】\]]\s*([A-Ea-e])"
    r"|([A-Ea-e])\s*【"
    r"|([A-Ea-e])\s*$)"
    r"|[:：]\s*[（(]\s*([A-Ea-e])\s*[)）])")
# 锚点前缀(从行首剥离,剩余为内容)
Q_PREFIX = re.compile(
    r"^\s*[:：]?\s*\d{1,2}\s*"
    r"(?:[.、．]\s*"
    r"(?:[（(][A-Ea-e][)）]\s*"
    r"|[【\[]\s*答案\s*[】\]]\s*[A-Ea-e]\s*"
    r"|[A-Ea-e]\s*(?=【)"
    r"|[A-Ea-e]\s*$)"
    r"|[:：]\s*[（(][A-Ea-e][)）]\s*)")
# 写作题锚点:"56. 论证有效性分析" / "57. 论说文" / "56.【参考范文】" / "57.【真题解析】"
W_START = re.compile(
    r"^\s*(5[67])\s*[.、．]\s*(?:[A-Ea-e]\s*)?(?:[【\[])?(?:论证有效性分析|论说文|写作|参考|真题解析|$)")
# 写作题前缀(剥离后保留同行内容,如 "57.【真题解析】材料主要……")
W_PREFIX = re.compile(
    r"^\s*5[67]\s*[.、．]\s*(?:[A-Ea-e]\s*)?(?:[【\[][^】\]]{0,10}[】\]]|论证有效性分析|论说文|写作)?\s*")
# 速查字母组:"1-5" / "1〜5" / "11～15" / "31～~35"(OCR 双波浪)
RANGE = re.compile(r"(\d{1,2})\s*[-~～—－至到]{1,2}\s*(\d{1,2})")
QUICK_MARK = re.compile(r"速查|快速查询")
# 页脚:含"页"字样/横线包裹的页码 —— 版式特征,任何位置剔除
FOOTER_TEXT = re.compile(
    r"^(20\d\d[^\n]{0,20}页[^\n]{0,14}"
    r"|[—\-－–—]\s*\d{1,3}\s*[—\-－–—]"
    r"|第\s*\d{1,2}\s*页([，,]?\s*共\s*\d{1,2}\s*页)?)$")
# 裸数字页码(2024 版)—— 仅页底区域剔除,防误伤正文
FOOTER_NUM = re.compile(r"^\d{1,3}$")
# 新段落起点(不向上缝合)
ITEM_START = re.compile(
    r"^(【|（\d|[（]\d|①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩|[A-E][.、．:：]"
    r"|[一二三四五六七八九十]+[、.，,]|（全文|\(全文|\d{1,2}\s*[-~～])")
TERMINATORS = "。？！；：…）)」』】"
CJK_RE = re.compile(r"[一-鿿]")


def cjk_ratio(s):
    return sum(1 for c in s if CJK_RE.match(c)) / len(s) if s else 0.0


def ocr_year(doc, year):
    """全页 RapidOCR -> [(pno, y0, x0, text)](pt 坐标),带缓存。"""
    cache = OCR_CACHE / f"{year}_answer_ocr_lines.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    lines = []
    for pno in range(len(doc)):
        pix = doc[pno].get_pixmap(dpi=DPI)
        res, _ = ocr(pix.tobytes())
        for item in (res or []):
            box, text, _ = item
            t = (text or "").strip()
            if not t:
                continue
            lines.append([pno,
                          min(p[1] for p in box) * 72 / DPI,
                          min(p[0] for p in box) * 72 / DPI,
                          t])
    OCR_CACHE.mkdir(exist_ok=True)
    cache.write_text(json.dumps(lines, ensure_ascii=False), encoding="utf-8")
    print(f"       OCR {year}: {len(lines)} 行 -> {cache.name}")
    return lines


def drop_footers(lines, doc):
    """页脚剔除:含"页"字样/横线页码行任何位置剔除;裸数字仅页底 20% 区域剔除。"""
    out = []
    for pno, y0, x0, t in lines:
        t = t.strip()
        h = doc[pno].rect.height
        if FOOTER_TEXT.match(t):
            continue
        if FOOTER_NUM.match(t) and y0 > 0.8 * h:
            continue
        out.append((pno, y0, x0, t))
    return out


def parse_quick(lines):
    """速查字母组 -> {题号: 字母};要求组宽 1-5 且字母数与题数一致。"""
    qmap = {}
    for ln in lines:
        ms = list(RANGE.finditer(ln))
        for i, m in enumerate(ms):
            a, b = int(m.group(1)), int(m.group(2))
            if not (1 <= a <= b <= 55 and b - a <= 4):
                continue
            end = ms[i + 1].start() if i + 1 < len(ms) else len(ln)
            letters = [c.upper() for c in re.findall(r"[A-Ea-e]", ln[m.end():end])]
            if len(letters) == b - a + 1:
                for j, q in enumerate(range(a, b + 1)):
                    qmap[q] = letters[j]
    return qmap


def regroup_rows(rows, y_tol=14):
    """同页同 y 的 OCR 行(表格并排片段)合并为一行文本,组内按 x 排序。"""
    rows = sorted(rows, key=lambda r: (r[0], r[1], r[2]))
    out, i = [], 0
    while i < len(rows):
        pno, y0, _, _ = rows[i]
        members = [rows[i]]
        j = i + 1
        while j < len(rows) and rows[j][0] == pno and abs(rows[j][1] - y0) < y_tol:
            members.append(rows[j])
            j += 1
        out.append(" ".join(m[3] for m in sorted(members, key=lambda r: r[2])))
        i = j
    return out


def split_questions(lines):
    """锚点扫描(单调递增)。返回 ({题号: (letter_or_None, 内容行列表)}, 缺失题号)。"""
    qmap = {}
    cur = None
    last = 0
    missing = []
    for (pno, y0, x0, t) in lines:
        m = Q_START.match(t) or W_START.match(t)
        if m:
            q = int(m.group(1))
            bare = m.re is Q_START and m.group(5) is not None
            if m.re is Q_START and bare and x0 > 72:
                m = None  # 裸字母锚点仅限左栏,防正文 "2. C" 类误判
        if m and 1 <= q <= 57 and q > last:
            if q > last + 1:
                missing.extend(range(last + 1, q))
            letter = None
            if m.re is Q_START:
                letter = next((g for g in m.groups()[1:6] if g), None)
            content = Q_PREFIX.sub("", t).strip() if m.re is Q_START \
                else W_PREFIX.sub("", t).strip()
            qmap.setdefault(q, [letter, []])
            if content:
                qmap[q][1].append((pno, content))
            cur, last = q, q
            continue
        if cur is not None:
            qmap[cur][1].append((pno, t))
    for q in range(1, 58):
        if q not in qmap:
            missing.append(q)
    missing = sorted(set(missing))
    return qmap, missing


def join_lines(rows):
    """行列表 -> 段落列表:中文断行无缝缝合,公式碎片/条目行保持独立。"""
    paras, buf = [], ""
    for (_, s) in rows:
        s = s.strip()
        if not s:
            continue
        # 短【...】标题行(如"【解析】母题94·利润问题")保持独立,不向下缝合
        if buf and not re.search(f"[{TERMINATORS}]$", buf) \
                and not (buf.startswith("【") and len(buf) <= 20) \
                and cjk_ratio(buf) > 0.35 and cjk_ratio(s) > 0.35 \
                and CJK_RE.match(s[0]) and not ITEM_START.match(s):
            buf += s
        else:
            if buf:
                paras.append(buf)
            buf = s
    if buf:
        paras.append(buf)
    return paras


def md_year(year):
    pdf = ANSWER_DIR / f"{year}年199管综真题解析.pdf"
    if not pdf.exists():
        print(f"[✘] {year}: 缺 PDF {pdf.name}")
        return 1
    doc = fitz.open(str(pdf))
    lines = drop_footers(ocr_year(doc, year), doc)
    lines.sort(key=lambda l: (l[0], l[1], l[2]))
    doc.close()

    # --- 速查区:标记行之后、首个题号锚点之前,且含字母组 ---
    quick_lines, quick, body_start = [], None, 0
    mark_idx = None
    for i, (_, _, _, t) in enumerate(lines):
        if QUICK_MARK.search(t) and len(t) <= 12:
            mark_idx = i
            break
    if mark_idx is not None:
        cand_rows = []
        for i in range(mark_idx + 1, len(lines)):
            t = lines[i][3]
            if (Q_START.match(t) or W_START.match(t)
                    or ("详解" in t and len(t) <= 12)):
                break
            cand_rows.append(lines[i])
        cand = regroup_rows(cand_rows)
        qm = parse_quick(cand)
        if len(qm) >= 40:
            quick, quick_lines = qm, cand
            body_start = mark_idx + 1 + len(cand_rows)
    body = lines[body_start:]
    qmap, missing = split_questions(body)

    # --- 字母校验:详解 vs 速查 ---
    no_letter, mismatch = [], []
    for q in range(1, 56):
        if q not in qmap:
            continue
        letter, _ = qmap[q]
        if not letter:
            no_letter.append(q)
        elif quick and q in quick and quick[q] != letter:
            mismatch.append((q, letter, quick[q]))

    # --- 组装 md ---
    sections = [
        ("一、问题求解（第 1~15 题）", range(1, 16)),
        ("二、条件充分性判断（第 16~25 题）", range(16, 26)),
        ("三、逻辑推理（第 26~55 题）", range(26, 56)),
        ("四、写作（第 56~57 题）", range(56, 58)),
    ]
    out = [f"# {year} 年 199 管综真题解析", ""]
    out += ["> 本文件由 RapidOCR 自动提取自《%d 年 199 管综真题解析》PDF," % year,
            "> 公式与个别字符可能存在识别误差,核对请对照原 PDF。", ""]
    if quick_lines:
        out += ["## 答案速查", ""]
        out += [f"- {ln}" for ln in quick_lines if ln.strip()]
        out.append("")
    for title, rng in sections:
        out += [f"## {title}", ""]
        for q in rng:
            if q not in qmap:
                continue
            letter, rows = qmap[q]
            out.append(f"### 第 {q} 题")
            out.append("")
            if letter:
                out += [f"**答案**：{letter}", ""]
            paras = join_lines(rows)
            if not paras:
                out += ["（内容缺失,见原 PDF）", ""]
                continue
            out += paras + [""]

    out_dir = OUTPUT_ROOT / f"{year}年"
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"{year}年199管综真题解析.md"
    md_path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")

    short = [q for q in range(1, 58) if q in qmap
             and sum(len(s) for _, s in qmap[q][1]) < 8]
    issues = bool(missing or no_letter or short)
    tag = "OK  " if not issues else "WARN"
    print(f"[{tag}] {year}: 题 57-{len(missing)}/57"
          f"{'  缺' + str(missing) if missing else ''}"
          f"{'  无字母' + str(no_letter) if no_letter else ''}"
          f"{'  短内容' + str(short) if short else ''}"
          f"{'  速查不符 ' + str(mismatch) if mismatch else ''}"
          f"  速查 {len(quick) if quick else 0}/55 -> {md_path.name}")
    return len(missing)


def main():
    only = [int(x) for x in sys.argv[1:]]
    years = only or list(range(2009, 2026))
    problems = 0
    for year in years:
        problems += md_year(year)
    print(f"\n{'=' * 50}")
    if problems:
        print(f"⚠ 共 {problems} 处题号缺失,见上方明细,请人工复核")
        sys.exit(1)
    print("17 年全部 57 题锚点齐整,答案 Markdown 生成完成")


if __name__ == "__main__":
    main()
