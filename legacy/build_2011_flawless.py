import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2011年199管综真题.pdf"
YEAR = 2011
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)
with open(f"{OUT_DIR}/ocr_cache.json") as f:
    cache = json.load(f)

# Define exact pixel-perfect slices for 2011:
exact_crops_2011 = {
    1: [(1, 110, 175)],
    2: [(1, 175, 230)],
    3: [(1, 230, 285)],
    4: [(1, 285, 342)],
    5: [(1, 342, 402)],
    6: [(1, 402, 472)],
    7: [(1, 472, 542)],
    8: [(1, 542, 605)],
    9: [(1, 605, 710)],
    10: [(1, 710, 775), (2, 45, 75)],
    
    11: [(2, 75, 135)],
    12: [(2, 135, 195)],
    13: [(2, 195, 255)],
    14: [(2, 255, 320)],
    15: [(2, 320, 395)],
    16: [(2, 550, 610)],
    17: [(2, 610, 668)],
    18: [(2, 668, 725)],
    19: [(2, 725, 775), (3, 45, 80)],
    
    20: [(3, 80, 142)],
    21: [(3, 142, 202)],
    22: [(3, 202, 272)],
    23: [(3, 272, 342)],
    24: [(3, 342, 422)],
    25: [(3, 422, 520)],
    
    26: [(3, 530, 770)],
    27: [(4, 60, 218)],
    28: [(4, 218, 435)],
    29: [(4, 435, 652)],
    30: [(4, 652, 775), (5, 45, 135)],
    
    31: [(5, 135, 315)],
    32: [(5, 315, 492)],
    33: [(5, 492, 670)],
    34: [(5, 670, 775), (6, 45, 218)],
    
    35: [(6, 218, 435)],
    36: [(6, 435, 612)],
    37: [(6, 612, 775), (7, 45, 95)],
    
    38: [(7, 95, 258)],
    39: [(7, 258, 560)],
    40: [(7, 560, 775), (8, 45, 158)],
    
    41: [(8, 158, 402)],
    42: [(8, 402, 625)],
    43: [(8, 625, 775), (9, 45, 95)],
    
    44: [(9, 95, 320)],
    45: [(9, 320, 565)],
    46: [(9, 565, 775)],
    
    47: [(10, 55, 240)],
    48: [(10, 240, 545)],
    49: [(10, 545, 648)],
    50: [(10, 648, 775)],
    
    51: [(11, 55, 198)],
    52: [(11, 198, 442)],
    53: [(11, 442, 668)],
    54: [(11, 668, 775), (12, 45, 140)],
    
    55: [(12, 140, 358)],
    56: [(12, 358, 775)],
    57: [(13, 50, 260)]
}

DPI = 200
LEFT_X = 55.0
RIGHT_X = 545.0

print(f"Rendering all 57 crops for 2011...")
for q, slices in exact_crops_2011.items():
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

print("All 57 crops for 2011 rendered successfully!")
