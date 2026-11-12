"""Analyze runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12) SdH spot checks."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, SdhOnsetError

def load(i):
    r = open_run(f"data/{i}")
    B = r.col("magnet_field")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    I = r.col_at(cur.idx)/cur.gain
    v = [c for c in chans if not c.is_current][0]
    V = r.col_at(v.idx)/v.gain
    R = V / I
    return r, B, R, I, r.col("T_sample")

fig, axes = plt.subplots(2, 3, figsize=(16, 8))
for k, i in enumerate((6, 7)):
    r, B, R, I, T = load(i)
    o = np.argsort(B)
    Bs, Rs = B[o], R[o]
    ax = axes[k, 0]
    ax.plot(B, np.abs(R), lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {i} raw: |Rxx| vs B  (T {T.mean():.2f} K, I {np.abs(I).mean()*1e9:.2f} nA)")

    # background-subtracted vs 1/B
    m = Bs > 1.0
    p = np.polyfit(Bs[m], Rs[m], 5)
    dR = Rs[m] - np.polyval(p, Bs[m])
    ax = axes[k, 1]
    ax.plot(1.0 / Bs[m], dR, lw=0.8)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)")
    ax.set_title(f"run {i}: poly5-subtracted, B>1 T")

    freqs, spec = sdh_fft(Rs[:, None], Bs, b_range=(1.0, Bs.max()), nfft=2048, bg_degree=5, log=False)
    sp = spec[0]
    ax = axes[k, 2]
    ax.plot(freqs, sp, lw=0.9)
    ax.set_xlim(0, 60); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT|")
    ax.set_title(f"run {i}: SdH FFT (B 1 - {Bs.max():.0f} T)")
    top = np.argsort(sp)[::-1][:400]
    # local maxima
    pk = [j for j in range(2, len(sp) - 2) if sp[j] == max(sp[j-2:j+3]) and freqs[j] > 2]
    pk = sorted(pk, key=lambda j: -sp[j])[:8]
    print(f"--- run {i}: I={np.abs(I).mean()*1e9:.3f} nA, T={T.mean():.3f} K, "
          f"R(B=0..0.2)={np.abs(Rs[Bs<0.25]).mean():.1f} Ohm, R(max)={np.abs(Rs).max():.1f} Ohm")
    print("   FFT peaks (F T, rel amp):", [(round(freqs[j],2), round(sp[j]/sp[pk[0]],3)) for j in pk])
    try:
        so = sdh_onset(Rs, Bs, r_full_scale=50e-6/np.abs(I).mean())
        print(so.summary())
    except SdhOnsetError as e:
        print("   sdh_onset FAILED:", e)

plt.tight_layout(); plt.savefig("hera_scratch/spot67.png", dpi=110)
print("saved hera_scratch/spot67.png")
