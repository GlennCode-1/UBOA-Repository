# 非空洞性：预声明后的解析核查

两组参数在 `ATTEMPT_LOG.jsonl` 中先于算术声明；以下没有按结果改变 loss、scope、tail bound 或参数，也不对应任何真实任务。它们只说明证书边界性质，不称为 synthetic validation 或实验性 power estimate。

## 1. 有信息的有限参数组

预声明 `R1C-PRE-001`：`alpha=1/20,r=0`，`Y_t=(1/2)Y_{t-1}+epsilon_t`，`Y_t=0` 对所有 `t<=0`，innovations 条件独立且各为 Rademacher `+/-1`。取 origins `0,...,n-1`、horizon 1、equal weight `1/n`、baseline 0、selected forecast `(1/2)Y_o`、raw MSE。

令 `q=1/4`。由于 selected error 恰为 `epsilon_t`，

`W=(1/n)sum_(t=1)^n(Y_t^2-epsilon_t^2)`。

其条件均值精确为

`mu_n=(1/3)[1-4(1-q^n)/(3n)]`。

写 `Y_t=sum_(j<=t)2^{-(t-j)}epsilon_j`。二次型中 `g=0`；Rademacher 的 `m4-s2^2=0`，所以 diagonal randomness 消失。对 `j<k`，

`A_jk=(1/n)2^{-(k-j)}[1-q^(n-k+1)]/(1-q)`，

`V_n=4sum_(j<k)A_jk^2`。

这正是接口的 paired quadratic variance；所有重叠 future shocks 保留。

### 明确的解析样本长度区域

对 `n>=4`，

`mu_n >= 1/3-4/(9n) >= 2/9`。

又因几何和上界，

`V_n <= 64/(27n)`，

故 `alpha=1/20` 的 Cantelli threshold 满足

`b_n=sqrt(19V_n) <= 8sqrt[19/(27n)]`。

当 `n>=913` 时右侧严格小于 `2/9`，因此 `mu_n>b_n`。这给出一个 finite、解析、非退化的有信息区域，而不只是“某处有正概率拒绝”。

对预声明的 `n=4096`，确定性计算为：

| quantity | value |
|---|---:|
| `mu_4096` | `0.333224826388889` |
| exact `V_4096` | `0.000578430552541488` |
| Cantelli threshold | `0.104834061727514` |
| `mu-threshold` | `0.228390764661375` |

此外，对 lower tail 再用 Cantelli，

`P(W>b|H) >= (mu-b)^2/[V+(mu-b)^2] = 0.989032573257503`。

这是该完全明示法则下的解析 rejection-probability lower bound，不是模拟结果，也不是对任何 benchmark 的性能主张。

## 2. 合法但完全无信息的参数组

预声明 `R1C-PRE-002`：`alpha=1/20,r=1/20`，`Y_t=(19/20)Y_{t-1}+epsilon_t`，初始历史全零，`epsilon_t in [-1,1]`，32 个 stride-one origins、horizon 12、equal weights，baseline 为 period-24 seasonal naive，selected mapping 在 24-lag frozen affine class `|intercept|<=4,||beta||_2<=8`，raw MSE。

seasonal rule 按本轮明确接口是 `Y_(o-12)`。该范围内的 uniform bounded-innovation whole-functional certificate 给：

| quantity | value |
|---|---:|
| `sum_j c_j^2` | `7,494,971,951.72487` |
| McDiarmid threshold | `105,955.012541088` |
| deterministic upper bound on `W` | `389.492144968127` |

最后一行使用 `W=sum w[(1-r)B-S] <=sum w(1-r)(E_i^b)^2`。因此 threshold 严格超过整个可达域上 `W` 的上界，拒绝事件为空。证书在数学上有效、常数有限且已知，但 **INFORMATIVENESS=FAIL**。

松弛来源并非单一 horizon 被当作独立样本，而是：`a=0.95` 的长记忆、12-step target、重叠 stride-one origins、宽 ridge class 和 raw square loss 的全域 error envelope 共同进入同一 innovation 的 aggregated sensitivity。

## 3. 结论

- 该法则类不是空的：`n>=913` 的明示 Rademacher AR(1) 区域有 threshold below mean，并在 `n=4096` 有解析 rejection-probability lower bound。
- 有限/可计算不保证有用：第二组甚至不可能拒绝。
- 两例都没有说明真实 UBOA benchmark 满足 dynamics、support 或 moment assumptions；真实应用仍需独立 certificate source。
