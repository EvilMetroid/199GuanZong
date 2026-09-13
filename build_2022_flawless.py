import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2022年199管综真题.pdf"
YEAR = 2022
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)

exact_crops_2022 = {
    1: [(0, 150, 215)],
    2: [(0, 215, 262)],
    3: [(0, 262, 322)],
    4: [(0, 322, 460)],
    5: [(0, 460, 574)],
    6: [(0, 574, 700)],
    
    7: [(1, 52, 112)],
    8: [(1, 112, 184)],
    9: [(1, 184, 292)],
    10: [(1, 292, 346)],
    11: [(1, 346, 404)],
    12: [(1, 404, 464)],
    13: [(1, 464, 532)],
    14: [(1, 532, 605)],
    15: [(1, 605, 700)],
    
    16: [(2, 168, 235)],
    17: [(2, 232, 300)],
    18: [(2, 300, 340)],
    19: [(2, 340, 386)],
    20: [(2, 386, 428)],
    21: [(2, 428, 470)],
    22: [(2, 475, 555)],
    23: [(2, 555, 608)],
    24: [(2, 612, 650)],
    25: [(2, 654, 700)],
    
    26: [(3, 82, 232)],
    27: [(3, 232, 368)],
    28: [(3, 368, 485)],
    29: [(3, 485, 635)],
    30: [(3, 635, 695), (4, 50, 110)],
    
    31: [(4, 110, 298)],
    32: [(4, 298, 412)],
    33: [(4, 412, 575)],
    34: [(4, 575, 692), (5, 50, 140)],
    
    35: [(5, 140, 254)],
    36: [(5, 254, 415)],
    37: [(5, 415, 545)],
    38: [(5, 545, 695)],
    
    39: [(6, 50, 165)],
    40: [(6, 165, 325)],
    41: [(6, 325, 472)],
    42: [(6, 472, 532)],
    43: [(6, 532, 675)],
    44: [(6, 675, 695), (7, 50, 182)],
    
    45: [(7, 182, 328)],
    46: [(7, 328, 386)],
    47: [(7, 386, 518)],
    48: [(7, 518, 648)],
    49: [(7, 648, 695), (8, 50, 168)],
    
    50: [(8, 168, 225)],
    51: [(8, 225, 355)],
    52: [(8, 355, 518)],
    53: [(8, 518, 665)],
    54: [(8, 665, 695), (9, 50, 228)],
    
    55: [(9, 228, 286)],
    56: [(9, 286, 490)],
    57: [(9, 490, 715)]
}

assert len(exact_crops_2022) == 57

zoom = 2.5
mat = fitz.Matrix(zoom, zoom)

for qn in range(1, 58):
    crops = exact_crops_2022[qn]
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
