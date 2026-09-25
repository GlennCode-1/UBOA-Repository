# Route 1：finite-lookback 原始损失的条件证书

状态：**已证明的条件定理**。它认证下述明确法则类，不认证任何未读取的真实 benchmark。全部结论针对一个固定、有限评估窗口；没有 anytime 声明。

## 1. 对象、条件核与原始 scope

在概率空间 `(Omega,F,P)` 上令 `H subset F` 包含评估前所有会影响选择、拟合、方法选择、超参数、scope、权重、阈值和证书参数的信息。未来创新空间取 standard Borel，故存在 regular conditional kernel

`K_omega(A)=P(A|H)(omega)`。

以下陈述均对一个共同的 `P`-a.s. 集合上的每个 frozen history `omega` 成立。给定 `H` 后：

1. `epsilon_1,...,epsilon_T` 是相互独立的向量创新块；渐进 filtration 为 `F_j=H vee sigma(epsilon_1,...,epsilon_j)`。
2. `Y_t in R^m` 满足有限 lag 仿射递推

   `Y_t=b_t+sum_{ell in L_t} A_{t,ell}Y_{t-ell}+epsilon_t`, `t=1,...,T`。

   `b_t,A_{t,ell},L_t` 均为 `H`-measurable；递推或预测所需的全部 `Y_t,t<=0` 已在 `H` 中明确给出。这里不把 shift-augmented 状态误称为欧氏收缩。
3. 原始 term 集合 `I` 有限。term `i` 保留其 origin `o_i`、horizon `h_i`、target member `m_i`、baseline `f_i^b`、selected mapping `f_i^s` 和非负权重。若原协议给 raw weights `a_i` 与 denominator `D_H>0`，定义 `w_i=a_i/D_H`；`D_H` 必须是 `H`-measurable 且不依赖未来实现。权重不必均匀或和为一，只需有限。
4. `f_i^c`, `c in {b,s}`，是联合可测、给定 `H` 后冻结的 finite-lookback mapping；其随机系数和产生它的完整选择/拟合历史直接属于 `H`。证明不把随机 fitted mapping 换成一个与实际选择无关的固定规则。
5. 对 `loss in {raw MAE, raw MSE}`，

   `B_i=loss(Y_{o_i+h_i,m_i},f_i^b)`, `S_i=loss(Y_{o_i+h_i,m_i},f_i^s)`,

   `W_r=sum_i w_i[(1-r)B_i-S_i]`, `mu_r^0=E[W_r|H]`,

   `T_r={mu_r^0<=0} in H`。未知 `mu_r^0` 不进入任何 rejection threshold。

## 2. Primitive transfer 与映射证书

对矩阵逐元素取绝对值，定义从 innovation block `j` 到 state `t` 的非负 transfer：

`G_{t,j}=0` 若 `j>t`，`G_{j,j}=I`，且对 `j<t`，

`G_{t,j}=sum_{ell in L_t:t-ell>=j}|A_{t,ell}|G_{t-ell,j}`。

若替换 `epsilon_j` 时两可能值的 `l_infinity` 距离至多 `d_j<infinity`，则

`|Delta Y_{t,q}| <= d_j sum_p G_{t,j}[q,p]`。

这是按有限 lag 递推直接证明的 innovation transfer，不需要增广状态欧氏收缩。

对 frozen affine mapping

`f_i^c=a_i^c+sum_{(k,q) in J_i^c} beta_{i,k,q}^c Y_{o_i-k,q}`

定义

`F_{i,j}^c=sum_{(k,q)} |beta_{i,k,q}^c| sum_p G_{o_i-k,j}[q,p]`,

其中 `o_i-k<=0` 的项对未来创新的贡献为零；target gain 为

`T_{i,j}=sum_p G_{o_i+h_i,j}[m_i,p]`。

若 actual selected map 只知属于冻结 ridge coefficient class `|a|<=a_bar, ||beta||_2<=R`，则以 Cauchy--Schwarz 取统一证书

`F_{i,j}^s <= R{sum_(k,q)[sum_p G_{o_i-k,j}[q,p]]^2}^{1/2}`。

这不执行 ridge 拟合。它覆盖任意 `H`-measurable 方法选择，只要实际已选系数逐 history 确实在该 class 内。

对 raw MSE，另需真实可达域的绝对 state envelope `M_{t,q}`。给定初始 `M_{t,q},t<=0` 与 innovation coordinate radius `q_{t,q}`，递推

`M_{t,q}=|b_{t,q}|+sum_(ell,p)|A_{t,ell}[q,p]|M_{t-ell,p}+q_{t,q}`。

令

`R_i^c=|a_i^c|+sum_(k,q)|beta_{i,k,q}^c|M_{o_i-k,q}`

（ridge class 用 `a_bar+R sqrt(sum M^2)`），并令 `E_i^c=M_{o_i+h_i,m_i}+R_i^c`。这些是 raw error 的路径上界；未截断 loss。

## 3. 定理 A：有界创新的 whole-functional local control

对每个 `j` 定义

`u_ij^MAE=d_j{(2-r)T_ij+(1-r)F_ij^b+F_ij^s}`，

`u_ij^MSE=2d_j{(1-r)E_i^b(T_ij+F_ij^b)+E_i^s(T_ij+F_ij^s)}`，

