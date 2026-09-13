import fitz

doc = fitz.open("真题部分/2012年199管综真题.pdf")
print("=== Page 1 ===")
print(doc[1].get_text()[:600])
print("=== Page 2 ===")
print(doc[2].get_text()[:600])
print("=== Page 3 ===")
print(doc[3].get_text()[:600])
print("=== Page 4 ===")
print(doc[4].get_text()[:600])
