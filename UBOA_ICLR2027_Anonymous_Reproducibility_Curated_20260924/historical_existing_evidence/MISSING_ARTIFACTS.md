# Missing and partial artifacts

所有条目均在固定 allowlist 与已定位项目材料内核查。没有扩大数据搜索，也没有生成替代物。

| 关切 | 状态 | 未找到/未保存 | 当前可用证据不能替代的原因 |
|---|---|---|---|
| C02 future paths | `MISSING` | 80 histories 各 4,096 条 future innovation paths | aggregate counts/digests 不能恢复 individual paths。 |
| C02 path decisions | `MISSING` | 每条 future path 的 potential-node decisions、terminal state 与 invariant record | 原 aggregate `0 violations` 不是本轮 independent replay。 |
| C02 binding execution trail | `PARTIAL` | 将每条 path/decision 与 batch digests 绑定的完整 execution transcript | 文件 hash 固定字节，不证明唯一历史运行或没有隐蔽执行。 |
| C03 20% rule denominator | `MISSING` | 精确定义、numerator、denominator、threshold comparison | 派生 masks 支持多种不等价分母，不能事后选择。 |
| C03 enforcement record | `MISSING` | execution-side missingness mask 与 eligibility log | 本轮 masks 是 `DERIVED_FROM_EXISTING_PREFIX`，不是历史日志。 |
| C03 all-candidate per-origin losses | `MISSING` | 六任务每个候选的逐-origin validation losses | 当前仅有所有候选 aggregate scores 和 selected/comparator arrays。 |
| C03 corrected preprocessing outputs | `MISSING_NOT_GENERATED` | calendar-hour Household series、strictly causal fill 后的 fit/selection/loss | 需要新的 preprocessing 与拟合；本轮禁止执行。 |
| C07 raw Brownian increments | `MISSING` | 200,000 条参考 path 的原 increments/paths | sorted terminal reference array 不可逆恢复它们。 |
| C07 generator execution transcript | `MISSING` | 原 stdout/stderr、环境快照、运行时间及 source-to-array binding log | generator source、声明配置和最终 array 均存在，但不证明实际唯一执行链。 |
| C07 unreached nodes | `NOT_CREATED_BY_DESIGN_OR_NOT_RETAINED` | 历史 fixed-sequence 未到达节点的观察统计量 | 本轮不补跑；16 个 exported records 仅覆盖 reached nodes。 |

第三方 raw dataset archives 未放入匿名 ZIP。这是有意的分发边界，不被描述为本轮搜索缺失；manifest 保存其仓库相对路径与 SHA256，派生 masks/时间表记录具体变换。

最终状态维持：`C02=PARTIAL`、`C03=PARTIAL`、`C07=PARTIAL`。

