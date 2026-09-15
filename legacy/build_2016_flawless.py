import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2016年199管综真题.pdf"
YEAR = 2016
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)

exact_crops_2016 = {
    1: [(1, 110, 192)],
    2: [(1, 192, 252)],
    3: [(1, 252, 330)],
    4: [(1, 330, 372)],
    5: [(1, 372, 450)],
    6: [(1, 450, 508)],
    7: [(1, 508, 550)],
    8: [(1, 550, 725)],
    9: [(1, 725, 775), (2, 45, 170)],
    
    10: [(2, 170, 212)],
    11: [(2, 212, 405)],
    12: [(2, 405, 485)],
    13: [(2, 485, 545)],
    14: [(2, 545, 604)],
    15: [(2, 604, 775)],
    
    16: [(3, 245, 305)],
    17: [(3, 305, 518)],
    18: [(3, 518, 580)],
    19: [(3, 580, 638)],
    20: [(3, 638, 724)],
    21: [(3, 724, 775), (4, 45, 76)],
    
    22: [(4, 76, 138)],
    23: [(4, 138, 190)],
    24: [(4, 190, 260)],
    25: [(4, 260, 335)],
    
    26: [(4, 370, 550)],
    27: [(4, 550, 775)],
    
    28: [(5, 50, 272)],
    29: [(5, 272, 450)],
    30: [(5, 450, 685)],
    31: [(5, 685, 775), (6, 45, 195)],
    
    32: [(6, 195, 393)],
    33: [(6, 393, 592)],
    34: [(6, 592, 775)],
    
    35: [(7, 50, 290)],
    36: [(7, 290, 488)],
    37: [(7, 488, 724)],
    38: [(7, 724, 775), (8, 45, 193)],
    
    39: [(8, 193, 412)],
    40: [(8, 412, 610)],
    41: [(8, 610, 775), (9, 45, 112)],
    
    42: [(9, 112, 312)],
    43: [(9, 312, 510)],
    44: [(9, 510, 588)],
    45: [(9, 588, 775), (10, 45, 95)],
    
    46: [(10, 95, 273)],
    47: [(10, 273, 452)],
    48: [(10, 452, 630)],
    49: [(10, 630, 775), (11, 45, 114)],
    
    50: [(11, 114, 312)],
    51: [(11, 312, 490)],
    52: [(11, 490, 688)],
    53: [(11, 688, 775), (12, 45, 95)],
    
    54: [(12, 95, 355)],
    55: [(12, 355, 448)],
    56: [(12, 448, 775), (13, 45, 72)],
    57: [(13, 72, 320)]
}

DPI = 200
LEFT_X = 55.0
RIGHT_X = 545.0

print(f"Rendering all 57 crops for 2016...")
for q, slices in exact_crops_2016.items():
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
