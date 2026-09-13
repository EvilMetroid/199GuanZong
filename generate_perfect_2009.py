import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2009-2024年199管综真题合集.pdf"
YEAR = 2009
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)

# Let's define the exact question crops
# Each question defines:
#   page1: (p_num, y_start, y_end)
#   optional page2: (p_num+1, y_start, y_end)
# Default margin x0=55, x1=540

with open(f"{OUT_DIR}/ocr_cache.json") as f:
    cache = json.load(f)

# Build question start y for each question
q_starts = {}
for p in range(1, 13):
    lines = cache[str(p)]
    for l in lines:
        txt = l['text']
        m = re.match(r'^(\d{1,2})[\.、．]', txt)
        if m:
            qn = int(m.group(1))
            if 1 <= qn <= 57 and qn not in q_starts:
                q_starts[qn] = (p, l['bbox'][1])

# Fix manually located questions
q_starts[16] = (3, cache['3'][8]['bbox'][1])
q_starts[19] = (3, 350.0) # Page 3 y=350 begins Q19
q_starts[20] = (3, 425.0) # Page 3 y=425 begins Q20
q_starts[49] = (9, 498.0) # Page 9 y=498 begins Q49

# Bottom margin of content on page
PAGE_BOTTOM = 678.0
PAGE_TOP = 42.0
LEFT_X = 55.0
RIGHT_X = 540.0

crops_def = {}
for q in range(1, 58):
    p, y0 = q_starts[q]
    
    # Determine where q ends
    # Check if there is q+1 on the same page
    if q < 57 and q_starts[q+1][0] == p:
        # Same page
        y1 = q_starts[q+1][1] - 4
        crops_def[q] = [(p, y0 - 5, y1)]
    else:
        # Last question on page p
        # It ends at PAGE_BOTTOM of page p
        y1 = PAGE_BOTTOM
        p1_slice = (p, y0 - 5, y1)
        
        # Does it continue to page p+1?
        # Check if q+1 starts below PAGE_TOP + 30 or if there is content before q+1
        if q < 57:
            next_p, next_y0 = q_starts[q+1]
            if next_p == p + 1 and next_y0 > PAGE_TOP + 40:
                # Yes, continued content before q+1 starts on page p+1
                p2_slice = (p + 1, PAGE_TOP, next_y0 - 5)
                crops_def[q] = [p1_slice, p2_slice]
            else:
                crops_def[q] = [p1_slice]
        else:
            # Q57 is on page 12, ends around 200
            crops_def[q] = [(p, y0 - 5, 220.0)]

# Special check for Q36 & Q37 (Shared prompt on page 6)
# Q36 prompt "36~37题基于以下题干:" starts at y=375
# Let's include shared prompt for Q36
crops_def[36] = [(6, 370.0, q_starts[37][1] - 4)]

# Special check for Q40 & Q41 (Shared prompt on page 7)
# "40~41题基于以下题干:" starts at y=425
crops_def[40] = [(7, 422.0, q_starts[41][1] - 4)]

# Special check for Q16 (Section 2 header starts at y=45 on page 3)
# Q16 itself starts at y=187, but section 2 instruction is y=45..175
# We can crop Q16 from y=180 to Q17 start
crops_def[16] = [(3, 178.0, q_starts[17][1] - 4)]

print("Rendering 57 crops at 200 DPI...")
DPI = 200
scale = DPI / 72.0

for q in range(1, 58):
    slices = crops_def[q]
    rendered_images = []
    for (p, sy0, sy1) in slices:
        page = doc[p]
        rect = fitz.Rect(LEFT_X, max(sy0, 0), RIGHT_X, min(sy1, page.rect.height))
        pix = page.get_pixmap(dpi=DPI, clip=rect)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        rendered_images.append(img)
    
    if len(rendered_images) == 1:
        final_img = rendered_images[0]
    else:
        # Stitch vertically
        total_w = max(im.width for im in rendered_images)
        total_h = sum(im.height for im in rendered_images) + 10
        final_img = Image.new("RGB", (total_w, total_h), (255, 255, 255))
        curr_y = 0
        for im in rendered_images:
            final_img.paste(im, (0, curr_y))
            curr_y += im.height + 10
            
    out_path = os.path.join(IMG_DIR, f"2009_q{q:02d}.png")
    final_img.save(out_path)

print("All 57 crops saved successfully!")
