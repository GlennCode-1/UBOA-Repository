# Existing evidence export report

## 结果

`FINAL_EXPORT_STATUS=PASS_PARTIAL_EXISTING_EVIDENCE_EXPORT`

本轮完成了一个固定 allowlist 的匿名证据导出。25 份历史原件同时保存于 `PRIVATE_EVIDENCE/` 与 `PUBLIC_EVIDENCE/`；身份 marker 扫描为零，因此 PUBLIC 原件没有内容变换，source、private、public 三方 SHA256 相同。另生成 17 个 Boolean missingness masks、1 个 mask index、1 个 missingness summary、1 个 Household timestamp-group TSV、1 个 derivation note 和 1 个导出工具，共 22 份派生/工具文件。派生文件统一标记为 `DERIVED_FROM_EXISTING_PREFIX` 或 `NEW_EXPORT_TOOL`。

匿名 `EXISTING_EVIDENCE_EXPORT.zip` 只包含 PUBLIC evidence、公开 manifest、说明、报告、缺失清单与 provenance log；不包含 `PRIVATE_EVIDENCE/`、个人绝对路径、电脑用户名、第三方 raw archives 或本机临时路径。

## C02

状态：`PARTIAL`。

本次没有重复打包已经存在于主 reproducibility supplement 的 F1/F2/H/results，而是保留其缺口边界：原 future innovations、individual terminal decisions 与 per-path invariant records 未找到，也没有生成。aggregate `0 pathwise violations` 仍只能归属于原 runtime aggregate record，不是新的 independent pathwise replay。

## C03

状态：`PARTIAL_WITH_EXPORTED_EXISTING_RECORDS`。

已导出：

- Stage36 master protocol 与实际 `run_workstream_e.py`；
- Stage37 `guarded_oos_runner.py`；
- 六任务 selection registry，含所有候选 aggregate scores；
- 六个 selected/comparator validation-loss NPZ；
- 17 个由既有 prefix 派生的 task/member missingness masks、leading-missing 信息；
- 27,670 行 Household consecutive-60-row timestamp groups。

独立验证确认六任务 validation NPZ 均与 registry 的 selected/comparator means 对齐；最小前两名 aggregate score gap 为 `0.018147357786163942`，`1e-12` 以内为 0/6。该结论只适用于已保存 aggregate scores。

六个已检查 target prefixes 的 leading missing 均为 0。Household 首个执行 group 为 `2006-12-16 17:24:00` 至 `18:23:00`；27,670/27,670 个 consecutive-60-row groups 跨 calendar-hour boundary。

原 20% missing-target execution denominator、mask、阈值比较和 eligibility log 仍未找到。派生 masks 展示可审计的原始前缀 missingness，但不能追认为历史 enforcement record。

## C07

状态：`PARTIAL_WITH_EXPORTED_EXISTING_RECORDS`。

已导出：

- generator source SHA256 `97813e2790ad9b34a840fbe13394b620cad142c26453ed19bead1cf48b7c70f5`；
- 声明 contract：200,000 paths、grid 2,048、seed `2027090801`、chunk size 2,000、linear empirical quantile；
- sorted reference array SHA256 `bbb43c2d578f85aef64b30f873812143409a9f3c341ceaf3ce4f42d97ff5f5cf`；
- 200,000 点 array 的 linear q95 `5.298829753159216`；
- Stage37 四任务 12 个 reached nodes；
- Stage32 Weather/ETTm2 4 个 reached nodes。

从导出的 paired-loss records 重算 16/16 self-normalized statistics，与保存值精确相同。0/16 落入 `[5.298829753159216, 5.322679900530264)`；仅替换 cutoff 的 decision change 为 0/16。边界按历史 `statistic >= cutoff` 计算，没有与 strict certificate boundary 混用。

原 Brownian increments、generator execution transcript 和唯一历史运行路径证明仍缺失。source 和 array hash 一致性不能补足该 provenance。

## 验证与硬零

- manifest：25/25 original、22/22 derived/tool files 通过 hash/size 检查；
- PUBLIC identity marker hits：0；
- Brownian generator executions：0；
- RNG calls/new random samples：0/0；
- training/fitting：0/0；
- confirmatory reruns：0；
- new prospective OOS reads：0；
- manuscript/frozen result modifications：0。

