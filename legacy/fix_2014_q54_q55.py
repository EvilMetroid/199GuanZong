with open("compile_complete_2014.py", "r") as f:
    code = f.read()

# Fix in compile_complete_2014.py where options are assigned
fix_target = """        all_questions.append({
            "question_no": q,
            "category": "逻辑推理",
            "stem": stem_part,
            "options": opts
        })"""

fix_replacement = """        if q == 54:
            opts = {
                "A": "墨灵参加国际象棋比赛。",
                "B": "庄聪参加中国象棋比赛。",
                "C": "孔智参加围棋比赛。",
                "D": "荀慧参加围棋比赛。",
                "E": "韩敏参加中国象棋比赛。"
            }
        elif q == 55:
            opts = {
                "A": "庄聪和韩敏参加中国象棋比赛。",
                "B": "韩敏和荀慧参加中国象棋比赛。",
                "C": "孔智和孟睿参加围棋比赛。",
                "D": "墨灵和孟睿参加围棋比赛。",
                "E": "韩敏和孔智参加围棋比赛。"
            }
        all_questions.append({
            "question_no": q,
            "category": "逻辑推理",
            "stem": stem_part,
            "options": opts
        })"""

code = code.replace(fix_target, fix_replacement)

# Also handle if q==54 didn't meet len(opt_parts) >= 4
fix_fallback = """        all_questions.append({
            "question_no": q,
            "category": "逻辑推理",
            "stem": raw,
            "options": {}
        })"""

fix_fallback_repl = """        if q == 54:
            stem_clean = raw.split("A.")[0].split("(A)")[0].strip()
            all_questions.append({
                "question_no": 54,
                "category": "逻辑推理",
                "stem": stem_clean,
                "options": {
                    "A": "墨灵参加国际象棋比赛。",
                    "B": "庄聪参加中国象棋比赛。",
                    "C": "孔智参加围棋比赛。",
                    "D": "荀慧参加围棋比赛。",
                    "E": "韩敏参加中国象棋比赛。"
                }
            })
        else:
            all_questions.append({
                "question_no": q,
                "category": "逻辑推理",
                "stem": raw,
                "options": {}
            })"""

code = code.replace(fix_fallback, fix_fallback_repl)

with open("compile_complete_2014.py", "w") as f:
    f.write(code)

