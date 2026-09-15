import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2019年199管综真题.pdf"
YEAR = 2019
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)

exact_crops_2019 = {
    1: [(1, 110, 170)],
    2: [(1, 170, 220)],
    3: [(1, 220, 448)],
    4: [(1, 448, 490)],
    5: [(1, 490, 610)],
    6: [(1, 610, 670)],
    7: [(1, 670, 775)],
    
    8: [(2, 50, 205)],
    9: [(2, 205, 302)],
    10: [(2, 302, 392)],
    11: [(2, 392, 472)],
    12: [(2, 472, 590)],
    13: [(2, 590, 775), (3, 45, 75)],
    
    14: [(3, 75, 130)],
    15: [(3, 130, 250)],
    16: [(3, 345, 425)],
    17: [(3, 425, 532)],
    18: [(3, 532, 625)],
    19: [(3, 625, 685)],
    20: [(3, 685, 775)],
    
    21: [(4, 50, 135)],
    22: [(4, 135, 195)],
    23: [(4, 195, 342)],
    24: [(4, 342, 435)],
    25: [(4, 435, 545)],
    
    26: [(4, 545, 725)],
    27: [(4, 725, 775), (5, 45, 230)],
    
    28: [(5, 230, 410)],
    29: [(5, 410, 625)],
    30: [(5, 625, 775), (6, 45, 95)],
    
    31: [(6, 95, 175)],
    32: [(6, 175, 378)],
    33: [(6, 378, 685)],
    34: [(6, 685, 775), (7, 45, 150)],
    
    35: [(7, 150, 305)],
    36: [(7, 305, 620)],
    37: [(7, 620, 775), (8, 45, 92)],
    
    38: [(8, 92, 310)],
    39: [(8, 310, 585)],
    40: [(8, 585, 712)],
    41: [(8, 712, 775), (9, 45, 190)],
    
    42: [(9, 190, 505)],
    43: [(9, 505, 682)],
    44: [(9, 682, 775), (10, 45, 92)],
    
    45: [(10, 92, 388)],
    46: [(10, 388, 605)],
    47: [(10, 605, 775), (11, 45, 92)],
    
    48: [(11, 92, 488)],
    49: [(11, 488, 568)],
    50: [(11, 568, 645)],
    51: [(11, 645, 775), (12, 45, 112)],
    
    52: [(12, 112, 310)],
    53: [(12, 310, 528)],
    54: [(12, 528, 775), (13, 45, 190)],
    55: [(13, 190, 278)],
    56: [(13, 278, 692)],
    57: [(13, 692, 775)]
}

DPI = 200
LEFT_X = 55.0
RIGHT_X = 545.0

print(f"Rendering all 57 crops for 2019...")
for q, slices in exact_crops_2019.items():
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
