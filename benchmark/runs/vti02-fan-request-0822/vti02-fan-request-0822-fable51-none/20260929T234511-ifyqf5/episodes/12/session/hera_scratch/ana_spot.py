"""Scratch: SdH spot checks runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D=0.
Raw R(B), background-subtracted oscillatory part, sdh_onset, sdh_fft in windows."""
import warnings, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency

base = Path(__file__).resolve().parents[1] / "data"
fig, ax = plt.subplots(3, 2, figsize=(14, 11))
for j, rid in enumerate([6, 7]):
    r = open_run(base / str(rid))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    T = r.col("T_sample")
    o = np.argsort(B); B, R, I, T = B[o], R[o], I[o], T[o]
    n12 = 3.2 if rid == 6 else -1.2
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n=== run {rid}: {r.tags[0][:60]}; {r.rows} pts, B {B.min():.2f}-{B.max():.2f}, T {T.min():.3f}-{T.max():.3f} K, "
          f"R {R.min():.1f}..{R.max():.1f} Ohm (signed), I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; F_L(full n) = {FL:.1f} T")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw R(B), n={n12:+.1f}e12 D=0"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("R (Ohm)")
    # onset
    rfs = 50e-6 / 10e-9
    for blo in (1.0, 2.0):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                on = sdh_onset(np.abs(R), B, b_lo=blo, r_full_scale=rfs)
            print(f"-- sdh_onset (b_lo={blo}):\n" + on.summary())
        except SdhOnsetError as e:
            print(f"-- sdh_onset (b_lo={blo}) FAILED: {e}")
    # FFT in windows
    for k, (b1, b2) in enumerate([(1.5, 10.0), (3.0, 10.0), (5.0, 10.0)]):
        m = (B >= b1) & (B <= b2)
        if m.sum() < 30: continue
        f, sp = sdh_fft(np.abs(R[m])[:, None], B[m], b_range=None, nfft=2048, bg_degree=5, log=False)
        sp = sp[0]; sel = (f > 2) & (f < 120)
        pk = f[sel][np.argsort(sp[sel])[::-1][:6]]
        print(f"   FFT window {b1}-{b2} T: top peaks (T): {np.round(np.sort(pk),1)}")
        ax[2, j].plot(f[sel], sp[sel] / sp[sel].max() + 1.1 * k, label=f"{b1}-{b2} T")
    ax[2, j].set_xlabel("F (T)"); ax[2, j].set_ylabel("|FFT| (offset)"); ax[2, j].legend(); ax[2, j].axvline(FL, color="k", ls=":")
    ax[2, j].set_title("SdH FFT (1/B), poly5 bg removed")
    # oscillatory part vs 1/B
    m = B >= 1.5
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[1, j].plot(1 / B[m], dR, lw=0.7); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("dR (Ohm)"); ax[1, j].set_title("R - poly5(B), B>1.5 T")
fig.tight_layout(); fig.savefig(Path(__file__).with_name("spot_runs67.png"), dpi=110)
print("saved spot_runs67.png")
