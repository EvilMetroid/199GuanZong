import os, sys, re, json
import fitz
from PIL import Image
import io

PDF_PATH = "真题部分/2023年199管综真题.pdf"
YEAR = 2023
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

doc = fitz.open(PDF_PATH)

crop_map_2023 = {
    # Page 1
    1: [(1, 90, 155)],
    2: [(1, 182, 255)],
    3: [(1, 282, 360)],
    4: [(1, 385, 450)],
    5: [(1, 468, 560)],
    6: [(1, 580, 660)],

    # Page 2
    7: [(2, 40, 165)],
    8: [(2, 172, 255)],
    9: [(2, 272, 355)],
    10: [(2, 372, 500)],
    11: [(2, 515, 675)],

    # Page 3
    12: [(3, 40, 160)],
    13: [(3, 175, 265)],
    14: [(3, 280, 435)],
    15: [(3, 455, 535)],

    # Page 4
    16: [(4, 60, 155)],
    17: [(4, 168, 235)],
    18: [(4, 245, 335)],
    19: [(4, 342, 430)],
    20: [(4, 438, 515)],
    21: [(4, 520, 615)],
    22: [(4, 628, 685)],

    # Page 5
    23: [(5, 42, 98)],
    24: [(5, 98, 155)],
    25: [(5, 155, 240)],
    26: [(5, 290, 450)],
    27: [(5, 460, 680)],

    # Page 6
    28: [(6, 40, 235)],
    29: [(6, 250, 430)],
    30: [(6, 445, 680)],

    # Page 7: Stem 31-32 is [40, 155]
    31: [(7, 40, 260)], # includes stem + Q31
    32: [(7, 40, 155), (7, 285, 385)], # stitch stem + Q32
    33: [(7, 400, 680)],

    # Page 8
    34: [(8, 38, 330)],
    35: [(8, 338, 680)],

    # Page 9: Stem 37-38 is [300, 400]
    36: [(9, 40, 280)],
    37: [(9, 300, 545)], # includes stem + Q37
    38: [(9, 300, 400), (9, 565, 655)], # stitch stem + Q38

    # Page 10
    39: [(10, 38, 300)],
    40: [(10, 315, 490)],
    41: [(10, 495, 685)],

    # Page 11
    42: [(11, 40, 185)],
    43: [(11, 188, 385)],
    44: [(11, 390, 685)],

    # Page 12: Stem 46-47 is [325, 440]
    45: [(12, 38, 320)],
    46: [(12, 325, 555)], # includes stem + Q46
    47: [(12, 325, 440), (12, 560, 685)], # stitch stem + Q47

    # Page 13
    48: [(13, 40, 345)],
    49: [(13, 355, 680)],

    # Page 14
    50: [(14, 40, 265)],
    51: [(14, 275, 455)],
    52: [(14, 460, 680)],

    # Page 15: Stem 54-55 is [305, 405]
    53: [(15, 40, 295)],
    54: [(15, 305, 545)], # includes stem + Q54
    55: [(15, 305, 405), (15, 550, 680)], # stitch stem + Q55

    # Page 16
    56: [(16, 75, 365)],
    57: [(16, 375, 480)]
}

DPI = 200

for qn in range(1, 58):
    rect_slices = crop_map_2023[qn]
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
        # vertical stitch with small padding
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
