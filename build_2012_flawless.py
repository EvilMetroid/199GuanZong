import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2012年199管综真题.pdf"
YEAR = 2012
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)
with open(f"{OUT_DIR}/ocr_cache.json") as f:
    cache = json.load(f)

# Define exact pixel-perfect slices for 2012:
exact_crops_2012 = {
    1: [(1, 115, 178)],
    2: [(1, 178, 400)],
    3: [(1, 400, 502)],
    4: [(1, 502, 630)],
    5: [(1, 630, 708)],
    6: [(1, 708, 775), (2, 45, 258)],
    
    7: [(2, 258, 395)],
    8: [(2, 395, 505)],
    9: [(2, 505, 610)],
    10: [(2, 610, 670)],
    11: [(2, 670, 728)],
    12: [(2, 728, 775), (3, 45, 78)],
    
    13: [(3, 78, 155)],
    14: [(3, 155, 265)],
    15: [(3, 265, 345)],
    16: [(3, 495, 555)],
    17: [(3, 555, 612)],
    18: [(3, 612, 672)],
    19: [(3, 672, 730)],
    20: [(3, 730, 775), (4, 45, 78)],
    
    21: [(4, 78, 140)],
    22: [(4, 140, 258)],
    23: [(4, 258, 318)],
    24: [(4, 318, 378)],
    25: [(4, 378, 475)],
    
    26: [(4, 490, 728)],
    27: [(4, 728, 775), (5, 45, 152)],
    28: [(5, 152, 312)],
    29: [(5, 312, 470)],
    30: [(5, 470, 668)],
    31: [(5, 668, 775), (6, 45, 135)],
    
    32: [(6, 135, 295)],
    33: [(6, 295, 472)],
    34: [(6, 472, 630)],
    35: [(6, 630, 775), (7, 45, 172)],
    
    36: [(7, 172, 352)],
    37: [(7, 352, 608)],
    38: [(7, 608, 708)],
    39: [(7, 708, 775), (8, 45, 155)],
    
    40: [(8, 155, 355)],
    41: [(8, 355, 552)],
    42: [(8, 552, 775), (9, 45, 135)],
    
    43: [(9, 135, 392)],
    44: [(9, 392, 552)],
    45: [(9, 552, 690)],
    46: [(9, 690, 775), (10, 45, 235)],
    
    47: [(10, 235, 432)],
    48: [(10, 432, 592)],
    49: [(10, 592, 730)],
    50: [(10, 730, 775), (11, 45, 215)],
    
    51: [(11, 215, 452)],
    52: [(11, 452, 708)],
    53: [(11, 708, 775), (12, 45, 135)],
    
    54: [(12, 135, 258)],
    55: [(12, 258, 428)],
    56: [(12, 428, 775), (13, 45, 75)],
    57: [(13, 75, 280)]
}

DPI = 200
LEFT_X = 55.0
RIGHT_X = 545.0

print(f"Rendering all 57 crops for 2012...")
for q, slices in exact_crops_2012.items():
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

print("All 57 crops for 2012 rendered successfully!")
