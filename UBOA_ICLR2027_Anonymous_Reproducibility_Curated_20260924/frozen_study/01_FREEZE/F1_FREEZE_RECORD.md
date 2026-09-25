# F1 scientific freeze record

Study: `UBOA_ROUTE_B_SYNTH_CONFIRMATORY_V1`

Status: `F1_SCIENTIFIC_PROTOCOL_FROZEN_NOT_EXECUTED`

The authoritative manifest identifier is stored in `01_FREEZE/MANIFEST_ID.txt` and the file hashes are stored in `01_FREEZE/SCIENTIFIC_FREEZE_MANIFEST.json`.

At this freeze:
- exact cell grid, truth conventions, replication counts, audit level, Holm rule, seed derivation and claim boundaries are locked;
- `09_OUTPUTS` contains only its empty README;
- no DGP path has been generated;
- implementation code does not yet exist and must be added under a new implementation directory without changing F1 files;
- any edit to a hashed F1 file invalidates the preregistration and must be recorded as a superseded prereg, not silently overwritten.
