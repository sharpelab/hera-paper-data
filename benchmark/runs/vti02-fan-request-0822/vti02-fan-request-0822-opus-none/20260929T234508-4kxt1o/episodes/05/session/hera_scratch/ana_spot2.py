"""Run 6/7 follow-up: point-to-point noise (sets the fan sensitivity choice) and
LL-minima indexing in 1/B (sets the fan's n range / expected F scale)."""
import numpy as np
from pathlib import Path
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, luttinger_frequency

DD = Path("/home/hera/measurements/zack/20260822-vti-02/data")

fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for j, (rid, nspot) in enumerate([(6, +3.2), (7, -1.2)]):
    r = open_run(DD / str(rid))
    ch = resolve_channels(r.meta); cur = current_channel(ch)
    I = r.col_at(cur.idx) / cur.gain
    B = r.col("magnet_field"); V = r.col("sr1_X")
    o = np.argsort(B); B, V, I = B[o], V[o], I[o]
    R = np.abs(V / I)
    fs = 50e-6 / np.median(np.abs(I))

    # point-to-point noise from the second difference in a smooth high-B window
    m = (B > 8.5)
    d2 = np.diff(V[m], 2)
    sig_V = np.std(d2) / np.sqrt(6)
    print(f"run {rid}: sr1 noise {sig_V*1e9:.2f} nV rms/pt = {sig_V/np.median(np.abs(I)):.2f} Ohm "
          f"({100*sig_V/50e-6:.3f} % of the 50 uV FS)")

    # LL minima -> index vs 1/B
    m = B > 1.2
    Bm, Rm = B[m], gaussian_filter1d(R[m], 2)
    pk, _ = find_peaks(-Rm, prominence=0.05 * (Rm.max() - Rm.min()))
    Bmin = Bm[pk]
    invB = 1 / Bmin
    print(f"  minima at B = {', '.join(f'{b:.3f}' for b in Bmin)}")
    if len(invB) >= 3:
        k = np.arange(len(invB))
        # minima are equally spaced in 1/B with spacing 1/F; index descending in B
        cf = np.polyfit(k, np.sort(invB), 1)
        F = 1 / abs(cf[0])
        print(f"  1/B spacing {abs(cf[0]):.5f} 1/T -> F = {F:.2f} T "
              f"(gate-cal F_L(full n) = {luttinger_frequency(abs(nspot)*1e16):.2f} T; ratio {F/luttinger_frequency(abs(nspot)*1e16):.3f})")
        print(f"  implied n if F is the full-density 4-fold surface: n = 4 e F / h = {4*1.602176634e-19*F/6.62607015e-34*1e-16:+.3f}e12 cm^-2")
        ax[1, j].plot(np.sort(invB), k, "o")
        ax[1, j].plot(np.sort(invB), (np.sort(invB) - cf[1]) / cf[0], "-", lw=0.8)
        ax[1, j].set_xlabel("1/B_min (1/T)"); ax[1, j].set_ylabel("index"); ax[1, j].set_title(f"run {rid} LL index, F = {F:.1f} T")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].plot(Bmin, np.interp(Bmin, B, R), "rv", ms=5)
    ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx (Ohm)"); ax[0, j].set_title(f"run {rid} minima (n_gate = {nspot:+.1f}e12)")

    # filling factors implied by the gate density
    nu = abs(nspot) * 1e16 * 6.62607015e-34 / (1.602176634e-19 * Bmin)
    print(f"  nu (gate n) at those minima: {', '.join(f'{v:.2f}' for v in nu)}")

fig.tight_layout(); fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_llindex.png", dpi=110)
print("saved spot_llindex.png")
