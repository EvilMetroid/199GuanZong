import fitz, re, json

doc = fitz.open("真题部分/2009-2024年199管综真题合集.pdf")

# We know the question distribution across pages:
# Page 1: Q1 ~ Q8
# Page 2: Q9 ~ Q15
# Page 3: Q16 ~ Q23
# Page 4: Q24 ~ Q29 (Q24-25 are 充分性, Q26-29 are 逻辑)
# Page 5: Q30 ~ Q33 (Q33 options spill to page 6? Let's check)
# Page 6: Q34 ~ Q37 (Q37 options spill to page 7? Let's check)
# Page 7: Q38 ~ Q41 (Q41 options spill to page 8?)
# Page 8: Q42 ~ Q45 (Q45 options spill to page 9?)
# Page 9: Q46 ~ Q50
# Page 10: Q51 ~ Q53 (Q53 options spill to page 11?)
# Page 11: Q54 ~ Q56 (Q56 is 论证有效性分析)
# Page 12: Q57 (论说文)

# Let's inspect line by line for each page
for p in range(1, 13):
    text = doc[p].get_text()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    q_in_p = []
    for l in lines:
        m = re.match(r'^(\d{1,2})[\.、．]', l)
        if m:
            q_in_p.append((int(m.group(1)), l[:30]))
    print(f"Page {p}: found questions: {[q[0] for q in q_in_p]}")

