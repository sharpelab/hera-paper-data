"""First read of SdH spot checks runs 6 (electron, n=+3.2e12, B 0->10) and 7 (hole, n=-1.2e12, B 10->0.3)."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, SdhOnsetError, summarize_run
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for k, rid in enumerate([6, 7]):
    r = open_run(f"data/{rid}")
    print(summarize_run(r)); print("comments:", r.meta["comments"])
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X")/ch["sr0"].gain; R = (r.col("sr1_X")/ch["sr1"].gain)/I
    T = r.col("T_sample"); itg = r.col("k_2400_tg_curr"); ibg = r.col("k_2400_bg_curr")
    sens = r.meta["instruments"].get("sr1", {}).get("sensitivity") if isinstance(r.meta.get("instruments"), dict) else None
    print(f"run {rid}: {len(B)} pts, B {B.min():.3f}..{B.max():.3f}, R {R.min():.1f}..{R.max():.1f} Ohm, I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA, T {T.mean():.3f}±{T.std():.3f}, Itg {itg.min()*1e12:+.0f}..{itg.max()*1e12:+.0f} pA, Ibg {ibg.min()*1e12:+.0f}..{ibg.max()*1e12:+.0f} pA, sr1 sens {sens}")
    o = np.argsort(B); B, R = B[o], R[o]
    ax[k,0].plot(B, R, "-", lw=0.8); ax[k,0].set_xlabel("B (T)"); ax[k,0].set_ylabel("Rxx (Ohm)"); ax[k,0].set_title(f"run {rid} raw")
    m = B > 1.0
    try:
        so = sdh_onset(R[m], B[m], r_full_scale=50e-6/10e-9)
        print(so.summary())
    except SdhOnsetError as e:
        print("sdh_onset:", e)
    for lo in [1.5, 2.5, 4.0]:
        f, sp = sdh_fft(R[m][:, None], B[m], b_range=(lo, B.max()), bg_degree=5, log=False)
        s = sp[0]; ax[k,1].plot(f, s/s[f>3].max(), label=f"B>{lo}")
        pk = f[(f>3)][np.argsort(s[f>3])[-4:]]
        print(f"  fft B>{lo}: top freqs {np.round(np.sort(pk),1)} T")
    ax[k,1].set_xlim(0, 80); ax[k,1].set_xlabel("F (T)"); ax[k,1].legend(); ax[k,1].set_title(f"run {rid} SdH FFT (lin R, bg deg 5)")
    # also dR/dB style: residual after polyfit plot inset
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spot_read.png", dpi=100); print("saved")
