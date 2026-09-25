# Independent truth formulas

## B1-MAE

For horizon h:
`eta_h = sum_{j=1}^h 0.5^(h-j) eps_j`, eps_j in {-1,+1}.
For shift delta:
`R_h(delta)=2^{-h} sum_{sign patterns} |eta_h-delta|`.
Cell risk is the equal average over h in {1,3,6}.

Selected shifts ±1/10 have identical risk. Comparator constants in the table were chosen with exact rational arithmetic:
- NEG: delta_b=0, theta=-1/1280;
- B02: delta_b=289/784, theta=1/50;
- B05: delta_b=5875/10336, theta=1/20;
- ALT08: delta_b=2747/3680, theta=2/25;
- STR40: delta_b=541/328, theta=2/5.

These truth labels do not depend on the realized H.

## QB-MSE

Let evaluation start at state y0 in H. For origin offset k:
`M2_k(H)=0.5^(2k)y0^2 + [1-0.5^(2k)]/(1-0.25)`.

For horizon h:
`Q_h=[1-0.5^(2h)]/(1-0.25)`.

For mapping `(0.5^h+gamma)Y_o`:
`R_gamma(H) = average_{k,h}[Q_h + gamma^2 M2_k(H)]`.

Selected gamma is ±0.1, so selected expected risk is sign-invariant, while realized losses and selected label remain adaptive.

`theta(H)=1-R_selected(H)/R_comparator(H)` and each null truth is determined from this exact value. The stationary nominal cell label must never override this H-specific truth.