`c_j=sum_i w_i u_ij`，`C=sum_j c_j^2`。

若上述量有限，则检验

`phi_r=1{W_r>b_r}`, `b_r=sqrt[(C/2)log(1/alpha)]`

满足

`1_T_r E[phi_r|H] <= alpha 1_T_r` a.s.

若 `C=0`，取 `b_r=0` 并仍使用严格规则 `W_r>0`。

### 证明

固定一个允许的 history。只替换 innovation block `epsilon_j`。direct transfer 给 target 与两个 forecast 的改变量上界。`| |e|-|e'| |<=|e-e'|` 逐项给出 MAE 的 `u_ij`。MSE 中 `|e^2-e'^2|<=2E|e-e'|`，其中 `E_i^c` 同时覆盖替换前后可达路径，给出 MSE 的 `u_ij`。对共享同一 innovation 的所有 origin/horizon/member term 先按权重求和，得到整个路径函数 `W_r` 的 block bounded difference `c_j`；不能先平方单项再相加。

在条件 product kernel `K_omega` 下应用有限乘积 bounded-difference inequality：

`K_omega(W_r-E_K W_r>=x)<=exp(-2x^2/C)`。

在 `T_r` 上 `mu_r^0<=0`，故 `{W_r>b_r} subset {W_r-mu_r^0>b_r}`，右侧概率至多 `alpha`。若 `C=0`，`W_r` 在 conditional support 上为常数并等于 `mu_r^0<=0`，严格事件 `{W_r>0}` 为空。因为以上对共同 full-measure history 集逐点成立，所得不等式是 a.s. given `H`，不是对 histories 的高概率陈述。证毕。

## 4. 定理 B：raw paired MSE 的精确 quadratic variance

这是一个更窄但允许无界创新的增强。给定 `H` 后，假设 dynamics 与两 forecast 均为精确线性/仿射，且把所有未来 innovation **scalar coordinates** 排成 `e=(e_1,...,e_N)`；这些 coordinates 条件独立、条件均值为零，且已知有限

`s_j^2=E[e_j^2|H]`, `m_3j=E[e_j^3|H]`, `m_4j=E[e_j^4|H]`。

direct signed transfer 把每个 error 写成

`error_i^c=d_i^c+(v_i^c)'e`。

于是，不丢弃任何 overlap term，

`W_r=e'Ae+2g'e+k`，其中

`A=sum_i w_i[(1-r)v_i^b(v_i^b)'-v_i^s(v_i^s)']`,

`g=sum_i w_i[(1-r)d_i^b v_i^b-d_i^s v_i^s]`,

`k=sum_i w_i[(1-r)(d_i^b)^2-(d_i^s)^2]`。

`A` 对称，且

`E[W_r|H]=k+sum_j A_jj s_j^2`，

`V_r=Var(W_r|H)` 等于

`sum_j A_jj^2(m_4j-s_j^4) + 4sum_{j<k}A_jk^2s_j^2s_k^2 + 4sum_j g_j^2s_j^2 + 4sum_j A_jj g_j m_3j`。

最后一项不能在未声明 symmetry/Gaussian 时删除。公式由展开中心化二次项、线性项，并用 coordinate independence 与零均值消去含未配对 coordinate 的 monomial 得到。

Cantelli 检验

`phi_r^Q=1{W_r>sqrt[V_r(1-alpha)/alpha]}`

同样满足 `1_T_r E[phi_r^Q|H]<=alpha 1_T_r` a.s.；`V_r=0` 时阈值为零并严格拒绝。这里只要求 raw MSE 的四阶矩有限，不把它截断成另一个对象。若同一时刻的成员创新相关，则上述 scalar-coordinate identity 不适用；应回到 block-level 定理 A，或另行提供完整联合矩张量。

## 5. 固定序列继承

设预先固定有限节点 `q=1,...,Q`，每个节点有 `H`-measurable truth event `T_q` 和上述 full-history conditional-level 检验 `phi_q`。令 `q*(H)=min{q:T_q holds}`；若不存在 true null，familywise error 为空。固定序列实际只在所有前节点拒绝后到达下一节点，但

`{fixed sequence rejects any true null} subset {phi_q*=1}`。

而

`E[1{phi_q*=1}|H]=sum_q 1{q*=q}E[phi_q|H]<=alpha`。

因此 first-true-null proof 原样继承。这里没有在“已到达 q*”条件下重新检验；到达事件可能依赖同一 future block。该结论仅覆盖预锁定的有限序列，不是 anytime guarantee。

## 6. 适用边界

- frozen fitter 仍允许 genuinely future-state-dependent drift。例如 `Y_t=0.5Y_{t-1}+epsilon_t` 有 `E[Y_{t+1}|F_t]=0.5Y_t`，虽 forecast mapping 在 `H` 后不更新，future conditional drift 仍随未来状态改变。定理对整个 future functional 积分，不把它换成 realized-path predictable mean。
- innovation support、moments、dynamics truth 或 parameter-set envelope 若只由 training 点估计而无逐-history bridge，则常数不可合法代入；定理本身仍成立，应用状态为 HOLD。
- 未声明的初始 lag、未来更新 fitted mapping、改变 horizon/origin scope、或把固定窗口反复查看，均不在本定理内。
