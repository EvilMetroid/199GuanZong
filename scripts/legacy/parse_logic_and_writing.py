import json, re

with open("199管综真题_Markdown题库/2009年/ocr_cache.json") as f:
    cache = json.load(f)

from fix_all_crops_2009 import exact_crops

q_lines = {q: [] for q in range(26, 58)}
for p in range(4, 13):
    for l in cache[str(p)]:
        txt = l['text']
        if "2009年真题" in txt or "绝密" in txt: continue
        ymid = (l['bbox'][1] + l['bbox'][3]) / 2.0
        for q in range(26, 58):
            for (sp, sy0, sy1) in exact_crops[q]:
                if sp == p and sy0 <= ymid <= sy1:
                    q_lines[q].append(txt)
                    break

def clean_logic_question(q_no, lines):
    # Join lines
    full_text = "\n".join(lines)
    # find options
    # match patterns like (A) or （A） or A) or A.
    # split into stem and options
    parts = re.split(r'(?:^|\n)\s*[（\(]?([A-E])[）\.\、](.*)', full_text)
    stem_raw = parts[0].strip()
    # clean stem: remove question number prefix like "26." or "26、"
    stem_clean = re.sub(r'^\d{1,2}[\.、．]\s*', '', stem_raw)
    
    # gather options
    options = {}
    i = 1
    while i < len(parts):
        letter = parts[i].upper()
        opt_text = parts[i+1].strip() if i+1 < len(parts) else ""
        options[letter] = opt_text
        i += 2
        
    return {
        "question_no": q_no,
        "category": "逻辑推理",
        "stem": stem_clean,
        "options": options
    }

logic_qs = []
for q in range(26, 56):
    res = clean_logic_question(q, q_lines[q])
    logic_qs.append(res)
    print(f"Q{q}: opts={list(res['options'].keys())}, stem_len={len(res['stem'])}")

