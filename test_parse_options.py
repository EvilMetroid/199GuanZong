import json, re

with open("199管综真题_Markdown题库/2009年/ocr_cache.json") as f:
    cache = json.load(f)

from fix_all_crops_2009 import exact_crops

q_lines = {q: [] for q in range(1, 58)}
for p in range(1, 13):
    for l in cache[str(p)]:
        txt = l['text']
        if "2009年真题" in txt or "绝密" in txt: continue
        ymid = (l['bbox'][1] + l['bbox'][3]) / 2.0
        for q, slices in exact_crops.items():
            for (sp, sy0, sy1) in slices:
                if sp == p and sy0 <= ymid <= sy1:
                    q_lines[q].append(txt)
                    break

def parse_options_from_lines(lines):
    full_txt = "\n".join(lines)
    # find options
    opts = {}
    opt_pattern = r'[（\(]([A-E])[）\)]([^\(（\n]+)'
    matches = list(re.finditer(opt_pattern, full_txt))
    if len(matches) >= 4:
        for m in matches:
            letter = m.group(1).upper()
            val = m.group(2).strip()
            opts[letter] = val
    return opts

missing_opts = []
for q in list(range(1, 16)) + list(range(26, 56)):
    opts = parse_options_from_lines(q_lines[q])
    if len(opts) < 5:
        missing_opts.append((q, list(opts.keys()), q_lines[q]))

print(f"Questions missing 5 options: {len(missing_opts)}")
for q, keys, lines in missing_opts:
    print(f"Q{q}: found {keys}")
    for l in lines:
        print("  ", l)
