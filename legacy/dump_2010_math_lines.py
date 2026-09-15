from extract_2010_from_crops import q_lines

for q in range(1, 26):
    print(f"=== Q{q} ===")
    for l in q_lines[q]:
        print(" ", l)
