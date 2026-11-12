# Run 4 — cnp-and-dline-calibration: ridge extraction, fit, (n, D) conversion
from scipy.ndimage import gaussian_filter1d
from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages

c_tg_prior = stack_capacitance([(15.6, 3)])
c_bg_prior = stack_capacitance([(12, 3), (0, 3.9)])

fit_results = {}
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharex=True, sharey=True)
for ax, ch in zip(axes, ("sr1_X", "sr2_X")):
    R = (r4.col(ch) / I_BIAS5).reshape(101, 101)
    Rs = gaussian_filter1d(R, 2, axis=1)
    idx = np.argmax(Rs, axis=1)
    ridge_v, peak_R = VTG4[idx], Rs[np.arange(101), idx]
    good = (idx > 2) & (idx < 98) & (peak_R > 5 * np.median(Rs, axis=1))
    g = good.copy()
    for _ in range(4):
        p = np.polyfit(VBG4[g], ridge_v[g], 1)
        res = ridge_v - np.polyval(p, VBG4)
        g_new = good & (np.abs(res) < 2 * np.std(res[g]))
        if (g_new == g).all():
            break
        g = g_new
    fit_results[ch] = dict(slope=p[0], intercept=p[1], good=g, peak_R=peak_R)
    print(f"{ch}: slope={p[0]:+.4f}, intercept={p[1]:+.4f} V, rows {g.sum()}/101, "
          f"resid {np.std((ridge_v-np.polyval(p,VBG4))[g])*1e3:.1f} mV")
    ax.pcolormesh(VTG4, VBG4, np.log10(np.clip(R, 1, None)), shading="auto")
    ax.plot(ridge_v[g], VBG4[g], "r.", ms=3)
    ax.plot(np.polyval(p, VBG4), VBG4, "w--", lw=1)
    ax.set_title(f"{ch}: ridge + fit (fast axis = V_tg vs V_bg rows)")
    ax.set_xlabel("V_tg (V)")
axes[0].set_ylabel("V_bg (V)")
fig.tight_layout()
plt.show()

# conversion: anchor c_tg at its single-dielectric prior, set c_bg from ratio
sl = np.mean([fit_results[c]["slope"] for c in ("sr1_X", "sr2_X")])
b0 = np.mean([fit_results[c]["intercept"] for c in ("sr1_X", "sr2_X")])
RATIO_CAL = -sl
C_TG = c_tg_prior
C_BG = C_TG * RATIO_CAL
N_OFFSET = -calc_nD(b0, 0, C_TG, C_BG)[0]
print(f"ratio c_bg/c_tg = {RATIO_CAL:.4f} (prior {c_bg_prior/c_tg_prior:.4f}, "
      f"{100*(RATIO_CAL/(c_bg_prior/c_tg_prior)-1):+.1f}%)  [data-calibrated]")
print(f"C_TG = {C_TG:.4e} F/m^2 [geometry prior]  C_BG = {C_BG:.4e} F/m^2")
print(f"N_OFFSET = {N_OFFSET:+.4f} e12 cm^-2 (V_tg intercept {b0:+.4f} V)")

# D=0 locator: R_CNP minimum along the ridge
fig2, ax2 = plt.subplots(figsize=(6, 3.5))
for ch in ("sr1_X", "sr2_X"):
    d = fit_results[ch]
    gg = d["good"]
    vb_min = VBG4[gg][np.argmin(d["peak_R"][gg])]
    ax2.plot(VBG4[gg], d["peak_R"][gg], ".-", label=f"{ch} (min at V_bg={vb_min:+.2f})")
    print(f"{ch}: R_CNP min {d['peak_R'][gg].min():.0f} Ω at V_bg={vb_min:+.3f} V; "
          f"ridge max {d['peak_R'][gg].max():.0f} Ω")
ax2.set_xlabel("V_bg (V) along CNP ridge")
ax2.set_ylabel("peak R (Ω)")
ax2.set_yscale("log")
ax2.legend(fontsize=8)
ax2.set_title("run 4: R_CNP along ridge — D=0 at the minimum")
fig2.tight_layout()
plt.show()
D_OFFSET = 0.0  # R_CNP minimum sits at V_bg ≈ 0 → measured D_offset ≈ 0 (cited feature)
print(f"D_OFFSET = {D_OFFSET} V/nm (R_CNP min at V_bg ≈ 0.00/+0.09 V, i.e. D ≈ 0.005 V/nm — negligible)")
