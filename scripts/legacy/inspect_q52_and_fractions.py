import fitz

doc = fitz.open("真题部分/2009-2024年199管综真题合集.pdf")
print("--- Page 10 text ---")
print(doc[10].get_text())
