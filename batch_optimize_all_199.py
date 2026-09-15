#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考研管综 199 历年真题全量智能转换与切分系统 (2009 - 2026)
- 支持混合双引擎：矢量原生解析引擎 + 扫描版神经网络 RapidOCR 引擎
- 严格题号锚点：必须为 "题号 + ．/./、" 且其后不接数字，正文行首数字
  （"16 人""30 天""1.5 米"）不会再被误当成题号——旧版 "题号+汉字/逗号"
  等宽松锚点是历史串题的根源。实测 18 年试卷正文均为单栏通栏排版，
  仅 A-E 选项横排成子栏，文本块按 (y, x) 排序即为阅读序
- 跨页多段拼接渲染原卷切片，1 题 1 图
- 输出：与 2009-2021 人工校核版同款的 Markdown 图文对照卷 + 同 schema
  的 JSONL 切分（year/question_no/category/stem/options/image），
  build_rag_chunks_from_md.py 可直接解析新年份 md 重建切分库

⚠ 覆盖保护：2009-2026 各年 md 已逐题人工/多模态校核。本脚本默认跳过
所有已存在 "{year}年199管综真题试卷.md" 的年份（直接载入其 jsonl 进
汇总库），防止 PDF 重抽覆盖校核成果与切片图；确需对旧年份重建请加
--force。切分库的规范重建入口是 build_rag_chunks_from_md.py（以校核
过的 md 为内容源），本脚本只用于全新年份 PDF 的首次转换。
"""

import os
import re
import sys
import glob
import json
import fitz  # PyMuPDF

try:
    from rapidocr_onnxruntime import RapidOCR
except ImportError:  # 矢量版年份不需要 OCR 引擎,缺失时仅扫描版不可用
    RapidOCR = None

OUTPUT_ROOT = "199管综真题_Markdown题库"
# 题号锚点的标点部分:全角 ．/、 不作小数点,直接跟数字也合法(如 "2．16 人…");
# 半角 . 后若紧跟数字则是小数(如 "1.5 米"),必须排除
QANCH = r"\s*(?:\.(?!\d)|[．、])"
ensure_dir = lambda d: os.makedirs(d, exist_ok=True)
ensure_dir(OUTPUT_ROOT)

# 16-25 条件充分性判断的 A-E 判定说明(标准短式,与校核版 md 一致)
LEGEND = {
    "A": "条件（1）充分，但条件（2）不充分",
    "B": "条件（2）充分，但条件（1）不充分",
    "C": "条件（1）和（2）单独都不充分，但条件（1）和条件（2）联合起来充分",
    "D": "条件（1）充分，条件（2）也充分",
    "E": "条件（1）和（2）单独都不充分，条件（1）和条件（2）联合起来也不充分",
}

# 个别年份 OCR/文本层缺陷的人工核对补丁(仅 --force 重建该年时生效;
# 正常流程中已校核年份整体跳过,不会走到补丁)
KNOWN_PATCHES = {
    ("2009", 16): (
        "16. $a_1 + a_2 + a_3 + \\dots + a_n = \\frac{1}{3}(4^n - 1)$。\n(1) 数列 $\\{a_n\\}$ 的通项公式为 $a_n = 2^n$。\n(2) 在数列 $\\{a_n\\}$ 中，对任意正整数 $n$，有 $a_1 + a_2 + a_3 + \\dots + a_n = 2^n - 1$。"
    ),
    ("2010", 14): (
        "14. 如图 2 所示，长方形 ABCD 的两条边分别为 8 米和 6 米，四边形 OEFG 的面积是 4 平方米，则阴影部分的面积为（ ）平方米。\n(A) 32  (B) 28  (C) 24  (D) 20  (E) 16"
    ),
    ("2025", 40): (
        "40．对于上述专家的观点，可以得出以下哪项？\n(A) 乙和丁支持戊。\n(B) 丙和戊支持甲。\n(C) 乙和丁支持戊。\n(D) 乙和丙支持己。\n(E) 戊和己支持乙。"
    ),
    ("2025", 41): (
        "41．根据以上信息，可知“：”中两个相邻图形符号表示的汉字有（ ）。\n(A) 春山\n(B) 梅园\n(C) 梅山\n(D) 花园\n(E) 山花"
    ),
    ("2020", 14): (
        "14. 如图 3 所示，A, B, C, D 两两相连，从一个节点沿线段到另一个节点当作 1 步，若机器人从节点 A 出发，随机走了 3 步，则机器人未到达节点 C 的概率为（ ）。\n(A) 4/9  (B) 11/27  (C) 10/27  (D) 1/3  (E) 8/27"
    ),
    ("2022", 50): (
        "50. 如果丁创作散文，则可以得出以下哪项？\n(A) 周创作小说。\n(B) 李创作诗歌。\n(C) 李创作小说。\n(D) 周创作戏剧。\n(E) 王创作小说。"
    ),
    ("2022", 54): (
        "54. 根据上述信息，可以得出以下哪项？\n(A) 甲有项目入选民用建筑。\n(B) 戊有项目入选工业建筑。\n(C) 乙有项目入选商业建筑。\n(D) 丁有项目入选居住建筑。\n(E) 丙有项目入选农业建筑。"
    ),
}

def preprocess_text(text):
    # 仅修复 OCR 把题号认成拉丁字母的个别情况(如 So.→50.),不得向正文注入
    # "N." 形态的伪题号锚点——旧版曾把行首 "3%" 改写成 "39.",使正文行被
    # 误当第 39 题起点而串题,该 hack 已移除
    text = re.sub(r"(\([A-E]\)[^\n]+?)\s*[sS][oO0]\s*[\.．、\s]?", r"\1\n50. ", text)
    text = re.sub(r"(\n|^)\s*[sS][oO0]\s*[\.．、\s]?", r"\1\n50. ", text)
    text = re.sub(r"(\n|^)\s*[sS]4\s*[\.．、\s]?", r"\1\n54. ", text)
    text = re.sub(r"(\n|^)\s*[lI|]\s*[\.．、\s]", r"\1\n1. ", text)
    text = re.sub(r"(\n|^)\s*([1-5])\x20([0-9])\s*[\.．、]", r"\1\n\2\3. ", text)
    text = re.sub(r"(\n|^)\s*(\d{1,2})\s*([「“])", r"\1\n\2. \3", text)
    return text

def extract_q_smart(text, q):
    # 严格锚点: 行首 "题号 + ．/./、"(半角 . 不得紧跟小数数字)。旧版
    # "题号+汉字/逗号/任意分隔" 宽松锚点会把 "16 人""30 天" 等正文行首
    # 数字误当题号,是串题的根源
    m = re.search(rf"(?:^|\n)\s*{q}{QANCH}", text)
    if not m:
        return ""
    start_pos = m.end()
    # 正文终点取"下一题锚点"与各章标题中最早出现者:二、条件充分性判断
    # 章题夹在第 15 题与第 16 题之间、逻辑/写作章题同理,若不提前截断,
    # 章题会混入末题题干,其 A-E 解题说明还会被误当成该题选项。
    # 章标题用完整短语匹配且不要求前导换行(2024 文本层 "E. 10二、…" 粘连)
    end_pos = len(text)
    for pe in (
        rf"\n\s*{q+1}{QANCH}",
        r"二、条件充分性判断",
        r"[二三四]、逻辑推理",
        r"[二三四]、写作",
    ):
        m = re.search(pe, text[start_pos:])
        if m and m.start() < end_pos - start_pos:
            end_pos = start_pos + m.start()
    return text[start_pos:end_pos].strip()

def split_options(raw, allow_scrambled=False):
    """把 "题干…A．…B．…" 或 "题干…(A) …(B) …" 形态的原始文本拆成
    (题干, 选项字典);A-E 不是恰好五项且顺序完整时按纯题干处理,
    返回 (raw, {}),由调用方按选项缺失告警。

    allow_scrambled 仅对逻辑题开放:双栏选项的文本层读取会把 A-E 顺序打乱
    (如 A B D C E),但纯文字选项内容完好,可按字母标记归位;数学选项的
    公式内容本身会被打散,按字母归位不可靠,一律保持原样。"""
    pats = (
        r"(?:^|\n)\s*([A-E])\s*[\.．、]\s*(.+?)(?=(?:(?:^|\n)\s*[A-E]\s*[\.．、]|\Z))",
        r"[(（]([A-E])[)）]\s*(.+?)(?=(?:(?:^|\n|\s)[(（][A-E][)）]|\Z))",
    )
    for pat in pats:
        ms = list(re.finditer(pat, raw, re.DOTALL))
        if len(ms) == 5 and [m.group(1) for m in ms] == ["A", "B", "C", "D", "E"]:
            opts = {m.group(1): re.sub(r"\s*\n\s*", "", m.group(2)).strip() for m in ms}
            return raw[:ms[0].start()].strip(), opts
    # 内联式:整行挤在一起 "…哪项?A．甲。B 乙。C．丙。D 丁。E.戊。",
    # 字母后可能没有标点。前缀取贪婪,命中最靠右的可行 A,避开题干中
    # 偶发的 A-E 字母;乱序数学选项(如 A 被排到末尾)无法命中,原样返回
    m = re.search(
        r"^(.*A)\s*[\.．、]?\s*(.+?)\s*B\s*[\.．、]?\s*(.+?)\s*C\s*[\.．、]?\s*(.+?)\s*D\s*[\.．、]?\s*(.+?)\s*E\s*[\.．、]?\s*(.+?)\s*$",
        raw, re.DOTALL)
    if m:
        opts = {k: re.sub(r"\s*\n\s*", "", g).strip()
                for k, g in zip("ABCDE", m.groups()[1:])}
        if all(opts.values()):
            return m.group(1)[:-1].strip(), opts
    if allow_scrambled:
        markers = list(re.finditer(r"(?<![A-Za-z])([A-E])\s*[\.．、]\s*", raw))
        letters = [mm.group(1) for mm in markers]
        if len(markers) == 5 and sorted(letters) == list("ABCDE"):
            opts = {}
            for i, mm in enumerate(markers):
                end = markers[i + 1].start() if i + 1 < len(markers) else len(raw)
                opts[mm.group(1)] = re.sub(r"\s*\n\s*", "", raw[mm.end():end]).strip()
            if all(opts.values()):
                return raw[:markers[0].start()].strip(), opts
    return raw, {}

def quote_block(text):
    """把多行文本转成 house 版式引用块(空行用 '>' 占位)。"""
    return "\n".join(("> " + l) if l else ">" for l in text.split("\n"))

def img_line(md_lines, images_dir, year, q):
    """按 house 版式在题目块末尾追加原卷切片引用(仅当切片图实际生成),
    返回相对路径;未生成时不写引用并返回 None,让 build_rag 报缺图告警。"""
    name = f"{year}_q{q:02d}.png"
    if not os.path.exists(os.path.join(images_dir, name)):
        return None
    md_lines.append(f"![{year}年第{q}题原卷切片](images/{name})\n")
    return f"images/{name}"

def crop_and_stitch(doc, spec, out_path, dpi=200):
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    if len(spec) == 1:
        pno, y0, y1 = spec[0]
        page = doc[pno]
        crop = fitz.Rect(15, max(0, y0), page.rect.x1 - 15, min(page.rect.y1, y1))
        if crop.height > 5 and crop.width > 5:
            pix = page.get_pixmap(matrix=mat, clip=crop)
            pix.save(out_path)
    else:
        pno1, y0_1, y1_1 = spec[0]
        pno2, y0_2, y1_2 = spec[1]
        c1 = fitz.Rect(15, max(0, y0_1), doc[pno1].rect.x1 - 15, min(doc[pno1].rect.y1, y1_1))
        c2 = fitz.Rect(15, max(0, y0_2), doc[pno2].rect.x1 - 15, min(doc[pno2].rect.y1, y1_2))
        pix1 = doc[pno1].get_pixmap(matrix=mat, clip=c1)
        pix2 = doc[pno2].get_pixmap(matrix=mat, clip=c2)

        temp_doc = fitz.open()
        h1 = c1.height
        h2 = c2.height
        tot_h = h1 + h2 + 8
        tot_w = doc[pno1].rect.width
        tpage = temp_doc.new_page(width=tot_w, height=tot_h)
        tmp1 = f"{out_path}_t1.png"
        tmp2 = f"{out_path}_t2.png"
        pix1.save(tmp1); pix2.save(tmp2)
        tpage.insert_image(fitz.Rect(0, 0, tot_w, h1), filename=tmp1)
        tpage.insert_image(fitz.Rect(0, h1 + 4, tot_w, tot_h), filename=tmp2)
        spix = tpage.get_pixmap(dpi=dpi)
        spix.save(out_path)
        if os.path.exists(tmp1): os.remove(tmp1)
        if os.path.exists(tmp2): os.remove(tmp2)

def clean_chinese_paragraphs(lines):
    body_parts = []
    curr = ""
    for l in lines:
        l = l.strip()
        if not l: continue
        is_cond = bool(re.match(r"^[\(（]\d+[\)）]|^[①②③④⑤⑥⑦⑧⑨]", l))
        is_prompt = bool(re.match(r"^(?:根据以上|以下哪项|基于以上|若|假设|根据上述|由此可见)", l))
        curr_is_cond = bool(re.match(r"^[\(（]\d+[\)）]|^[①②③④⑤⑥⑦⑧⑨]", curr))

        if is_cond or is_prompt:
            if curr: body_parts.append(curr)
            curr = l
        elif curr_is_cond:
            curr += l
        else:
            curr += l
    if curr: body_parts.append(curr)

    formatted = []
    in_cond = False
    for p in body_parts:
        if bool(re.match(r"^[\(（]\d+[\)）]|^[①②③④⑤⑥⑦⑧⑨]", p)):
            formatted.append(p)
            in_cond = True
        else:
            if in_cond:
                formatted.append("")
                in_cond = False
            formatted.append(p)
            formatted.append("")
    res = "\n".join(formatted).strip()
    return re.sub(r"\n{3,}", "\n\n", res)

def render_math_question(md_lines, all_chunks, images_dir, year, q, full_text):
    """渲染 1-25 题(house 版式):q==16 时先输出 "## 二、条件充分性判断"
    章题与解题说明;1-15 题附 A-E 选项,16-25 题选项统一取 LEGEND。"""
    if q == 16:
        md_lines.append("## 二、条件充分性判断：第 16～25 小题，每小题 3 分，共 30 分。要求判断每题给出的条件（1）和（2）能否充分支持题干所陈述的结论。A、B、C、D、E 五个选项为判断结果，请选择一项符合试题要求的判断，在答题卡上将所选项涂黑。\n")
        md_lines.append("### 解题说明：")
        md_lines.append("\n".join(f"- **{k}**．{LEGEND[k]}" for k in "ABCDE") + "\n")

    if (str(year), q) in KNOWN_PATCHES:
        raw = re.sub(rf"^\s*{q}\s*[\.．、]\s*", "", KNOWN_PATCHES[(str(year), q)])
    else:
        raw = extract_q_smart(full_text, q)

    q_type = "问题求解" if q <= 15 else "条件充分性判断"
    stem_clean, opts = split_options(raw)
    stem_clean = clean_chinese_paragraphs(stem_clean.splitlines())
    if q >= 16:
        opts = dict(LEGEND)

    md_lines.append(f"### 第 {q} 题\n")
    md_lines.append(f"{stem_clean}\n")
    if q <= 15:
        for k in "ABCDE":
            if k in opts:
                md_lines.append(f"- **{k}**．{opts[k]}")

    img_rel = img_line(md_lines, images_dir, year, q)
    all_chunks.append({
        "year": int(year),
        "question_no": q,
        "category": q_type,
        "stem": stem_clean,
        "options": {k: opts[k] for k in "ABCDE" if k in opts},
        "image": img_rel,
    })

def render_logic_questions(md_lines, all_chunks, images_dir, year, logic_text):
    """渲染 26-55 题(house 版式):共享题干独立成 "### X~Y 题基于以下题干"
    块;jsonl 中 stem 按 build_rag 规范拼为 "共享题干\\n\\n本题题干"。"""
    # 共享题干独立成块(先从 logic_text 中移除,再逐题输出)
    shared_dict = {}
    for ms in re.finditer(
            rf"(\d+[\s~～\-－—到至]+\d+\s*题基于以下题干.*?)(?=\n\s*\d{{2}}{QANCH}|\Z)",
            logic_text, re.DOTALL):
        s_raw = ms.group(1).strip()
        logic_text = logic_text.replace(ms.group(1), "")
        s_clean = clean_chinese_paragraphs(s_raw.splitlines())
        m_range = re.search(r"(\d+)[\s~～\-－—到至]+(\d+)", s_clean)
        if m_range:
            start_q, end_q = int(m_range.group(1)), int(m_range.group(2))
            shared_dict[start_q] = (end_q, s_clean)

    for q in range(26, 56):
        shared_text = None
        if q in shared_dict:
            end_q, shared_text = shared_dict[q]
            md_lines.append(f"### {q}~{end_q} 题基于以下题干\n")
            md_lines.append(quote_block(shared_text) + "\n")

        if (str(year), q) in KNOWN_PATCHES:
            raw = re.sub(rf"^\s*{q}\s*[\.．、]\s*", "", KNOWN_PATCHES[(str(year), q)])
        else:
            raw = extract_q_smart(logic_text, q)

        stem_body, opts = split_options(raw, allow_scrambled=True)
        stem_body = clean_chinese_paragraphs(stem_body.splitlines())

        md_lines.append(f"### 第 {q} 题\n")
        md_lines.append(f"{stem_body}\n")
        for k in "ABCDE":
            if k in opts:
                md_lines.append(f"- **{k}**．{opts[k]}")

        img_rel = img_line(md_lines, images_dir, year, q)

        stem = (shared_text + "\n\n" + stem_body) if shared_text else stem_body
        all_chunks.append({
            "year": int(year),
            "question_no": q,
            "category": "逻辑推理",
            "stem": stem,
            "options": {k: opts[k] for k in "ABCDE" if k in opts},
            "image": img_rel,
        })
    return logic_text

def render_writing(md_lines, all_chunks, images_dir, year, writing_text):
    """渲染 56-57 写作题(house 版式):第一段为题目要求(粗体行),其余为材料
    (引用块);文本层没分段时整体进引用块,交由后续人工校核。"""
    m56 = re.search(r"56\s*[\.．、，,](?!\d)(.+?)(?=57\s*[\.．、，,](?!\d)|\Z)", writing_text, re.DOTALL)
    m57 = re.search(r"57\s*[\.．、，,](?!\d)(.+?)\Z", writing_text, re.DOTALL)

    w56_text = clean_chinese_paragraphs(m56.group(1).splitlines()) if m56 else ""
    w57_text = clean_chinese_paragraphs(m57.group(1).splitlines()) if m57 else ""

    def split_body(text):
        parts = text.split("\n\n")
        if len(parts) >= 2 and ("有效性" in parts[0] or "论说文" in parts[0]):
            return parts[0], "\n\n".join(parts[1:])
        return "", text

    req56, mat56 = split_body(w56_text)
    req57, mat57 = split_body(w57_text)

    for q, cat, req, mat in (
        (56, "论证有效性分析", req56, mat56),
        (57, "论说文", req57, mat57),
    ):
        md_lines.append(f"### 第 {q} 题 · {cat} (30 分)\n" if q == 56 else f"### 第 {q} 题 · {cat} (35 分)\n")
        if req:
            md_lines.append(f"**{req}**\n")
        if mat:
            md_lines.append(quote_block(mat) + "\n")
        img_rel = img_line(md_lines, images_dir, year, q)
        all_chunks.append({
            "year": int(year),
            "question_no": q,
            "category": cat,
            "stem": w56_text if q == 56 else w57_text,
            "options": {},
            "image": img_rel,
        })

def crop_question_slices(doc, q_locs, images_dir, year, page_top_skip=65, page_bottom_skip=30):
    """按题号锚点坐标逐题渲染原卷切片(全宽裁切,跨页纵向拼接),1 题 1 图。"""
    for q in range(1, 58):
        out_img = f"{images_dir}/{year}_q{q:02d}.png"
        if q not in q_locs:
            continue
        pno1, y_start, _, _ = q_locs[q]
        if q + 1 in q_locs:
            pno2, next_y, _, _ = q_locs[q + 1]
            if pno1 == pno2:
                y_end = max(y_start + 30, next_y - 6)
                spec = [(pno1, max(0, y_start - 6), y_end)]
            else:
                spec = [(pno1, max(0, y_start - 6), doc[pno1].rect.y1 - page_bottom_skip),
                        (pno2, page_top_skip, max(page_top_skip + 10, next_y - 6))]
        else:
            spec = [(pno1, max(0, y_start - 6), doc[pno1].rect.y1 - page_bottom_skip)]
        crop_and_stitch(doc, spec, out_img)

def slice_logic_writing_text(full_text):
    """从全文中切出 (逻辑题区, 写作题区)。"""
    idx_logic = full_text.find("二、逻辑推理") if "二、逻辑推理" in full_text else full_text.find("三、逻辑推理")
    idx_writing = full_text.find("四、写作") if "四、写作" in full_text else full_text.find("三、写作")
    logic_text = full_text[idx_logic:idx_writing] if (idx_logic != -1 and idx_writing != -1) else full_text[idx_logic:]
    writing_text = full_text[idx_writing:] if idx_writing != -1 else full_text
    return logic_text, writing_text

def process_vector_year(pdf_path, year, out_dir):
    print(f"[*] [矢量引擎] 正在精细解析 {year} 年 199 管综真题...")
    doc = fitz.open(pdf_path)
    images_dir = os.path.join(out_dir, "images")
    ensure_dir(images_dir)

    # 0. 找到正文起始页（跳过考生注意事项/封面）
    start_pno = 0
    for pno in range(min(5, len(doc))):
        t = doc[pno].get_text()
        if "考生注意事项" in t or "答题前" in t:
            if "问题求解" in t or "向题求解" in t:
                start_pno = pno
                break
            continue
        if "问题求解" in t or "向题求解" in t or re.search(r"^\s*1\s*[\.．、\s][一-龥A-Za-z]", t, re.M):
            start_pno = pno
            break

    # 1. 扫描所有题号起始位置与边界（从正文页开始）
    #    正文为单栏通栏排版,题号锚点均在左缘(x0<150);严格 "题号+句点类"
    #    且其后不接数字,避免把 "16 人""1.5 米" 等行首数字误当锚点
    q_locs = {} # qnum -> (pno, y0, y1, text)
    for pno in range(start_pno, len(doc)):
        page = doc[pno]
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (round(b[1], 1), round(b[0], 1)))
        for b in blocks:
            t = b[4].strip()
            if b[0] < 150 and b[1] < 800:
                m = re.match(rf"^(\d{{1,2}}){QANCH}", t)
                if m:
                    qnum = int(m.group(1))
                    if 1 <= qnum <= 57 and qnum not in q_locs:
                        q_locs[qnum] = (pno, b[1], b[3], t)

    # 2. 提取并清洗非页码文本（从正文页开始,按 (y, x) 阅读序）
    page_texts = []
    for pno in range(start_pno, len(doc)):
        blocks = doc[pno].get_text("blocks")
        blocks.sort(key=lambda b: (round(b[1], 1), round(b[0], 1)))
        c_lines = []
        for b in blocks:
            t = b[4].strip()
            if (b[1] > 800 and t.isdigit()) or (b[1] < 65 and t.isdigit()):
                continue
            if t.isdigit() and len(t) <= 2:
                continue
            c_lines.append(t)
        page_texts.append("\n".join(c_lines))

    full_text = "\n" + preprocess_text("\n".join(page_texts))

    # 3. 逐题渲染原卷切片
    crop_question_slices(doc, q_locs, images_dir, year)

    # 4. 分块解析题目内容(house 版式,供 build_rag_chunks_from_md.py 解析)
    all_chunks = []
    md_lines = []
    md_lines.append(f"# {year} 年全国硕士研究生招生考试管理类专业学位联考综合能力试题 (199)\n")
    md_lines.append("## 一、问题求解：第 1-15 小题，每小题 3 分，共 45 分。下列每题给出的 A、B、C、D、E 五个选项中，只有一项是符合试题要求的。请在答题卡上将所选的字母涂黑。\n")

    for q in range(1, 26):
        render_math_question(md_lines, all_chunks, images_dir, year, q, full_text)

    md_lines.append("---\n\n## 三、逻辑推理（第 26-55 题，每小题 2 分，共 60 分）\n")
    logic_text, writing_text = slice_logic_writing_text(full_text)
    render_logic_questions(md_lines, all_chunks, images_dir, year, logic_text)

    md_lines.append("---\n\n## 四、写作（第 56-57 题，共 65 分）\n")
    render_writing(md_lines, all_chunks, images_dir, year, writing_text)

    # 写入 Markdown 与 JSONL
    out_md = os.path.join(out_dir, f"{year}年199管综真题试卷.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    out_jsonl = os.path.join(out_dir, f"{year}年199真题_chunks.jsonl")
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"[✔] {year} 年解析完成！生成 57 题图文对照试卷：{out_md}")
    return all_chunks

def process_scanned_year(pdf_path, year, out_dir):
    print(f"[*] [OCR神经网络引擎] 正在智能识别并切分扫描版 {year} 年 199 管综真题...")
    if RapidOCR is None:
        raise RuntimeError(
            "扫描版年份需要 rapidocr_onnxruntime,请先安装:pip install rapidocr_onnxruntime")
    rapid_ocr = RapidOCR()
    doc = fitz.open(pdf_path)
    images_dir = os.path.join(out_dir, "images")
    ensure_dir(images_dir)

    # 逐页进行 RapidOCR 识别
    ocr_pages = []
    for pno in range(len(doc)):
        pix = doc[pno].get_pixmap(dpi=150)
        res, _ = rapid_ocr(pix.tobytes())
        # res 包含 [ [box, text, score], ... ]
        # 转换为统一的 block 结构: (x0, y0, x1, y1, text)
        page_blocks = []
        if res:
            for item in res:
                box, text, _ = item
                x0 = min(pt[0] for pt in box) * (72 / 150)
                y0 = min(pt[1] for pt in box) * (72 / 150)
                x1 = max(pt[0] for pt in box) * (72 / 150)
                y1 = max(pt[1] for pt in box) * (72 / 150)
                page_blocks.append((x0, y0, x1, y1, text))
        ocr_pages.append(page_blocks)

    # 0. 确定正文起始页（跳过考生须知/封面）
    start_pno = 0
    for pno, blocks in enumerate(ocr_pages):
        txt = " ".join([b[4] for b in blocks])
        if "考生注意事项" in txt or "答题前" in txt:
            if "问题求解" in txt or "向题求解" in txt:
                start_pno = pno
                break
            continue
        if "问题求解" in txt or "向题求解" in txt or any(re.match(rf"^1{QANCH}", b[4].strip()) for b in blocks if b[0] < 150):
            start_pno = pno
            break

    # 定位题号(严格锚点,同矢量引擎)
    q_locs = {}
    for pno in range(start_pno, len(ocr_pages)):
        blocks = ocr_pages[pno]
        for b in blocks:
            x0, y0, x1, y1, t = b
            if x0 < 150 and y0 < 780:
                m = re.match(rf"^(\d{{1,2}}){QANCH}", t)
                if m:
                    qnum = int(m.group(1))
                    if 1 <= qnum <= 57 and qnum not in q_locs:
                        q_locs[qnum] = (pno, y0, y1, t)

    # 渲染切片图
    crop_question_slices(doc, q_locs, images_dir, year, page_top_skip=60, page_bottom_skip=30)

    # 拼接文本（从正文页开始,按 (y, x) 阅读序）
    full_ocr_lines = []
    for pno in range(start_pno, len(ocr_pages)):
        blocks = ocr_pages[pno]
        blocks.sort(key=lambda b: (round(b[1], 1), round(b[0], 1)))
        for b in blocks:
            t = b[4].strip()
            if (b[1] > 800 and t.isdigit()) or (b[1] < 65 and t.isdigit()):
                continue
            if t.isdigit() and len(t) <= 2:
                continue
            full_ocr_lines.append(t)

    full_text = "\n".join(full_ocr_lines)
    logic_text, writing_text = slice_logic_writing_text(full_text)

    all_chunks = []
    md_lines = []
    md_lines.append(f"# {year} 年全国硕士研究生招生考试管理类专业学位联考综合能力试题 (199)\n")
    md_lines.append("## 一、问题求解：第 1-15 小题，每小题 3 分，共 45 分。下列每题给出的 A、B、C、D、E 五个选项中，只有一项是符合试题要求的。请在答题卡上将所选的字母涂黑。\n")

    for q in range(1, 26):
        render_math_question(md_lines, all_chunks, images_dir, year, q, full_text)

    md_lines.append("---\n\n## 三、逻辑推理（第 26-55 题，每小题 2 分，共 60 分）\n")
    render_logic_questions(md_lines, all_chunks, images_dir, year, logic_text)

    md_lines.append("---\n\n## 四、写作（第 56-57 题，共 65 分）\n")
    render_writing(md_lines, all_chunks, images_dir, year, writing_text)

    out_md = os.path.join(out_dir, f"{year}年199管综真题试卷.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    out_jsonl = os.path.join(out_dir, f"{year}年199真题_chunks.jsonl")
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"[✔] 扫描版 {year} 年识别切分完成！{out_md}")
    return all_chunks

def run_all(force=False):
    all_pdfs = sorted(glob.glob("真题部分/*年199管综真题.pdf"))
    print(f"==================================================")
    print(f"找到 {len(all_pdfs)} 套真题试卷，启动全量流水线...")
    print(f"==================================================")

    total_database = []

    for pdf in all_pdfs:
        filename = os.path.basename(pdf)
        year = re.search(r"(\d{4})年", filename).group(1)
        year_out_dir = os.path.join(OUTPUT_ROOT, f"{year}年")

        # 覆盖保护:已有校核版 md 的年份默认跳过(直接载入其 jsonl 进汇总库),
        # 防止 PDF 重抽覆盖人工校核成果与切片图;确需重建请加 --force
        existing_md = os.path.join(year_out_dir, f"{year}年199管综真题试卷.md")
        if os.path.exists(existing_md) and not force:
            existing_jsonl = os.path.join(year_out_dir, f"{year}年199真题_chunks.jsonl")
            if os.path.exists(existing_jsonl):
                with open(existing_jsonl, "r", encoding="utf-8") as f:
                    total_database.extend(json.loads(l) for l in f if l.strip())
                print(f"[SKIP] {year} 年已有校核版 md,直接载入其 jsonl(重建请加 --force)")
            else:
                print(f"[SKIP] {year} 年已有校核版 md 但缺少 jsonl,"
                      f"请运行 python3 build_rag_chunks_from_md.py {year} 生成")
            continue

        ensure_dir(year_out_dir)
        doc = fitz.open(pdf)
        text_count = sum(len(p.get_text()) for p in doc)

        if text_count > 2000:
            chunks = process_vector_year(pdf, year, year_out_dir)
        else:
            chunks = process_scanned_year(pdf, year, year_out_dir)

        if chunks:
            total_database.extend(chunks)

    # 输出全库汇总
    summary_jsonl = os.path.join(OUTPUT_ROOT, "199管综历年真题_全量RAG切分库.jsonl")
    with open(summary_jsonl, "w", encoding="utf-8") as f:
        for c in total_database:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"\n==================================================")
    print(f"全部 {len(all_pdfs)} 套试卷(2009-2025)流水线完毕")
    print(f"📊 汇总库 Chunk 总数:{len(total_database)} 条")
    print(f"📁 汇总检索知识库路径:{summary_jsonl}")
    print(f"⚠ 切分库规范重建入口为 build_rag_chunks_from_md.py(以校核 md 为内容源)")
    print(f"==================================================")

if __name__ == "__main__":
    run_all(force="--force" in sys.argv)
