# Work 分批审查提示词（直接复制）

以下模板配合本仓库的 `audit/REVIEW_PROTOCOL.md` 使用。Work 可以读取 GitHub 仓库并保存结果，**但仍需要逐步验收，不默认具备无限时长或自动跨会话续跑能力**。请先把 GitHub 连接到 Work，并确认仓库有读取、提交权限。

## 1. 首次启动：先建立可靠起点

```text
请在 Work 中继续我的 GitHub 仓库 EvilMetroid/199GuanZong 的 990 道管综客观题独立审查。

先读取以下文件：
- audit/README.md
- audit/REVIEW_PROTOCOL.md
- audit/PROGRESS.md
- audit/WORK_PROMPTS.md
- audit/issues/ISSUE_REGISTER.md
- audit/ledger/ 下对应年度的逐题台账
- audit/reports/ 下历史报告（仅作线索，不能直接继承其已验证结论）

严格执行四门验收：逐张打开 PNG 对照 Markdown；不参考原解析独立推导；对照答案和选项唯一性；逐步审查原解析。对每题形成可复算记录，禁止只写“同答案”“穷举证实”“逻辑通顺”。
本次先从 2025 年第 01—05 题开始，若时间不够就如实只完成部分，不得假称完成。
仅写 audit/ 下的 reviews、ledger、issues、PROGRESS，先不要改原题和解析。每完成一个小批次便保存到 GitHub。最后报告每题结果、文件链接、commit SHA、下一次建议起点。
```

## 2. 日常续审：无需重复长背景

```text
继续 EvilMetroid/199GuanZong 的 990 题审查。以仓库 audit/REVIEW_PROTOCOL.md 为唯一验收标准，读取 audit/PROGRESS.md、年度 ledger、问题清单与已有 reviews，查找尚未完成的题号。
本次处理【YYYY 年第 NN—MM 题】（默认 5—10 题，若碰到共用题干连带处理）。对每题：实际检查 PNG 与 Markdown；独立求解及验证 A—E；核对原答案；逐步审计原解析；标注每个实际发现的问题并给修正建议。不要继承历史“已证明”状态，不要仅抄旧解析。尽量逐题给足数学证明、逻辑反例或选项对比。
批次证据提交到 audit/reviews/YYYY-NN-MM.md，更新 audit/ledger/YYYY.md、audit/issues/ISSUE_REGISTER.md（如有问题）及 audit/PROGRESS.md。不得改题库原文。完成后交付 GitHub 提交链接和可复算的本批统计，明确下一批范围。
```

## 3. 严重问题专项复核

```text
请审查仓库 EvilMetroid/199GuanZong 的 audit/issues/ISSUE_REGISTER.md 中【问题 ID 或某一年全部 open 项】。逐条打开原卷 PNG、试卷 Markdown、解析 Markdown，重新独立证明，区分原 PNG 异常与 Markdown 转录错误。给出支持/反例、源文件定位、具体修正文本、证据等级及是否仍有争议。只更新审查目录；任何源文件改动需先单独提出 PR 草案并由我确认。逐条更新 issue 状态，不能笼统打包。
```

## 4. 批次质量复检（适用于另一次 Work）

```text
请独立抽审 EvilMetroid/199GuanZong 中 audit/reviews/ 的最新一个批次。禁止直接把已记录结论视作正确；重新推理、打开图片、核查证明的隐含前提/反例/选项唯一性。对未满足 audit/REVIEW_PROTOCOL.md 的题目撤销 accepted，写明证据缺口，更新 ledger 和 PROGRESS，并为新发现缺陷写入问题清单。不要覆盖未核查题目的状态。
```

## 5. 全量最终验收（必须完成全部批次后才使用）

```text
审计 EvilMetroid/199GuanZong 的 audit/ 下全部结果，逐题统计 18×55=990 道；检验所有 accepted 的四门证据及源文件版本，检查题号缺漏、重复、问题 ID 闭环、题图共享题干、答案不唯一及保留争议。输出终版 Markdown 报告，报告应逐项罗列每个具体问题、证据、修正建议及处理结果。若任何题缺证，必须列出题号和缺口，不得宣称完成全部 990 题。
```

## 分批节奏建议

- 默认 5 道/批；简单题可到 10 道，复杂题组降低批量。
- Work 最好按 **一个批次 → 保存 GitHub → 核对 → 下一批** 循环，避免单次运行过长、上下文漂移和记录丢失。
- 先重点攻克 2025（历史源图/解析争议较多）、2022（精简解析）、2026（人工推演解析），随后按年度补齐；改变顺序时以 ledger 未完成状态为准。
- 18 年 × 55 道 = 990 道，每批 5 题约 198 个批次。**这是审查规模估算，不是承诺每批都能一次自动完成**。
