# Route A reference matcher

This implementation consumes only manually authored request/evidence JSON metadata. It does not
load scientific data, compute predictions, select a model, run a statistical test, or verify whether
a data-generating assumption is true.

Run the deterministic suite from this directory:

```bash
python3 test_matcher.py
```

Run one match by sending JSON with top-level `request` and `evidence` objects:

```bash
python3 matcher.py < request_and_evidence.json
```

The public rule statement and relative non-amplification proof are in Appendix B of the manuscript.
The implementation is deliberately small and incomplete. Its passing fixtures establish conformance
on the enumerated cases only; they do not measure audit accuracy against humans or establish any
statistical guarantee for real applications.


## Retrospective real-record demonstrations

`python3 real_record_demo.py` applies the existing matcher to hand-authored metadata describing the saved Weather/ETTm2 protocol history. It recomputes no scientific statistic. It shows that an observed decision cannot be upgraded to a full-history conditional guarantee and that literal observed-record copying fails when the applied method is not retained. The matcher still relies on correctly annotated metadata; it does not authenticate the historical record.
