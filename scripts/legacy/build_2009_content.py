import json, re, os

# Let's read the vector PDF text and OCR cache
import fitz

doc = fitz.open("真题部分/2009-2024年199管综真题合集.pdf")
pages_text = [doc[p].get_text() for p in range(len(doc))]

with open("199管综真题_Markdown题库/2009年/ocr_cache.json") as f:
    ocr_cache = json.load(f)

# Standard options for 条件充分性判断
COND_OPTIONS = {
    "A": "条件（1）充分，但条件（2）不充分",
    "B": "条件（2）充分，但条件（1）不充分",
    "C": "条件（1）和条件（2）单独都不充分，但条件（1）和条件（2）联合起来充分",
    "D": "条件（1）充分，条件（2）也充分",
    "E": "条件（1）和条件（2）单独都不充分，条件（1）和条件（2）联合起来也不充分"
}

print("Ready to construct 2009 questions...")
