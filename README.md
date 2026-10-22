# Cyclic caisson literature data

Digitized literature curves, model inputs, and leave-one-case-out predictions for 15 constant-amplitude cyclic tests of suction caissons (SC) and hybrid suction caissons (HSC). This release supports the published-data comparison in Section 4.4 of the associated manuscript.

| Dataset | Cases | Foundation | Reference cycles |
|---|---|---|---:|
| Zhu et al. (2013) | CV2-3, CV2-4, CV2-5 | SC | 4,000 |
| Li et al. (2021) | I-CH2, I-CH3, I-CH4, I-CH5 | SC | 1,000 |
| Li et al. (2021) | IO-CH2, IO-CH3, IO-CH4 | HSC | 1,000 |
| Luo et al. (2020) | CA1, CA2, CA3, CA4, CA5 | SC | 1,000,000 |

The observations are **digitized publication curves**, not original instrument records. Curve resampling density does not represent the number of independent measurements. The release contains 11,130 curve points, 664 evaluation points, and 30 saved model fits. Luo inputs retain the provisional checks described below.

## Files

- `data/cases.csv`: the 15 case inputs, reference scales, cycle counts, and initial rotation offsets.
- `data/cyclic_histories.csv`: normalized accumulated rotation histories, with one row per digitized curve point.
- `data/evaluation_points.csv`: the exact evaluation grids used for the reported errors.
- `data/li_hsc_monotonic.csv`: extracted IO-H load–displacement curve, including extraction coordinates and stroke bounds.
- `results/`: saved fold parameters, point predictions, case errors, and dataset averages.
- `provenance/`: source identifiers, digitization coordinates, axis calibrations, archived metric tables, and input checks.
- `scripts/reproduce.py`: independently runnable prediction, scoring, and refitting checks.
- `figures/literature_predictions.pdf` and `.png`: the manuscript comparison figure.
- `DATA_DICTIONARY.md`: definitions and units.

## Reproduction

Requires Python 3.10 or later. From this directory:

```sh
python -m pip install -r requirements.txt
python scripts/reproduce.py
```

The script reads only the release files. It reconstructs the saved predictions, recomputes the error tables, checks that no target case appears in its training set, and refits all 30 models. Outputs go to `generated/`; archived data and results are not overwritten. No source PDFs or manuscript workspace are required. The script starts from the supplied monotonic state inputs; it does not repeat PDF digitization or independently resolve source-curve matching.

## Calculation

The normalized accumulated rotation is `r(N) = (theta_N - theta_0) / theta_s`. The terminal total rotation ratio is `R_end = theta_0/theta_s + r(N_end)`.

The proposed model is

```text
X = zeta_b * (1/q - 1)
r(N) = (c0 + c1*X) * (N^alpha - 1)/(N_ref^alpha - 1)
```

The direct power-law comparator is

```text
r(N) = b * (N/N_ref)^beta
```

Each dataset is calibrated separately. Each fold leaves out one entire case and trains on the remaining cases: two for Zhu, six for Li, and four for Luo. Li's SC and HSC cases share coefficients but use foundation-specific monotonic inputs. Coefficients are not transferred from the authors' own model tests.

For the proposed model, nonnegative `c0` and `c1` minimize `sum[scale_i*(r_i(N_ref)-c0-c1*X_i)]^2`. The exponent minimizes the mean of the per-case mean squared differences between the normalized process `r_i(N)/r_i(N_ref)` and the growth function. The direct power law uses equal case weighting and squared residuals normalized by each training case's reference increment. Both exponents are bounded between 0.01 and 2. Only training observations at or below the reference cycle count enter calibration.

Evaluation uses 40 logarithmically spaced points up to the common reference count, with eight additional points when the digitized history extends beyond it. Observations are interpolated linearly in log cycle count. Per-case process NRMSE is `100*RMSE(r_pred-r_obs)/abs(r_obs(N_ref))`. Terminal error is `100*abs(R_pred-R_obs)/abs(R_obs)`. Dataset results average the case errors equally. Different cycle ranges and reference increments should be considered when comparing errors across papers.

## Monotonic inputs and reference scales

