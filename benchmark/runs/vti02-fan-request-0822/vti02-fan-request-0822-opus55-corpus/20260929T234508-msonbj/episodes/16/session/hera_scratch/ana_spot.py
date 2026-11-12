import numpy as np, json, warnings
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency
import sys; sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count"); import fs_count_b0 as m

out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}")
    print(summarize_run(r))
    B = r.col("magnet_field"); V = r.col("sr1_X"); I = r.col("sr0_X") / -1e6
    R = V / I
    o = np.argsort(B); B, R, Vr = B[o], R[o], V[o]
    sens = 50e-6; Ibias = np.median(I)
    print(f"run {rid}: I med {Ibias*1e9:.3f} nA; R range {R.min():.1f}..{R.max():.1f} Ohm; max |V|/sens {np.abs(Vr).max()/sens:.3f}")
    FL = float(luttinger_frequency(n12 * 1e16))
    print(f"  F_L = {FL:.2f} T")
    try:
        on = sdh_onset(R, B, r_full_scale=sens / Ibias)
        print(on.summary())
        onb = on.onset_b
    except Exception as e:
        print("  onset error:", e); onb = None
    ax[0, j].plot(B, R, lw=.6); ax[0, j].set_title(f"run {rid} n={n12:+}e12 raw R"); ax[0, j].set_xlabel("B (T)")
    # bg-subtracted
    for k, (lo, lab) in enumerate([(onb or 1.5, 'onset'), ]):
        pass
    res = {}
    for cut in ([onb] if onb else []) + [1.5, 2.0, 3.0, 4.0]:
        if cut is None: continue
        for deg in (3, 5, 7):
            f, s = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=deg, nfft=4096)
            sp = s[0]; msk = f > 2
            pk = []
            from scipy.signal import find_peaks
            idx, _ = find_peaks(sp[msk], prominence=0.08 * sp[msk].max())
            ff = f[msk][idx]; aa = sp[msk][idx]
            top = sorted(zip(aa, ff), reverse=True)[:6]
            res[(round(cut, 2), deg)] = [(round(x, 2), round(y / sp[msk].max(), 2)) for y, x in top]
            print(f"  cut {cut:.2f} deg {deg}: peaks (F, rel amp) {res[(round(cut,2),deg)]}")
            if deg == 5 and abs(cut - (onb or 1.5)) < 1e-6 or (deg == 5 and cut == 2.0):
                ax[2, j].plot(f, sp / sp[msk].max(), lw=.8, label=f"cut {cut:.2f}")
    # delta R vs 1/B
    cut = max(onb or 1.5, 1.0)
    mk = B >= cut
    p = np.polyfit(B[mk], np.log10(R[mk]), 5)
    dR = np.log10(R[mk]) - np.polyval(p, B[mk])
    ax[1, j].plot(1 / B[mk], dR, lw=.6); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_title(f"run {rid}: dlogR, deg-5 bg in B, B>{cut:.2f}")
    ax[2, j].axvline(FL, color='k', ls='--', label='F_L')
    # model
    try:
        EF, orb = m.abab_fs(n12); ms = m.abab_mstar(n12)
        print("  ABAB orbits:", [(round(F, 2)) for F, k in orb], "m*", [(round(F,2), round(mm,3)) for F, mm in ms])
        for F, k in orb: ax[2, j].axvline(F, color='C3', ls=':', alpha=.7)
        a4 = m.abca_fs(n12); am = m.abca_mstar(n12)
        print("  ABCA:", a4[1:], "m*", am)
    except Exception as e:
        print("  model err", e)
    ax[2, j].set_xlim(0, 2 * FL); ax[2, j].legend(fontsize=7); ax[2, j].set_xlabel("F (T)")
    out[rid] = dict(onset=onb, FL=FL, peaks={f"{k[0]}_{k[1]}": v for k, v in res.items()})
plt.tight_layout(); plt.savefig("hera_scratch/spot_fft.png", dpi=90)
json.dump(out, open("hera_scratch/spot_fft.json", "w"), indent=1, default=float)
