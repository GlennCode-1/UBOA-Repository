# UBOA Existing-Evidence Export

状态：`PARTIAL_EXISTING_EVIDENCE_EXPORT`。

本目录只整理此前已经定位的 C02/C03/C07 证据。它不包含新的统计实验、随机样本、训练、拟合、confirmatory rerun 或新 prospective OOS 访问。

## 目录

- `PUBLIC_EVIDENCE/C07_BROWNIAN_REFERENCE/`：历史 reference generator source、声明配置和 200,000 点 sorted reference array。generator 仅作为源码导出，没有执行。
- `PUBLIC_EVIDENCE/C03_COHORT_PROTOCOL/`：计划 protocol、Stage36 实际 preprocessing/selection source 与 Stage37 guarded runner source。
- `PUBLIC_EVIDENCE/C03_VALIDATION/`：六任务 aggregate candidate score registry 与 selected/comparator validation-loss arrays。
- `PUBLIC_EVIDENCE/C07_REACHED_STATISTICS/`：Stage37 四任务和 Stage32 Weather/ETTm2 的 paired-loss evidence 与完整 16 个 reached-node records。
- `PUBLIC_EVIDENCE/DERIVED_PREFIX_DIAGNOSTICS/`：从既有前 80% prefix 确定性生成的 missingness masks、摘要与 Household 60-row timestamp groups。它们明确不是历史 execution logs。
- `PUBLIC_EVIDENCE/TOOLS/`：本次确定性导出/派生工具；不含 RNG、模型或 confirmatory 执行入口。

`PUBLIC_EVIDENCE_MANIFEST.json` 为每个文件记录 source role、仓库相对路径、source/public SHA256、历史原件或新派生身份及变换。`EXPORT_VERIFICATION.json` 位于 ZIP 旁边，对 ZIP 和导出目录作最终验证。

## 边界

- source/public hash 相同只固定文件字节，不证明该文件是唯一历史运行路径。
- 16 个 reached-node records 不包含未到达节点。
- selected/comparator validation losses 不是 all-candidate per-origin losses。
- prefix missingness masks 不能替代缺失的原 20% denominator/enforcement record。
- 本包不分发第三方 raw archives，也不包含 `PRIVATE_EVIDENCE/`。

