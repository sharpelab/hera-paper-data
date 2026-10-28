import numpy as np
from hera.analysis import open_run, summarize_run

run = open_run("data/0")
print(summarize_run(run))
print("cols:", run.cols)
print("interrupted:", run.interrupted)

vtg = run.col_at(1)  # k_tg_volt (swept axis; also fp'd at idx 3)
itg = run.col("k_tg_curr")
ibg = run.col("k_bg_curr")
# current channel: sr830_1_X / gain(-1e6) = current (A); gain sign just flips
I = run.col("sr830_1_X") / (-1e6)
# voltage channels: X / 100 = V_xx
v2 = run.col("sr830_2_X") / 100.0   # 2T, 5-4
v3 = run.col("sr830_3_X") / 100.0   # 4T longitudinal, 30-31

print("\n--- gate leakage ---")
print(f"|I_tg| max = {np.abs(itg).max():.3e} A   (expect pA, < 1 nA)")
print(f"|I_bg| max = {np.abs(ibg).max():.3e} A   (parked; expect floor)")

print("\n--- measured device current (sr830_1) ---")
print(f"I  med = {np.median(I)*1e9:.3f} nA   min {I.min()*1e9:.3f}  max {I.max()*1e9:.3f}")

print("\n--- resistances from MEASURED current (not stale meas_config) ---")
R2 = v2 / I
R3 = v3 / I
print(f"R_2T (5-4)        med = {np.median(R2)/1e3:.2f} kOhm   range [{R2.min()/1e3:.2f}, {R2.max()/1e3:.2f}]")
print(f"R_4T_xx (30-31)   med = {np.median(R3):.1f} Ohm     range [{R3.min():.1f}, {R3.max():.1f}]")

print("\n--- flat-channel guard ---")
for nm in ("sr830_1_X","sr830_2_X","sr830_3_X"):
    x = run.col(nm)
    print(f"{nm}: std/|med| = {np.std(x)/ (abs(np.median(x))+1e-30):.3f}  nan={np.isnan(x).any()}")

# phase sanity
for nm in ("sr830_1_P","sr830_2_P","sr830_3_P"):
    p = run.col(nm)
    print(f"{nm} (phase): med {np.median(p):.1f} deg  range [{p.min():.1f},{p.max():.1f}]")

# Rxx vs Vtg, a few points
print("\n--- R_4T_xx vs Vtg (every 10th pt) ---")
for k in range(0, len(vtg), 10):
    print(f"  Vtg={vtg[k]:+.3f} V   I={I[k]*1e9:.3f} nA   V4={v3[k]*1e6:.2f} uV   R4={R3[k]:.1f} Ohm")
