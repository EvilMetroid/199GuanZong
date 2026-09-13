from parse_all_chunks import q_positions, all_text, sorted_qs

for q in [27, 33, 34, 52]:
    start = q_positions[q]
    idx = sorted_qs.index(q)
    end = q_positions[sorted_qs[idx+1]]
    print(f"=== Q{q} ===")
    print(all_text[start:end])
