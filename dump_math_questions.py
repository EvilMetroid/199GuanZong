import fitz

doc = fitz.open("真题部分/2009-2024年199管综真题合集.pdf")
print("=== PAGE 1 ===")
print(doc[1].get_text())
print("=== PAGE 2 ===")
print(doc[2].get_text())
print("=== PAGE 3 ===")
print(doc[3].get_text())
print("=== PAGE 4 ===")
print(doc[4].get_text())
