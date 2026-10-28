# Scratch: SdH spot checks runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D=0.
# Raw traces, onset, FFT tones -> what the Landau fan must resolve.
import numpy as np, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import (open_run, resolve_channels, sdh_fft, sdh_onset,
                           SdhOnsetError, luttinger_frequency)

OUT = {}
fig, axes = plt.subplots(2, 3, figsize=(15, 7))

for row, (rid, nlabel) in enumerate([(6, "+3.2e12 e-side"), (7, "-1.2e12 h-side")]):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field")
    cfg = r.meta["measurement_config"]
    i = r.col("sr0_X") / cfg["sr0_gain"]              # A (signed)
    i_med = np.median(np.abs(i))
    v = r.col("sr1_X")                                # V, unity gain
    R = v / i_med
    OUT[rid] = dict(i_med=i_med, R0=float(R[np.argmin(np.abs(B))]))
    order = np.argsort(B)
    B, R = B[order], R[order]
    m = B > 0.05
    B, R = B[m], R[m]

    ax = axes[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid}: n = {nlabel}, raw Rxx(B); I_med {i_med*1e9:.2f} nA")

    # onset + tones
    try:
        so = sdh_onset(R, B, r_full_scale=50e-6 / i_med, b_lo=0.3)
        OUT[rid]["onset"] = so.onset_b
        OUT[rid]["summary"] = so.summary()
        OUT[rid]["tones"] = [(t.freq, t.contrast, t.onset_b, t.censored, t.marginal,
                              t.harmonic_of) for t in so.tones]
    except SdhOnsetError as e:
        OUT[rid]["onset_err"] = str(e)

    # FFT over the high-B window
    for col, (blo, bhi) in enumerate([(2.0, 10.0), (4.0, 10.0)]):
        mm = (B >= blo) & (B <= bhi)
        if mm.sum() < 50: continue
        freqs, spec = sdh_fft(R[mm][:, None], B[mm], nfft=4096, bg_degree=5)
        ax = axes[row, 1 + col]
        ax.plot(freqs, spec[0], lw=0.8)
        ax.set_xlim(0, 120); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT|")
        ax.set_title(f"run {rid} FFT, B {blo}-{bhi} T")
        pk = freqs[(freqs > 3)][np.argsort(spec[0][(freqs > 3)])[-6:]][::-1]
        OUT[rid][f"fft_{blo}_{bhi}_top"] = list(np.round(pk, 2))

fig.tight_layout()
fig.savefig("hera_scratch/spot_fft.png", dpi=110)

for rid in (6, 7):
    print(f"===== run {rid} =====")
    for k, val in OUT[rid].items():
        if k == "summary":
            print(val)
        else:
            print(f"  {k}: {val}")

# Luttinger check: full-density single-FS frequency at the two spots
for n12 in (3.2, 1.2):
    print(f"n = {n12}e12: F_L = {luttinger_frequency(n12*1e16):.1f} T")
