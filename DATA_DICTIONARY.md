# Data dictionary

CSV files use UTF-8 and comma delimiters. `dataset` and `case` together form a case identifier. Blank cells in auxiliary archived tables mean not applicable or not supplied, not zero.

## Core inputs

| Field | Meaning | Units |
|---|---|---|
| `dataset` | Zhu2013, Li2021, or Luo2020 | identifier |
| `case` | Case designation from the source | identifier |
| `foundation` | SC or HSC | category |
| `zeta_b` | Maximum cyclic load divided by reference capacity | dimensionless |
| `q` | Monotonic local tangent stiffness divided by secant stiffness | dimensionless |
| `X` | `zeta_b*(1/q-1)` | dimensionless |
| `calibration_scale` | Monotonic rotation scale or Li displacement proxy used in weighted amplitude fitting | see `scale_unit` |
| `scale_unit` | `deg` for Zhu/Luo; `mm_proxy` for Li | category |
| `N_ref` | Common calibration reference count for that dataset | cycles |
| `N_end` | Last digitized point used for terminal scoring | cycles, may be noninteger |
| `N_reported` | Test endpoint reported by the original paper | cycles |
| `theta0_over_theta_s` | Offset added to accumulated rotation ratio to form total rotation ratio | dimensionless |
| `r_ref` | Observed accumulated rotation ratio at `N_ref` | dimensionless |
| `r_end` | Observed accumulated rotation ratio at `N_end` | dimensionless |
| `input_status` | Archived inputs or conditional Luo inputs with pending source checks | category |

## Curve and prediction tables

| Field | Meaning | Units |
|---|---|---|
| `N` | Digitized or evaluation cycle count | cycles, may be noninteger |
| `r_observed` | `(theta_N-theta_0)/theta_s`, as reconstructed for that source | dimensionless |
| `r_predicted` | Model prediction of the same quantity | dimensionless |
| `model` | Proposed model or Direct power law | category |
| `r_end_observed`, `r_end_predicted` | Terminal accumulated ratios | dimensionless |
| `R_end_observed`, `R_end_predicted` | Terminal total ratios, including the stored initial offset | dimensionless |
| `process_nrmse_pct` | Per-case RMSE over the supplied evaluation grid, divided by the observed reference increment | percent |
| `terminal_total_ratio_ape_pct` | Absolute relative error in the terminal total ratio | percent |
| `terminal_total_ratio_mape_pct` | Arithmetic mean of terminal APE across the indicated cases | percent |
| `scoring_subset` | `all`, or `without_CA1_scoring_only` without changing trained models | category |
| `n_cases` | Number of cases in an error average | count |

In `results/folds.json`, `training` gives all training cases and `held_out` gives the target. Proposed-model parameters are `c0`, `c1`, `alpha`; direct-power parameters are `b`, `beta`. All are dimensionless under the released normalization. `b` is the predicted accumulated ratio at `N_ref`, not the coefficient multiplying unscaled `N^beta`.

## Extraction and provenance

- `zhu_li_sc_vector_points.csv`: `N`, `r_acc` are the extracted cycle/normalized-increment coordinates. `x_pdf`, `y_pdf` are PDF coordinates in points. `figure`, `method`, and `path_id` identify the original panel and curve path.
- `li_hsc_vector_points.csv`: `r_increment` is the normalized accumulated rotation. `y_stroke_low/high` bound the traced ordinate across the drawn line width; these are digitization bounds, not experimental confidence limits. `x_pdf/y_pdf` and `stroke_span_pdf` use PDF points; `page` is the one-based PDF page.
- `li_hsc_monotonic.csv`: `displacement_mm` and `load_N` are loading-point displacement and horizontal load. `y_stroke_low/high` are load-coordinate extraction bounds in N; `x_pdf/y_pdf` and `stroke_span_pdf` use PDF points. `page` and `figure` identify the source.
- `luo_digitized_points.csv`: for `kind=total`, `x=N` and `y=total rotation (deg)`; for `kind=normalized`, `x=N` and `y=(theta_N-theta_0)/theta_0`; for `kind=monotonic`, `x=rotation (deg)` and `y=moment (N m)`. `x_pixel/y_pixel` locate the traced point on the source image, `point` orders points on a curve, and `figure/page/image` identify the source panel. The raster files themselves are not distributed.
- `luo_input_checks.csv`: `theta_s`, `theta0_deg`, `reference_increment_deg` are in degrees. `peak` and `capacity` are in N m; `q`, `X`, `zeta`, and `theta0_to_monotonic_theta_s` are dimensionless. `theta0_cross_panel_range_pct` is the reconstruction diagnostic range relative to the adopted initial reference, not a statistical interval. `status/input_caution` preserve unresolved input checks.
- `sources.json`, `li_hsc_extraction.json`, and `luo_axis_calibration.json`: publication hashes and extraction calibration. Hashes identify the source PDF version; they do not imply that the PDF is included.
- `export_manifest.json`: project-relative archival paths and hashes used to assemble the release. Those paths are provenance records, not runtime dependencies.
- `*_archived_metrics.csv`: original evaluation outputs retained for comparison. For Zhu/Li, stored process ordinates are normalized increments. Luo archived `observed_end/predicted_end` are increments in degrees; the core result tables convert them to ratios using the supplied `theta_s`.

Zhu and Li SC monotonic curve point sets are not claimed to be reconstructed here. The release preserves the actual archived scalar inputs and Li SC hyperbolic parameters used in the calculation; Li HSC and Luo extracted monotonic point sets are supplied separately.
