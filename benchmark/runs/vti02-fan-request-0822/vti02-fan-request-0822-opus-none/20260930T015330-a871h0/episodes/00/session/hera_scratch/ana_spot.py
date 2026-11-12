"""Runs 6 & 7 — sdh-spot-check read: raw R(B), background-subtracted, FFT, onsets."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_fft, sdh_onset, SdhOnsetError,
                           GateCalibration, luttinger_frequency)

def trace(i):
    r = open_run(f"data/{i}")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    B = r.col("magnet_field")
    I = r.col_at(cur.idx) / 1.0  # already gain-divided? no: X/gain
    # resolve_channels gain model: physical = X / gain
    Ical = r.col_at(cur.idx) / cur.gain
    v = [c for c in chans if not c.is_current]
    out = {}
    for c in v:
        out[c.cid] = (r.col_at(c.idx) / c.gain) / Ical
    return r, B, Ical, out

for i in (6, 7):
    r, B, I, Rs = trace(i)
    T = r.col("T_sample")
    itg = r.col("k_2400_tg_curr"); ibg = r.col("k_2400_bg_curr")
    print(f"=== run {i} ===")
    print(f"  T {T.mean():.3f} K ({T.min():.3f}-{T.max():.3f}); I_meas {np.median(np.abs(I))*1e9:.3f} nA "
          f"({np.abs(I).min()*1e9:.3f}-{np.abs(I).max()*1e9:.3f})")
    print(f"  I_tg |med| {np.median(np.abs(itg))*1e12:.1f} pA max {np.abs(itg).max()*1e12:.1f} pA; "
          f"I_bg |med| {np.median(np.abs(ibg))*1e12:.1f} pA max {np.abs(ibg).max()*1e12:.1f} pA")
    for cid, R in Rs.items():
        Ra = np.abs(R)
        print(f"  {cid}: R(B~0)={Ra[np.argmin(np.abs(B))]:.1f} ohm  R(Bmax)={Ra[np.argmax(B)]:.1f} ohm  "
              f"min {Ra.min():.1f} max {Ra.max():.1f}")
        # full-scale check: sens 50 uV / I
        fs = 50e-6 / np.median(np.abs(I))
        print(f"    full scale = {fs:.0f} ohm; max/FS = {Ra.max()/fs:.3f}")
        # order ascending in B for onset
        o = np.argsort(B)
        Bs, Rss = B[o], Ra[o]
        try:
            res = sdh_onset(Rss, Bs, r_full_scale=fs)
            print(res.summary())
        except SdhOnsetError as e:
            print(f"    sdh_onset FAILED: {e}")
        f, spec = sdh_fft(Rss[:, None], Bs, b_range=(2.0, Bs.max()), nfft=2048)
        s = spec[0]
        m = (f > 2) & (f < 80)
        pk = f[m][np.argmax(s[m])]
        print(f"    FFT(2-{Bs.max():.1f} T) dominant freq = {pk:.2f} T")
        # top 6 local peaks
        ss = s[m]; ff = f[m]
        loc = [j for j in range(1, len(ss)-1) if ss[j] > ss[j-1] and ss[j] > ss[j+1]]
        loc.sort(key=lambda j: -ss[j])
        print("    peaks:", ", ".join(f"{ff[j]:.1f} T ({ss[j]/ss[loc[0]]:.2f})" for j in loc[:6]))

# --- expected Luttinger frequency at the two spots
CAL = GateCalibration(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894e16, D_offset=-0.013e9)
for name, (vtg, vbg) in {"e": (0.9836, 1.1661), "h": (-0.2770, -0.4650)}.items():
    n = CAL.density(vtg, vbg)
    print(f"{name}: n = {n*1e-16:+.3f}e12 cm^-2, F_L(full) = {luttinger_frequency(n):.2f} T")

# --- plots
fig, axes = plt.subplots(2, 2, figsize=(13, 8))
for k, i in enumerate((6, 7)):
    r, B, I, Rs = trace(i)
    cid, R = next(iter(Rs.items()))
    Ra = np.abs(R); o = np.argsort(B); Bs, Rss = B[o], Ra[o]
    axes[k, 0].plot(Bs, Rss, lw=0.8)
    axes[k, 0].set(xlabel="B (T)", ylabel=f"R_{cid} (ohm)", title=f"run {i} raw")
    m = Bs > 1.0
    bg = np.polyval(np.polyfit(Bs[m], Rss[m], 5), Bs[m])
    axes[k, 1].plot(1/Bs[m], Rss[m]-bg, lw=0.8)
    axes[k, 1].set(xlabel="1/B (1/T)", ylabel="dR (ohm)", title=f"run {i} detrended vs 1/B")
plt.tight_layout(); plt.savefig("hera_scratch/spot_67.png", dpi=110)
print("wrote hera_scratch/spot_67.png")
