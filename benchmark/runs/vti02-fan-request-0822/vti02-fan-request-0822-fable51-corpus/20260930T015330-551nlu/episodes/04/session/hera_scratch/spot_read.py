"""First-pass read of the SdH spot checks (runs 6 electron, 7 hole): onset + FFT per sdh-spot-check step 6."""
import numpy as np, json, sys
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
for rid in (6, 7):
    r = open_run(f"data/{rid}")
    print("="*80); print(summarize_run(r))
    B = r.col("magnet_field"); X = r.col("sr1_X")
    mc = r.meta["measurement_config"]
    amp = None
    try:
        amp = r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]
    except Exception as e: print("amp lookup failed", e)
    I = (amp or 1.0)/mc["bias_resistor"]; R = X / I
    o = np.argsort(B); B, R = B[o], R[o]
    print(f"run {rid}: I_bias {I*1e9:.2f} nA, B {B.min():.2f}-{B.max():.2f} T, {len(B)} pts, R {R.min():.1f}..{R.max():.1f} Ohm")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6/I)
        print(on.summary())
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
