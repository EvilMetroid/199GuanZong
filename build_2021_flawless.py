import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2021年199管综真题.pdf"
YEAR = 2021
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)

exact_crops_2021 = {
    1: [(1, 108, 168)],
    2: [(1, 168, 230)],
    3: [(1, 234, 292)],
    4: [(1, 296, 352)],
    5: [(1, 352, 410)],
    6: [(1, 410, 588)],
    7: [(1, 588, 650)],
    8: [(1, 650, 700)],
    9: [(1, 700, 775), (2, 50, 226)],
    
    10: [(2, 226, 294)],
    11: [(2, 294, 352)],
    12: [(2, 352, 396)],
    13: [(2, 396, 460)],
    14: [(2, 460, 520)],
    15: [(2, 520, 592)],
    
    16: [(3, 50, 110)],
    17: [(3, 110, 170)],
    18: [(3, 170, 230)],
    19: [(3, 230, 310)],
    20: [(3, 310, 370)],
    21: [(3, 370, 430)],
    22: [(3, 430, 510)],
    23: [(3, 510, 570)],
    24: [(3, 570, 630)],
    25: [(3, 630, 695)],
    
    26: [(3, 740, 775), (4, 50, 195)],
    27: [(4, 195, 400)],
    28: [(4, 400, 645)],
    29: [(4, 645, 775), (5, 50, 195)],
    
    30: [(5, 195, 360)],
    31: [(5, 360, 562)],
    32: [(5, 562, 725)],
    33: [(5, 725, 775), (6, 50, 235)],
    
    34: [(6, 235, 400)],
    35: [(6, 400, 584)],
    36: [(6, 584, 775)],
    
    37: [(7, 50, 235)],
    38: [(7, 235, 418)],
    39: [(7, 418, 700)],
    40: [(7, 700, 775), (8, 50, 215)],
    
    41: [(8, 215, 298)],
    42: [(8, 298, 584)],
    43: [(8, 584, 775)],
    
    44: [(9, 50, 240)],
    45: [(9, 240, 572)],
    46: [(9, 572, 775)],
    
    47: [(10, 50, 276)],
    48: [(10, 276, 336)],
    49: [(10, 336, 570)],
    50: [(10, 575, 775), (11, 50, 135)],
    
    51: [(11, 135, 280)],
    52: [(11, 280, 578)],
    53: [(11, 578, 775)],
    
    54: [(12, 50, 248)],
    55: [(12, 248, 336)],
    
    56: [(12, 375, 675)],
    57: [(12, 675, 775)]
}

assert len(exact_crops_2021) == 57

zoom = 2.5
mat = fitz.Matrix(zoom, zoom)

for qn in range(1, 58):
    crops = exact_crops_2021[qn]
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
