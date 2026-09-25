# Deterministic invalid fixtures

These fixtures are mandatory and run before any stochastic path.

1. `B1_MISSING_SUPPORT`
   - remove the structural state/support envelope or innovation diameter.
   - expected result: `INVALID_CERTIFICATE / HOLD`; no local rejection.

2. `QB_MISSING_M4`
   - exact quadratic MSE requested but fourth moment is absent.
   - expected result: `INVALID_CERTIFICATE / HOLD`.

3. `QB_CORRELATED_SCALAR_COORDS`
   - declare within-time scalar innovation coordinates correlated while invoking the scalar-coordinate independent variance identity.
   - expected result: interface rejects applicability; no silent diagonal formula.

4. `SCOPE_MUTATION`
   - certificate frozen for horizons `{1,3,6}` but evaluation request asks `{1,6}` or changes weights.
   - expected result: mismatch / unsupported request; no copied positive conclusion.

5. `NONFINITE_CERTIFICATE`
   - inject NaN/Inf into a required primitive.
   - expected result: unresolved/invalid; never promote.

Any positive terminal promotion from one of these five fixtures is an implementation FAIL.
