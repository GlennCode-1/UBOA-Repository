# UBOA Route-B Synthetic Confirmatory Preregistration

状态：**SCIENTIFIC PROTOCOL FROZEN; NO STOCHASTIC STUDY EXECUTED**

本包是 real applicability screen 得到零合格 prospective real candidate 后的预注册 synthetic P-class confirmatory study。它不重新搜索真实数据，也不复用 Route A 的 432,000 条 synthetic records。

核心原则：

1. Route 1 的有限样本 `a.s. given H` 保证来自 `07_REFERENCE/ROUTE1_THEOREM_AND_PROOF.md`，不是由 Monte Carlo 证明。
2. 本 study 只检验实现是否与冻结 theorem/certificate 一致、fresh conditional operating behavior 是否出现 implementation red flag，以及何时 certificate informative/vacuous。
3. 所有随机路径必须在 scientific protocol 与实现代码双重冻结后一次性生成。
4. 任何 FAIL/HOLD、低 power、零 promotion 或 assumption-screen failure 都必须保留。
5. 不允许用本 study 的结果修改 cell grid、loss、horizon、alpha、threshold ladder、seed 或 certificate 后再把重跑称为 confirmatory。

执行顺序只有两个宏阶段：
- **F1 pre-execution audit + code dry-run**：不得生成任何 DGP 路径。
- **F2 locked execution**：审计通过并冻结代码哈希后，运行一次完整 study。

入口：
- `01_FREEZE/FROZEN_PROTOCOL.md`
- `02_DESIGN/CELL_TABLE_ALL.tsv`
- `03_ANALYSIS/ANALYSIS_AND_DECISION_RULES.md`
- `04_IMPLEMENTATION/IMPLEMENTATION_CONTRACT.md`
- `06_PROMPTS/`
