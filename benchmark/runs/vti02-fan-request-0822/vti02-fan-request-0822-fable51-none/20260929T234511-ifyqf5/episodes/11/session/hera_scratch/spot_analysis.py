"""SdH spot checks, runs 6 (electron, n=+3.2e12, 0->10 T) and 7 (hole, n=-1.2e12, 10->0.3 T):
raw R(B), background-subtracted oscillatory part, 1/B FFT, per-tone onset via hera.analysis.sdh_onset."""
import sys, json, numpy as np, matplotlib, warnings
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, luttinger_frequency
from scipy.constants import e, h

def load(rid):
    r = open_run(f"data/{rid}")
    chs = resolve_channels(r.meta)
    cur = current_channel(chs)
    I = r.col(cur.col) / cur.gain
    v = [c for c in chs if c.cid == "sr1"][0]
    R = (r.col(v.col) / v.gain) / I
    B = r.col("magnet_field")
    o = np.argsort(B)
    return r, B[o], R[o], I[o], r.col("T_sample")[o], chs

out = {}
fig, axs = plt.subplots(3, 2, figsize=(14, 12))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r, B, R, I, T, chs = load(rid)
    mc = r.meta["measurement_config"]
    sens = None
    try:
        sens = r.meta["instruments"]["sr1"]["parameters"]["sensitivity"]["value"]
    except Exception:
        pass
    Ib = np.median(I)
    print(f"\n===== run {rid}: n = {n12:+.1f}e12, {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T, T_sample {T.mean():.3f} +/- {T.std():.3f} K, I_bias med {Ib*1e9:.3f} nA, sr1 sens {sens}")
    print(f"  R(B<0.1) = {np.median(R[B<0.15]):.1f} Ohm; R range {R.min():.1f} .. {R.max():.1f} Ohm; R at 10T {R[-1]:.1f}")
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"  Luttinger full-density frequency F_L = {FL:.2f} T (single 4-fold FS); n from F: F * 4e/h = {FL*4*e/h*1e-16:.2f}e12")
    ax = axs[0, j]; ax.plot(B, R, lw=0.8); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {rid}: n={n12:+.1f}e12, D=0, raw Rxx(B)")
    # local minima/maxima positions >1.5 T (oscillation extrema)
    from scipy.signal import find_peaks
    from scipy.ndimage import gaussian_filter1d
    sel = B > 1.0
    Rs = gaussian_filter1d(R[sel], 1.5)
    pk, _ = find_peaks(Rs, prominence=3); mn, _ = find_peaks(-Rs, prominence=3)
    print(f"  maxima (B>1T): {np.round(B[sel][pk], 2).tolist()}")
    print(f"  minima (B>1T): {np.round(B[sel][mn], 2).tolist()}")
    # 1/B of minima and their spacing
    if len(mn) > 2:
        ib = 1 / B[sel][mn]; d = -np.diff(ib)
        print(f"  1/B minima spacings (1/T): {np.round(d, 4).tolist()} -> F ~ {np.round(1/d, 1).tolist()} T")
    # FFT in 1/B over a couple of windows
    for (blo, bhi) in [(1.5, 10.0), (2.0, 6.0), (4.0, 10.0)]:
        m = (B >= blo) & (B <= bhi)
        try:
            f, spec = sdh_fft(R[m][:, None], B[m], nfft=2048, bg_degree=5, log=False)
            sp = spec[0]; fm = f > 2
            top = np.argsort(sp[fm])[::-1][:6]
            fp_, _ = find_peaks(sp[fm], prominence=0.15 * sp[fm].max())
            print(f"  FFT [{blo},{bhi}] T: peaks at F = {np.round(f[fm][fp_], 1).tolist()} T (amp rel {np.round(sp[fm][fp_]/sp[fm].max(), 2).tolist()})")
            if (blo, bhi) == (1.5, 10.0):
                ax2 = axs[2, j]; ax2.plot(f, sp, lw=0.8); ax2.set_xlim(0, 60); ax2.set_xlabel("F (T)"); ax2.set_ylabel("FFT amp")
                ax2.set_title(f"run {rid} FFT in 1/B, B in [{blo},{bhi}] T, bg deg 5"); ax2.axvline(FL, color="r", ls="--", lw=1, label=f"F_L={FL:.1f} T")
                ax2.axvline(FL/2, color="orange", ls=":", lw=1, label="F_L/2"); ax2.legend(fontsize=8)
        except Exception as ex:
            print(f"  FFT [{blo},{bhi}] failed: {ex}")
    # background-subtracted
    m = B > 1.0
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax1 = axs[1, j]; ax1.plot(1 / B[m], dR, lw=0.8); ax1.set_xlabel("1/B (1/T)"); ax1.set_ylabel("dRxx (Ohm)"); ax1.set_title(f"run {rid}: Rxx minus deg-5 poly(B), vs 1/B")
    # onset
    rfs = (sens / Ib) if sens else None
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            on = sdh_onset(R, B, b_lo=0.3, r_full_scale=rfs)
        print(on.summary())
        out[rid] = dict(onset_b=float(on.onset_b), onset_freq=float(on.onset_freq),
                        tones=[dict(freq=float(t.freq), contrast=float(t.contrast), onset_b=float(t.onset_b), censored=bool(t.censored), marginal=bool(t.marginal), harmonic_of=(None if t.harmonic_of is None else float(t.harmonic_of))) for t in on.tones])
    except Exception as ex:
        print(f"  sdh_onset failed: {ex}")
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs6_7.png", dpi=110)
json.dump(out, open("hera_scratch/spot_onsets.json", "w"), indent=1)
print("\nsaved hera_scratch/spot_runs6_7.png")
