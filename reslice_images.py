#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新切分原卷切片图(只重写 images/,md 仅在共享题干引用块后插入一行图片,
幂等;不改动任何既有 md 文本)。

背景:
  早期切图以"下一题锚点 y0 - 6"为下界、跨页用固定页边距(page_top_skip=
  page_bottom_skip),且锚点检测是块级、无单调性约束。文本层乱码年份
  (2009/2020/2022)大量题号锚点漏检,纯扫描年份(2023/2025)整卷走 OCR,
  导致部分切片图定位不准或少切内容。

本脚本按"行级锚点 + 归属划分"重建全部切片图:
  1. 行级锚点检测(PyMuPDF dict 行;纯扫描年份用 RapidOCR 行框并缓存到
     ocr_cache/)。接受六类行首形态:全角点号、ASCII 点号(小数保护)、
     点号后接数字(2009 "7.32+br+c")、拆位数字"1 5."(2018 Q15)、
     数字贴中文(2020 "8某网店")、孤立数字行(仅当恰为期望下一题号)。
     带中文/数字的行首模式限制 x0<100(左栏题号区),并要求题号在阅读序
     上严格递增——"16 人""1.5 米"等题干内数字不会误判。
  2. 每行归属于其前方最近的锚点实体(题目或共享题干标题),页码行剔除;
     两源合并年份下同一锚点行取 8pt 容差,防重复行归属前一题;章节大
     标题("二、…"及其后解题说明、"四、写作…")不归属任何题。内嵌公式/
     折行片段回收(claim_pre_lines):公式组与题号垂直居中时(如 2024 Q15
     大括号组),上方片段阅读序误归上一题;按"锚点行右侧有尾段 + 片段
     紧贴题号段末端 + 行底贴锚点顶或整行跨越锚点顶"预归属本题,防上一
     题吞整行、本题少切;行尾远处的图形标签不满足,不被误抢。
     题目切图 = 其全部归属行按页取并集上下各留 4pt,N 页纵向拼接;
     内容一行不少,至多略微伸入相邻题的行距。左右裁边留 5pt 防题号贴边。
  3. 共享题干(形如"35~36 题基于以下题干",含 OCR 变体"基千")独立切成
     images/{year}_shared_{a}_{b}.png,并在 md 对应引用块之后插入图片行。
  4. 文本层年份有锚点缺失时,缺项用 OCR 行补齐(缓存 ocr_cache/),
     锚点按"文本层优先、OCR 补缺"合并,归属行取两源并集。
  5. 题号两源皆丢(如整行乱码/图形题)但相邻题都在时,按缺口修复:
     切点为缺口中最后一行判定说明行或前一题 A-E 选项行末尾。
  6. 图形墨迹回收(expand_for_ink):曲线/阴影等绘制墨迹不属任何文本
     行,超出属题行范围时会漏切(2011 图1/图2、2024 (图1)~(图4)、
     2025 集装箱图/圆内四边形等)。逐页 1x 栅格找暗像素带(行 bbox
     ±4pt 内不计;带的 y 范围与 px 按整带计,垫边盖住 95% 的表格
     底线也参与判定,至少一行不被切图覆盖才处理),按"距上方切图
     距离 ≤ 距下方 +10 则归上方,否则归下方、间隙 ≤25pt"扩展最近
     切图;页顶带(无上切图,如 2023 Q7 图跨页到 p2 顶)归前一页
     最后属题;图注行("图1"
     "（图1）")常落在下一题题号行下方,同时归属题与下一题两图;
     被两题边界切开的图(上带归上题、下带归下题,如 2024 Q8 图顶点
     标签被切)在下题侧链式并带扩到整图。
     深色带多轮迭代到不动点(空心图形如菱形靠上段先扩、中下段下一轮
     才够到间隙阈值)。扫描件淡笔画(灰度 200-245)会碎成噪声被滤掉
     (gray_continuation):从每个切图底边向下沿"每行浅灰 ≥2 且暗 ≤3"
     的续行扩展(如 2025 Q19 菱形下半;只被文字行硬停、别的切图不
     挡),末端再吸附紧凑标记(图形顶点/顶点标签),与深色带交替
     迭代到不动点。

用法:
    python3 reslice_images.py            # 2009-2026 全量
    python3 reslice_images.py 2013 2022  # 指定年份