**Zhu:** the archived monotonic state inputs are retained: `theta_s` in degrees and the tangent-to-secant stiffness ratio `q`. Cyclic observations come from Fig. 8(c). `theta_0/theta_s = 1` is used. The stored digitized endpoints differ slightly from the source's reported test counts; both are retained. Predictions and terminal scoring use the digitized endpoints. The reference count remains 4,000.

**Li:** cyclic observations come directly from the reported normalized rotation curves in Fig. 9(a,b). Absolute rotation is not reconstructed from displacement. The monotonic input comes from horizontal load–loading-point displacement in Fig. 7, with separate I-H and IO-H curves. Under the proportional-displacement approximation, `q = (dH/dy)/(H/y)` estimates the rotational tangent-to-secant ratio. The displacement scale also supplies the amplitude-fitting weight; it is in millimeters and is not a measured angle. Comparable weighting across SC and HSC is an approximation.

The SC hyperbolic proxy uses `H_inf = 32.164 N`, `y_r = 2.062 mm`, and reported capacity `32.5 N`. The HSC proxy uses `H_inf = 37.17751605071756 N`, `y_r = 1.5609730405633806 mm`, and reported capacity `37 N`. For `H_peak = zeta_b*capacity`, `q = 1-H_peak/H_inf` and `y_s = y_r*H_peak/(H_inf-H_peak)`. HSC fitting uses 401 equally spaced displacement points over 0–40 mm, with the fitted processing origin anchored to zero; the exported extraction retains the original traced ordinate. The cyclic comparison takes `theta_0/theta_s = 1`.

**Luo:** the supplied calculation uses Fig. 7(a) total rotation, subtracts the initial reference inferred from the earliest common pair of Fig. 7(a,b) readings, and divides by the independent monotonic `theta_s`. Therefore the stored `theta_0/theta_s` is retained for each case. This reconstruction does not establish a physical difference between the two reference quantities.

The current Luo inputs use M1 provisionally for all five cases. The low-angle M1 extraction and the CA2/M2 pairing remain to be checked. The processing uses an ascending monotonic branch, PCHIP interpolation, and a nominal ±0.05 degree finite-difference window for the local slope. Capacity is 2.0 N m. The associated results are **conditional on these inputs**. Reproducing the calculation does not close those checks. CA2 was previously reported by Zhu et al. (2018) and is counted only once in this release.

## Reported comparisons

| Dataset | Proposed process NRMSE (%) | Power-law process NRMSE (%) | Proposed terminal MAPE (%) | Power-law terminal MAPE (%) |
|---|---:|---:|---:|---:|
| Zhu | 11.51 | 24.38 | 16.51 | 30.90 |
| Li, SC + HSC | 8.30 | 11.99 | 9.77 | 15.12 |
| Luo, all five cases | 43.04 | 68.41 | 60.61 | 102.59 |
| Luo, excluding CA1 from scoring | 9.83 | 37.96 | 14.02 | 60.34 |

The last row changes only the error average. All original leave-one-out predictions and training sets are retained; no case is removed or refitted to generate that row.

## Sources

- Zhu, B., Byrne, B. W., and Houlsby, G. T. (2013). Long-Term Lateral Cyclic Response of Suction Caisson Foundations in Sand. *Journal of Geotechnical and Geoenvironmental Engineering*, 139(1), 73–83. [DOI](https://doi.org/10.1061/(ASCE)GT.1943-5606.0000738).
- Li et al. (2021). 饱和砂土中裙式吸力基础水平循环特性和累积转角变化规律. *岩土力学*, 42(3), 611–619. [DOI](https://doi.org/10.16285/j.rsm.2020.1296).
- Luo, L., O'Loughlin, C. D., Bienen, B., Wang, Y., Cassidy, M. J., and Morgan, N. (2020). Effect of the ordering of cyclic loading on the response of suction caissons in sand. *Géotechnique Letters*, 10(2), 303–310. [DOI](https://doi.org/10.1680/jgele.19.00031).

Please cite the original studies when using their digitized data and identify this repository's version or commit. Original publication PDFs are not redistributed. Release snapshot: 2026-10-22.
