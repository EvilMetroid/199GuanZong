import os, sys, re, json
import fitz
from PIL import Image
from rapidocr_onnxruntime import RapidOCR
import io

ocr = RapidOCR()

def ocr_pdf_pages(pdf_path, out_cache_path):
    doc = fitz.open(pdf_path)
    print(f"Loaded {pdf_path}, {len(doc)} pages.")
    pages_ocr = {}
    for p_idx in range(len(doc)):
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
                score = float(item[2])
                x0 = min(pt[0] for pt in box) * scale
                y0 = min(pt[1] for pt in box) * scale
                x1 = max(pt[0] for pt in box) * scale
                y1 = max(pt[1] for pt in box) * scale
                lines.append({"text": text, "bbox": [x0, y0, x1, y1], "score": score})
        pages_ocr[p_idx] = lines
        print(f"Page {p_idx}: OCR {len(lines)} lines")
    with open(out_cache_path, "w", encoding="utf-8") as f:
        json.dump(pages_ocr, f, ensure_ascii=False, indent=2)
    return pages_ocr

if __name__ == "__main__":
    year = int(sys.argv[1])
    pdf_path = f"真题部分/{year}年199管综真题.pdf"
    out_dir = f"199管综真题_Markdown题库/{year}年"
    os.makedirs(out_dir, exist_ok=True)
    cache_path = f"{out_dir}/ocr_cache.json"
    ocr_pdf_pages(pdf_path, cache_path)
