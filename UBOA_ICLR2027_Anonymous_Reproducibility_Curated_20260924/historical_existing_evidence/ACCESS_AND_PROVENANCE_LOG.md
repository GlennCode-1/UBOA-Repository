# Access and provenance log

日期：2026-09-17。所有路径均为 `${UBOA_REPO}` 相对路径或当前导出相对路径。

## 输入冻结

- 指令包：`UBOA_Forensics_Challenge_Followup_20260916.zip`
- 指令包 SHA256：`51a2a6d43cf9877d24071c9b7329746374a1becd928d0471d2ba4c99144c6323`
- 当前 repository commit：`2e973cdc2ba36fec3070dfc8261a3228c0849284`
- 导出 allowlist：25 份原件；来源逐项记录于 `PUBLIC_EVIDENCE_MANIFEST.json`。
- 搜索边界：只使用 prompt 和上一轮 `PATCH_README` 已定位的路径；没有第二轮数据/benchmark 搜索。

## 读取与命令类别

1. 用 `shasum -a 256` 和 `unzip -l` 核验/列出 follow-up ZIP；解压到 task-scoped 临时目录。
2. 读取 `README.md`、`04_PROMPTS/CODEX_EXPORT_EXISTING_EVIDENCE.md`、`01_REVIEW/CHALLENGE_PREFLIGHT.md`、`INTEGRATED_FINDINGS.md`、`LIMITATIONS_BOUNDARIES.md`、`PACKAGE_MANIFEST.json` 与 execution/package-validation 说明。
3. 用固定 `find`/`rg` 检查已定位 Brownian、Stage36、Stage37、Stage32 文件存在性。未全盘搜索个人目录或新数据。
4. 在复制前对 25 份 allowlisted 原件作 byte-level 身份 marker 扫描。未发现个人绝对路径、本机用户名或主机名。
5. 静态解析 `export_existing_evidence.py`；确认没有 RNG、model fit 或 confirmatory 调用。运行一次 deterministic export builder，第一次在最终自扫描处返回 `HOLD_PUBLIC_IDENTITY_MARKER: export tool`，原因是检测器源码含自身检测字面量，而非 evidence 泄露。
6. 删除该次由本任务创建的未完成 `PUBLIC_EVIDENCE/` 与 `PRIVATE_EVIDENCE/`，分段构造 marker 后重建。首次 HOLD 保留在本日志，不覆盖。
7. 第二次 builder 完成 25 份 original byte copies 与 22 份 derived/tool files。所有原件 source/private/public SHA256 相同。
8. prefix derivation 只读取六个既有 Stage36 archive 的前 `floor(0.8*N)` decoded rows。没有打开 final 20% source suffix。第三方 archives 未复制到导出。
9. 静态解析并运行 `verify_existing_evidence_export.py`。它读取导出 array/JSON/JSONL/NPZ/NPY/TSV，验证 manifest、privacy、q95、validation means/gaps、16 reached statistics、17 masks 和 Household timestamp groups。
10. 被导出的 `independent_implementation.py` 含历史 RNG generator，但本轮从未 import、调用或执行该 generator。
11. 用 `zip -r -X` 构建 `EXISTING_EVIDENCE_EXPORT.zip`，输入仅为 `PUBLIC_EVIDENCE/`、public manifest、public README、export report、missing list 与本日志。`PRIVATE_EVIDENCE/`、private manifest、verifier 和第三方 raw archives 均未加入。
12. 对 ZIP 运行最终 deterministic verification：成员名无 absolute/upward/private path，ZIP 外 `EXPORT_VERIFICATION.json` 记录最终 ZIP SHA256、大小、成员数及全部数值/hash/privacy checks。该 verification 不放入 ZIP，避免自包含 hash 循环。
13. 最终验证后删除本任务创建的临时指令包解压目录；正式导出、PUBLIC/PRIVATE evidence、manifest、报告和 verification 保留。

## 允许的派生对象

- 17 个 task/member Boolean missingness masks；
- `mask_index.json` 与 `missingness_summary.json`；
- 27,670 行 Household 60-row timestamp-group TSV；
- derivation note 与确定性导出工具。

这些对象统一标记 `DERIVED_FROM_EXISTING_PREFIX`，不冒充原 execution log，不产生 scientific outcome。

## 未执行

- RNG / Monte Carlo / reference draws；
- model training、fitting、prediction 或 benchmark；
- `run_confirmatory.py` 或 confirmatory study replay；
- 新 prospective OOS/raw suffix 读取；
- manuscript、frozen protocol/source/H/results/hash 修改；
- 未到达节点补跑；
- blind review 或 matcher scoring。

硬计数：`RNG=0`，`new random samples=0`，`training/fitting=0`，`confirmatory reruns=0`，`new prospective OOS reads=0`，`manuscript/frozen writes=0`。
