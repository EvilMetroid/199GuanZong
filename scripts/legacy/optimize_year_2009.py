import os, sys, re, json
import fitz
from rapidocr_onnxruntime import RapidOCR

PDF_PATH = "真题部分/2009-2024年199管综真题合集.pdf"
YEAR = 2009
OUT_DIR = f"199管综真题_Markdown题库/{YEAR}年"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

ocr = RapidOCR()

def run_ocr_and_locate():
    doc = fitz.open(PDF_PATH)
    print(f"Loaded {PDF_PATH}, total pages: {len(doc)}")
    
    pages_ocr = {}
    for p_idx in range(1, 13):
        page = doc[p_idx]
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        ocr_res, _ = ocr(img_bytes)
        scale = 72.0 / 200.0
        lines = []
        if ocr_res:
            for item in ocr_res:
                box = item[0]
                text = item[1].strip()
                score = item[2]
                x0 = min(pt[0] for pt in box) * scale
                y0 = min(pt[1] for pt in box) * scale
                x1 = max(pt[0] for pt in box) * scale
                y1 = max(pt[1] for pt in box) * scale
                lines.append({"text": text, "bbox": [x0, y0, x1, y1], "score": float(score)})
        pages_ocr[p_idx] = lines
        print(f"Page {p_idx}: OCR detected {len(lines)} lines")

    with open(f"{OUT_DIR}/ocr_cache.json", "w", encoding="utf-8") as f:
        json.dump(pages_ocr, f, ensure_ascii=False, indent=2)
    print("OCR cache saved successfully.")

if __name__ == "__main__":
    run_ocr_and_locate()
