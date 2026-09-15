import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2014年199管综真题.pdf"
YEAR = 2014
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)
with open(f"{OUT_DIR}/ocr_cache.json") as f:
    cache = json.load(f)

exact_crops_2014 = {
    1: [(1, 115, 178)],
    2: [(1, 178, 238)],
    3: [(1, 238, 410)],
    4: [(1, 410, 478)],
    5: [(1, 478, 642)],
    6: [(1, 642, 700)],
    7: [(1, 700, 742)],
    8: [(1, 742, 775), (2, 45, 118)],
    
    9: [(2, 118, 190)],
    10: [(2, 190, 232)],
    11: [(2, 232, 282)],
    12: [(2, 282, 475)],
    13: [(2, 475, 548)],
    14: [(2, 548, 608)],
    15: [(2, 608, 675)],
    16: [(3, 135, 198)],
    
    17: [(3, 198, 258)],
    18: [(3, 258, 320)],
    19: [(3, 320, 412)],
    20: [(3, 412, 492)],
    21: [(3, 492, 552)],
    22: [(3, 552, 610)],
    23: [(3, 610, 692)],
    24: [(3, 692, 775)],
    25: [(4, 55, 172)],
    
    26: [(4, 172, 352)],
    27: [(4, 352, 532)],
    28: [(4, 532, 690)],
    29: [(4, 690, 775), (5, 45, 115)],
    
    30: [(5, 115, 452)],
    31: [(5, 452, 630)],
    32: [(5, 630, 775), (6, 45, 198)],
    
    33: [(6, 198, 355)],
    34: [(6, 355, 535)],
    35: [(6, 535, 775), (7, 45, 75)],
    
    36: [(7, 75, 472)],
    37: [(7, 472, 512)],
    38: [(7, 512, 572)],
    39: [(7, 572, 775), (8, 45, 72)],
    
    40: [(8, 72, 275)],
    41: [(8, 275, 532)],
    42: [(8, 532, 715)],
    43: [(8, 715, 775), (9, 45, 158)],
    
    44: [(9, 158, 328)],
    45: [(9, 328, 532)],
    46: [(9, 532, 672)],
    47: [(9, 672, 775), (10, 45, 118)],
    
    48: [(10, 118, 238)],
    49: [(10, 238, 415)],
    50: [(10, 415, 632)],
    51: [(10, 632, 775), (11, 45, 80)],
    
    52: [(11, 80, 440)],
    53: [(11, 440, 520)],
    54: [(11, 520, 600)],
    55: [(11, 600, 730)],
    56: [(11, 730, 775), (12, 45, 395)],
    57: [(12, 395, 620)]
}

DPI = 200
LEFT_X = 55.0
RIGHT_X = 545.0

print(f"Rendering all 57 crops for 2014...")
for q, slices in exact_crops_2014.items():
    rendered = []
    for (p, sy0, sy1) in slices:
        page = doc[p]
        rect = fitz.Rect(LEFT_X, sy0, RIGHT_X, sy1)
        pix = page.get_pixmap(dpi=DPI, clip=rect)
        rendered.append(Image.open(io.BytesIO(pix.tobytes("png"))))
    
    if len(rendered) == 1:
        final_im = rendered[0]
    else:
        tw = max(im.width for im in rendered)
        th = sum(im.height for im in rendered) + 6
        final_im = Image.new("RGB", (tw, th), (255, 255, 255))
        cy = 0
        for im in rendered:
            final_im.paste(im, (0, cy))
            cy += im.height + 6
    
    out_path = os.path.join(IMG_DIR, f"{YEAR}_q{q:02d}.png")
    final_im.save(out_path)

print("All 57 crops for 2014 rendered successfully!")
