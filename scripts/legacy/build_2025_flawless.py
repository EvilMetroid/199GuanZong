import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2025年199管综真题.pdf"
YEAR = 2025
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)

crop_map_2025 = {
    1: [(0, 150, 225)],
    2: [(0, 225, 295)],
    3: [(0, 295, 385)],
    4: [(0, 385, 485)],
    5: [(0, 485, 660), (1, 40, 85)], # cross-page
    
    6: [(1, 85, 215)],
    7: [(1, 215, 315)],
    8: [(1, 315, 395)],
    9: [(1, 395, 445)],
    10: [(1, 445, 620)],
    11: [(1, 620, 665), (2, 35, 90)], # cross-page
    
    12: [(2, 90, 165)],
    13: [(2, 165, 225)],
    14: [(2, 225, 280)],
    15: [(2, 280, 480)],
    
    16: [(3, 80, 165)],
    17: [(3, 165, 240)],
    18: [(3, 240, 335)],
    19: [(3, 335, 540)],
    20: [(3, 540, 660)],
    
    21: [(4, 60, 140)],
    22: [(4, 140, 240)],
    23: [(4, 240, 320)],
    24: [(4, 320, 410)],
    25: [(4, 410, 520)],
    
    26: [(4, 550, 660), (5, 40, 245)], # cross-page
    27: [(5, 245, 560)],
    28: [(5, 560, 660), (6, 40, 245)], # cross-page
    29: [(6, 245, 540)],
    30: [(6, 540, 660), (7, 40, 275)], # cross-page
    
    31: [(7, 275, 660)],
    32: [(8, 40, 385)],
    33: [(8, 385, 660)],
    34: [(9, 40, 385)],
    35: [(9, 385, 660), (10, 40, 130)], # cross-page
    
    36: [(10, 130, 355)],
    37: [(10, 355, 660)],
    38: [(11, 40, 345)],
    39: [(11, 345, 660), (12, 40, 220)], # 39-40 shared stem + Q39
    40: [(11, 345, 660), (12, 220, 340)], # 39-40 shared stem + Q40
    
    41: [(12, 340, 445)],
    42: [(12, 445, 660)],
    43: [(13, 40, 290)],
    44: [(13, 290, 660), (14, 40, 75)], # cross-page
    
    45: [(14, 75, 280)],
    46: [(14, 280, 480)],
    47: [(14, 480, 660), (15, 40, 75)], # cross-page
    48: [(15, 75, 295)],
    49: [(15, 295, 480)],
    
    50: [(15, 480, 660), (16, 40, 220)], # stem + Q50
    51: [(15, 480, 660), (16, 40, 140), (16, 220, 310)], # stem + Q51
    
    52: [(16, 310, 530)], # stem + Q52
    53: [(16, 310, 410), (16, 530, 660), (17, 40, 75)], # stem + Q53
    
    54: [(17, 80, 570)], # stem + Q54
    55: [(17, 80, 440), (17, 570, 660), (18, 40, 95)], # stem + Q55
    
    56: [(18, 95, 660), (19, 40, 105)], # cross-page
    57: [(19, 105, 250)]
}

DPI = 200

for qn in range(1, 58):
    rect_slices = crop_map_2025[qn]
    pil_slices = []
    for (page_idx, y0, y1) in rect_slices:
        page = doc[page_idx]
        rect = fitz.Rect(0, y0, page.rect.width, y1)
        pix = page.get_pixmap(dpi=DPI, clip=rect)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        pil_slices.append(img)
    
    if len(pil_slices) == 1:
        final_img = pil_slices[0]
    else:
        w = max(im.width for im in pil_slices)
        h = sum(im.height for im in pil_slices) + (len(pil_slices) - 1) * 10
        final_img = Image.new("RGB", (w, h), (255, 255, 255))
        curr_y = 0
        for im in pil_slices:
            final_img.paste(im, (0, curr_y))
            curr_y += im.height + 10

    out_path = os.path.join(IMG_DIR, f"{YEAR}_q{qn:02d}.png")
    final_img.save(out_path)

print(f"Generated all 57 flawless images for {YEAR}!")
