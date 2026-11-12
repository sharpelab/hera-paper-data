"""SdH spot checks (runs 6 e-side, 7 h-side): raw R(B), onset, FFT tones.
Feeds the landau-fan design (B_lo, density window, resolvable tone splits)."""
import sys, json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset
from sharpelab_nb.gates import calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
SPOTS = {6: ("electron", +3.2, 0.9836, 1.1661), 7: ("hole", -1.2, -0.2770, -0.4650)}


def load(rid):
    r = open_run(f"data/{rid}")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    I = r.col_at(cur.idx) / cur.gain
    v = [c for c in chans if not c.is_current and c.cid == "sr1"][0]
    R = (r.col_at(v.idx) / v.gain) / I
    B = r.col("magnet_field")
    o = np.argsort(B)
    return r, B[o], R[o], I[o], r.col("T_sample")[o]


fig, axes = plt.subplots(2, 3, figsize=(16, 8))
out = {}
for k, rid in enumerate((6, 7)):
    side, n_nom, vtg, vbg = SPOTS[rid]
    r, B, R, I, T = load(rid)
    n_cal, D_cal = calc_nD(vtg, vbg, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
    F_L = abs(n_cal) * 1e16 * 6.62607e-34 / (4 * 1.602177e-19)
    print(f"\n===== run {rid} ({side}) n={n_cal:+.3f}e12 D={D_cal:+.3f} F_Lifshitz(full-n)={F_L:.1f} T")
    print(f"  B {B.min():.3f}..{B.max():.3f} T, {len(B)} pts; R {np.abs(R).min():.0f}..{np.abs(R).max():.0f} Ohm; "
          f"I median {np.median(I)*1e9:.3f} nA; T {T.mean():.3f}+-{T.std():.3f} K")
    rail = 50e-6 / np.median(I)   # 50 uV FS / I -> Ohm full scale
    print(f"  full scale {rail:.0f} Ohm; max |R| = {np.abs(R).max():.0f} ({100*np.abs(R).max()/rail:.1f} % FS)")

    ax = axes[k, 0]
    ax.plot(B, np.abs(R), lw=0.8)
    ax.set_xlabel("B (T)"); ax.set_ylabel("|Rxx| (Ohm)"); ax.set_title(f"run {rid} raw — {side}, n={n_cal:+.2f}e12")

    # background-subtracted
    p = np.polyfit(B, np.abs(R), 5)
    dR = np.abs(R) - np.polyval(p, B)
    ax = axes[k, 1]
    ax.plot(1 / B[B > 0.25], dR[B > 0.25], lw=0.8)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)"); ax.set_title("background-subtracted vs 1/B")

    # FFT over the high-B half
    for blo in (1.0, 2.0, 4.0):
        m = B >= blo
        if m.sum() < 30:
            continue
        f, sp = sdh_fft(np.abs(R)[m][:, None], B[m], nfft=4096, bg_degree=5, log=False)
        sp = sp[0]
        keep = (f > 2) & (f < 120)
        fk, spk = f[keep], sp[keep]
        top = np.argsort(spk)[::-1][:400]
        # local maxima
        pk = [i for i in range(1, len(spk) - 1) if spk[i] > spk[i - 1] and spk[i] > spk[i + 1]]
        pk = sorted(pk, key=lambda i: -spk[i])[:6]
        df = 1 / (1 / blo - 1 / B.max())
        print(f"  FFT B>={blo} T (df={df:.2f} T): peaks " +
              ", ".join(f"{fk[i]:.1f}T({spk[i]/spk.max():.2f})" for i in sorted(pk, key=lambda i: fk[i])))
        axes[k, 2].plot(fk, spk / spk.max(), lw=1, label=f"B>{blo} T")
    axes[k, 2].axvline(F_L, color="k", ls=":", label=f"F_L(full n)={F_L:.0f} T")
    axes[k, 2].set_xlabel("F (T)"); axes[k, 2].set_ylabel("norm |FFT|"); axes[k, 2].legend(fontsize=7)
    axes[k, 2].set_title("SdH FFT")

    try:
        so = sdh_onset(np.abs(R), B, r_full_scale=rail)
        print(so.summary())
        out[rid] = dict(onset_b=float(so.onset_b), onset_freq=float(so.onset_freq),
                        tones=[(float(t.freq), float(t.contrast), float(t.onset_b)) for t in so.tones],
                        n_cal=float(n_cal), F_L=float(F_L))
    except Exception as e:
        print("  sdh_onset FAILED:", type(e).__name__, e)
        out[rid] = dict(error=str(e), n_cal=float(n_cal), F_L=float(F_L))

fig.tight_layout(); fig.savefig("hera_scratch/spots_67.png", dpi=110)
json.dump(out, open("hera_scratch/spots_67.json", "w"), indent=1, default=float)
print("\nsaved hera_scratch/spots_67.png")
