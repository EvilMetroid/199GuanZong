import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2020年199管综真题.pdf"
YEAR = 2020
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)

exact_crops_2020 = {
    1: [(1, 108, 150)],
    2: [(1, 150, 208)],
    3: [(1, 208, 306)],
    4: [(1, 306, 360)],
    5: [(1, 360, 400)],
    6: [(1, 400, 450)],
    7: [(1, 452, 495)],
    8: [(1, 495, 554)],
    9: [(1, 554, 738)],
    10: [(1, 738, 775), (2, 48, 182)],
    
    11: [(2, 148, 250)],
    12: [(2, 250, 362)],
    13: [(2, 362, 442)],
    14: [(2, 442, 605)],
    15: [(2, 605, 675)],
    
    16: [(3, 132, 200)],
    17: [(3, 200, 262)],
    18: [(3, 262, 322)],
    19: [(3, 322, 395)],
    20: [(3, 395, 455)],
    21: [(3, 455, 515)],
    22: [(3, 515, 570)],
    23: [(3, 572, 630)],
    24: [(3, 630, 703)],
    25: [(3, 703, 775)],
    
    26: [(4, 90, 304)],
    27: [(4, 304, 515)],
    28: [(4, 515, 702)],
    29: [(4, 702, 775), (5, 50, 150)],
    
    30: [(5, 150, 408)],
    31: [(5, 408, 642)],
    32: [(5, 642, 722)],
    33: [(5, 722, 775), (6, 50, 172)],
    
    34: [(6, 172, 372)],
    35: [(6, 372, 595)],
    36: [(6, 595, 775), (7, 50, 92)],
    
    37: [(7, 92, 314)],
    38: [(7, 314, 395)],
    39: [(7, 395, 558)],
    40: [(7, 558, 775)],
    
    41: [(8, 50, 212)],
    42: [(8, 212, 376)],
    43: [(8, 376, 600)],
    44: [(8, 600, 775), (9, 50, 69)],
    
    45: [(9, 69, 272)],
    46: [(9, 272, 476)],
    47: [(9, 476, 558)],
    48: [(9, 558, 775)],
    
    49: [(10, 50, 256)],
    50: [(10, 256, 542)],
    51: [(10, 542, 775)],
    
    52: [(11, 50, 315)],
    53: [(11, 315, 502)],
    54: [(11, 502, 775), (12, 50, 75)],
    55: [(12, 75, 168)],
    
    56: [(12, 168, 516)],
    57: [(12, 516, 780)]
}

zoom = 2.5
mat = fitz.Matrix(zoom, zoom)

for qn in range(1, 58):
    crops = exact_crops_2020[qn]
    pil_imgs = []
    for (pno, y0, y1) in crops:
        page = doc[pno]
        rect = page.rect
        clip = fitz.Rect(35, max(0, y0 - 2), rect.width - 35, min(rect.height, y1 + 2))
        pix = page.get_pixmap(matrix=mat, clip=clip)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        pil_imgs.append(img)
    
    if len(pil_imgs) == 1:
        final_img = pil_imgs[0]
    else:
        total_w = max(im.width for im in pil_imgs)
        total_h = sum(im.height for im in pil_imgs)
        final_img = Image.new("RGB", (total_w, total_h), (255, 255, 255))
        curr_y = 0
        for im in pil_imgs:
            final_img.paste(im, (0, curr_y))
            curr_y += im.height
            
    out_path = os.path.join(IMG_DIR, f"{YEAR}_q{qn:02d}.png")
    final_img.save(out_path)

print(f"Updated 57 images in {IMG_DIR}")
