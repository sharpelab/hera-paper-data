"""Runs 6/7 SdH spot checks: raw -> computed onset -> 1/B FFT with B-window split."""
import warnings

from hera.analysis import sdh_onset, sdh_fft

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
SPOTS = [(6, "electron", +3.20), (7, "hole", -1.20)]


def rxx(r):
    """Four-probe R_xx(B) on sr1, sorted ascending in B, with the measured current."""
    B = r.col("magnet_field")
    I = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    R = (r.col("sr1_X") / 1.0) / I           # sr1 gain = 1 (device card)
    o = np.argsort(B)
    return B[o], R[o], I[o]


fig, axes = plt.subplots(2, 3, figsize=(16, 8))
spot_read = {}

for k, (rid, side, n12) in enumerate(SPOTS):
    r = run(rid)
    B, R, I = rxx(r)
    F_L = abs(n12) * 1e16 * cst.h / (4 * cst.e)
    r_fs = 50e-6 / abs(np.median(I))    # both spot checks ran sr1 at 50 uV -> ~5 kOhm FS

    print("=" * 72)
    print(f"run {rid} — {side}, nominal n = {n12:+.2f}e12, F_L = {F_L:.2f} T")
    print(f"  B {B.min():.3f} -> {B.max():.3f} T ({len(B)} pts), "
          f"T_sample {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")
    print(f"  I = {np.median(I) * 1e9:.3f} nA; R_xx {R.min():.1f} .. {R.max():.1f} Ohm; "
          f"max|R| = {np.abs(R).max():.0f} = {100 * np.abs(R).max() / r_fs:.1f} % of "
          f"{r_fs:.0f} Ohm full scale (no rail)")
    for g, lbl in (("k_2400_tg_curr", "I_tg"), ("k_2400_bg_curr", "I_bg")):
        c = r.col(g)
        print(f"  {lbl}: median {np.median(c) * 1e12:+.0f} pA, range "
              f"[{c.min() * 1e12:+.0f}, {c.max() * 1e12:+.0f}] pA (trip 1 nA — never armed)")

    # --- 0. RAW first
    ax = axes[k, 0]
    ax.plot(B, R, lw=0.8)
    ax.set(xlabel="B (T)", ylabel=r"$R_{xx}$ ($\Omega$)",
           title=f"run {rid} — {side} n={n12:+.2f}e12 — RAW")
    ax.grid(alpha=0.3)

    # --- 1. onset, computed (landau-fan step-1 B_lo contract)
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter("always")
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print("\n" + on.summary())
        for w in ws:
            print(f"  [warn] {w.message}")
    b_lo, b_hi = on.onset_b, B.max()

    # --- 2. FFT in 1/B, full record + the mandatory low-B / high-B split
    inv_mid = 0.5 * (1 / b_lo + 1 / b_hi)
    b_mid = 1 / inv_mid
    ax = axes[k, 1]
    peaks = {}
    for rng, lab, sty in [((b_lo, b_hi), f"full {b_lo:.2f}-{b_hi:.0f} T", "-"),
                          ((b_lo, b_mid), f"low {b_lo:.2f}-{b_mid:.2f} T", "--"),
                          ((b_mid, b_hi), f"high {b_mid:.2f}-{b_hi:.0f} T", ":")]:
        fr, amp = sdh_fft(R[:, None], B, b_range=rng, nfft=2048, log=False)
        a = amp[0]
        band = (fr > 1.5) & (fr < 2.2 * F_L)
        ax.plot(fr, a / np.nanmax(a[band]), sty, lw=1.0, label=lab)
        loc = band & (a > np.roll(a, 1)) & (a > np.roll(a, -1)) & (a > 0.05 * np.nanmax(a[band]))
        pk, pa = fr[loc], a[loc] / np.nanmax(a[band])
        peaks[lab.split()[0]] = list(zip(np.round(pk, 2), np.round(pa, 2)))
        print(f"  FFT [{lab}]: " + ", ".join(f"{f:.2f}T/{v:.2f}" for f, v in zip(pk, pa)))
    ax.axvline(F_L, color="k", lw=1.2, label=f"$F_L$ = {F_L:.1f} T")
    ax.set(xlabel="F (T)", ylabel="|FFT| (norm)", xlim=(0, 1.6 * F_L),
           title="FFT in 1/B — B-window split")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)

    # --- 3. the detrended record the FFT actually sees
    ax = axes[k, 2]
    m = B >= b_lo
    ax.plot(1 / B[m], R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m]), lw=0.8)
    ax.set(xlabel="1/B (1/T)", ylabel=r"$\Delta R$ ($\Omega$)",
           title=f"detrended (deg-5 in B), B > {b_lo:.2f} T")
    ax.grid(alpha=0.3)

    spot_read[rid] = dict(side=side, n12=n12, F_L=F_L, onset=b_lo,
                          dF=1 / (1 / b_lo - 1 / b_hi), peaks=peaks)
    print(f"  record resolution delta_F = 1/(1/{b_lo:.2f} - 1/{b_hi:.0f}) = "
          f"{spot_read[rid]['dF']:.2f} T")

plt.tight_layout()
plt.show()
