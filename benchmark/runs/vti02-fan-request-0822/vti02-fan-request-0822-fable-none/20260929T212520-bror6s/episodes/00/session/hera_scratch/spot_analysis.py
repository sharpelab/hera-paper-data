# SdH spot checks: run 6 (electron, n=+3.2e12, B 0->10 T) and run 7 (hole, n=-1.2e12, B 10->0.3 T)
import numpy as np, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, luttinger_frequency

OUT = "hera_scratch"

def load(rid):
    r = open_run(f"data/{rid}")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    I = r.col(cur.col) / cur.gain
    vch = [c for c in chans if c.cid == "sr1"][0]
    R = (r.col(vch.col) / vch.gain) / I
    B = r.col("magnet_field")
    # sort ascending in B, drop |B| < 0.05 (avoid 1/B blowup later; keep for R(B) plot)
    idx = np.argsort(B)
    return r, B[idx], R[idx], I[idx]

results = {}
fig, axes = plt.subplots(2, 2, figsize=(12, 7))
for row, (rid, tag, sens) in enumerate([(6, "electron n=+3.2e12", 50e-6), (7, "hole n=-1.2e12", 50e-6)]):
    r, B, R, I = load(rid)
    Ib = np.median(np.abs(I))
    r_fs = sens / Ib
    print(f"=== run {rid} ({tag}): {len(B)} pts, B {B.min():.3f}..{B.max():.3f} T, "
          f"I_bias~{Ib*1e9:.2f} nA, R(Bmin)={R[np.argmin(np.abs(B))]:.1f} ohm, Rmax={np.nanmax(np.abs(R)):.1f} ohm, r_fs={r_fs:.0f}")
    ax = axes[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (ohm)"); ax.set_title(f"run {rid} — {tag}")
    m = B > 0.29
    try:
        o = sdh_onset(np.abs(R[m]), B[m], r_full_scale=r_fs)
        print(o.summary())
        results[rid] = o
    except Exception as e:
        print(f"run {rid} sdh_onset: {type(e).__name__}: {e}")
        results[rid] = None
    # FFT over the useful window
    mm = B > 1.0
    freqs, spec = sdh_fft(np.abs(R[mm])[:, None], B[mm], nfft=4096, log=False)
    ax2 = axes[row, 1]
    ax2.plot(freqs, spec[0], lw=0.8)
    ax2.set_xlim(0, 120); ax2.set_xlabel("F (T)"); ax2.set_ylabel("FFT mag")
    ax2.set_title(f"run {rid} FFT (B>1 T)")
    # reference lines: full-density single-FS Onsager frequency
    n_si = (3.2e12 if rid == 6 else 1.2e12) * 1e4
    FL = luttinger_frequency(n_si)
    ax2.axvline(FL, color="r", ls="--", lw=0.8, label=f"F_L={FL:.1f} T (1 FS, g=4)")
    ax2.legend(fontsize=8)
fig.tight_layout()
fig.savefig(f"{OUT}/spot_runs67.png", dpi=110)
print("saved", f"{OUT}/spot_runs67.png")
