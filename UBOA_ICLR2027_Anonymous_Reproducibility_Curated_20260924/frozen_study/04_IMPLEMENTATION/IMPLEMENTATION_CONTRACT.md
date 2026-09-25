# Implementation contract

## Zero-randomness dry-run requirement

Before the implementation freeze, code may execute:
- parsing;
- exact rational arithmetic;
- deterministic theorem/certificate fixtures;
- hash checks;
- symbolic/numeric formula comparisons on hard-coded arrays.

It may **not** call any RNG, generate a synthetic path, execute a Monte Carlo loop, or read any real benchmark data.

## Required modules

Implement separate modules for:
1. `seed_schedule.py`: pure SHA256 seed derivation;
2. `generators.py`: B1 Rademacher and QB Gaussian dynamics;
3. `selection.py`: validation forecasts, loss, deterministic tie-break;
4. `truth.py`: independent exact truth formulas;
5. `certificate_b1.py`: Theorem A scalar-AR implementation;
6. `certificate_qb.py`: exact quadratic `A,g,k,V`;
7. `fixed_sequence.py`: potential local tests plus operational stopping;
8. `run_confirmatory.py`: the only stochastic entry point;
9. `analyze_confirmatory.py`: frozen analysis;
10. `verify_outputs.py`: schema/hash/denominator checks.

Do not reuse a hidden old simulator unless its complete source is copied into this package and independently checked against the frozen protocol.

## Seed derivation

Master seed is frozen as:
`7fae9301e8e38493e1917601eef359468a74b79fab00cd4a31777da6074dc110`.

For a stream key string:
`key = master_seed + "|" + cell_id + "|" + stream_type + "|" + index`

Compute SHA256 UTF-8 digest; use the first 16 bytes as an unsigned big-endian integer to initialize `numpy.random.PCG64DXSM`.

Allowed stream types: `outer`, `inner`.

No seed search, retry seed, “nice seed”, or replacement seed.

## Chronology

The locked command must process chronology in two machine-controlled phases with no human redesign point between them.

**Outer-H phase**
1. For all 10 cells and all outer indices 0..7, start from the predeclared initial state.
2. Generate burn-in and validation only.
3. Validation origins are exactly 256..319 (64 origins) with horizons {1,3,6}; the last validation target is state 325.
4. Freeze the selected rule after all validation targets are available.
5. `H` contains states through time 325 plus every protocol/selection/certificate coordinate. The first evaluation origin is exactly 325, so its input state is already in H and every evaluation target uses innovations strictly after H.
6. Write all 80 immutable history records, exact truths, first-true-null labels and certificate thresholds to `H_FREEZE_MANIFEST.json`; no cell/history may be dropped.
7. Hash that manifest.

**Inner-future phase**
8. Without manual selection or design edits, initialize the frozen inner stream for every history and generate exactly 4096 evaluation continuations.
9. Evaluation origins are 325..836 for B1 (512 origins) and 325..580 for QB (256 origins), always with horizons {1,3,6}.

No evaluation innovation may influence selection, truth classification, certificate constants, cell retention, or the set of per-history binomial audits. The realized set of finite-J histories is therefore H-measurable and fixed before the inner futures.

## Output schema

Per history:
- cell id / outer index / hashes;
- full pre-evaluation selected label and terminal state;
- exact truth at r=0,.02,.05;
- first true null;
- certificate thresholds at all nodes;
- inner counts: local rejects, reached, terminal reports, false promotions;
- invalid count;
- informativeness margins.

Raw inner paths need not be retained if storage is excessive, but the exact RNG key, aggregate counts, code hash and a deterministic checksum of each generated batch must be stored. If raw paths are retained, they remain internal artifacts and must not be selectively discarded.

## Implementation freeze F2

Before first stochastic run, create `IMPLEMENTATION_FREEZE.json` containing:
- SHA256 of every executable source file;
- Python / NumPy / SciPy versions;
- OS/architecture;
- scientific-protocol manifest hash;
- exact command that will run the study.

Claude audit must return `PASS_TO_EXECUTE` on this frozen source. Any source edit after that invalidates F2 and requires a new audit before execution.

## Crash policy

If execution crashes without source changes, resume/restart from the same frozen hashes and same seeds; log the crash. If any source change is needed, first run is preserved as failed/incomplete, a new F2 hash is created, and the repaired run is labeled `REPAIR_RUN`, not the original confirmatory run.
