import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2013年199管综真题.pdf"
YEAR = 2013
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)
with open(f"{OUT_DIR}/ocr_cache.json") as f:
    cache = json.load(f)

exact_crops_2013 = {
    1: [(1, 110, 190)],
    2: [(1, 190, 250)],
    3: [(1, 250, 310)],
    4: [(1, 310, 385)],
    5: [(1, 385, 465)],
    6: [(1, 465, 545)],
    7: [(1, 545, 665)],
    8: [(1, 665, 725)],
    9: [(1, 725, 775)],
    
    10: [(2, 45, 112)],
    11: [(2, 112, 210)],
    12: [(2, 210, 270)],
    13: [(2, 270, 325)],
    14: [(2, 325, 365)],
    15: [(2, 365, 570)],
    16: [(2, 665, 775)],
    
    17: [(3, 45, 110)],
    18: [(3, 110, 182)],
    19: [(3, 182, 242)],
    20: [(3, 242, 320)],
    21: [(3, 320, 385)],
    22: [(3, 385, 452)],
    23: [(3, 452, 532)],
    24: [(3, 532, 610)],
    25: [(3, 610, 715)],
    
    26: [(3, 715, 775), (4, 45, 268)],
    27: [(4, 268, 448)],
    28: [(4, 448, 645)],
    29: [(4, 645, 775), (5, 45, 108)],
    
    30: [(5, 108, 425)],
    31: [(5, 425, 545)],
    32: [(5, 545, 662)],
    33: [(5, 662, 775), (6, 45, 110)],
    
    34: [(6, 110, 385)],
    35: [(6, 385, 665)],
    36: [(6, 665, 722)],
    37: [(6, 722, 775), (7, 45, 228)],
    
    38: [(7, 228, 388)],
    39: [(7, 388, 605)],
    40: [(7, 605, 775), (8, 45, 72)],
    
    41: [(8, 72, 252)],
    42: [(8, 252, 450)],
    43: [(8, 450, 608)],
    44: [(8, 608, 775), (9, 45, 112)],
    
    45: [(9, 112, 390)],
    46: [(9, 390, 628)],
    47: [(9, 628, 775), (10, 45, 72)],
    
    48: [(10, 72, 232)],
    49: [(10, 232, 430)],
    50: [(10, 430, 588)],
    51: [(10, 588, 775)],
    
    52: [(11, 45, 232)],
    53: [(11, 232, 495)],
    54: [(11, 495, 555)],
    55: [(11, 555, 665)],
    56: [(11, 665, 775), (12, 45, 330)],
    57: [(12, 330, 550)]
}

DPI = 200
LEFT_X = 55.0
RIGHT_X = 545.0

print(f"Rendering all 57 crops for 2013...")
for q, slices in exact_crops_2013.items():
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

print("All 57 crops for 2013 rendered successfully!")
