# legacy/

题库构建早期(2024 年前后)的一次性脚本,全部已被根目录三个核心脚本
(`batch_optimize_all_199.py` / `build_rag_chunks_from_md.py` / `reslice_images.py`)
取代,**不再维护,不要依赖**。保留仅用于追溯当年的构建过程。

按用途分组:

- `extract_199_markdown.py` — 最早的 PDF→md 单卷提取器(批量化前的原型)。
- `build_*_flawless.py` / `build_full_2009.py` / `build_2009_content.py` —
  各年 md 逐题重写/修正脚本(每年一个,对应"flawless"修订轮)。
- `compile_complete_*.py` — 各年整卷编译脚本。
- `optimize_year_2009.py` / `run_year_refiner.py` — 单年精修(OCR + 图片)。
- `parse_*.py` / `dump_*.py` / `find_*.py` / `inspect_*.py` / `trace_*.py` /
  `map_*.py` / `make_*.py` / `group_*.py` / `extract_2010_from_crops.py` —
  坐标/切图/文本层排查用的探索脚本。
- `fix_*.py` — 个别题目定点修复(如 `fix_2014_q54_q55.py`)。
- `generate_*.py` — 早期切片图生成。
- `update_2024_markdown_with_ocr.py` — 2024 年 OCR 补正。
- `test_*.py` — 当年各解析路径的验证脚本(非 pytest,直接 `python3` 运行)。

注意:其中部分脚本互相引用(如 `group_ocr_by_crops.py` 引用
`fix_all_crops_2009.py`)且读写相对路径,只在仓库根目录上下文 + 当年的
中间产物齐全时才有意义。
