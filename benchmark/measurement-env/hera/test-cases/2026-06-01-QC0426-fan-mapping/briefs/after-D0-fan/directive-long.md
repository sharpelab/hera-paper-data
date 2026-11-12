<!-- variant: directive-long | autonomy: LOW (move named) | length: LONG -->

# Brief

The first B-n Landau fan at the charge-neutral D = 0 line (data/27, to 8 T)
confirms the fan technique works but is washed out at the VTI's ~1.2 K — too
featureless to read the stacking. Before committing to the long D-series,
**introduce the doped-Si global back gate** (the second Keithley, `k_2410`, wired
and currently zeroed): first **map the device vs the top gate and Si gate**
(a TG-Si `megasweep`, DC205 × k_2410, at fixed field) to see how the Si gate moves
n and where the CNP lands, then **re-take the D = 0 fan with Si screening applied**
(e.g. Si ≈ +60 V) and, optionally, **map the Si-dependence directly** (a VSi-n
sweep at D = 0). Keep TG on the DC205 (`DC_bias`), BG on k_bg, the
capacitance-based calc_nD for (n, D), and current on sr0 with gain division; field
range and Si set-points are yours. Land the Si-gate maps and the screened fan.
