"""Runs 6 & 7 — raw-first: look at the oscillations in 1/B, then FFT with a proper detrend."""
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

def spec(B, R, blo, bhi, deg=5, nfft=1 << 16):
    m = (B >= blo) & (B <= bhi)
    Bw, Rw = B[m], R[m]
    Rd = Rw - np.polyval(np.polyfit(Bw, Rw, deg), Bw)
    x = 1.0 / Bw; xi = np.linspace(x.min(), x.max(), 4096)
    yi = np.interp(xi, x, Rd)
    yi = yi - np.polyval(np.polyfit(xi, yi, 2), xi)      # kill any residual ramp in 1/B too
    w = np.hanning(len(xi))
    Y = np.abs(np.fft.rfft(yi * w, n=nfft))
    f = np.fft.rfftfreq(nfft, d=xi[1] - xi[0])
    return f, Y, x.max() - x.min(), m.sum(), (Bw, Rd)

def peaks(f, Y, span, fmin=3.0, fmax=100.0, nmax=10):
    k = (f > fmin) & (f < fmax); fk, Yk = f[k], Y[k]
    idx = [i for i in range(1, len(Yk) - 1) if Yk[i] > Yk[i-1] and Yk[i] > Yk[i+1]]
    idx.sort(key=lambda i: -Yk[i])
    out, used = [], []
    res = 1.0 / span
    for i in idx:
        if all(abs(fk[i] - u) > res for u in used):
            out.append((fk[i], Yk[i])); used.append(fk[i])
        if len(out) >= nmax: break
    return out, np.median(Yk)

for rid, n_spot in ((6, 3.2), (7, -1.2)):
    B, R, Ib = trace(rid)
    FL = float(luttinger_frequency(abs(n_spot) * 1e16))
    print(f"\n===== run {rid}: n = {n_spot:+.2f}e12  F_L = {FL:.2f} T =====")
    fig, axes = plt.subplots(3, 2, figsize=(13, 11))
    wins = [(0.5, 10.0), (1.0, 10.0), (1.5, 10.0), (2.5, 10.0), (1.0, 3.0), (4.0, 10.0)]
    for ax, (blo, bhi) in zip(axes.ravel(), wins):
        f, Y, span, N, (Bw, Rd) = spec(B, R, blo, bhi)
        pk, med = peaks(f, Y, span)
        print(f"  B[{blo},{bhi}] N={N:4d} 1/B span={span:.4f} df={1/span:.2f} T  noise~{med:.1f}")
        for fr, a in pk[:6]:
            if a < 4 * med: continue
            print(f"      f = {fr:6.2f} T  amp {a:8.1f} ({a/med:5.1f}x)  f/F_L = {fr/FL:5.3f}  "
                  f"periods = {fr*span:5.1f}")
        ax.plot(f, Y, lw=0.8)
        for x0, lab, col in ((FL, "F_L", "k"), (0.72*FL, ".72", "r"), (0.28*FL, ".28", "b")):
            ax.axvline(x0, color=col, ls="--", lw=0.8)
        ax.set_xlim(0, 2.5*FL); ax.set_title(f"run {rid} B[{blo},{bhi}] df={1/span:.1f}T", fontsize=9)
        ax.set_xlabel("F (T)")
    fig.tight_layout(); fig.savefig(f"hera_scratch/fft3_run{rid}.png", dpi=110); plt.close(fig)

    # raw look
    fig, ax = plt.subplots(2, 1, figsize=(11, 7))
    ax[0].plot(B, R, lw=0.7); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx (Ohm)")
    ax[0].set_title(f"run {rid} raw  n={n_spot}e12")
    m = B >= 0.5; Bw = B[m]; Rd = R[m] - np.polyval(np.polyfit(Bw, R[m], 5), Bw)
    ax[1].plot(1/Bw, Rd, lw=0.7, marker='.', ms=2); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("dRxx (Ohm)")
    ax[1].set_title("detrended (poly5 in B) vs 1/B")
    fig.tight_layout(); fig.savefig(f"hera_scratch/raw_run{rid}.png", dpi=110); plt.close(fig)
