"""Runs 6 & 7 — controlled FFT: explicit 1/B resample, B-space detrend, Hann, zero-pad.
Design inputs for the fan: tone set, partition vs F_L, onset, required window + Delta(1/B)."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, luttinger_frequency

def trace(rid):
    g = open_run(f"data/{rid}")
    c = list(g.cols); d = np.asarray(g.data)
    p1 = g.meta["instruments"]["sr1"]["snapshot"]["parameters"]
    Ib = p1["amplitude"]["value"] / g.meta["measurement_config"]["bias_resistor"]
    B = d[:, c.index("magnet_field")]; R = d[:, c.index("sr1_X")] / Ib
    o = np.argsort(B)
    return B[o], R[o], Ib

def spec(B, R, blo, bhi, deg=3, nfft=1 << 15, win=True):
    m = (B >= blo) & (B <= bhi)
    Bw, Rw = B[m], R[m]
    Rd = Rw - np.polyval(np.polyfit(Bw, Rw, deg), Bw)       # detrend in B-space, before 1/B
    x = 1.0 / Bw
    xi = np.linspace(x.min(), x.max(), 2048)                # uniform 1/B
    yi = np.interp(xi, x, Rd)
    w = np.hanning(len(xi)) if win else np.ones(len(xi))
    Y = np.abs(np.fft.rfft(yi * w, n=nfft))
    f = np.fft.rfftfreq(nfft, d=xi[1] - xi[0])
    return f, Y, (x.max() - x.min()), m.sum()

def peaks(f, Y, fmin=2.0, fmax=90.0, nmax=8):
    k = (f > fmin) & (f < fmax); fk, Yk = f[k], Y[k]
    idx = [i for i in range(1, len(Yk) - 1) if Yk[i] > Yk[i-1] and Yk[i] > Yk[i+1]]
    idx.sort(key=lambda i: -Yk[i])
    out, used = [], []
    for i in idx:                                            # de-duplicate within 1.5 T
        if all(abs(fk[i] - u) > 1.5 for u in used):
            out.append((fk[i], Yk[i])); used.append(fk[i])
        if len(out) >= nmax: break
    return out

for rid, n_spot in ((6, 3.2), (7, -1.2)):
    B, R, Ib = trace(rid)
    FL = float(luttinger_frequency(abs(n_spot) * 1e16))
    print(f"\n===== run {rid}: n = {n_spot:+.2f}e12, F_L = {FL:.2f} T, I_bias {Ib:.2e} A, "
          f"R range {R.min():.0f}..{R.max():.0f} Ohm (FS {5e-5/Ib:.0f}) =====")
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    wins = [(1.0, 10.0), (1.5, 10.0), (2.0, 10.0), (1.5, 4.5)]
    for ax, (blo, bhi) in zip(axes.ravel(), wins):
        f, Y, span, N = spec(B, R, blo, bhi)
        df = 1.0 / span
        pk = peaks(f, Y)
        print(f"  B[{blo},{bhi}] N={N:4d} span(1/B)={span:.4f} df={df:.2f} T")
        for fr, a in pk[:6]:
            print(f"      f = {fr:6.2f} T  amp {a:9.1f}  f/F_L = {fr/FL:5.3f}  "
                  f"periods in window = {fr*span:5.2f}")
        ax.plot(f, Y, lw=0.8)
        for x0, lab, col in ((FL, "F_L", "k"), (0.72*FL, "0.72F_L", "r"), (0.28*FL, "0.28F_L", "b")):
            ax.axvline(x0, color=col, ls="--", lw=0.8); ax.text(x0, ax.get_ylim()[1]*0.9, lab, fontsize=7, color=col)
        ax.set_xlim(0, 2.2*FL); ax.set_title(f"run {rid}  B in [{blo},{bhi}] T   df={df:.1f} T", fontsize=9)
        ax.set_xlabel("F (T)")
    fig.tight_layout(); fig.savefig(f"hera_scratch/fft_run{rid}.png", dpi=110); plt.close(fig)

    # amplitude vs B: Gaussian-windowed magnitude of the two leading tones, to read onsets
    f, Y, span, N = spec(B, R, 1.0, 10.0)
    lead = [fr for fr, a in peaks(f, Y)[:3]]
    print(f"  leading tones {['%.1f' % x for x in lead]}")
