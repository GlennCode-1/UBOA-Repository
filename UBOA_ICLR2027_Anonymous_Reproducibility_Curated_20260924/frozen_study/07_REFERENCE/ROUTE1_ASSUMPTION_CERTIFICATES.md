# 原始接口与 assumption certificates

## 1. 三类标签

| 标签 | 含义 | 能否进入阈值 |
|---|---|---|
| `STRUCTURAL_ASSUMPTION` | 对 conditional law class 的声明，例如未来创新独立、真实 transition 系数属于给定集合、support/moment envelope 成立 | 只有声明同时给出有限数值时可继续；它不是数据认证 |
| `ALGEBRAIC_CERTIFICATE` | 在结构前提下，由显式参数纯函数计算出的 `G,M,F,T,E,c,C,V` | 可以 |
| `UNKNOWN/HOLD` | 常数只有训练估计、经验最大值、未核验 fitted object，或缺逐-history bridge | 不可以 |

“有限”“已知”“实际有信息”是三件事：有限常数可能当前未知；已知常数也可能产生不可能拒绝的阈值。

## 2. `certificate_interface.py` 的纯参数算法

模块没有文件、网络、随机数、数据或拟合入口。调用者必须显式传入：

1. `dynamics`：member 数、最大 future time、每个 `t` 的 intercept、有限 lag 矩阵、innovation block diameter、coordinate radius，以及所有所需 `t<=0` 初始值和 absolute envelope。
2. `scope`：逐 term 的 `origin,horizon,target_member,weight`。非均匀权重直接保留；相同 target 或共享 innovation 不合并为“独立样本”。
3. 每个 term 的 baseline/selected mapping。精确 affine 系数写成 `(member,lag,value)`；ridge class 写特征坐标、intercept bound 与 coefficient `l2` radius。
4. `r,alpha,loss`。支持原始 MAE/MSE；没有 truncation 参数。

算法依次：

- 以 finite-lag recursion 计算 elementwise absolute transfer `G_{t,j}`，不构造 shift state contraction；
- 递推 raw-state absolute envelope `M_t`；
- 对每个原始 term 计算 target gain、baseline/selected mapping gain 和 raw-error envelope；
- 对同一 innovation time 的全部 term 先求 `c_j=sum_i w_i u_ij`，最后求 `sum_j c_j^2`；
- 输出 conditional McDiarmid threshold 和仅供比较的 Efron--Stein/Cantelli bound；
- 对 scalar linear dynamics + exact affine maps，可另构造 signed transfer、`A,g,k` 及保留 `m3` 的 exact conditional variance。

二次型实现当前有意限制为 scalar state、未来 scalar innovations 条件独立。数学公式可扩至逐 coordinate 独立的向量模型，但代码不假装已实现联合 member moment tensor。

## 3. 三种可计算性情形

### A. dynamics/moments 真值已知

若 transition、innovation support 或二至四阶条件矩由设计机制/物理机制给定，并对几乎每个 `H` 真正成立，则直接计算是合法的 `ALGEBRAIC_CERTIFICATE`。例：受控装置明确注入 bounded independent shocks；这不是对本项目真实 benchmark 的事实声明。

### B. 真值属于事前结构集合

若只知真实参数 `theta in Theta_H`，但 `Theta_H` 对每个 history 是已知集合，可用 envelope 递推：以 `sup_Theta |A_{t,ell}|`、intercept/support/radius 上界替换参数，再运行同一非负 recursion。对 exact quadratic variance，必须对 `A(theta),g(theta),moments(theta)` 的整个集合取合法上界；把各参数边界分别代入一个非单调公式并不自动有效。

这一情形认证的是“若真实 law 属于预先声明集合，则控制成立”。它不证明 law 确实属于该集合。

### C. 只从 training 估计

