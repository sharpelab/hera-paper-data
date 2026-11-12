"""Runs 6 & 7 — SdH spot checks. Raw first, then background-subtracted 1/B + FFT + sdh_onset."""
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset

I_BIAS = None

def load(rid):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field")
    I = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    V = r.col("sr1_X") / 1.0
    R = V / I
    T = r.col("T_sample")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    o = np.argsort(B)
    return dict(r=r, B=B[o], R=R[o], I=I[o], V=V[o], T=T[o], itg=itg[o], ibg=ibg[o])

out = {}
fig, axes = plt.subplots(3, 2, figsize=(13, 11))
for j, rid in enumerate((6, 7)):
    d = load(rid)
    B, R, I = d["B"], d["R"], d["I"]
    out[rid] = dict(npts=len(B), Bmin=float(B.min()), Bmax=float(B.max()),
                    R0=float(R[np.argmin(np.abs(B - B.min()))]), Rmax=float(R.max()), Rmin=float(R.min()),
                    I_med=float(np.median(I)), I_spread=float(I.max() - I.min()),
                    T_mean=float(d["T"].mean()), T_range=[float(d["T"].min()), float(d["T"].max())],
                    itg_absmax=float(np.abs(d["itg"]).max()), ibg_absmax=float(np.abs(d["ibg"]).max()))
    # raw
    ax = axes[0, j]
    ax.plot(B, R, lw=0.8)
    ax.set_xlabel("B (T)"); ax.set_ylabel(r"$R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {rid} raw — {d['r'].tags[0][:40]}")
    # background subtract in B space over the high-B window
    mask = B >= 1.0
    Bm, Rm = B[mask], R[mask]
    p = np.polyfit(Bm, Rm, 5)
    dR = Rm - np.polyval(p, Bm)
    ax = axes[1, j]
    ax.plot(1.0 / Bm, dR, lw=0.8)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel(r"$\Delta R$ ($\Omega$)")
    ax.set_title(f"run {rid} — deg-5 B-space background removed (B>1 T)")
    out[rid]["dR_rms"] = float(np.std(dR))
    out[rid]["dR_ptp"] = float(np.ptp(dR))
    # FFT over a few windows
    ax = axes[2, j]
    for blo, bhi in ((1.0, 10.0), (2.0, 10.0), (4.0, 10.0)):
        sel = (B >= blo) & (B <= bhi)
        if sel.sum() < 20:
            continue
        f, spec = sdh_fft(R[sel][:, None], B[sel], bg_degree=5, log=False, nfft=2048)
        s = spec[0]
        ax.plot(f, s / s.max(), lw=0.9, label=f"{blo}-{bhi} T (df={1/(1/blo-1/bhi):.1f} T)")
        k = f > 3
        pk = f[k][np.argsort(s[k])[::-1][:6]]
        out[rid][f"fft_{blo}_{bhi}_toppeaks"] = [round(float(x), 2) for x in pk]
    ax.set_xlim(0, 60); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)")
    ax.legend(fontsize=7); ax.set_title(f"run {rid} SdH FFT")
    # sdh_onset
    try:
        so = sdh_onset(R, B, r_full_scale=50e-6 / max(np.median(np.abs(I)), 1e-12))
        out[rid]["onset_summary"] = so.summary()
        out[rid]["onset_b"] = float(so.onset_b)
        out[rid]["onset_freq"] = float(so.onset_freq)
        out[rid]["tones"] = [dict(freq=round(float(t.freq), 2), contrast=round(float(t.contrast), 4),
                                  onset_b=round(float(t.onset_b), 3), censored=t.censored,
                                  marginal=t.marginal, near_residual=t.near_residual,
                                  harmonic_of=(round(float(t.harmonic_of), 2) if t.harmonic_of else None))
                             for t in so.tones]
        out[rid]["untracked"] = [(round(float(a), 2), b) for a, b in so.untracked]
    except Exception as e:
        out[rid]["onset_error"] = f"{type(e).__name__}: {e}"

fig.tight_layout()
fig.savefig("hera_scratch/spots_67.png", dpi=110)
print(json.dumps(out, indent=1, default=str))
