import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft

F_L = 35.2

def load(d):
    r = open_run(d); mc = r.meta["measurement_config"]
    B = np.asarray(r.col("magnet_field")); I = np.asarray(r.col("sr0_X")) / mc["sr0_gain"]
    out = {"B": B}
    for ch in ["sr1", "sr2"]:
        sens = mc.get(f"{ch}_sens", np.inf)
        bad = np.abs(np.asarray(r.col(f"{ch}_X"))) > 0.88 * sens
        out[ch] = np.where(bad, np.nan, np.asarray(r.col(f"{ch}_X")) / I)
    return out

a1, a2 = load("data/1"), load("data/2")
B = np.concatenate([a1["B"], a2["B"]]); order = np.argsort(B); B = B[order]
R = {ch: np.concatenate([a1[ch], a2[ch]])[order] for ch in ["sr1", "sr2"]}
print(f"stitched 0.1-{B.max():.2f}T, {len(B)} pts")

windows = [(1.3, B.max()), (2.0, B.max()), (2.5, B.max()), (3.0, B.max())]
degs = [3, 5, 7]
fig, axes = plt.subplots(2, 2, figsize=(14, 9))
for row, ch in enumerate(["sr1", "sr2"]):
    g = np.isfinite(R[ch]); Bc, Rc = B[g], R[ch][g]
    axw = axes[row, 0]
    for (lo, hi) in windows:
        freqs, spec = sdh_fft(Rc.reshape(-1, 1), Bc, b_range=(lo, hi), bg_degree=5)
        m = (freqs > 2) & (freqs < 60)
        axw.plot(freqs[m], spec[0][m] / spec[0][m].max(), lw=1, label=f"B[{lo:.1f},{hi:.1f}]")
    axw.axvline(F_L, color="g", ls="--", lw=1); axw.set_title(f"{ch}: window sweep (bg_deg5, norm)")
    axw.set_xlabel("freq (T)"); axw.legend(fontsize=7)
    axd = axes[row, 1]
    for dg in degs:
        freqs, spec = sdh_fft(Rc.reshape(-1, 1), Bc, b_range=(2.0, B.max()), bg_degree=dg)
        m = (freqs > 2) & (freqs < 60)
        axd.plot(freqs[m], spec[0][m] / spec[0][m].max(), lw=1, label=f"bg_deg={dg}")
    axd.axvline(F_L, color="g", ls="--", lw=1); axd.axvline(F_L/2, color="orange", ls=":", lw=1, label="F_L/2")
    axd.set_title(f"{ch}: bg_degree sweep (B[2,{B.max():.1f}])"); axd.set_xlabel("freq (T)"); axd.legend(fontsize=7)
    # robust peak report: window B[2.5,max], bg5 (suppresses low-f envelope/MR)
    freqs, spec = sdh_fft(Rc.reshape(-1, 1), Bc, b_range=(2.5, B.max()), bg_degree=5)
    mag = spec[0]; m = freqs > 6     # ignore <6T envelope artifact band
    pk = sorted([(float(freqs[m][i]), float(mag[m][i] / mag[m].max())) for i in np.argsort(mag[m])[::-1][:5]], key=lambda t: -t[1])
    print(f"{ch} peaks (B[2.5,{B.max():.1f}], f>6T): " + ", ".join(f"{f:.1f}T({a:.2f})" for f, a in pk))
plt.tight_layout(); plt.savefig("hera_scratch/sdh_stability.png", dpi=110)
print("saved hera_scratch/sdh_stability.png")
