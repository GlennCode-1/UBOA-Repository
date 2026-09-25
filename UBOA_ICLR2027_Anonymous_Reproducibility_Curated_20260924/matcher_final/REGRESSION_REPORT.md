# FINAL_MATCHER regression report

## 结论

`matcher.py` 是基于 exposed V2 revised checker 的 FINAL_MATCHER candidate。源码只增加两个 fail-closed guard：M2 要求非空 string provenance；M4 的 `theorem` / `asymptotic_theorem` 要求非空 premises。M1--M8 的分支结构、科学坐标、conclusion-type checks、validity-coordinate matching、论文、冻结 synthetic results 与历史证据均未修改。

候选状态：`FINAL_MATCHER_CANDIDATE_WITH_ONE_DECLARED_LEGACY_FIXTURE_INCOMPATIBILITY`。

## 定向回归

`python3 -m unittest -v test_final_matcher.py`：9/9 test methods PASS。

| Scope | Cases | Result |
|---|---:|---|
| 新 M2 gap | F08_C4 | reject: `OBSERVED_COPY_PROVENANCE_MISSING` |
| 新 M4 gap | F28_C4 | reject: `THEOREM_PREMISES_EMPTY` |
| M2/M4 positive controls | F08_C1, F28_C1 | ESTABLISHED |
| 已修 conclusion type | F05_C4, F24_C3 | reject: `CONCLUSION_TYPE_MISMATCH` |
| 已修 validity coordinates | F25_C3, F29_C3 | reject: coordinate-specific validity mismatch |
| Revised development regressions | 18 | 18/18 unchanged PASS |
| Frozen legacy gold except obsolete M2 fixture | 22 | 22/22 unchanged PASS |

## V2 post-exposure regression

V2 已经暴露，只作为 development regression；这里不称 held-out、independent 或新 benchmark。

- cases: 160
- ambiguous labels excluded from error comparison: 3
- exceptions: 0
- false accepts: 0（revised baseline 为 2；仅 F08_C4、F28_C4 被本补丁关闭）
- permissible-but-not-licensed: 10，全部是已知 M5 `declared_coarsenings` 表示不匹配；本轮按“只修两个 genuine gaps”要求未改该分支

## Legacy compatibility disclosure

原封不动运行 frozen `reference_matcher/test_matcher.py` 时，6 个 test methods 中 5 个 PASS、1 个 FAIL。唯一失败 subcase 是 `observed_decision_copy`：旧 fixture 的 metadata 没有 provenance，却把预期写成 `ESTABLISHED`。这与本轮强制 M2 provenance 的要求直接冲突，不能同时满足。

- frozen gold cases: 22/23 保持原结果
- intentional reclassification: 1/23，`observed_decision_copy` -> `UNSUPPORTED_REQUEST`
- frozen exact/trace/schema test methods: PASS
- `reference_matcher/test_regressions.py`: PASS，18/18 records
- 在同一旧 M2 fixture 的测试副本中加入规范 provenance string 后，positive control 为 `M2_OBSERVED_COPY`

旧 fixture、旧 hash 和旧 expected record 均未修改。这个差异是输入契约收紧，不是被隐藏的 legacy pass。

## Execution boundaries

- RNG calls: 0
- stochastic simulations: 0
- model training/fitting: 0
- new OOS access: 0
- manuscript edits: 0
- frozen result/history edits: 0
