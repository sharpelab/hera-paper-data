# run 4: CNP ridge extraction + (n,D) calibration (cnp-and-dline-calibration steps 0-4)
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from hera.analysis import fan_grids, resistance_grids, GateCalibration, luttinger_frequency
from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages

fg = fan_grids("data/4")
rg = resistance_grids(fg, channels=["sr1", "sr2"])
Vbg, Vtg = fg.slow, fg.grid("k_2400_tg_volt")[0]

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
fits = {}
for ax, ch in zip(axes, ("sr1", "sr2")):
    R = np.abs(rg.R[ch])
    Rs = gaussian_filter1d(R, sigma=2, axis=1)
    idx = Rs.argmax(axis=1)
    ridge, peakR = Vtg[idx], Rs[np.arange(len(idx)), idx]
    edge = (idx <= 2) | (idx >= len(Vtg) - 3)          # guard: edge-clipped rows
    keep = ~edge
    for _ in range(5):                                  # guard: robust fit
        p = np.polyfit(Vbg[keep], ridge[keep], 1)
        res = ridge - np.polyval(p, Vbg)
        new = ~edge & (np.abs(res) < 2 * res[keep].std())
        if (new == keep).all():
            break
        keep = new
    rms = (ridge[keep] - np.polyval(p, Vbg[keep])).std()
    fits[ch] = p
    print(f"{ch}: slope {p[0]:+.4f}, intercept {p[1]:+.4f} V, rms {rms*1e3:.1f} mV, "
          f"rows kept {keep.sum()}/101 (edge-clipped {edge.sum()}), "
          f"ridge peak R [{peakR[keep].min():.0f}, {peakR[keep].max():.0f}] Ohm")
    pc = ax.pcolormesh(Vtg, Vbg, R, shading="auto", cmap="inferno")
    ax.plot(ridge[keep], Vbg[keep], "c.", ms=3)
    ax.plot(np.polyval(p, Vbg), Vbg, "c--", lw=1, label=f"fit slope {p[0]:+.3f}")
    ax.set_xlabel("V_tg (V) [fast]"); ax.set_title(f"{ch} |R| (Ohm)"); ax.legend(loc="lower left")
    fig.colorbar(pc, ax=ax)
axes[0].set_ylabel("V_bg (V) [slow]")
fig.suptitle("run 4: CNP ridge + fit (ridge V_tg vs V_bg rows — orientation stated per recipe)")
fig.tight_layout(); plt.show()

# conversion: ratio data-calibrated, scale anchored on c_tg stack prior (15.6 nm hBN)
slope = np.mean([fits[c][0] for c in fits]); b = np.mean([fits[c][1] for c in fits])
c_tg = stack_capacitance([(15.6, 3)])
c_bg = -slope * c_tg
n_off_disp = -calc_nD(b, 0, c_tg, c_bg)[0]           # sharpelab display units: 1e12 cm^-2
cal = GateCalibration(c_tg=c_tg, c_bg=c_bg, n_offset=n_off_disp * 1e16, D_offset=0.0)  # SI
print(f"\ncombined slope {slope:+.4f} (c_bg/c_tg = {-slope:.4f}; geometry prior 1.300, {100*(-slope/1.3-1):+.1f}%)")
print(f"c_tg = {c_tg:.4e} F/m^2 (prior anchor), c_bg = {c_bg:.4e} F/m^2 (ratio-calibrated)")
print(f"n_offset = {n_off_disp:+.4f} e12 cm^-2; D_offset = 0 (stated assumption — no D-symmetric feature examined yet)")

# D=0 line, clipped to validators by dropping; realized window + F_L
ns = np.linspace(-8, 8, 1601)
vt, vb = calc_gate_voltages(ns, np.zeros_like(ns), c_tg, c_bg, n_offset=n_off_disp)
ok = (vt >= -3.0) & (vt <= 3.0) & (vb >= -4.5) & (vb <= 4.5)
print(f"D=0 realized n window: [{ns[ok].min():.2f}, {ns[ok].max():.2f}] e12 cm^-2 (TG-limited)")
for n_req in (-6.0, 6.0):
    vtg_p, vbg_p = calc_gate_voltages(n_req, 0.0, c_tg, c_bg, n_offset=n_off_disp)
    FL = float(luttinger_frequency(abs(n_req) * 1e16))
    print(f"  n = {n_req:+.1f} e12 cm^-2, D=0 -> (Vtg, Vbg) = ({vtg_p:+.3f}, {vbg_p:+.3f}); "
          f"F_L = {FL:.1f} T, Nyquist d(1/B) <= {1/(2*FL):.2e} /T")
