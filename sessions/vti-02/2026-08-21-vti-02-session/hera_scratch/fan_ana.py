"""Landau fan read: raw map, per-column FFT in 1/B, F(n) peak set vs F_L and the model curves.
Usage: menv python hera_scratch/fan_ana.py <run_id> [scale]
"""
import sys, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, fan_grids, resistance_grids, sdh_fft, luttinger_frequency
import importlib.util
def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, Path.home() / "measurement_env/hera/models" / rel / "fs_count_b0.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

DATA = Path(__file__).resolve().parents[1] / "data"
rid = int(sys.argv[1]); scale = float(sys.argv[2]) if len(sys.argv) > 2 else 0.90
C_TG, C_BG, N_OFF = 2.7961e-3, 2.0330e-3, -0.069
r = open_run(DATA / str(rid)); f = fan_grids(r); rg = resistance_grids(f)
B = f.slow; R = rg.R["sr1"]; Vtg = f.grid("k_2400_tg_volt")[0]; Vbg = f.grid("k_2400_bg_volt")[0]
e = 1.602176634e-19
n_design = (C_TG * Vtg + C_BG * Vbg) / e * 1e-16 + N_OFF          # design frame, 1e12
n_act = scale * n_design
print(f"run {rid}: {f.nrows}/{len(r.meta['slow_setpoints'][0])} rows, nfast {f.nfast}; B {B.min():.2f}..{B.max():.2f} T; n_design {n_design.min():.2f}..{n_design.max():.2f} (x{scale} actual)")
print(f"R: {np.nanmin(R):.0f}..{np.nanmax(R):.0f} Ohm; I {rg.current.min()*1e9:.2f}..{rg.current.max()*1e9:.2f} nA; T {f.grid('T_sample').min():.3f}..{f.grid('T_sample').max():.3f} K")
rfs = 50e-6 / 1e-8
print(f"railed (>0.9 x 5 kOhm): {(np.abs(R) > 0.9*rfs).sum()} pts")

order = np.argsort(B); Bs = B[order]; Rs = R[order]
fig, axs = plt.subplots(1, 3, figsize=(19, 5.5))
ax = axs[0]; pc = ax.pcolormesh(n_act, Bs, Rs, shading="nearest", cmap="RdBu_r", vmin=np.nanpercentile(Rs, 2), vmax=np.nanpercentile(Rs, 98))
plt.colorbar(pc, ax=ax, label="R (B1-B2) [Ohm]"); ax.set_xlabel("n [1e12 cm^-2] (x scale)"); ax.set_ylabel("B [T]"); ax.set_title(f"run {rid} raw")
# per-column FFT (uniform-1/B record; sdh_fft resamples/detrends in B)
if f.nrows >= 8:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        freqs, spec = sdh_fft(Rs, Bs, b_range=(Bs.min(), Bs.max()), bg_degree=3, nfft=2048, log=False)
    spec_n = spec / np.nanmax(spec[:, freqs > 2], axis=1, keepdims=True)
    ax = axs[1]; pc = ax.pcolormesh(n_act, freqs, spec_n.T, shading="nearest", cmap="magma", vmin=0, vmax=1)
    ax.set_ylim(0, 60); ax.set_xlabel("n [1e12]"); ax.set_ylabel("F [T]"); ax.set_title(f"per-column FFT (B {Bs.min():.1f}-{Bs.max():.1f} T, bg deg 3)")
    ncol = np.linspace(0.3, 4.0, 50)
    FL = luttinger_frequency(ncol * 1e16)
    ax.plot(ncol, FL, "w--", lw=1, label="F_L (g=4)")
    try:
        m4 = _load("tetra_fs", "tetralayer_fs_count")
        ab = [m4.abab_fs(n * 1e16)[1] for n in ncol[ncol >= 0.4]]
        nn = ncol[ncol >= 0.4]
        for k, lab in ((0, "ABAB light"), (-1, "ABAB heavy")):
            ax.plot(nn, [o[k][0] for o in ab], "c-", lw=1, label=lab)
    except Exception as ex:
        print("ABAB model overlay failed:", ex)
    try:
        m3 = _load("tri_fs", "trilayer_fs_count")
        tri = [m3.aba_fs(n * 1e16)[1] for n in ncol[ncol >= 0.4]]
        for k, lab in ((0, "ABA light"), (-1, "ABA heavy")):
            ax.plot(ncol[ncol >= 0.4], [o[k][0] for o in tri], "y:", lw=1, label=lab)
    except Exception as ex:
        print("trilayer overlay failed:", ex)
    seg = 10.34 * 1.745 * (0.2865 * ncol / scale + 0.22) * 1.0
    ax.plot(ncol, seg, "g:", lw=1, label="series segment (prior)")
    ax.legend(fontsize=7, loc="upper left")
    # peak table per column
    ax = axs[2]
    print("column peaks (n_act : F [T] (rel amp) ...):")
    for j in range(0, f.nfast, max(1, f.nfast // 14)):
        sp = spec_n[j]; m = freqs > 2.5
        pk = [(freqs[i], sp[i]) for i in range(2, len(sp) - 2) if m[i] and sp[i] > sp[i-1] and sp[i] > sp[i+1] and sp[i] > 0.25]
        pk = sorted(pk, key=lambda t: -t[1])[:5]
        print(f"  n={n_act[j]:+.2f}: " + ", ".join(f"{f0:.1f} ({a:.2f})" for f0, a in pk) + f"   F_L={luttinger_frequency(n_act[j]*1e16):.1f}")
        ax.plot(freqs, sp + 0.9 * j / f.nfast * 8, lw=0.7)
    ax.set_xlim(0, 60); ax.set_xlabel("F [T]"); ax.set_ylabel("FFT (offset by column)"); ax.set_title("column spectra")
plt.tight_layout(); out = Path(__file__).resolve().parent / f"fan_{rid}.png"; plt.savefig(out, dpi=90); print("saved", out)
