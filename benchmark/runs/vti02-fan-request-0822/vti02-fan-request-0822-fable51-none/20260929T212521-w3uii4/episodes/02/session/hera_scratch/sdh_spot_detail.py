import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels
fig, ax = plt.subplots(3, 2, figsize=(14, 11))
for k, rid in enumerate([6, 7]):
    r = open_run(f"data/{rid}"); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X")/ch["sr0"].gain; X = r.col("sr1_X"); P1 = r.col("sr1_P"); P0 = r.col("sr0_P")
    R = X/I
    o = np.argsort(B); B, R, P1, P0, I = B[o], R[o], P1[o], P0[o], I[o]
    # setpoint vs readback
    sp = np.sort(np.asarray(r.setpoints, float)); print(f"run {rid}: setpoint-readback |dB| max {np.abs(B-sp).max()*1e3:.1f} mT, median {np.median(np.abs(B-sp))*1e3:.2f} mT")
    ax[0,k].plot(B, R, "-", lw=0.7); ax[0,k].set_xlim(0, 4); ax[0,k].set_title(f"run {rid}: R vs B, 0-4 T zoom"); ax[0,k].set_ylabel("R (Ohm)")
    ax[1,k].plot(1/B[B>0.9], R[B>0.9], "-", lw=0.7); ax[1,k].set_xlabel("1/B (1/T)"); ax[1,k].set_title("R vs 1/B (B>0.9)")
    ax[2,k].plot(B, P1, ".", ms=2, label="sr1 phase"); ax[2,k].plot(B, P0, ".", ms=2, label="sr0 phase"); ax[2,k].legend(); ax[2,k].set_xlabel("B (T)"); ax[2,k].set_title("phases")
    # minima positions in 1/B for B between 1 and 4 T
    from scipy.signal import find_peaks
    m = (B > 1.0) & (B < 4.0)
    mins, _ = find_peaks(-R[m], prominence=3)
    Bm = B[m][mins]
    print(f"  minima B (1-4 T): {np.round(Bm, 3)}")
    print(f"  1/B spacing: {np.round(np.diff(1/Bm), 4)}")
    print(f"  R at minima: {np.round(R[m][mins], 1)}")
    # high-B: minima 4-10 T
    m = (B > 4.0)
    mins, _ = find_peaks(-R[m], prominence=5); Bm = B[m][mins]
    print(f"  minima B (4-10 T): {np.round(Bm, 3)}; R {np.round(R[m][mins], 0)}")
    print(f"  I range {I.min()*1e9:.3f}-{I.max()*1e9:.3f} nA; I vs B: at 0 T {I[0]*1e9:.3f}, 10 T {I[-1]*1e9:.3f}")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spot_detail.png", dpi=100)
