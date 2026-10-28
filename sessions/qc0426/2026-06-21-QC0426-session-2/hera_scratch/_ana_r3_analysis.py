# SdH FFT + stability: bg-subtracted vs 1/B, then FFT peak across extraction choices
import scipy.constants as cst
F_L = cst.h / (4 * cst.e) * 3.5e16
m = B >= 1.5
coef = np.polyfit(B[m], R1[m], 4); dR1 = R1[m] - np.polyval(coef, B[m])

fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
ax[0].plot(1 / B[m], dR1, ".-", ms=4, lw=0.8)
ax[0].set_xlabel("1/B [1/T]"); ax[0].set_ylabel("dRxx [ohm]"); ax[0].grid(alpha=0.3)
ax[0].set_title("sr1 bg-sub vs 1/B (B>1.5T): large but few, irregular")

print(f"F_L = {F_L:.1f} T ; FFT dominant peak (>2T) vs extraction choice:")
for cut in (1.5, 2.0, 3.0, 4.0):
    pks = []
    for deg in (3, 5, 7):
        f, mag = sdh_fft(R1[:, None], B, b_range=(cut, B.max()), bg_degree=deg)
        mag = np.asarray(mag).squeeze(); pks.append(f[f > 2][np.argmax(mag[f > 2])])
    print(f"  cut {cut:.1f}T  bg(3,5,7): " + ", ".join(f"{p:5.1f}T" for p in pks))

for deg, c in [(3, "C0"), (5, "C1"), (7, "C2")]:
    f, mag = sdh_fft(R1[:, None], B, b_range=(3.0, B.max()), bg_degree=deg)
    mag = np.asarray(mag).squeeze()
    ax[1].plot(f, mag / mag[f > 2].max(), color=c, lw=1.1, label=f"bg-deg {deg}")
ax[1].axvline(F_L, ls="--", c="k", label=f"F_L={F_L:.0f}T")
ax[1].set_xlim(0, 45); ax[1].set_xlabel("F [T]"); ax[1].set_ylabel("norm FFT (>2T)")
ax[1].legend(); ax[1].set_title("FFT (cut 3T): broad ~10-20T blob, detrender-dependent")
plt.show()
