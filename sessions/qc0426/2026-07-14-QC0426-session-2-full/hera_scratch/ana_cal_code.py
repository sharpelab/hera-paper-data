# Run 4 — map re-form, ridge fits, calibration (proven in hera_scratch/cnp_cal2.py)
from scipy.ndimage import gaussian_filter1d
from scipy.constants import epsilon_0, e as qe
from sharpelab_nb.gates import calc_gate_voltages

r4 = run(4)
fg = fan_grids(r4)
rg = resistance_grids(fg)
vbg = fg.slow
vtg = np.asarray(fg.grid("k_2400_tg_volt"))[0]
RAIL = 4.3e3  # sr1-3 sens 2e-5 rails at ~4.37 kOhm @ 5 nA

def extract_ridge(ch):
    R = np.asarray(rg.R[ch]); ridge, keep = [], []
    for i in range(R.shape[0]):
        row = gaussian_filter1d(R[i], 2); j = int(np.argmax(row))
        if np.sum(R[i] > RAIL) >= 3:
            idx = np.where(R[i] > RAIL)[0]
            if idx.max() - idx.min() < 20: j = int(np.round(idx.mean()))
            else: ridge.append(np.nan); keep.append(False); continue
        ridge.append(vtg[j]); keep.append(2 < j < len(row) - 3)
    ridge, keep = np.array(ridge), np.array(keep)
    k = keep & np.isfinite(ridge)
    for _ in range(4):
        p = np.polyfit(vbg[k], ridge[k], 1)
        res = ridge - np.polyval(p, vbg); s = np.nanstd(res[k])
        k2 = keep & np.isfinite(ridge) & (np.abs(res) < 2 * s)
        if k2.sum() == k.sum(): break
        k = k2
    return ridge, k, p, float(np.nanstd(res[k]))

fits = {ch: extract_ridge(ch) for ch in ("sr1", "sr2")}
for ch, (_, k, p, rms) in fits.items():
    print(f"{ch}: slope {p[0]:+.4f}, intercept {p[1]:+.4f} V, resid rms {rms*1e3:.1f} mV, rows {k.sum()}/61")

# calibration: anchor c_tg at geometry (15.6 nm hBN); ratio + intercept from data (channel mean)
c_tg = epsilon_0 * 3 / 15.6e-9
ratio = -np.mean([fits["sr1"][2][0], fits["sr2"][2][0]])
c_bg = ratio * c_tg
b = np.mean([fits["sr1"][2][1], fits["sr2"][2][1]])
n_offset = -c_tg * b / qe                    # SI m^-2 (hera GateCalibration convention)
cal = GateCalibration(c_tg, c_bg, n_offset=n_offset)   # session calibration, D_offset = 0 (stated assumption)
n_off_e12 = n_offset * 1e-16                 # sharpelab_nb.gates convention (1e12 cm^-2)
print(f"ratio c_bg/c_tg = {ratio:.4f} (geometry prior 1.300); c_tg = {c_tg:.4e} (anchor), c_bg = {c_bg:.4e} F/m^2")
print(f"intercept b = {b:+.4f} V -> n_offset = {n_off_e12:+.4f} e12 cm^-2; D_offset = 0 (assumed, no locating feature)")
ns_test = np.linspace(-8, 8, 801)
for D0 in (0.0, 0.2, 0.4):
    Vt, Vb = calc_gate_voltages(ns_test, D0*np.ones_like(ns_test), c_tg, c_bg, n_offset=n_off_e12)
    ok = (np.abs(Vt) <= 3.0) & (np.abs(Vb) <= 4.5)
    print(f"D={D0}: realized n-window {ns_test[ok].min():+.2f} .. {ns_test[ok].max():+.2f} e12 cm^-2")

fig, axes = plt.subplots(1, 4, figsize=(19, 4.6), sharey=True)
for ax, ch in zip(axes[:2], ("sr1", "sr2")):
    R = np.asarray(rg.R[ch]); rv, k, p, _ = fits[ch]
    pm = ax.pcolormesh(vtg, vbg, np.log10(np.clip(R, 10, None)), cmap="inferno", shading="auto")
    plt.colorbar(pm, ax=ax, label="log10 R (Ohm)")
    ax.plot(rv[k], vbg[k], "c.", ms=3); ax.plot(np.polyval(p, vbg), vbg, "c-", lw=0.7)
    ax.set_title(f"{ch}: slope {p[0]:+.3f}, b {p[1]:+.3f} V"); ax.set_xlabel("V_tg (V)")
pm = axes[2].pcolormesh(vtg, vbg, np.asarray(rg.current)*1e9, cmap="viridis", shading="auto")
plt.colorbar(pm, ax=axes[2], label="I_drain (nA)"); axes[2].set_title("sr0 drain current"); axes[2].set_xlabel("V_tg (V)")
pm = axes[3].pcolormesh(vtg, vbg, np.clip(np.asarray(rg.R["sr3"]), -50, 400), cmap="RdBu_r", shading="auto")
plt.colorbar(pm, ax=axes[3], label="R_xy (Ohm)"); axes[3].set_title("sr3 (Rxy @ B=0)"); axes[3].set_xlabel("V_tg (V)")
axes[0].set_ylabel("V_bg (V)")
fig.suptitle("run 4 - 0 T gatemap: CNP ridge + fits (cyan), drain current, Hall channel")
fig.tight_layout()
