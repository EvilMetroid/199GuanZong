import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2018年199管综真题.pdf"
YEAR = 2018
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)

exact_crops_2018 = {
    1: [(2, 110, 170)],
    2: [(2, 170, 298)],
    3: [(2, 298, 375)],
    4: [(2, 375, 540)],
    5: [(2, 540, 582)],
    6: [(2, 582, 658)],
    7: [(2, 658, 775), (3, 45, 76)],
    
    8: [(3, 76, 138)],
    9: [(3, 138, 198)],
    10: [(3, 198, 242)],
    11: [(3, 242, 300)],
    12: [(3, 300, 356)],
    13: [(3, 356, 438)],
    14: [(3, 438, 662)],
    15: [(3, 662, 775)],
    
    16: [(4, 220, 280)],
    17: [(4, 280, 342)],
    18: [(4, 342, 430)],
    19: [(4, 430, 490)],
    20: [(4, 490, 708)],
    21: [(4, 708, 775), (5, 45, 76)],
    
    22: [(5, 76, 160)],
    23: [(5, 160, 242)],
    24: [(5, 242, 314)],
    25: [(5, 314, 395)],
    
    26: [(5, 428, 615)],
    27: [(5, 615, 775)],
    
    28: [(6, 215, 500)],
    29: [(6, 500, 775)],
    
    30: [(7, 50, 260)],
    31: [(7, 260, 320)],
    32: [(7, 320, 422)],
    33: [(7, 422, 666)],
    34: [(7, 666, 775), (8, 45, 92)],
    
    35: [(8, 92, 378)],
    36: [(8, 378, 560)],
    37: [(8, 560, 775)],
    
    38: [(9, 50, 278)],
    39: [(9, 278, 482)],
    40: [(9, 482, 665)],
    41: [(9, 665, 775), (10, 45, 72)],
    
    42: [(10, 72, 440)],
    43: [(10, 440, 604)],
    44: [(10, 604, 775), (11, 45, 114)],
    
    45: [(11, 114, 360)],
    46: [(11, 360, 524)],
    47: [(11, 524, 726)],
    48: [(11, 726, 775), (12, 45, 76)],
    
    49: [(12, 76, 260)],
    50: [(12, 260, 424)],
    51: [(12, 424, 688)],
    52: [(12, 688, 775), (13, 45, 140)],
    
    53: [(13, 140, 346)],
    54: [(13, 346, 594)],
    55: [(13, 594, 666)],
    56: [(13, 666, 775), (14, 45, 340)],
    57: [(14, 340, 600)]
}

DPI = 200
LEFT_X = 55.0
RIGHT_X = 545.0

print(f"Rendering all 57 crops for 2018...")
for q, slices in exact_crops_2018.items():
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
