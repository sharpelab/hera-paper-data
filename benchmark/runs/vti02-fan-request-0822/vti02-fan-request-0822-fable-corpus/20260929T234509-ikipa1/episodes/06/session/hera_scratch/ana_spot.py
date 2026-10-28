"""SdH spot-check read: runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12).
Onset via sdh_onset, tones via sdh_fft, compared against F_L = (h/4e)n."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, resolve_channels

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"

def read(rid, n_cm2, label):
    run = open_run(f"{BASE}/{rid}")
    B = run.col("magnet_field")
    # sr1 = Rxx (B_1-B_2), gain 1; I_bias from metadata
    mc = run.meta["measurement_config"]
    ibias = None
    # I_bias: sr1 drive amplitude / bias resistor -- take from instruments snapshot if present
    sens = None
    pars = run.meta["instruments"]["sr1"]["snapshot"]["parameters"]
    amp = pars["amplitude"]["value"]; sens = pars["sensitivity"]["value"]
    Rbias = mc["bias_resistor"]
    if amp: ibias = amp / Rbias
    print(f"   sr1 amplitude={amp}, sensitivity={sens}, I_bias={ibias}")
    R = run.col("sr1_X") / ibias
    FL = luttinger_frequency(n_cm2)
    print(f"   F_L({n_cm2:+.2e} cm^-2) = {FL:.2f} T")
    # sort ascending in B
    idx = np.argsort(B); B, R = B[idx], R[idx]
    rfs = sens / ibias if sens else None
    try:
        on = sdh_onset(R, B, r_full_scale=rfs)
        print(on.summary())
        onset = on.onset_b
    except Exception as e:
        print("   sdh_onset:", type(e).__name__, e)
        on, onset = None, None
    return run, B, R, FL, on, onset

res = {}
res['e'] = read(6, +3.2e12, "electron")
res['h'] = read(7, -1.2e12, "hole")
