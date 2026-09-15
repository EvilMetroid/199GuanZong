import fitz, json, re

doc = fitz.open("真题部分/2010年199管综真题.pdf")

# Standard options for 条件充分性判断
COND_OPTIONS = {
    "A": "条件（1）充分，但条件（2）不充分",
    "B": "条件（2）充分，但条件（1）不充分",
    "C": "条件（1）和条件（2）单独都不充分，但条件（1）和条件（2）联合起来充分",
    "D": "条件（1）充分，条件（2）也充分",
    "E": "条件（1）和条件（2）单独都不充分，条件（1）和条件（2）联合起来也不充分"
}

# Math questions 1~25
# Let's inspect text for 1~25
print("=== Math text sample ===")
for p in range(1, 4):
    print(f"Page {p} text length: {len(doc[p].get_text())}")
