# Run 7 — cnp-and-dline-calibration: per-channel ridge fit -> (n, D) conversion
from scipy.ndimage import gaussian_filter1d
E = cst.e; EPS0 = cst.epsilon_0
NFAST = 161
g = run(7)
vt, vb = g.col("k_2400_tg_volt"), g.col("k_2400_bg_volt")
i_dr = np.abs(g.col("sr0_X")) / 1e6                      # measured drain current
gr = lambda c: c[:len(c) // NFAST * NFAST].reshape(-1, NFAST)
VT, VB, IDR = gr(vt), gr(vb), gr(i_dr)
nrows = VT.shape[0]
print(f"I_drain over map: med {np.median(IDR)*1e9:.2f} nA ({IDR.min()*1e9:.2f}–{IDR.max()*1e9:.2f})")

# ridge extraction per channel (fast axis = V_tg; rows = V_bg) with the three
# step-1 guards: edge-clip, no-clear-ridge, 2σ iterative outlier rejection
fits = {}
for ch in ("sr1", "sr2", "sr3"):
    R = gr(g.col(f"{ch}_X")) / IDR
    rows_v, ridge_v = [], []
    for j in range(nrows):
        sm = gaussian_filter1d(R[j], 3); k = int(np.argmax(sm))
        if 5 < k < NFAST - 6 and sm[k] > 2 * np.median(sm):
            rows_v.append(VB[j, 0]); ridge_v.append(VT[j, k])
    rows_v, ridge_v = np.array(rows_v), np.array(ridge_v)
    m = np.ones(len(rows_v), bool)
    for _ in range(3):
        p = np.polyfit(rows_v[m], ridge_v[m], 1)
        res = ridge_v - np.polyval(p, rows_v)
        m = np.abs(res) < 2 * max(res[m].std(), 1e-4)
    p = np.polyfit(rows_v[m], ridge_v[m], 1)
    fits[ch] = (p[0], p[1], (ridge_v - np.polyval(p, rows_v))[m].std(), int(m.sum()), rows_v[m], ridge_v[m])
    print(f"{ch}: slope {p[0]:+.4f}, intercept {p[1]:+.4f} V, rms {fits[ch][2]*1e3:.1f} mV, rows {m.sum()}/{nrows}")

# conversion — axis orientation: ridge V_tg vs rows V_bg => c_bg/c_tg = -slope.
# Anchor: TG at its stack prior (single 14.9 nm hBN dielectric); sr2 (weak short
# channel) reported but not driving; sr1/sr3 spread 0.4% => one calibration.
slope = float(np.mean([fits["sr1"][0], fits["sr3"][0]]))
b = float(np.mean([fits["sr1"][1], fits["sr3"][1]]))
c_tg_cal = EPS0 * 3.0 / 14.9e-9
c_bg_cal = -slope * c_tg_cal
n_off = -(c_tg_cal * b) / E
cal = GateCalibration(c_tg_cal, c_bg_cal, n_offset=n_off, D_offset=0.0)
print(f"\nratio c_bg/c_tg = {-slope:.4f} (geometry prior 0.6963, {(-slope/0.6963-1)*100:+.1f}%)")
print(f"c_tg = {c_tg_cal*1e3:.4f} mF/m² (ANCHOR, geometry prior) | c_bg = {c_bg_cal*1e3:.4f} mF/m² (ratio-calibrated)")
print(f"n_offset = {n_off:.3e} m^-2 ({n_off*1e-16:+.4f}e12 cm^-2); D_offset = 0 (stated assumption)")
vv = np.linspace(-1.1, 1.15, 50)
print(f"closure: max|n| on ridge = {np.abs(cal.density(slope*vv+b, vv)).max()*1e-16:.4f}e12 cm^-2")

# D=0 designer, clip by dropping (validators ±0.8 / ±5.0)
ns = np.linspace(-2.5e16, 2.5e16, 2001)
q = E * (ns - n_off) / 2.0
Vt_l, Vb_l = q / c_tg_cal, q / c_bg_cal
keep = (np.abs(Vt_l) <= 0.8) & (np.abs(Vb_l) <= 5.0)
print(f"D=0 realized window: n = {ns[keep].min()*1e-16:+.3f} .. {ns[keep].max()*1e-16:+.3f} e12 cm^-2 "
      f"(V_bg only ±{np.abs(Vb_l[keep]).max():.2f} V — TG is the binding gate)")
for tag, nv in (("hole", ns[keep].min()), ("electron", ns[keep].max())):
    FL = cst.h * abs(nv) / (4 * E)
    print(f"F_L({tag} edge) = {FL:.1f} T -> Δ(1/B) ≤ {1/(3*FL):.2e} /T (1/3 Nyquist)")

# overlay: fit + D=0 line on the sr1 map
fig, ax = plt.subplots(figsize=(6.5, 5))
R1 = gr(g.col("sr1_X")) / IDR
pm = ax.pcolormesh(VT, VB, R1 / 1e3, shading="nearest", cmap="inferno")
fig.colorbar(pm, ax=ax, label="sr1 Rxx (kΩ)")
for ch, c in (("sr1", "c"), ("sr3", "lime")):
    ax.plot(fits[ch][5], fits[ch][4], ".", color=c, ms=3, label=f"{ch} ridge")
ax.plot(slope * vv + b, vv, "w--", lw=1, label=f"fit {slope:+.4f}·V_bg{b:+.4f}")
ax.plot(Vt_l[keep], Vb_l[keep], "b:", lw=1.5, label="D = 0 line")
ax.set_xlabel("V_tg (V)"); ax.set_ylabel("V_bg (V)"); ax.legend(fontsize=7)
plt.show()