若真实 AR/seasonal dynamics、support、moments 或 contraction 只用 training estimate 代替，则 `H`-conditional a.s. 结论没有闭合。普通高概率 parameter interval 只给 joint/marginal coverage，不能自动变成每个 realized `H` 上都正确的 envelope。除非另有逐-history valid bridge，状态为 `HOLD_TRAINING_ESTIMATE_NOT_A_LOCAL_CERTIFICATE`。

预测器系数与 dynamics 参数要区分。实际 frozen predictor coefficient 本身是 `H`-measurable；若合法读取，它可以作为 mapping 参数直接进入定理。当前任务不读取任何实物。若只使用 ridge class，实际映射必须由算法设计保证逐 history 落在该 class；“使用了 ridge penalty”本身不等于已知 coefficient radius。

## 4. 明确 mapping 证书

### Finite-lookback affine

`f_o=a+sum_(k,q) beta_(k,q)Y_(o-k,q)`。

- coordinate Lipschitz：`ell_(k,q)=|beta_(k,q)|`；
- innovation gain：`F_j=sum |beta_(k,q)| rowsum(G_(o-k,j),q)`；
- range：`|f_o|<=|a|+sum |beta_(k,q)|M_(o-k,q)`。

所有 `o-k<=0` 坐标必须在初始 history 中；它们的 future innovation gain 为零，但 range 不能省略。

### Frozen ridge coefficient class

给定特征向量 `x_o=(Y_(o-k,q))_(k,q)`，class 为 `|a|<=a_bar, ||beta||_2<=R`。统一公式：

`|f_o|<=a_bar+R||M_features||_2`,

`F_j<=R||(rowsum G_(o-k,j),q)_(k,q)||_2`。

这覆盖 class 内任意随机但 `H`-measurable selected coefficient；没有在未来状态上重拟合。若需更紧证书，可输入实际 frozen affine coefficients，而不是扩大 class。

### Seasonal naive，含 `horizon>seasonality`

对 period `s` 与 positive horizon `h`，定义

`q=s ceil(h/s)`, `f_(o,h)=Y_(o+h-q,m)`。

因此 affine lag 是 `q-h in {0,...,s-1}`，coefficient 为 1。例：`s=24,h=36` 时预测为 `Y_(o-12,m)`；`h=48` 时为 `Y_(o,m)`。这是“使用最近一个已观测到的同季相值”的明确版本。若项目实现采用另一递归定义，必须另写 mapping，不能沿用此证书名称。

## 5. 攻击检查

1. **共享未来冲击。** 两个完全重复 target term、权重 `1/4,3/4`、`r=0`、零预测、MAE、innovation diameter 2 时，各加权影响为 `1` 与 `3`。正确做法给 `c_1^2=(1+3)^2=16`；错误地当独立 term 平方给 `1^2+3^2=10`，会低估阈值。检查器验证前者。
2. **初始状态。** origin 0 的 lookback/seasonal lag 可引用负时刻；缺任何所需 initial absolute envelope 即报错，不以零填充。
3. **nuisance envelope。** observed maximum、training residual maximum 或 point estimate 都不是未来 support bound。没有结构来源则 HOLD。
4. **固定 horizon scope。** `max_time` 必须覆盖每个 `o_i+h_i`，且每个原始 term 显式进入 `scope`；接口不提供自动挑 horizon 功能。
5. **方法选择历史。** actual map 若在 future block 内更新，便不再是 `H`-measurable frozen mapping，证书失效。
6. **denominator。** denominator 必须在 `H` 中正且有限；若随 missing future outcomes 改变，需把其 sensitivity 纳入 path functional，当前公式不覆盖。

## 6. 代码与证明的对应边界

`certificate_interface.py` 是可复核的代数实现，不是形式化证明器，也不认证输入真值。`check_certificates.py` 只做有限确定性恒等式/边界检查：无随机路径、无 Monte Carlo、无数据读取、无模型训练。通过检查意味着实现与列出的公式一致，不意味着真实应用的 structural assumptions 成立。
