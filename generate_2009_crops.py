import fitz, os, re
from PIL import Image
import io

doc = fitz.open("真题部分/2009-2024年199管综真题合集.pdf")
out_dir = "199管综真题_Markdown题库/2009年/images"
os.makedirs(out_dir, exist_ok=True)

# Let's inspect blocks on each page to find exact y ranges for questions
# Page margins: left ~ 60, right ~ 535
# Page height ~ 792, width ~ 595

def get_page_blocks(p_num):
    page = doc[p_num]
    # get text with layout
    blocks = page.get_text("blocks")
    # block: (x0, y0, x1, y1, text, block_no, block_type)
    return blocks

print("Inspecting question spans...")
