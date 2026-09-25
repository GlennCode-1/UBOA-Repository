# Independent pre-execution audit binding

The future stochastic entry point is fail-closed. It accepts execution only when
`11_PREEXEC_AUDIT/FINAL_VERDICT.json` contains:

```json
{
  "verdict": "PASS_TO_EXECUTE",
  "implementation_freeze_sha256": "<SHA256 of 10_IMPLEMENTATION/IMPLEMENTATION_FREEZE.json>"
}
```

`status` may be used instead of `verdict`, but the hash field is mandatory. A
verdict for any earlier source hash is rejected. The auditor remains responsible
for the four files required by `06_PROMPTS/CLAUDE_PREEXEC_AUDIT.md`.

The exact future command is recorded in `IMPLEMENTATION_FREEZE.json`. It must not
be run during the implementation dry-run.
