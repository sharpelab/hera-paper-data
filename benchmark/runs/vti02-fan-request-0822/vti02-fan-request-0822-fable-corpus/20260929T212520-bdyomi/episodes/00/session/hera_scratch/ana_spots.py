# Spot-check analysis: runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12)
# Raw R(B), measured onset (sdh_onset), FFT vs model tones (fs_count_b0).
import sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fs

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"

def load_spot(fid):
    run = open_run(f"{BASE}/{fid}")
    B = run.col("magnet_field")
    mc = run.meta["measurement_config"]
    gain = 1.0  # sr1 unity (device card)
    # I_bias from drive amplitude / bias resistor
    amp = None
    for inst in ("sr1",):
        pass
    return run, B, mc

for fid, n_cm2, side in [(6, +3.2e12, "electron"), (7, -1.2e12, "hole")]:
    run = open_run(f"{BASE}/{fid}")
    print(f"=== run {fid} ({side}, n={n_cm2:+.2e}) ===")
    print(f"cols: {run.cols}")
    B = run.col("magnet_field")
    X = run.col("sr1_X")
    # I_bias: drive amplitude / 100 MOhm. Amplitude not in columns; use meas config comment or sr1 snapshot
    try:
        ampl = run.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]
    except Exception:
        ampl = None
    print(f"sr1 drive amplitude: {ampl}")
    Ib = (ampl or 1.0) / 100e6
    R = X / Ib
    idx = np.argsort(B)
    Bs, Rs = B[idx], R[idx]
    print(f"B range {Bs.min():.3f}..{Bs.max():.3f} T, {len(Bs)} pts; R(0) ~ {Rs[:5].mean():.1f} ohm, R(max B) ~ {Rs[-5:].mean():.1f} ohm")
    print(f"T_sample {np.nanmin(run.col('T_sample')):.3f}-{np.nanmax(run.col('T_sample')):.3f} K")
    for g in ("k_2400_tg_curr", "k_2400_bg_curr"):
        c = run.col(g)
        print(f"{g}: med {np.nanmedian(c)*1e12:+.0f} pA, extremes {np.nanmin(c)*1e12:+.0f}/{np.nanmax(c)*1e12:+.0f} pA")
    n_m2 = n_cm2 * 1e4  # cm^-2 -> m^-2
    FL = float(luttinger_frequency(abs(n_m2)))
    print(f"F_L = {FL:.1f} T")
    try:
        on = sdh_onset(Rs, Bs)
        print(on.summary())
    except SdhOnsetError as e:
        print(f"SdhOnsetError: {e}")
        on = None
    # FFT over above-onset window
    blo = on.onset_b if on else 1.5
    f, a = sdh_fft(Rs.reshape(-1, 1), Bs, b_range=(max(blo, 1.0), Bs.max()))
    a = a.reshape(1, -1) if a.ndim == 2 and a.shape[-1] == 1 else np.atleast_2d(a)
    # model tones
    try:
        _, orbits = fs.abab_fs(n_m2)
        abab = [o[0] for o in orbits]
    except Exception as e:
        abab = []
        print("abab model:", e)
    try:
        r = fs.abca_fs(n_m2)
        abca = r[4]
    except Exception as e:
        abca = None
        print("abca model:", e)
    print(f"model ABAB tones: {['%.1f' % x for x in abab]}, ABCA F_total: {abca}")
    np.save(f"/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot{fid}_fft.npy", np.vstack([f, a[0]]))

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(Bs, Rs, lw=0.6)
    ax[0].set(xlabel="B (T)", ylabel="Rxx (ohm)", title=f"run {fid} raw ({side}, n={n_cm2/1e12:+.1f}e12)")
    ax[1].plot(f, a[0], lw=0.8)
    for x in abab:
        ax[1].axvline(x, color="C1", ls="--", alpha=0.7)
    if abca:
        ax[1].axvline(abca, color="C2", ls=":", alpha=0.7)
    ax[1].axvline(FL, color="k", ls="-", alpha=0.3)
    ax[1].set(xlabel="F (T)", ylabel="FFT amp (log)", title=f"FFT b>{max(blo,1.0):.2f} T; ABAB dashed, ABCA dotted, F_L grey", xlim=(0, FL * 1.6))
    fig.tight_layout()
    fig.savefig(f"/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot{fid}.png", dpi=110)
    print()
