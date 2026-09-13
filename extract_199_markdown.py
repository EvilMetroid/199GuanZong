#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考研管综 199 真题 PDF 转 Markdown 与按题切分处理器
- 针对 199 试卷三大模块（数学基础、逻辑推理、写作）进行 Item-Level 结构化切分
- 对数学公式/几何图自动生成高保真切片图嵌入 Markdown，保证 100% 不乱码、不失真
- 逻辑推理自动规范化 A-E 选项与题干
- 写作题目格式化为标准 Markdown 引用与要求说明
- 同步生成便于大模型 RAG / 向量库检索的 JSONL 切片数据
"""

import os
import re
import sys
import json
import glob
import fitz  # PyMuPDF

OUTPUT_ROOT = "199管综真题_Markdown题库"

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def crop_question_image(doc, page_num, rect, out_path, dpi=200):
    page = doc[page_num]
    crop_rect = fitz.Rect(
        max(0, rect.x0),
        max(0, rect.y0),
        min(page.rect.x1, rect.x1),
        min(page.rect.y1, rect.y1)
    )
    if crop_rect.height <= 5 or crop_rect.width <= 5:
        return
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, clip=crop_rect)
    pix.save(out_path)

def process_year(pdf_path, output_dir):
    filename = os.path.basename(pdf_path)
    year_match = re.search(r"(\d{4})年", filename)
    if not year_match:
        return []
    year = year_match.group(1)
    
    print(f"[*] 正在处理 {year} 年 199 管综真题...")
    doc = fitz.open(pdf_path)
    
    year_out_dir = os.path.join(output_dir, f"{year}年")
    images_dir = os.path.join(year_out_dir, "images")
    ensure_dir(images_dir)
    
    # 1. 扫描定位所有 1~57 题的起始位置与坐标
    q_locations = {}
    for pno in range(1, len(doc)):
        page = doc[pno]
        for b in page.get_text("blocks"):
            if b[0] < 120:
                m = re.match(r"^\s*(\d{1,2})\s*[\.．、\s]", b[4])
                if m:
                    qnum = int(m.group(1))
                    if 1 <= qnum <= 57 and qnum not in q_locations:
                        q_locations[qnum] = (pno, b)
                        
    # 2. 抽取全文文本并切割大模块
    page_texts = []
    for pno in range(len(doc)):
        if pno == 0 and "绝密" in doc[0].get_text():
            continue
        page_texts.append(doc[pno].get_text())
    full_text = "\n".join(page_texts)
    
    idx_math = full_text.find("一、问题求解")
    idx_logic = full_text.find("二、逻辑推理") if "二、逻辑推理" in full_text else full_text.find("三、逻辑推理")
    idx_writing = full_text.find("四、写作") if "四、写作" in full_text else full_text.find("三、写作")
    
    math_text = full_text[idx_math:idx_logic] if idx_logic != -1 else ""
    logic_text = full_text[idx_logic:idx_writing] if (idx_logic != -1 and idx_writing != -1) else ""
    writing_text = full_text[idx_writing:] if idx_writing != -1 else ""
    
    all_chunks = []
    
    # 3. 处理数学部分 (1-25)
    math_questions = {}
    for q in range(1, 26):
        next_pat = rf"\n(?:{q+1}\s*[\.．、\s]|二、条件充分性判断|二、逻辑推理|三、逻辑推理|\Z)"
        m = re.search(rf"\n{q}\s*[\.．、\s](.+?)(?={next_pat})", math_text, re.DOTALL)
        q_type = "问题求解" if q <= 15 else "条件充分性判断"
        q_stem = m.group(1).strip() if m else ""
        
        # 裁剪试题高清图片
        q_img_rel = None
        if q in q_locations:
            pno, b = q_locations[q]
            page = doc[pno]
            y_top = max(0, b[1] - 4)
            if q + 1 in q_locations and q_locations[q+1][0] == pno:
                y_bottom = q_locations[q+1][1][1] - 4
            else:
                y_bottom = page.rect.y1 - 30
            
            if y_bottom > y_top + 10:
                crop = fitz.Rect(page.rect.x0 + 15, y_top, page.rect.x1 - 15, y_bottom)
                img_name = f"{year}_q{q:02d}.png"
                img_abs = os.path.join(images_dir, img_name)
                crop_question_image(doc, pno, crop, img_abs)
                q_img_rel = f"images/{img_name}"
                
        math_questions[q] = {
            "no": q,
            "subject": "数学基础",
            "type": q_type,
            "raw_text": q_stem,
            "image": q_img_rel
        }
        all_chunks.append({
            "chunk_id": f"{year}_math_{q:02d}",
            "year": int(year),
            "subject": "数学基础",
            "question_no": q,
            "category": q_type,
            "text": q_stem,
            "image": q_img_rel
        })
        
    # 4. 处理逻辑部分 (26-55)
    logic_questions = {}
    for q in range(26, 56):
        next_pat = rf"\n(?:{q+1}\s*[\.．、\s]|三、写作|四、写作|\Z)"
        m = re.search(rf"\n{q}\s*[\.．、\s](.+?)(?={next_pat})", logic_text, re.DOTALL)
        raw_stem = m.group(1).strip() if m else ""
        
        options = {}
        stem_body = raw_stem
        opt_matches = list(re.finditer(r"\n([A-E])[\.．、\s](.+?)(?=\n[A-E][\.．、\s]|\Z)", "\n" + raw_stem, re.DOTALL))
        if opt_matches:
            first_opt_start = raw_stem.find(opt_matches[0].group(0).strip())
            if first_opt_start != -1:
                stem_body = raw_stem[:first_opt_start].strip()
            for om in opt_matches:
                options[om.group(1)] = om.group(2).strip().replace("\n", "")
                
        logic_questions[q] = {
            "no": q,
            "subject": "逻辑推理",
            "type": "逻辑单选题",
            "stem": stem_body,
            "options": options,
            "raw": raw_stem
        }
        all_chunks.append({
            "chunk_id": f"{year}_logic_{q:02d}",
            "year": int(year),
            "subject": "逻辑推理",
            "question_no": q,
            "category": "逻辑单选题",
            "stem": stem_body,
            "options": options
        })
        
    # 5. 处理写作部分 (56-57)
    writing_questions = {}
    m56 = re.search(r"56\s*[\.．、\s](.+?)(?=57\s*[\.．、\s]|\Z)", writing_text, re.DOTALL)
    m57 = re.search(r"57\s*[\.．、\s](.+?)$", writing_text, re.DOTALL)
    
    if m56:
        writing_questions[56] = {
            "no": 56,
            "subject": "中文写作",
            "type": "论证有效性分析 (30分)",
            "content": m56.group(1).strip()
        }
        all_chunks.append({
            "chunk_id": f"{year}_writing_56",
            "year": int(year),
            "subject": "中文写作",
            "question_no": 56,
            "category": "论证有效性分析",
            "content": m56.group(1).strip()
        })
        
    if m57:
        writing_questions[57] = {
            "no": 57,
            "subject": "中文写作",
            "type": "论说文 (35分)",
            "content": m57.group(1).strip()
        }
        all_chunks.append({
            "chunk_id": f"{year}_writing_57",
            "year": int(year),
            "subject": "中文写作",
            "question_no": 57,
            "category": "论说文",
            "content": m57.group(1).strip()
        })
        
    # 6. 生成 Markdown 文档
    full_md_path = os.path.join(year_out_dir, f"{year}年199管综真题试卷.md")
    with open(full_md_path, "w", encoding="utf-8") as f:
        f.write(f"# {year} 年全国硕士研究生入学统一考试\n")
        f.write(f"# 管理类专业学位联考综合能力试题 (199)\n\n")
        f.write("> **试卷结构**：\n")
        f.write("> - 一、数学基础（第 1-25 题，共 75 分）\n")
        f.write("> - 二、逻辑推理（第 26-55 题，共 60 分）\n")
        f.write("> - 三、写作（第 56-57 题，共 65 分）\n\n---\n\n")
        
        f.write("## 一、数学基础（第 1-25 题，共 75 分）\n\n")
        f.write("### (一) 问题求解：第 1~15 小题，每小题 3 分，共 45 分\n\n")
        for q in range(1, 16):
            item = math_questions.get(q, {})
            f.write(f"#### 第 {q} 题（问题求解）\n\n")
            if item.get("image"):
                f.write(f"![{year}年第{q}题]({item['image']})\n\n")
            if item.get("raw_text"):
                f.write(f"<details><summary>展开文字版 OCR 参考</summary>\n\n```text\n{item['raw_text']}\n```\n</details>\n\n")
                
        f.write("### (二) 条件充分性判断：第 16~25 小题，每小题 3 分，共 30 分\n\n")
        f.write("> **选项说明**：\n")
        f.write("> - A. 条件 (1) 充分，但条件 (2) 不充分\n")
        f.write("> - B. 条件 (2) 充分，但条件 (1) 不充分\n")
        f.write("> - C. 条件 (1) 和条件 (2) 单独都不充分，但条件 (1) 和条件 (2) 联合起来充分\n")
        f.write("> - D. 条件 (1) 充分，条件 (2) 也充分\n")
        f.write("> - E. 条件 (1) 和条件 (2) 单独都不充分，联合起来也不充分\n\n")
        for q in range(16, 26):
            item = math_questions.get(q, {})
            f.write(f"#### 第 {q} 题（条件充分性判断）\n\n")
            if item.get("image"):
                f.write(f"![{year}年第{q}题]({item['image']})\n\n")
            if item.get("raw_text"):
                f.write(f"<details><summary>展开文字版 OCR 参考</summary>\n\n```text\n{item['raw_text']}\n```\n</details>\n\n")
                
        f.write("\n---\n\n## 二、逻辑推理（第 26-55 题，每小题 2 分，共 60 分）\n\n")
        for q in range(26, 56):
            item = logic_questions.get(q, {})
            f.write(f"#### 第 {q} 题\n\n")
            f.write(f"{item.get('stem', '')}\n\n")
            opts = item.get("options", {})
            if opts:
                for k in ["A", "B", "C", "D", "E"]:
                    if k in opts:
                        f.write(f"- **{k}**．{opts[k]}\n")
            else:
                f.write(f"{item.get('raw', '')}\n")
            f.write("\n")
            
        f.write("\n---\n\n## 三、写作（第 56-57 题，共 65 分）\n\n")
        if 56 in writing_questions:
            f.write("### 第 56 题 · 论证有效性分析 (30 分)\n\n")
            f.write(f"{writing_questions[56]['content']}\n\n")
        if 57 in writing_questions:
            f.write("### 第 57 题 · 论说文 (35 分)\n\n")
            f.write(f"{writing_questions[57]['content']}\n\n")

    # 7. 写入 RAG 切分 JSONL 数据
    jsonl_path = os.path.join(year_out_dir, f"{year}年199真题_chunks.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            
    print(f"[✔] {year} 年真题处理完成！试卷已生成：{full_md_path}，生成题目切片：{len(all_chunks)} 道")
    return all_chunks

if __name__ == "__main__":
    ensure_dir(OUTPUT_ROOT)
    target_year = sys.argv[1] if len(sys.argv) > 1 else "2024"
    if target_year == "all":
        all_pdfs = sorted(glob.glob("真题部分/*年199管综真题.pdf"))
        print(f"找到 {len(all_pdfs)} 套年份真题，开始批量全量转换...")
        all_data = []
        for p in all_pdfs:
            chunks = process_year(p, OUTPUT_ROOT)
            if chunks:
                all_data.extend(chunks)
        total_jsonl = os.path.join(OUTPUT_ROOT, "199管综历年真题_全量RAG切分库.jsonl")
        with open(total_jsonl, "w", encoding="utf-8") as f:
            for c in all_data:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        print(f"\n🎉 全部年份转换完成！全量切片库已生成：{total_jsonl}")
    else:
        pdf_path = f"真题部分/{target_year}年199管综真题.pdf"
        if os.path.exists(pdf_path):
            process_year(pdf_path, OUTPUT_ROOT)
        else:
            print(f"未找到文件：{pdf_path}")
