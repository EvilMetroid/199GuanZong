import fitz

doc = fitz.open('真题部分/2025年199管综真题.pdf')
print("Pages:", len(doc))

# Let's inspect pages 15, 16, 17, 18, 19
for p in [15, 16, 17, 18, 19]:
    pix = doc[p].get_pixmap(dpi=150)
    pix.save(f'page_{p}_preview.png')
print("Rendered 15-19")
