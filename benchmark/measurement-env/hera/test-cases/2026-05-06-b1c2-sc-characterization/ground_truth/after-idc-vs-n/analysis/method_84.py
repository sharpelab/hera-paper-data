# Isaac's analysis convention applied to data/84 (the `# Idc vs n` sweep).
# Extracted/re-grounded 2026-06-05 for the HERA analysis-reproduction test.
#
# PROVENANCE NOTE: data/84 is NOT individually plotted in Isaac's ana notebook
# (`20260415_ana.ipynb` has no `data_id = 84`). The lines below are his VERBATIM
# Rxx/Rxy convention as it appears for every adjacent sweep in that notebook
# (cells 25 / 28 for the nT maps, cell 34 for data/85). The current channel is
# sr830_1; sr830_4 is the four-probe longitudinal voltage. This is the canonical
# read for this cooldown's `bottom device` wiring (mc: sr1/sr2 = 28-4,
# sr3 = 5-30, sr4 = 30-31). Applied here to data/84 so the answer key reads the
# right quantity (Rxx), not raw sr830_4_X.

data_id = 84
dat = sl.pload(folder_path, data_id)

# data/84 is a 2D multimegasweep: slow axis = (k_tg, k_bg) density line at fixed
# D (51 frames, n: -0.6 -> -0.4 e16 cm^-2); fast axis = dc205 bias, -15..15 V.
# Idc(nA) = dc205(V) * 10  (bias_resistor = 1e8 Ohm => 15 V -> 150 nA).

Ixx = dat['sr830_1_X'] / dat['measurement_config']['sr1_gain']   # AC current bias (~1 nA)
Rxx2 = (dat['sr830_4_X'] / 1e2) / Ixx   # four-probe Rxx  (Isaac's "Rxx2")
Rxx  = (dat['sr830_2_X'] / 1e2) / Ixx   # two-probe-ish Rxx on sr2 (28-4)
Rxy  = (dat['sr830_3_X'] / 1e2) / Ixx   # Rxy / off-diagonal on sr3 (5-30)

# Read as a 2D map of Rxx2 vs (Idc, density-frame): a low-Rxx (~0-1 Ohm) SC-like
# diamond centered at Idc = 0, widest mid-window and narrowing toward both ends
# of the density line -> a density-dependent critical current. See
# ../figures/ana_84_idc-vs-n_Rxx_sr830_4.png and the trace overlay.
