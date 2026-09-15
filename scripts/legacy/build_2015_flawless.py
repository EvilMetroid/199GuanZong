import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2015年199管综真题.pdf"
YEAR = 2015
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)

exact_crops_2015 = {
    1: [(1, 110, 155)],
    2: [(1, 155, 225)],
    3: [(1, 225, 265)],
    4: [(1, 265, 395)],
    5: [(1, 395, 455)],
    6: [(1, 455, 535)],
    7: [(1, 535, 594)],
    8: [(1, 594, 775)],
    
    9: [(2, 50, 148)],
    10: [(2, 148, 212)],
    11: [(2, 212, 310)],
    12: [(2, 310, 406)],
    13: [(2, 406, 512)],
    14: [(2, 512, 775)],
    
    15: [(3, 50, 283)],
    16: [(3, 283, 365)],
    17: [(3, 365, 448)],
    18: [(3, 448, 508)],
    19: [(3, 508, 568)],
    20: [(3, 568, 628)],
    21: [(3, 628, 684)],
    22: [(3, 684, 775)],
    
    23: [(4, 50, 114)],
    24: [(4, 114, 175)],
    25: [(4, 175, 265)],
    26: [(4, 310, 508)],
    27: [(4, 508, 705)],
    28: [(4, 705, 775), (5, 45, 170)],
    
    29: [(5, 170, 348)],
    30: [(5, 348, 645)],
    31: [(5, 645, 775), (6, 45, 132)],
    32: [(6, 132, 212)],
    33: [(6, 212, 410)],
    34: [(6, 410, 648)],
    35: [(6, 648, 775), (7, 45, 130)],
    
    36: [(7, 130, 328)],
    37: [(7, 328, 460)],
    38: [(7, 460, 685)],
    39: [(7, 685, 725)],
    40: [(7, 725, 775), (8, 45, 115)],
    
    41: [(8, 115, 313)],
    42: [(8, 313, 372)],
    43: [(8, 372, 628)],
    44: [(8, 628, 775), (9, 45, 172)],
    
    45: [(9, 172, 350)],
    46: [(9, 350, 530)],
    47: [(9, 530, 726)],
    48: [(9, 726, 775), (10, 45, 192)],
    
    49: [(10, 192, 390)],
    50: [(10, 390, 588)],
    51: [(10, 588, 775)],
    
    52: [(11, 50, 270)],
    53: [(11, 270, 488)],
    54: [(11, 488, 775)],
    
    55: [(12, 50, 145)],
    56: [(12, 145, 580)],
    57: [(12, 580, 750)]
}

DPI = 200
LEFT_X = 55.0
RIGHT_X = 545.0

print(f"Rendering all 57 crops for 2015...")
for q, slices in exact_crops_2015.items():
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
