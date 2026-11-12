import json, os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from sharpelab_nb import gates

D = "data/0"; I_BIAS = 5e-9
meta = json.load(open(f"{D}/metadata.json")); cols = meta["columns"]
a = np.loadtxt(f"{D}/data.tsv.gz")
idx = {c: i for i, c in enumerate(cols)}
bg_sp = np.array(meta["slow_setpoints"]); tg_sp = np.array(meta["fast_setpoints"])
nB, nT = len(bg_sp), len(tg_sp)
bg = a[:, idx["k_2400_volt"]]; tg = a[:, idx["DC_bias"]]

def grid(chan):
    R = (a[:, idx[chan]] / I_BIAS).reshape(nB, nT)
    return R

def ridge_of(chan, smooth=1.5):
    R = grid(chan)
    tgc, rmax = [], []
    for i in range(nB):
        rs = gaussian_filter1d(R[i], smooth)
        sel = rs >= 0.98 * rs.max()
        tgc.append(tg_sp[sel].mean()); rmax.append(rs.max())
    return np.array(tgc), np.array(rmax)

fits = {}
for ch in ["sr1_X", "sr2_X"]:
    tgc, rmax = ridge_of(ch)
    p = np.polyfit(bg_sp, tgc, 1)
    resid = tgc - np.polyval(p, bg_sp)
    fits[ch] = dict(tgc=tgc, slope=p[0], b=p[1], resid=resid, rmax=rmax)
    print(f"{ch}: slope={p[0]:+.4f} c_bg/c_tg={-p[0]:+.4f} b={p[1]:+.4f}V rms={resid.std()*1e3:.1f}mV")

# ---- canonical calibration: average the two consistent Rxx channels ----
slope = np.mean([fits[c]["slope"] for c in fits]); ratio = -slope
b_int = np.mean([fits[c]["b"] for c in fits])
c_tg = gates.stack_capacitance([(15.6, 3)])      # anchor: geometry prior (15.6 nm hBN)
c_bg = ratio * c_tg                               # data-calibrated ratio
n_offset = -gates.calc_nD(b_int, 0.0, c_tg, c_bg)[0]
print(f"\nCALIB: ratio c_bg/c_tg={ratio:.4f} | c_tg={c_tg:.4e}(geom) c_bg={c_bg:.4e}(ratio) | b={b_int:+.4f}V | n_offset={n_offset:+.4f}e12")

# closure check: n along fitted ridge ~ 0
vbg_line = np.linspace(-4.5, 4.5, 200); vtg_line = slope * vbg_line + b_int
n_line, D_line = gates.calc_nD(vtg_line, vbg_line, c_tg, c_bg, n_offset, 0.0)
print(f"closure: max|n| on ridge={np.abs(n_line).max():.4f}e12  D-range on ridge=[{D_line.min():.3f},{D_line.max():.3f}]V/nm")

# ---- D=0 line design, clip to validators by dropping ----
TGv, BGv = (-6.0, 7.0), (-4.5, 4.5)
ns = np.linspace(-5, 5, 401)
Vtg0, Vbg0 = gates.calc_gate_voltages(ns, np.zeros_like(ns), c_tg, c_bg, n_offset, 0.0)
keep = (Vtg0 >= TGv[0]) & (Vtg0 <= TGv[1]) & (Vbg0 >= BGv[0]) & (Vbg0 <= BGv[1])
print(f"D=0 line realized n-window: [{ns[keep].min():+.2f}, {ns[keep].max():+.2f}]e12  ({keep.sum()}/{len(ns)} pts in-range)")
# check D constant on designed line
nchk, Dchk = gates.calc_nD(Vtg0[keep], Vbg0[keep], c_tg, c_bg, n_offset, 0.0)
print(f"D=0 line roundtrip: max|D|={np.abs(Dchk).max():.2e}V/nm  n monotonic={np.all(np.diff(nchk)>0)}")

# ================= FIGURES =================
fig, axes = plt.subplots(2, 2, figsize=(13, 10))
for ax, ch in zip(axes[0], ["sr1_X", "sr2_X"]):
    R = grid(ch)
    pc = ax.pcolormesh(tg_sp, bg_sp, np.clip(R, 0, 4400), shading="auto", cmap="inferno")
    ax.plot(fits[ch]["tgc"], bg_sp, "c.", ms=4, label="ridge (plateau center)")
    ax.plot(fits[ch]["slope"]*bg_sp+fits[ch]["b"], bg_sp, "w-", lw=1, label=f"fit s={fits[ch]['slope']:.3f}")
    ax.plot(Vtg0[keep], Vbg0[keep], "g--", lw=1.2, label="D=0 line")
    ax.set_xlabel("V_tg (DC_bias, V)"); ax.set_ylabel("V_bg (V)")
    ax.set_title(f"{ch}  Rxx [Ω, clipped 4.4k]"); ax.legend(fontsize=7, loc="upper right")
    fig.colorbar(pc, ax=ax)
ax = axes[1, 0]
for ch in fits:
    ax.plot(bg_sp, fits[ch]["resid"]*1e3, ".-", label=f"{ch} rms={fits[ch]['resid'].std()*1e3:.1f}mV")
ax.axhline(0, color="k", lw=0.5); ax.set_xlabel("V_bg (V)"); ax.set_ylabel("ridge fit residual (mV)")
ax.set_title("CNP-line residuals vs V_bg (curvature check)"); ax.legend(fontsize=8)
ax = axes[1, 1]
ax.plot(ns[keep], Vtg0[keep], label="V_tg(n) @ D=0")
ax.plot(ns[keep], Vbg0[keep], label="V_bg(n) @ D=0")
ax.set_xlabel("n (1e12 cm^-2)"); ax.set_ylabel("gate V"); ax.set_title("D=0 line design (clipped)"); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig("hera_scratch/cnp_calib.png", dpi=110)
print("\nsaved hera_scratch/cnp_calib.png")
