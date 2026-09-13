import fitz, re

doc = fitz.open("真题部分/2010年199管综真题.pdf")
text = "\n".join([doc[p].get_text() for p in range(1, 4)])
text = re.sub(r'2010\s*年真题[^\n]*\n', '', text)

# Print questions 1 to 25
for q in range(1, 26):
    m = re.search(rf'(?:^|\n)\s*{q}[\.、．\s]', text)
    if m:
        start = m.start()
        # next question
        m_next = re.search(rf'(?:^|\n)\s*{q+1}[\.、．\s]', text[start:])
        end = start + m_next.start() if m_next else start + 300
        print(f"--- Q{q} ---")
        print(text[start:end].strip()[:200])
