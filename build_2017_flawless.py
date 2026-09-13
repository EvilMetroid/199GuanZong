import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2017年199管综真题.pdf"
YEAR = 2017
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)

exact_crops_2017 = {
    1: [(2, 110, 182)],
    2: [(2, 182, 248)],
    3: [(2, 248, 288)],
    4: [(2, 288, 475)],
    5: [(2, 475, 535)],
    6: [(2, 535, 575)],
    7: [(2, 575, 635)],
    8: [(2, 635, 695)],
    9: [(2, 695, 775)],
    
    10: [(3, 50, 104)],
    11: [(3, 104, 145)],
    12: [(3, 145, 270)],
    13: [(3, 270, 335)],
    14: [(3, 335, 502)],
    15: [(3, 502, 592)],
    
    16: [(4, 50, 142)],
    17: [(4, 142, 204)],
    18: [(4, 204, 264)],
    19: [(4, 264, 342)],
    20: [(4, 342, 402)],
    21: [(4, 402, 558)],
    22: [(4, 566, 628)],
    23: [(4, 628, 686)],
    24: [(4, 686, 775)],
    
    25: [(5, 50, 125)],
    26: [(5, 165, 345)],
    27: [(5, 345, 505)],
    28: [(5, 505, 725)],
    29: [(5, 725, 775), (6, 45, 268)],
    
    30: [(6, 268, 540)],
    31: [(6, 540, 775), (7, 45, 74)],
    32: [(7, 74, 272)],
    33: [(7, 272, 490)],
    34: [(7, 490, 568)],
    35: [(7, 568, 775), (8, 45, 108)],
    
    36: [(8, 108, 285)],
    37: [(8, 285, 482)],
    38: [(8, 482, 680)],
    39: [(8, 680, 775), (9, 45, 188)],
    
    40: [(9, 188, 445)],
    41: [(9, 445, 642)],
    42: [(9, 642, 775), (10, 45, 130)],
    
    43: [(10, 130, 348)],
    44: [(10, 348, 545)],
    45: [(10, 545, 775)],
    
    46: [(11, 50, 308)],
    47: [(11, 308, 565)],
    48: [(11, 565, 775)],
    
    49: [(12, 50, 252)],
    50: [(12, 252, 530)],
    51: [(12, 530, 775), (13, 45, 115)],
    
    52: [(13, 115, 234)],
    53: [(13, 234, 452)],
    54: [(13, 452, 708)],
    55: [(13, 708, 775), (14, 45, 124)],
    
    56: [(14, 124, 500)],
    57: [(14, 500, 750)]
}

DPI = 200
LEFT_X = 55.0
RIGHT_X = 545.0

print(f"Rendering all 57 crops for 2017...")
for q, slices in exact_crops_2017.items():
    rendered = []
    for (p, sy0, sy1) in slices:
        page = doc[p]
        rect = fitz.Rect(LEFT_X, sy0, RIGHT_X, sy1)
        pix = page.get_pixmap(dpi=DPI, clip=rect)
        rendered.append(Image.open(io.BytesIO(pix.tobytes("png"))))
    
    if len(rendered) == 1:
        final_im = rendered[0]
    else:
        tot_w = max(im.width for im in rendered)
        gap = 6
        tot_h = sum(im.height for im in rendered) + gap * (len(rendered) - 1)
        final_im = Image.new("RGB", (tot_w, tot_h), (255, 255, 255))
        cur_y = 0
        for im in rendered:
            final_im.paste(im, (0, cur_y))
            cur_y += im.height + gap
    
    out_name = f"{YEAR}_q{q:02d}.png"
    final_im.save(os.path.join(IMG_DIR, out_name))

print("Rendered 57 images successfully.")