注意:运行后请重跑 build_rag_chunks_from_md.py 校验(图片行会被其忽略,
jsonl schema 不变,预期仍为 1026 条零告警)。
"""

import json
import os
import re
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / "199管综真题_Markdown题库"
OCR_CACHE = ROOT / "ocr_cache"
PDF_DIR = ROOT / "真题部分"
DPI = 200
PAD = 4          # 切图上下留白(pt),宁多勿少
X_MARGIN = 100   # 题号左栏判定上限(pt)

# 行首题号模式:(正则, x0 上限或 None, 是否要求"恰为下一题号")
Q_PATTERNS = [
    (re.compile(r"^(\d{1,2})\s*[．、]"), None, False),  # "45 ．某大学"
    (re.compile(r"^(\d{1,2})\s*\.(?!\d)"), None, False),  # "24 .设曲线"
    (re.compile(r"^(\d{1,2})\s*\.(?=\d)"), X_MARGIN, False),  # "7.32+br+c"
    (re.compile(r"^(\d)\s+(\d)\s*[\.．、](?!\d)"), None, False),  # "1 5. 函数"
    (re.compile(r"^(\d{1,2})(?=[　-鿿])"), X_MARGIN, False),  # "8某网店"
    (re.compile(r"^(\d{1,2})$"), X_MARGIN, True),           # 孤立数字行(需下一行佐证)
]
BARE_NEXT = re.compile(r"^[\.．、]|[　-鿿]")  # 孤立数字行的下一行须以此开头
# 判定说明/选项行:（A）条件… / A. 选项 / (A)25 等(用于题号丢失时的缺口修复)
LEGEND_LINE = re.compile(r"^[（(][A-E][)）].*条件")
OPT_LINE = re.compile(r"^[（(]?[A-E][)）.．、:：\s]")
# 共享题干标题:35~36 题基于以下题干(OCR 常把"于"识成"千")
SHARED_HEAD = re.compile(r"^(\d{2})\s*[~～\-－—到至]\s*(\d{2})\s*题基.以下题干")
# 图注行:"图1" / "图 1" / "（图1）",可带句点/空格
CAPTION_LINE = re.compile(r"^[（(]?\s*图\s*\d{1,2}\s*[．。.\s]*[)）]?$")
# 章节大标题:一、问题求解 / 二、条件充分性判断 / 三、逻辑推理 / 四、写作
SECTION_HEAD = re.compile(r"^[一二三四]\s*[、.．,，]")
SECTION_KW = ("问题求解", "向题求解", "条件充分", "逻辑推理", "写作")
PAGE_NUM = re.compile(r"^\d{1,2}$")
# 页脚行("2009 年真题－第 7 页(共30 页)",2025 "…199管综真题·第 10 页";
# 文本层常把页脚拆成两行,后半形如"1 页(共30 页)")
FOOTER = re.compile(r"年真题|199管综真题|^\d{1,2}\s*页\s*（\s*共")


def get_text_lines(doc):
    """PDF 文本层行级提取:[(pno, y0, y1, x0, text, x1)]。"""
    lines = []
    for pno in range(len(doc)):
        d = doc[pno].get_text("dict")
        for blk in d["blocks"]:
            if blk.get("type") != 0:
                continue
            for ln in blk["lines"]:
                txt = "".join(s["text"] for s in ln["spans"]).strip()
                if txt:
                    b = ln["bbox"]
                    lines.append([pno, b[1], b[3], b[0], txt, b[2]])
    return lines


def est_x1(line):
    """旧版 5 元组缓存行的 x1 估计:按字宽累加(CJK/全角约 10.5pt,
    其余约 5.5pt)。仅用于读取旧缓存,新缓存直接存真实 x1。"""
    x0, text = line[3], line[4]
    return x0 + sum(10.5 if ord(c) > 0x2E80 else 5.5 for c in text)


def get_ocr_lines(doc, year):
    """RapidOCR(150dpi)行框 [pno, y0, y1, x0, text, x1];
    缓存 ocr_cache/{year}_ocr_lines.json。旧 5 元组缓存自动升级
    (x1 用 est_x1 估计,不重跑 OCR)。"""
    cache = OCR_CACHE / f"{year}_ocr_lines.json"
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        if data and len(data[0]) == 6:
            return data
        data = [l + [est_x1(l)] for l in data]
        OCR_CACHE.mkdir(exist_ok=True)
        cache.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return data
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    lines = []
    for pno in range(len(doc)):
        pix = doc[pno].get_pixmap(dpi=150)
        res, _ = ocr(pix.tobytes())
        for item in (res or []):
            box, text, _ = item
            t = (text or "").strip()
            if not t:
                continue
            x0 = min(p[0] for p in box) * 72 / 150
            x1 = max(p[0] for p in box) * 72 / 150
            y0 = min(p[1] for p in box) * 72 / 150
            y1 = max(p[1] for p in box) * 72 / 150
            lines.append([pno, y0, y1, x0, t, x1])
    OCR_CACHE.mkdir(exist_ok=True)
    cache.write_text(json.dumps(lines, ensure_ascii=False), encoding="utf-8")
    print(f"       OCR {year}: {len(lines)} 行 -> {cache.name}")
    return lines


def is_page_number(line):
    pno, y0, y1, x0, t, _x1 = line
    # 只看页面上下边距:正文页页眉/页脚在 y<70 / y>770(842pt 页高)。
    # 不得带 x0 条件——页中部的纯数字行可能是绘制墨迹(2011 Q18 梯形
    # 腿 '1' 碎片 y646 x431),误判为页码会从归属行中消失,导致题图
    # 少切公式/图形上沿。题号锚点不受影响:裸数字模式本就要求 x0≤100。
    return bool(PAGE_NUM.match(t)) and len(t) <= 2 and (
        y0 > 770 or y0 < 70)


def find_body_start(lines):
    """正文起始页:首个含"问题求解"(OCR 变体"向题求解")的页。"""
    by_page = {}
    for l in lines:
        by_page.setdefault(l[0], []).append(l[4])
    for pno in sorted(by_page):
        if "问题求解" in " ".join(by_page[pno]) or "向题求解" in " ".join(by_page[pno]):
            return pno
    return 0


def scan_entities(lines, start_pno):
    """阅读序扫描题号锚点与共享题干标题。
    返回 (q_anchor {q: line}, shared [(a, b, line)], last_q)。"""
    ordered = sorted(lines, key=lambda l: (l[0], l[1], l[3]))
    q_anchor, shared = {}, []
    last_q = 0
    for i, line in enumerate(ordered):
        pno, y0, y1, x0, t, _x1 = line
        if pno < start_pno or is_page_number(line):
            continue
        t = t.strip()
        ms = SHARED_HEAD.match(t)
        if ms:
            a, b = int(ms.group(1)), int(ms.group(2))
            if a > last_q and b > a and b <= 57:
                shared.append((a, b, line))
            continue
        for pat, xmax, need_seq in Q_PATTERNS:
            m = pat.match(t)
            if not m:
                continue
            q = int(m.group(1) + m.group(2)) if m.lastindex == 2 else int(m.group(1))
            ok = (1 <= q <= 57 and q not in q_anchor
                  and (q == last_q + 1 if need_seq else q > last_q)
                  and (xmax is None or x0 <= xmax))
            if ok and need_seq:
                # 孤立数字行还需下一行(同页、行距<40pt)以点号或中文开头,
                # 防表格行号/公式数字误判
                ok = False
                for nxt in ordered[i + 1:]:
                    if nxt[0] != pno:
                        break
                    if is_page_number(nxt) or not nxt[4].strip():
                        continue
                    if nxt[1] - y1 < 40 and BARE_NEXT.match(nxt[4].strip()):
                        ok = True
                    break
            if ok:
                q_anchor[q] = line
                last_q = q
            break
    return q_anchor, shared, last_q


def is_section_head(line):
    pno, y0, y1, x0, t, _x1 = line
    t = t.strip()
    return x0 <= X_MARGIN and bool(SECTION_HEAD.match(t)) \
        and any(k in t for k in SECTION_KW)


def claim_pre_lines(lines, anchor_map):
    """公式行回收:公式内嵌于题干时,文本层把该视觉行拆成"题号段 +
    公式片段 + 尾段"(如 2024 Q15 "15．设非负实数x、y 满足 {2≤xy≤8;
    x/2≤y≤2x} ,则x+2y 的最大值为";Q4 的分式同理)。较高的公式,上
    方片段位于题号段上方,阅读序误归上一题:上一题切图吞掉整行,本题
    切图反而丢公式顶行。预归属条件(同页,排除锚点/页码/页脚行):
      ① 锚点行右侧同视觉行(|Δy0|≤8、x0>ax0+40)存在尾段——题号段后
         有内容,说明该行有内嵌公式或折行;
      ② 候选行 x0 ∈ [ax1−8, min(tx0, ax1+60))——紧贴题号段末端,
         排除行尾远处的图形标签(2011 Q19 梯形下底旁 'x+10');
      ③ 与锚点行垂直带 [ay0−16, ay1+16] 相交;
      ④ 且其一:(a) 行底贴锚点行顶(ay0−ly1 ∈ [−2, 5]),公式上行;
         (b) 行跨越锚点行顶(ly0−ay0 ≤ −7 且 ay0−ly1 ≤ −7),图形题
         竖笔等高片段(2011 Q18 梯形右侧边)。贴题号行高度的图形孤片
         (2011 Q19 旁 'l.':顶距 −3.5、底距 −8.2)两者皆不满足,仍归
         前一题(其一题切图带已覆盖,无损)。
    返回 {行坐标: 实体键}。"""
    by_page = {}
    for l in lines:
        if l[4].strip():
            by_page.setdefault(l[0], []).append(l)
    anchor_pts = {(p, y0, x0) for (p, y0, _y1, x0, _t, _x1) in anchor_map}
    claimed = {}
    for (pno, ay0, ay1, ax0, _at, ax1), key in anchor_map.items():
        page = by_page.get(pno, [])
        trails = [l[3] for l in page
                  if (l[0], l[1], l[3]) not in anchor_pts
                  and abs(l[1] - ay0) <= 8 and l[3] > ax0 + 40]
        if not trails:
            continue
        hi_x = min(max(trails), ax1 + 60)
        for l in page:
            lpno, ly0, ly1, lx0, lt, _lx1 = l
            if (lpno, ly0, lx0) in anchor_pts:
                continue
            if is_page_number(l) \
               or (len(lt.strip()) < 40 and FOOTER.search(lt.strip())):
                continue
            if not (ax1 - 8 <= lx0 < hi_x):
                continue
            if ly0 > ay1 + 16 or ly1 < ay0 - 16:
                continue
            gap = ay0 - ly1   # 底距:行底到锚点顶(>0 在上方)
            top = ly0 - ay0   # 顶距:行顶到锚点顶(<0 在上方)
            if not ((-2 <= gap <= 5) or (top <= -7 and gap <= -7)):
                continue
            claimed[(lpno, ly0, lx0)] = key
    return claimed


def assign_lines(lines, q_anchor, shared, start_pno):
    """把每行归属到前方最近的锚点实体。返回 {("q", q) | ("s", (a, b)): [(pno, y0, y1)]}。
    首个锚点之前的行(封面/说明)丢弃;页码行丢弃;实体在遇到空页后终止
    (防止 Q57 吞入试卷后的杂页)。

    两源(文本层+OCR)年份下同一锚点行存在两份近似坐标的行,用 8pt 容差
    把两份都判为锚点行,否则另一份会归属前一题,使其图多切一行
    (如 Q56 图切到"57. 论说文"行)。
    章节大标题("二、条件充分性判断…"及其后解题说明、"四、写作…")不归属
    任何题,跳到下一锚点为止,避免 Q15/Q25/Q55 图吞入章节说明。"""
    events = {}
    anchor_map = {}
    for q, ln in q_anchor.items():
        events[(ln[0], ln[1], ln[3])] = ("q", q)
        anchor_map[(ln[0], ln[1], ln[2], ln[3], ln[4], ln[5])] = ("q", q)
    for a, b, ln in shared:
        events[(ln[0], ln[1], ln[3])] = ("s", (a, b))
        anchor_map[(ln[0], ln[1], ln[2], ln[3], ln[4], ln[5])] = ("s", (a, b))
    events.update(claim_pre_lines(lines, anchor_map))
    ev_list = [(pno, y0, x0, key) for (pno, y0, x0), key in events.items()]
    owner = {}
    cur = None
    prev = None
    skipping = False
    for line in sorted(lines, key=lambda l: (l[0], l[1], l[3])):
        pno, y0, y1, x0, t, _x1 = line
        if pno < start_pno or is_page_number(line) \
           or (len(t) < 40 and FOOTER.search(t)):
            continue
        key = events.get((pno, y0, x0))
        if key is None:
            best, bestd = None, 9.0
            for epno, ey0, ex0, ekey in ev_list:
                if epno == pno:
                    d = max(abs(ey0 - y0), abs(ex0 - x0))
                    if d < bestd:
                        best, bestd = ekey, d
            key = best
        if key is not None:
            if key != cur:
                prev = cur
            cur, skipping = key, False
            owner.setdefault(cur, []).append((pno, y0, y1))
            continue
        # 图注行("图1"/"（图1）"):图常画在属题下方,图注落在下一题题号
        # 行之下时,阅读序把它吞给下一题,属题图便丢了图注(2011 图1/
        # 图2、2019 图2~图5、2020 图1~图3)。同时归 cur 与 prev:prev 须
        # 在图注同页(末段 80pt 内)或前一页(末行须低于 y500,跨页流
        # 续,如 2019 图5)。跳过模式中的图注(2013 图2 落在"二、"说明
        # 区)也按此归属,不再随说明丢弃。
        if cur is not None and len(t) <= 8 and CAPTION_LINE.match(t):
            owner.setdefault(cur, []).append((pno, y0, y1))
            if prev is not None and prev != cur:
                psegs = owner.get(prev, [])
                pm = max(s[0] for s in psegs)
                if pno <= pm + 1:
                    pym = max(yy1 for (pp, _a, yy1) in psegs if pp == pm)
                    if (pno == pm and y1 - pym <= 80) or (
                            pno == pm + 1 and pym >= 500):
                        owner.setdefault(prev, []).append((pno, y0, y1))
            continue
        if skipping:
            continue
        if is_section_head(line):
            skipping = True
            continue
        if cur is None:
            continue
        owner.setdefault(cur, []).append((pno, y0, y1))
    # 空页截断
    for key, segs in owner.items():
        pages = [s[0] for s in segs]
        first = min(pages)
        keep, p = [], first
        for s in segs:
            while p < s[0]:
                if p not in set(pages):
                    break
                p += 1
            if p > s[0]:
                break
            keep.append(s)
        owner[key] = keep
    return owner


def rescue_missing(q_anchor, lines):
    """题号修复:题号在文本层与 OCR 中均丢失、但相邻题 q-1 与 q+1 锚点
    都在时,从两锚点之间的缺口切出本题起始行。切点取:
      a) 缺口中最后一行"判定说明行"(（E）条件(1)和(2)…——"二、"节标题
         后首个题的题号最常丢);否则
      b) 缺口开头连续 A-E 选项行的末尾(前一题的选项)。
    返回 [(q, 恢复的行)]。"""
    rescued = []
    for q in [q for q in range(1, 58) if q not in q_anchor]:
        prev, nxt = q_anchor.get(q - 1), q_anchor.get(q + 1)
        if not prev or not nxt:
            continue
        lo, hi = (prev[0], prev[1]), (nxt[0], nxt[1])
        gap = [l for l in lines
               if lo < (l[0], l[1]) <= hi and not is_page_number(l)]
        cut = None
        for i, l in enumerate(gap):
            if LEGEND_LINE.match(l[4].strip()):
                cut = i
        if cut is None:
            run = 0
            for i, l in enumerate(gap):
                if OPT_LINE.match(l[4].strip()):
                    run = i + 1
                else:
                    break
            if 0 < run < len(gap):
                cut = run - 1
        if cut is None or cut + 1 >= len(gap):
            continue
        cand = gap[cut + 1]
        if SHARED_HEAD.match(cand[4].strip()):
            continue  # 与共享题干标题撞位,不冒险
        rescued.append((q, cand))
    return rescued


def stitch_and_save(doc, segments, out_path):
    """segments: [(pno, y0, y1)] 按页序;单页直接裁,N 页纵向拼接(4pt 缝)。"""
    mat = fitz.Matrix(DPI / 72, DPI / 72)
    if len(segments) == 1:
        pno, y0, y1 = segments[0]
        page = doc[pno]
        rect = fitz.Rect(5, max(0, y0), page.rect.x1 - 5, min(page.rect.y1, y1))
        if rect.height > 5 and rect.width > 5:
            page.get_pixmap(matrix=mat, clip=rect).save(out_path)
        return
    pieces, heights, tmps = [], [], []
    for pno, y0, y1 in segments:
        page = doc[pno]
        rect = fitz.Rect(5, max(0, y0), page.rect.x1 - 5, min(page.rect.y1, y1))
        pieces.append(page.get_pixmap(matrix=mat, clip=rect))
        heights.append(rect.height)
    tot_w = doc[segments[0][0]].rect.width
    tot_h = sum(heights) + 4 * (len(segments) - 1)
    tmp = fitz.open()
    page = tmp.new_page(width=tot_w, height=tot_h)
    y = 0
    for i, piece in enumerate(pieces):
        tmp_img = f"{out_path}_seg{i}.png"
        piece.save(tmp_img)
        tmps.append(tmp_img)
        page.insert_image(fitz.Rect(0, y, tot_w, y + heights[i]), filename=tmp_img)
        y += heights[i] + 4
    page.get_pixmap(dpi=DPI).save(out_path)
    tmp.close()
    for f in tmps:
        if os.path.exists(f):
            os.remove(f)


def segments_for(segs):
    """行坐标列表 -> 按页 (pno, min_y0 - PAD, max_y1 + PAD) 段列表。"""
    per = {}
    for pno, y0, y1 in segs:
        lo, hi = per.get(pno, (y0, y1))
        per[pno] = (min(lo, y0), max(hi, y1))
    return [(pno, lo - PAD, hi + PAD) for pno, (lo, hi) in sorted(per.items())]


MD_SHARED_HEAD = re.compile(
    r"^###\s*(\d+)\s*[~～\-－—到至]\s*(\d+)\s*题基于以下题干")

# 图形墨迹回收参数
INK_DARK = 200     # 灰度阈值(0-255,< 判为墨迹)
INK_MIN_PX = 10    # 暗像素总数下限,杀浅淡扫描斑(2023 p16 等)
INK_MIN_H = 1.5    # 带高下限(pt),杀 0.5pt 扫描发丝线(2025 p11)
INK_MAX_GAP = 25   # 带与最近切图的间隙上限(pt)
INK_X_EDGE = 568   # x0 超过此值的带是右页边扫描记号(2013-2015 多见)
INK_Y_FOOT = 765   # y0 超过此值在页脚区(页脚行本就不进带)
INK_CROSS_Y = 500  # 页顶带归前一页末题:其末行须低于该 y(流页要求)
INK_TOP_NEAR = 60  # 页顶带须距本页首个切图不超过该值
INK_SPLIT_GAP = 10 # 跨界拆分图形:同图相邻墨迹带的垂直间隙上限(pt)

# 浅灰笔画续行参数(灰度 200-245 的淡笔画,如 2025 Q19 菱形下半)
INK_GRAY_HI = 245   # 浅灰上限(> 视为纸面)
INK_GRAY_MIN = 2    # 续行每行浅灰像素下限
INK_DARK_CAP = 3    # 续行每行暗像素上限(再多即文字行,停止续行)
INK_CONT_START = 8  # 首续行须距切图底边不超过该值(pt)
INK_CONT_GAP = 2    # 续行允许的空行间隔
INK_CONT_LEN = 60   # 单次续行长度上限(pt),防噪声链
# 续行末端吸附(紧凑标记:菱形底顶点、顶点标签 B,非续行也非文字行)
INK_ABS_GAP = 6     # 标记带顶须距上一末端不超过该值(pt)
INK_ABS_H = 12      # 单标记带高度上限(pt),更高即文字行
INK_ABS_PX = 150    # 单标记带墨迹像素上限,更多即文字行


def page_ink_rows(doc, pno, lines):
    """1x 栅格(1px=1pt)扫描单页:每行暗像素 x 列表,行 bbox(±4pt,
    同行多段均算)内的已排除。行 bbox 含页码/页脚行(它们只是不进
    归属,墨迹仍属"已覆盖")。切图覆盖不在此排除——成带时只作"种子"
    条件。返回 (rows {y: [x...]}, w, h),多轮迭代复用同一结果。"""
    page = doc[pno]
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1),
                          colorspace=fitz.csGRAY)
    w, h = pix.width, pix.height
    samples = pix.samples
    line_rows = [[] for _ in range(h)]
    for l in lines:
        if l[0] != pno or not l[4].strip():
            continue
        ly0, ly1 = max(0, int(l[1]) - 4), min(h - 1, int(l[2]) + 4)
        lx0, lx1 = max(0, int(l[3]) - 4), min(w - 1, int(l[5]) + 4)
        for y in range(ly0, ly1 + 1):
            line_rows[y].append((lx0, lx1))
    rows = {}
    for y in range(h):
        xs = [x for x, v in enumerate(samples[y * w:(y + 1) * w])
              if v < INK_DARK]
        if not xs:
            continue
        ivs = line_rows[y]
        if ivs:
            xs = [x for x in xs
                  if not any(a <= x <= b for a, b in ivs)]
        if xs:
            rows[y] = xs
    return rows, w, h


def ink_bands_on_page(rows, w, h, page_crops):
    """把逐行暗像素聚成墨迹带 [(by0, by1, bx0, bx1, px)]:相邻暗行(行距
    ≤2pt 连带)成带,y 范围与 px 按整带计——被切图垫边盖住大部分的
    带(如 2023 Q57 答案表底线)也能以整带参与阈值判定。只返回至少
    有一行不被任何切图覆盖(整行宽)的带(有"种子"),被切图并集
    完全盖住的带不重复处理;跨切图边沿的带走"相交"分支,切图扩
    到含整带,底线不会被垫边切断。"""
    crop_row = bytearray(h)
    for lo, hi in page_crops.values():
        lo, hi = max(0, int(lo)), min(h - 1, int(hi))
        if lo <= hi:
            crop_row[lo:hi + 1] = b"\x01" * (hi - lo + 1)
    bands = []
    for y in sorted(rows):
        xs = rows[y]
        if bands and y - bands[-1][1] <= 2:
            b = bands[-1]
            bands[-1] = (b[0], y, min(b[2], xs[0]), max(b[3], xs[-1]),
                         b[4] + len(xs), b[5] or not crop_row[y])
        else:
            bands.append((y, y, xs[0], xs[-1], len(xs), not crop_row[y]))
    return [(y0, y1, x0, x1, c)
            for (y0, y1, x0, x1, c, seeded) in bands if seeded]


def expand_for_ink(doc, lines, owner, start_pno):
    """图形墨迹回收(归属后处理,就地扩展 owner):
      - 逐页(仅有切图的页)找 ink_bands_on_page;
      - 过滤:px<INK_MIN_PX、带高≤INK_MIN_H、bx0>INK_X_EDGE、
        by0>INK_Y_FOOT;
      - 带与切图相交 → 相交的切图都扩到含整带;
      - 否则最近切图:距上切图 ≤ 距下切图 + 10 归上方(图在文字下,
        属上方题),否则归下方(公式在题号上,属下方题);间隙须
        ≤INK_MAX_GAP;
      - 跨界拆分图形(归下方的带上方 INK_SPLIT_GAP 内有 x 交叠的另一
        带,同一图被两题边界切开)→ 下题向上链式并带扩到整图,上题
        保留过切;
      - 页顶带(本页无上切图、距首切图 ≤INK_TOP_NEAR、且前一页
        末行低于 INK_CROSS_Y)→ 归前一页最后属题(2023 Q7 图跨页);
      - 扩展 = 向该实体归属行追加 (pno, by0−2, by1+2),segments_for
        按页 min/max 自然并入,跨页自动拼接。
    多轮迭代到不动点:空心图形(如 2025 Q19 菱形,中部留白把墨迹带
    拆成几段)靠上方带先扩切图、下一轮中部带的间隙才缩到阈值内,
    单轮会漏切。每轮扩展都增大切图覆盖,被收掉的带下轮不再检出,
    必然收敛。
    返回扩展动作列表 [(pno, by0, by1, entity, 方式)](供日志/诊断)。"""
    actions = []

    def extend(key, pno, by0, by1, how):
        owner.setdefault(key, []).append((pno, by0 - 2, by1 + 2))
        actions.append((pno, by0, by1, key, how))

    rows_cache = {}

    def get_rows(pno):
        if pno not in rows_cache:
            rows_cache[pno] = page_ink_rows(doc, pno, lines)
        return rows_cache[pno]

    for _round in range(6):
        page_crops_all = {}
        for key, segs in owner.items():
            per = {}
            for pno, y0, y1 in segs:
                lo, hi = per.get(pno, (y0, y1))
                per[pno] = (min(lo, y0), max(hi, y1))
            for pno, (lo, hi) in per.items():
                page_crops_all.setdefault(pno, {})[key] = (lo - PAD, hi + PAD)
        before = len(actions)
        for pno, page_crops in sorted(page_crops_all.items()):
            if pno < start_pno:
                continue
            rows, w, h = get_rows(pno)
            bands = [b for b in ink_bands_on_page(rows, w, h, page_crops)
                     if b[4] >= INK_MIN_PX and (b[1] - b[0]) >= INK_MIN_H
                     and b[2] <= INK_X_EDGE and b[0] <= INK_Y_FOOT]
            for (by0, by1, bx0, bx1, px) in bands:
                up, dn, ov = [], [], []
                for k, (lo, hi) in page_crops.items():
                    if hi < by0:
                        up.append(k)
                    elif lo > by1:
                        dn.append(k)
                    else:
                        ov.append(k)
                if ov:
                    for k in ov:
                        lo, hi = page_crops[k]
                        # 切图没盖住整带才扩:带比切图大(含带完全包住
                        # 切图,如 2023 答案速查表整表成带而切图在带内)
                        # 或两端任一突出;带完全在切图内则不动。
                        if lo > by0 or hi < by1:
                            extend(k, pno, by0, by1, "相交")
                    continue
                up_key = max(up, key=lambda k: page_crops[k][1]) if up else None
                dn_key = min(dn, key=lambda k: page_crops[k][0]) if dn else None
                gap_up = by0 - page_crops[up_key][1] if up_key else None
                gap_dn = page_crops[dn_key][0] - by1 if dn_key else None
                if up_key is not None or dn_key is not None:
                    if up_key is not None and (dn_key is None
                                               or gap_up <= gap_dn + 10):
                        tkey, tgap = up_key, gap_up
                    else:
                        tkey, tgap = dn_key, gap_dn
                    if tgap <= INK_MAX_GAP:
                        extend(tkey, pno, by0, by1,
                               "距%s%.1f" % ("上" if tkey is up_key else "下",
                                            tgap))
                        if tkey is dn_key:
                            # 跨界拆分图形:本带归下题,而上方 INK_SPLIT_GAP
                            # 内 x 有交叠的另一墨迹带(常归了上题)实为同一
                            # 图——下题切图顶边落在图中部(如 2024 Q8 图,
                            # 顶点标签 B 被切掉)。向上链式并带,把下题扩到
                            # 整图;上题保留过切,允许。
                            lo_dn = page_crops[dn_key][0]
                            chain_lo = by0
                            for _ in range(3):
                                best = None
                                for (u0, u1, ux0, ux1, _upx) in bands:
                                    if (u1 < chain_lo
                                            and chain_lo - u1 <= INK_SPLIT_GAP
                                            and ux0 <= bx1 + 6
                                            and ux1 >= bx0 - 6
                                            and lo_dn > u1):
                                        if best is None or u1 > best[1]:
                                            best = (u0, u1)
                                if best is None:
                                    break
                                chain_lo = best[0]
                            if chain_lo < by0:
                                extend(tkey, pno, chain_lo, by1, "跨界整图")
                        continue
                # 页顶带:本页无上切图(最近切图间隙超限时也走这里,
                # 如 2023 Q7 图在 p2 顶、距 Q8 切图 33pt)
                if up_key is None and pno > start_pno:
                    first_top = min(lo for lo, _ in page_crops.values())
                    prev_pages = page_crops_all.get(pno - 1, {})
                    if prev_pages and first_top <= by1 + INK_TOP_NEAR:
                        last = max(prev_pages.items(),
                                   key=lambda kv: kv[1][1])
                        if last[1][1] >= INK_CROSS_Y:
                            extend(last[0], pno, by0, by1, "页顶跨页")
        if len(actions) == before:
            break
    return actions


def gray_continuation(doc, lines, owner, start_pno):
    """浅灰笔画续行(墨迹回收的第二通道,就地扩展 owner):
    深色带检测只认灰度 <INK_DARK 的像素,扫描件里的淡笔画(200-245,
    每行仅零星暗点)会碎成 px<INK_MIN_PX 的碎带被当噪声滤掉——如
    2025 Q19 菱形下半的两条斜边。本通道不找"带",而是从每个切图
    底边向下沿淡笔画续行:行须浅灰像素 ≥INK_GRAY_MIN 且暗像素
    ≤INK_DARK_CAP(再多就是文字行),空行间隔 ≤INK_CONT_GAP,首行
    距底边 ≤INK_CONT_START,单次 ≤INK_CONT_LEN。续行走只被文字行
    (行 bbox ±4pt)硬停,别的切图覆盖不停——下题切图的 4pt 垫边若
    也挡,图形底段(如菱形斜边收尾 531-536)会被截在半空。续行末端
    再链式吸附紧凑标记:暗像素超续行上限、却不是文字行的下方小墨块
    (如菱形底顶点、顶点标签 B),单段高 ≤INK_ABS_H 且墨迹
    ≤INK_ABS_PX 才收,遇文字行即止。
    与 expand_for_ink 交替迭代到不动点。
    返回扩展动作列表 [(pno, by0, by1, entity, 方式)]。"""
    page_crops_all = {}
    for key, segs in owner.items():
        per = {}
        for pno, y0, y1 in segs:
            lo, hi = per.get(pno, (y0, y1))
            per[pno] = (min(lo, y0), max(hi, y1))
        for pno, (lo, hi) in per.items():
            page_crops_all.setdefault(pno, {})[key] = (lo - PAD, hi + PAD)
    actions = []
    for pno, page_crops in sorted(page_crops_all.items()):
        if pno < start_pno:
            continue
        page = doc[pno]
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1),
                              colorspace=fitz.csGRAY)
        w, h = pix.width, pix.height
        samples = pix.samples
        # 只有文字行(行 bbox ±4pt)硬停续行;别的切图(含其 4pt 垫边)
        # 不停——图形底顶点先被下题收走时,其切图垫边会挡住续行走,
        # 让图形底段少切。
        covered = bytearray(h)
        for l in lines:
            if l[0] != pno or not l[4].strip():
                continue
            ly0, ly1 = max(0, int(l[1]) - 4), min(h - 1, int(l[2]) + 4)
            if ly0 <= ly1:
                covered[ly0:ly1 + 1] = b"\x01" * (ly1 - ly0 + 1)

        def row_stats(y):
            """(暗像素数, 浅灰像素数, 浅灰 x 左界)。暗超上限早停。"""
            row = samples[y * w:(y + 1) * w]
            dark = gray = 0
            gx0 = w
            for x, v in enumerate(row):
                if v < INK_DARK:
                    dark += 1
                    if dark > INK_DARK_CAP:
                        return dark, 0, w
                elif v < INK_GRAY_HI:
                    gray += 1
                    if gx0 == w:
                        gx0 = x
            return dark, gray, gx0

        for key, (lo, hi) in sorted(page_crops.items(),
                                    key=lambda kv: -kv[1][1]):
            hi_i = int(hi)
            if hi_i >= h - 2:
                continue
            y = hi_i + 1
            first = None
            while y <= min(hi_i + INK_CONT_START, h - 1):
                if covered[y]:
                    break
                dark, gray, _g = row_stats(y)
                if gray >= INK_GRAY_MIN and dark <= INK_DARK_CAP:
                    first = y
                    break
                y += 1
            if first is None:
                continue
            end, gap, y, total, gx_min = first, 0, first + 1, 0, w
            while y <= min(hi_i + INK_CONT_LEN, h - 1):
                if covered[y]:
                    break
                dark, gray, gx0 = row_stats(y)
                if gray >= INK_GRAY_MIN and dark <= INK_DARK_CAP:
                    end, gap, total = y, 0, total + gray
                    if gx0 < gx_min:
                        gx_min = gx0
                elif gray == 0:
                    gap += 1
                    if gap > INK_CONT_GAP:
                        break
                y += 1
            # 末端吸附:紧凑标记(菱形底顶点、顶点标签 B)暗像素超续行
            # 上限不被续,也不是文字行;在末端下方 INK_ABS_GAP 内找
            # "高 ≤INK_ABS_H 且墨迹 ≤INK_ABS_PX"的紧凑带并入,链式最多
            # 3 段,遇文字行即止。
            for _abs in range(3):
                b0 = None
                yy = end + 1
                while yy <= min(end + INK_ABS_GAP, h - 1):
                    if covered[yy]:
                        yy = h + 1
                        break
                    d, g, _gx = row_stats(yy)
                    if d > 0 or g >= 1:
                        b0 = yy
                        break
                    yy += 1
                if b0 is None:
                    break
                b1, px, yy = b0, 0, b0
                while yy <= min(b0 + INK_ABS_H, h - 1):
                    if covered[yy]:
                        break
                    d, g, _gx = row_stats(yy)
                    if d > 0 or g >= 1:
                        b1, px = yy, px + d + g
                    else:
                        break
                    yy += 1
                if px > INK_ABS_PX or b1 > INK_Y_FOOT:
                    break
                end = b1
            if end - first < 2 or total < 12 or gx_min > INK_X_EDGE:
                continue
            owner.setdefault(key, []).append((pno, hi - 1, end + 2))
            actions.append((pno, first, end, key, "浅灰续行"))
    return actions


def insert_shared_image_lines(md_path, year, shared_groups):
    """在每个共享题干引用块之后插入图片行(幂等)。返回 (插入数, 缺失标题)。"""
    lines = md_path.read_text(encoding="utf-8").split("\n")
    inserted, missing = 0, []
    for a, b in shared_groups:
        idx = None
        for j, l in enumerate(lines):
            m = MD_SHARED_HEAD.match(l.strip())
            if m and (int(m.group(1)), int(m.group(2))) == (a, b):
                idx = j
                break
        if idx is None:
            missing.append((a, b))
            continue
        j, in_quote, last_content = idx + 1, False, idx
        while j < len(lines):
            s = lines[j].strip()
            if s.startswith(">"):
                in_quote = True
                last_content = j
                j += 1
            elif s == "" and in_quote:
                break
            elif s == "":
                j += 1
            else:
                break
        rel = f"images/{year}_shared_{a}_{b}.png"
        img_line = f"![{year}年{a}~{b}题共享题干原卷切片]({rel})"
        k = last_content + 1
        while k < len(lines) and lines[k].strip() == "":
            k += 1
        if k < len(lines) and lines[k].strip() == img_line:
            continue  # 已插入(幂等)
        lines = lines[:last_content + 1] + ["", img_line] + lines[last_content + 1:]
        inserted += 1
    if inserted:
        md_path.write_text("\n".join(lines), encoding="utf-8")
    return inserted, missing


def compute_owner(doc, year):
    """锚点 + 归属(不含切图):返回 (lines, owner, shared, start_pno,
    missing, src)。
    1) 锚点:优先文本层(>2000 字符视为有文本层);缺失题号用 OCR 补齐,
       归属行走"文本行 + OCR 行"并集(两套坐标同处 pt 空间,取并集
       只会略增边界、不会少切)
    2) 题号两源皆丢的缺口修复(相邻题都在时)
    3) 行归属到实体"""
    text_len = sum(len(p.get_text()) for p in doc)
    if text_len > 2000:
        text_lines = get_text_lines(doc)
        start_pno = find_body_start(text_lines)
        q_anchor, shared, _ = scan_entities(text_lines, start_pno)
        missing = [q for q in range(1, 58) if q not in q_anchor]
        if missing:
            ocr_lines = get_ocr_lines(doc, year)
            q_o, shared_o, _ = scan_entities(ocr_lines, find_body_start(ocr_lines))
            for q in missing:
                if q in q_o:
                    q_anchor[q] = q_o[q]
            have = {(a, b) for a, b, _ in shared}
            for a, b, ln in shared_o:
                if (a, b) not in have:
                    shared.append((a, b, ln))
            lines = text_lines + ocr_lines
            missing = [q for q in range(1, 58) if q not in q_anchor]
            src = "文本层+OCR 补齐"
        else:
            lines = text_lines
            src = "文本层"
    else:
        lines = get_ocr_lines(doc, year)
        start_pno = find_body_start(lines)
        q_anchor, shared, _ = scan_entities(lines, start_pno)
        missing = [q for q in range(1, 58) if q not in q_anchor]
        src = "OCR"
    if missing:
        # 题号两源皆丢的缺口修复(相邻题都在时)
        for q, ln in rescue_missing(q_anchor, lines):
            q_anchor[q] = ln
            print(f"       ~ {year} Q{q} 题号丢失,按缺口修复"
                  f"(p{ln[0]} y{ln[1]:.0f})")
        missing = [q for q in range(1, 58) if q not in q_anchor]
    owner = assign_lines(lines, q_anchor, shared, start_pno)
    return lines, owner, shared, start_pno, missing, src


def reslice_year(year):
    pdf = PDF_DIR / f"{year}年199管综真题.pdf"
    out_dir = OUTPUT_ROOT / f"{year}年"
    images_dir = out_dir / "images"
    if not pdf.exists():
        print(f"[✘] {year}: 缺 PDF {pdf.name}")
        return 1
    images_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf))

    lines, owner, shared, start_pno, missing, src = compute_owner(doc, year)
    if missing:
        print(f"[✘] {year}: 仍缺锚点 {missing}(来源 {src})")

    # 图形墨迹回收(深色带 + 浅灰续行交替到不动点)+ 切图
    actions = []
    for _r in range(4):
        a_dark = expand_for_ink(doc, lines, owner, start_pno)
        a_gray = gray_continuation(doc, lines, owner, start_pno)
        actions.extend(a_dark)
        actions.extend(a_gray)
        if not a_dark and not a_gray:
            break
    if actions:
        ids = sorted({k[1] for (_p, _a, _b, k, _h) in actions},
                     key=lambda x: (0, x) if isinstance(x, int) else (1, x))
        print(f"       * 墨迹回收 {len(actions)} 处: "
              + ", ".join(f"Q{x}" if isinstance(x, int)
                          else f"s{x[0]}_{x[1]}" for x in ids))
    written = 0
    for q in range(1, 58):
        key = ("q", q)
        if key not in owner or not owner[key]:
            if q not in missing:
                print(f"       ! {year} Q{q} 无归属行,未写图")
            continue
        stitch_and_save(doc, segments_for(owner[key]),
                        images_dir / f"{year}_q{q:02d}.png")
        written += 1
    shared_groups = []
    for a, b, _ln in shared:
        key = ("s", (a, b))
        if key in owner and owner[key]:
            stitch_and_save(doc, segments_for(owner[key]),
                            images_dir / f"{year}_shared_{a}_{b}.png")
            shared_groups.append((a, b))
            written += 1

    # 3) md 插入共享题干图片行
    md_path = out_dir / f"{year}年199管综真题试卷.md"
    md_info = ""
    if md_path.exists() and shared_groups:
        inserted, not_found = insert_shared_image_lines(md_path, year, shared_groups)
        md_info = f", md 图片行 +{inserted}"
        if not_found:
            print(f"       ! {year} md 未找到共享题干标题 {not_found}")
    elif shared_groups:
        print(f"       ! {year} 无 md,共享题干图未挂入")

    status = "OK " if not missing else "WARN"
    print(f"[{status}] {year}: 锚点 {57 - len(missing)}/57({src})"
          f", 共享题干 {len(shared_groups)} 组, 写图 {written} 张{md_info}")
    return len(missing)


def main():
    only = [int(x) for x in sys.argv[1:]]
    years = only or list(range(2009, 2027))
    problems = 0
    for year in years:
        problems += reslice_year(year)
    print(f"\n{'=' * 50}")
    if problems:
        print(f"⚠ 共 {problems} 处锚点缺失,见上方明细,请人工复核")
        sys.exit(1)
    print("全部年份 57 题锚点齐整,切片图重建完成")


if __name__ == "__main__":
    main()
