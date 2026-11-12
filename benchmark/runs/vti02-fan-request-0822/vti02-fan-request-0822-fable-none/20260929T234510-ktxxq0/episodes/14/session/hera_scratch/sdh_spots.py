"""SdH spot-check analysis, runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12), D=0.
Raw R(B), onset + tone table via sdh_onset, FFT in 1/B via sdh_fft.
Model anchors (md_spot_e/h): e-side total F=33.1 T; ABAB pair ~7.5/25.6 T; ABCA single 33.1 T.
h-side total F=12.4 T; ABAB pair ~5.3/7.1 T; ABCA LK-dead."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, SdhOnsetError

fig, ax = plt.subplots(2, 3, figsize=(15, 8))
for row, (rid, tag) in enumerate([(6, "electron n=+3.2e12"), (7, "hole n=-1.2e12")]):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field")
    chs = {c.cid: c for c in resolve_channels(r.meta)}
    cur = current_channel(list(chs.values()))
    I = r.col(cur.col) / cur.gain
    Rxx = (r.col("sr1_X") / chs["sr1"].gain) / I
    srt = np.argsort(B); B, Rxx, I = B[srt], Rxx[srt], I[srt]
    print(f"=== run {rid} ({tag}): {r.rows} pts, B {B.min():.2f}-{B.max():.2f} T, "
          f"R {np.abs(Rxx).min():.0f}-{np.abs(Rxx).max():.0f} Ohm, I {np.abs(I).mean()*1e9:.3f} nA ===")
    ax[row, 0].plot(B, np.abs(Rxx), lw=0.6)
    ax[row, 0].set_xlabel("B (T)"); ax[row, 0].set_ylabel("|Rxx| (Ohm)")
    ax[row, 0].set_title(f"run {rid} raw — {tag}")
    # full-scale check: sens 50 uV, I_bias nominal from measured I
    r_fs = 50e-6 / np.abs(I).mean()
    print(f"  full-scale ~{r_fs:.0f} Ohm; max R = {np.abs(Rxx).max():.0f} ({100*np.abs(Rxx).max()/r_fs:.0f}% FS)")
    # onset + tones
    try:
        o = sdh_onset(np.abs(Rxx), B, r_full_scale=r_fs)
        print(o.summary())
    except SdhOnsetError as e:
        print(f"  sdh_onset: FAILED — {e}")
        o = None
    # FFT over sensible windows
    for k, (blo, bhi) in enumerate([(1.5, B.max()), (3.0, B.max())]):
        sel = (B >= blo) & (B <= bhi)
        f, s = sdh_fft(np.abs(Rxx[sel])[:, None], B[sel])
        s = s[0]
        ax[row, 1 + k].plot(f, s / s.max(), lw=0.8)
        ax[row, 1 + k].set_xlim(0, 60); ax[row, 1 + k].set_xlabel("F (T)")
        ax[row, 1 + k].set_title(f"run {rid} FFT, B {blo:.1f}-{bhi:.0f} T")
        top = f[np.argsort(s)[::-1][:6]]
        print(f"  FFT window {blo:.1f}-{bhi:.1f} T: top peaks at F = {np.sort(top)} T")
    for a in ax[row, 1:]:
        for F, c in [(33.1, "r"), (25.6, "g"), (7.5, "g"), (12.4, "r"), (5.3, "b"), (7.1, "b")]:
            a.axvline(F, color=c, ls=":", lw=0.6, alpha=0.5)
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spots.png", dpi=110)
print("saved hera_scratch/sdh_spots.png")
