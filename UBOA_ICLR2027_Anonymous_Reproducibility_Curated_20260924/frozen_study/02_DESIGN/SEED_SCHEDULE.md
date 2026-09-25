# Seed schedule

Master seed:
`7fae9301e8e38493e1917601eef359468a74b79fab00cd4a31777da6074dc110`

Per-stream derivation:
```python
payload = f"{master_seed}|{cell_id}|{stream_type}|{index}".encode("utf-8")
digest = sha256(payload).digest()
seed = int.from_bytes(digest[:16], "big", signed=False)
rng = numpy.random.Generator(numpy.random.PCG64DXSM(seed))
```

- outer index: `0..7`;
- inner stream index: same outer-history index;
- stream types are exactly `outer` and `inner`;
- one inner stream emits all 4096 continuations in fixed order.

The seed table does not depend on results, selected label, truth depth or power.
