# FINAL_MATCHER native input contract

本文件固定 matcher 的原生 JSON 表示。它不扩展 M1--M8，不验证外部事实，也不把注释本身当作 provenance 鉴真或 theorem premise 的证明。

## Conditioning coarsenings

- `evidence.metadata.declared_coarsenings` 的规范形式是 JSON string array。
- 当 `conditional_bound` 的 source conditioning 与 request conditioning 不同时，数组必须包含 **request 的 `validity.conditioning` 裸标识符**，按字符串精确匹配。例如 request 为 `"selected_label"` 时，规范条目是 `"selected_label"`。
- `"full_history to selected_label"` 等人类可读路径不是原生条目，matcher 不解析路径文本、偏序或别名。
- 同时必须有 `same_joint_law=true`、`same_error_event=true`、`integrable_indicator=true`、`bound_constant_or_coarser_measurable=true`。这些值必须是 JSON boolean `true`。
- source 与 target 相同时不发生 coarsening；该分支按相同 conditioning 的 theorem instantiation 检查。

## Observed-record provenance

- M2 的 `evidence.kind` 和 `evidence.conclusion_type` 均为 `"observed_decision"`。
- `evidence.metadata.provenance` 必须是去除首尾空白后仍非空的 JSON string。它可以是稳定记录 ID、相对 artifact locator 或审计记录标识。
- 缺键、非字符串、空字符串或纯空白字符串均返回 `OBSERVED_COPY_PROVENANCE_MISSING`。
- matcher 只检查此 locator 已明确声明；它不打开 locator，也不鉴真其内容。
- `reached_nodes_only`、`method_retained`、`boundary_retained` 仍必须分别为 JSON boolean `true`。

## Conclusion types

下列值按精确字符串匹配：

| Evidence kind | Evidence conclusion | Request conclusion |
|---|---|---|
| `structural_identity` | `structural_identity` | `structural_identity` 或在有限正 denominator 下为 `relative_ratio` |
| `observed_decision` | `observed_decision` | `observed_decision` |
| `finite_design_empirical` | `empirical_rate` | `empirical_rate` |
| `theorem`, `asymptotic_theorem` | `probability_bound` | `probability_bound` |
| `conditional_bound` | `probability_bound` | `probability_bound` |
| `local_validity_family` | `local_node_bounds` | `fixed_sequence_error_bound` |

不存在大小写归一化、别名或隐式转换。已有 conclusion-type guards 未修改。

## Theorem premises

- 对 `theorem` 与 `asymptotic_theorem`，`evidence.premises` 必须是至少含一个字符串的非空 JSON array。
- `evidence.verified_assumptions` 必须是 string array，且每个 declared premise 必须以精确字符串出现在其中。
- 空 premises 返回 `THEOREM_PREMISES_EMPTY`；缺少某一验证项返回 `UNVERIFIED_ASSUMPTION:<premise>`。
- matcher 不判断 premise 是否真实，只检查声明与外部验证注释的闭合性。

## Coordinate matching

除 M5 明确忽略 conditioning 后再检查合法 coarsening 外，`error_event`、`conditioning`、`law_quantifier`、`coverage_unit`、`support_mode`、`sample_regime`、`selection_mechanism` 均按 JSON 值精确匹配。M1 的全部 validity-coordinate matching 和既有 conclusion-type checking 均保持不变。
