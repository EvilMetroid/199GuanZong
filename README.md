# 考研管综 199 真题题库(2009–2026)

199 管综历年真题(试卷 + 答案解析)的结构化 Markdown 题库 + RAG 切分库(JSONL),
每年一卷、57 题,每题附原卷切片图。2009–2026 各卷 md 已逐题人工/多模态校核,
**md 是本题库的唯一内容源**。

## 目录结构

```
真题部分/                          各年原始试卷 PDF(每年一个,单文件)
答案部分/                          各年答案解析 PDF(四种版式混合)
199管综真题_Markdown题库/
  {year}年/
    {year}年199管综真题试卷.md     试卷正文(人工校核过)
    {year}年199真题_chunks.jsonl   该年 57 条 RAG 切分
    images/                        {year}_q01..q57.png + {year}_shared_{a}_{b}.png
  199管综历年真题_全量RAG切分库.jsonl  18 年共 1026 条汇总
199管综历年真题_全量RAG切分库.jsonl  汇总库的根目录镜像
199管综答案_Markdown题库/
  {year}年/
    {year}年199管综真题解析.md        答案解析(OCR 提取 + VLM 逐页对照原 PDF 校核;
                                       2026 年为人工整理:原 PDF 只给答案字母,
                                       第 1~55 题解析系据真题推演补全)
    {year}年199真题解析_chunks.jsonl  该年 57 条答案 RAG 切分
  199管综历年真题_全量RAG切分库_答案.jsonl  2009–2026 年 1026 条汇总
199管综历年真题_全量RAG切分库_答案.jsonl  答案汇总库的根目录镜像
ocr_cache/                         RapidOCR 行框缓存(真题 _ocr_lines / 答案 _answer_ocr_lines,可删)
build_rag_chunks_from_md.py        真题 md → RAG 切分库(当前唯一生成入口)
build_answer_md.py                 答案解析 PDF → 逐年 md(全量 RapidOCR,幂等)
build_answer_rag_chunks.py         答案解析 md → RAG 切分库
reslice_images.py                  原卷切片图重建 + 共享题干图片行(幂等)
legacy/                            83 个一次性构建/调试脚本(见 legacy/README.md)
```

## 当前工作流

日常只需四条命令,都在仓库根目录执行:

1. **重建 RAG 切分库**(md 有改动后跑):

   ```bash
   python3 build_rag_chunks_from_md.py            # 全量
   python3 build_rag_chunks_from_md.py 2024       # 指定年份
   ```

   校验标准:18 年 × 57 题 = 1026 条、零告警(题干为空/选项不齐/缺图会告警并非 0 退出)。

2. **重建答案解析 md**(答案部分 PDF 有变时跑;RapidOCR 全量,带缓存、幂等):

   ```bash
   python3 build_answer_md.py             # 2009–2025 全量
   python3 build_answer_md.py 2016 2024   # 指定年份
   ```

   4 种版式(2009–2021 文都"速查+详解"、2022 精简版、2023 清晰扫描、
   2024/2025)统一输出:答案速查(原书有则收录)+ 四大板块,每年 57 题,
   每题 `### 第 N 题` + `**答案**：X`。校验:57 题锚点缺失 / 答案字母缺失 /
   与速查表不符 / 内容过短均告警,锚点缺失非 0 退出。公式为 OCR 原文
   (不做 LaTeX 转换),核对请对照原 PDF。
   注:2026 年无独立答案解析 PDF,其解析为人工整理(原 PDF 只给答案字母,
   第 1~55 题解析系据真题推演并经程序穷举复核补全,第 51 题原 E 已更正为 C),
   不要对 2026 运行本脚本。

3. **重建答案 RAG 切分库**(答案解析 md 有改动后跑):

   ```bash
   python3 build_answer_rag_chunks.py            # 全量
   python3 build_answer_rag_chunks.py 2013 2018  # 指定年份
   ```

   字段:year / question_no / category / answer / explanation。category
   与真题库一致(1-15 问题求解、16-25 条件充分性判断、26-55 逻辑推理、
   56/57 写作);answer 为 1-55 题的 A-E 字母,写作题为 null。与真题库
   按 (year, question_no) 关联。校验:每年 57 条、答案字母缺失非 0 退出;
   解析为空仅告警(2022 精简版原书个别题目仅给答案)。

4. **重建原卷切片图**(需要改图时跑,幂等):

   ```bash
   python3 reslice_images.py            # 2009–2026 全量
   python3 reslice_images.py 2013 2022  # 指定年份
   ```

   行级题号锚点 + 归属划分,文本层优先、RapidOCR 补缺(缓存 ocr_cache/),
   两源皆丢的题号按相邻题缺口修复;切图按"题目全部行 ±4pt、跨页拼接",
   只可能略伸入相邻题、不会少切;切边切断的图形/表格线墨迹按深色带
   回收扩展(跨切分拆开的图形按整图扩),浅灰笔画(如立体图隐藏边)
   按续行回收。同时把共享题干("N~M 题基于以下题干")
   单独切图,并在 md 对应引用块后插入图片行(已存在则跳过)。

## 注意

- **不要重跑 `legacy/batch_optimize_all_199.py`**。它是 md 最初生成时的批量流水线,
  输出会覆盖已校核的 md,仅留作历史参考。
- 答案 md 为 RapidOCR 自动提取(答案 PDF 内嵌文本层同样是低质 OCR),
  2009–2025 已由 VLM 逐页对照原 PDF(200–400dpi 渲染)校核,OCR 错误
  已就地修正、布局与答案字母以原书为准;个别 PDF 印刷本身模糊处保留
  原文并记入校核报告的存疑清单,使用仍请对照原 PDF 核对。
- **不要重跑 `build_answer_md.py`**:它会用 OCR 原文整体覆盖答案 md,
  冲掉已就地修正的 VLM 校核结果;只有答案 PDF 本身更换时才需要重跑,
  且重跑后需重新逐页校核。
- 2022 答案书为精简版,部分题目只有答案无解析(脚本告警"短内容",属书的
  真实状态);2023/2025 没有"答案速查"板块。
- `2022/2023/2025/2026` 年的 md 处于持续人工修订中,脚本只做增量(图片行),
  不要整体重写。
- 切片图原则:内容必须完整,允许少量切到相邻题的行距,禁止少切。
- 2010 年原卷没有共享题干,其余 17 年共有 52 组。

## 依赖

- Python 3 + `PyMuPDF`(fitz)
- `rapidocr_onnxruntime`(仅 reslice_images.py 遇到纯扫描/乱码年份时需要)
- `Pillow`(reslice_images.py 跨页拼接用)

安装:`pip install PyMuPDF rapidocr_onnxruntime Pillow`

## 详细方法

PDF 转 Markdown 的完整踩坑与方法论见
[199管综真题PDF转Markdown与切分优化实战指南.md](199管综真题PDF转Markdown与切分优化实战指南.md)。
