# Cyclic caisson literature data

Processed data from digitized publication curves used in the manuscript comparison; these are not original instrument records.

| File | Contents |
|---|---|
| Zhu2013.csv | Three SC cyclic histories |
| Li2021.csv | Four SC and three HSC cyclic histories |
| Luo2020.csv | Five SC cyclic histories |
| monotonic_inputs.csv | Corresponding reference inputs |

In the history files, `N` is cycle count and `normalized_rotation_increment` is `(theta_N - theta_0)/theta_s` (dimensionless). Digitized cycle counts may be noninteger. Case labels follow the sources. SC denotes conventional suction caissons; HSC denotes hybrid suction caissons with external skirts.

In the input file, `zeta_b` is the maximum-load/capacity ratio; `q` is the tangent/secant stiffness ratio. `theta_s_deg` is the monotonic reference rotation in degrees. Li uses `displacement_proxy_mm` (millimeters) instead: cyclic rotations are digitized directly, while proportional displacement supplies the stiffness estimate and calibration weight. `theta0_over_theta_s` is the dimensionless initial offset; adding it to the increment gives total rotation normalized by `theta_s`. Blank cells mean not applicable. Luo inputs remain provisional pending low-angle extraction and CA2 reference-curve matching checks.

Sources: [Zhu et al. (2013)](https://doi.org/10.1061/(ASCE)GT.1943-5606.0000738), [Li et al. (2021)](https://doi.org/10.16285/j.rsm.2020.1296), [Luo et al. (2020)](https://doi.org/10.1680/jgele.19.00031).
