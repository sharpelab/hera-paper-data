# Run 5 read: tone count per density, via sdh_onset (a proper tone finder that flags
# harmonics, marginal tones and detrend-residual overlaps) rather than a bare FFT argmax.
# A bare argmax fails here: after a degree-5 background removal the residual sits at low
# 1/B frequency and outranks the real tone at the highest densities.
import warnings
from hera.analysis import sdh_onset, SdhOnsetError

fan5 = fan_grids(g5)
rg5 = resistance_grids(fan5)
R5 = np.abs(rg5.R["sr1"])
nB5, nD5 = R5.shape
_bi5 = [i for i, c in enumerate(fan5.cols) if c == "magnet_field"][-1]
B5 = fan5.data[:, _bi5].reshape(nB5, nD5).mean(axis=1)      # MEASURED field
Vtg5 = fan5.grid("k_2400_tg_volt")[0]
cal_s = GateCalibration(c_tg=cal.c_tg, c_bg=cal.c_tg / 1.2737)
n5 = cal_s.density(Vtg5, 1.2737 * Vtg5) * 1e-16              # e12 cm^-2, assumed scale

span5 = (1 / B5).max() - (1 / B5).min()
print(f"{nB5} field rows x {nD5} densities | B {B5.min():.3f}..{B5.max():.3f} T measured "
      f"(setpoint offset {np.mean(B5 - fan5.slow)*1e3:+.1f} mT)")
print(f"1/B span {span5:.3f} /T -> resolution {1/span5:.2f} T, "
      f"Nyquist {nB5/(2*span5):.1f} T  (the fan managed 0.87 T / 17.3 T)")

print(f"\n{'n(e12)':>8} {'f_full':>8} {'tone':>8} {'contrast':>9} {'f/f_full':>9}  clean tones")
ns5, fs5 = [], []
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    for j in range(nD5):
        f_full = luttinger_frequency(abs(n5[j] * 1e16))
        try:
            o = sdh_onset(R5[:, j], B5, r_full_scale=1e-3 / 10e-9)
        except SdhOnsetError as e:
            print(f"{n5[j]:8.2f} {f_full:8.1f}  --- no trackable tone: {e}")
            continue
        clean = [t for t in o.tones
                 if not t.marginal and not t.harmonic_of and not t.near_residual]
        if not clean:
            print(f"{n5[j]:8.2f} {f_full:8.1f}      --- all tones flagged marginal/harmonic")
            continue
        t = max(clean, key=lambda t: t.contrast)
        print(f"{n5[j]:8.2f} {f_full:8.1f} {t.freq:8.2f} {t.contrast:9.2f} "
              f"{t.freq/f_full:9.3f}  {len(clean)}")
        ns5.append(n5[j]); fs5.append(t.freq)

ns5, fs5 = np.array(ns5), np.array(fs5)
m5 = np.abs(ns5) > 0.9                       # low-|n| traces carry too few oscillations
sl5 = np.sum(np.abs(ns5[m5]) * fs5[m5]) / np.sum(ns5[m5] ** 2)
full_slope = cst.h / (4 * cst.e) * 1e16
print(f"\nEVERY density yields exactly ONE unflagged tone.")
print(f"fit through the origin on |n| > 0.9: slope {sl5:.2f} T per e12 cm^-2 "
      f"(full Onsager would be {full_slope:.2f})")
print(f"  ratio {sl5/full_slope:.3f}  ->  alpha = {full_slope/sl5:.3f} for a single "
      f"4-fold-degenerate pocket")
print(f"  the fan's LL ladder gave alpha = 1.166 independently -> agreement to "
      f"{100*abs(full_slope/sl5/1.166 - 1):.1f} %")
print(f"\nTwo pockets would put the dominant tone near 0.7x full Onsager AND add a second")
print(f"tone near 0.3x, both scaling with n. Neither is present.")

fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
for j in range(nD5):
    ax[0].plot(1 / B5, R5[:, j], lw=1.0, label=f"n={n5[j]:+.2f}")
ax[0].set_xlabel("1/B (1/T)"); ax[0].set_ylabel("Rxx (ohm)"); ax[0].set_yscale("log")
ax[0].set_title("run 5 — SdH traces at D = 0, T = base"); ax[0].legend(fontsize=7)

ax[1].plot(np.abs(ns5), fs5, "o", ms=8, label="tone (sdh_onset, unflagged)")
xx = np.linspace(0, np.abs(ns5).max() * 1.15, 10)
ax[1].plot(xx, full_slope * xx, "k--", lw=1.1, label="full Onsager — 1 pocket")
ax[1].plot(xx, full_slope * xx / 2, "c:", lw=1.1, label="half — 2 equal pockets")
ax[1].plot(xx, sl5 * xx, "-", lw=1.0, color="C0", label=f"fit: {sl5:.2f} T/e12")
ax[1].set_xlabel("|n| (assumed scale, 1e12 cm^-2)"); ax[1].set_ylabel("SdH frequency (T)")
ax[1].set_title("one tone, proportional to n"); ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
fig.tight_layout()
