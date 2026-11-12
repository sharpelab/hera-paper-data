"""Runs 6/7 — FFT cutoff + stability ladder (sdh-spot-check Verify).

Run 6's sdh_onset(b_lo=0.1) returns onset_b = 0.10 T carried by censored@edge
tones (3.0/3.8/5.4/9.5/14.1 T) — residual MR background leaking through the
degree-5 poly over a 0.1-10 T window, not SdH (F_L = 33 T cannot oscillate at
0.1 T). The recipe's fix: raise the cutoff until the slow-tone amplitudes stop
shrinking, then read the onset from that window.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

DIR = "/home/hera/measurements/zack/20260822-vti-02/data"
SPOTS = {6: ("electron", +3.2), 7: ("hole", -1.2)}


def load(rid):
    run = open_run(f"{DIR}/{rid}")
    mc = run.meta["measurement_config"]
    B = run.col("magnet_field")
    R = (run.col("sr1_X") / 1.0) / (run.col("sr0_X") / mc["sr0_gain"])
    k = B > 0.05
    B, R = B[k], np.abs(R[k])
    o = np.argsort(B)
    return B[o], R[o]


def peaks(freqs, sp, fmin=1.0, top=6):
    p, _ = find_peaks(sp)
    p = p[freqs[p] >= fmin]
    p = p[np.argsort(sp[p])[::-1]][:top]
    return sorted([(float(freqs[i]), float(sp[i])) for i in p], key=lambda t: t[0])


for rid, (side, n12) in SPOTS.items():
    B, R = load(rid)
    F_L = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"\n################ run {rid} — {side}, n = {n12:+.2f}e12, F_L = {F_L:.2f} T ################")

    # --- cutoff ladder: where do the slow tones stop shrinking? ---
    print("\n-- cutoff ladder (bg_degree 5, B_hi = 10 T) --")
    for cut in (0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0):
        if cut <= B.min():
            continue
        f, s = sdh_fft(R[:, None], B, b_range=(cut, 10.0), bg_degree=5)
        s = s[0]
        dF = 1.0 / (1.0 / cut - 1.0 / 10.0)
        pk = peaks(f, s, fmin=1.0)
        mx = max(a for _, a in pk) if pk else 1.0
        _m = (f > 0) & (f < 2.0)
        lo_amp = s[_m].max() if _m.any() else np.nan
        txt = "  ".join(f"{fr:.1f}T({a/mx:.2f})" for fr, a in pk)
        print(f"  cut {cut:4.1f}  dF {dF:5.2f}  |F<2T| {lo_amp/mx:5.2f}   {txt}")

    # --- bg_degree stability at the chosen window ---
    cut = 1.5 if rid == 6 else 1.0
    print(f"\n-- bg_degree stability (window {cut}-10 T) --")
    for deg in (3, 4, 5, 6, 7):
        f, s = sdh_fft(R[:, None], B, b_range=(cut, 10.0), bg_degree=deg)
        s = s[0]
        pk = peaks(f, s, fmin=2.0)
        mx = max(a for _, a in pk) if pk else 1.0
        print(f"  deg {deg}: " + "  ".join(f"{fr:.2f}T({a/mx:.2f})" for fr, a in pk))

    # --- B-window split: F_L-tone origin test (breakdown tone grows with B) ---
    print(f"\n-- B-window split (low/high half of the 1/B record above {cut} T) --")
    ib = 1.0 / B[(B >= cut) & (B <= 10.0)]
    b_mid = 1.0 / np.median(ib)
    for lab, rng in (("low-B ", (cut, b_mid)), ("high-B", (b_mid, 10.0))):
        f, s = sdh_fft(R[:, None], B, b_range=rng, bg_degree=5)
        s = s[0]
        pk = peaks(f, s, fmin=2.0)
        mx = max(a for _, a in pk) if pk else 1.0
        print(f"  {lab} {rng[0]:.2f}-{rng[1]:.2f} T (dF {1/(1/rng[0]-1/rng[1]):.2f}): "
              + "  ".join(f"{fr:.1f}T({a/mx:.2f})" for fr, a in pk))

    # --- onset re-read from the cleaned window ---
    print(f"\n-- sdh_onset with b_lo = {cut} T --")
    try:
        on = sdh_onset(R, B, b_lo=cut, r_full_scale=5050.0)
        print("  " + on.summary().replace("\n", "\n  "))
    except Exception as e:
        print(f"  {type(e).__name__}: {e}")

# --- the electron-side partition arithmetic ---
print("\n\n================ electron-side (run 6) partition check ================")
B, R = load(6)
f, s = sdh_fft(R[:, None], B, b_range=(1.5, 10.0), bg_degree=5)
s = s[0]
F_L = float(luttinger_frequency(3.2e16))
pk = peaks(f, s, fmin=2.0, top=8)
print(f"F_L(n=3.2e12) = {F_L:.2f} T; peaks above 2 T:")
for fr, a in pk:
    print(f"  {fr:7.2f} T  amp {a/max(x for _, x in pk):.3f}   f/F_L {fr/F_L:.3f}")
print("\npair sums (f_i + f_j) vs F_L and vs each candidate F_L-tone:")
fr = [x for x, _ in pk]
for i in range(len(fr)):
    for j in range(i + 1, len(fr)):
        ssum = fr[i] + fr[j]
        close = [k for k in fr if abs(k - ssum) < 1.0]
        if close or abs(ssum - F_L) / F_L < 0.15:
            print(f"  {fr[i]:6.2f} + {fr[j]:6.2f} = {ssum:6.2f}  "
                  f"(F_L ratio {ssum/F_L:.3f}; partition {fr[i]/ssum:.3f}/{fr[j]/ssum:.3f})"
                  + (f"  == observed tone {close}" if close else ""))
