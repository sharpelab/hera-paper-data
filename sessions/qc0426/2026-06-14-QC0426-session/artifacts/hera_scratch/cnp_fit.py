import json, gzip, numpy as np
from scipy.ndimage import gaussian_filter1d
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages

FID = 18
m = json.load(open(f"data/{FID}/metadata.json"))
cols = m["columns"]; ci = {c: i for i, c in enumerate(cols)}
d = np.loadtxt(gzip.open(f"data/{FID}/data.tsv.gz"))
bg = np.array(m["slow_setpoints"]); tg = np.array(m["fast_setpoints"])
nb, nf = len(bg), len(tg)
print("cols:", cols, "| grid", nb, "x", nf, "=", nb*nf, "rows on disk", d.shape[0])

I = d[:, ci["sr0_X"]] / -1e6            # measured drain current
def grid(ch):  # 4T voltage reshaped (V), and R via I_bias=5nA (avoids I-glitch blowup)
    return d[:, ci[ch]].reshape(nb, nf)
V1, V2, V3 = grid("sr1_X"), grid("sr2_X"), grid("sr3_X")
Igrid = I.reshape(nb, nf)
Ibias = 5e-9

def ridge(V):
    """Per BG row: TG at max |smoothed Rxx|. Returns tg_cnp, clipped mask, peakR."""
    tgc = np.zeros(nb); clipped = np.zeros(nb, bool); peak = np.zeros(nb)
    for i in range(nb):
        s = gaussian_filter1d(np.abs(V[i]), 1.5)
        j = int(np.argmax(s))
        tgc[i] = tg[j]; peak[i] = np.abs(V[i, j]) / Ibias
        clipped[i] = (j <= 1 or j >= nf - 2)
    return tgc, clipped, peak

tg1, clip1, pk1 = ridge(V1)
tg2, clip2, pk2 = ridge(V2)

# --- fit CNP line per channel: Vtg_cnp = slope*Vbg + intercept (slope = -c_bg/c_tg) ---
def fit(tgc, clip, name):
    good = ~clip
    p, res = np.polyfit(bg[good], tgc[good], 1, full=True)[:2]
    slope, inter = p
    pred = np.polyval(p, bg[good])
    rms = float(np.sqrt(np.mean((tgc[good]-pred)**2)))
    print(f"  {name}: slope={slope:+.4f}  intercept={inter:+.4f} V  "
          f"ratio(c_bg/c_tg)={-slope:.4f}  rows={good.sum()}/{nb}  RMS={rms*1e3:.0f} mV  clipped={list(np.where(clip)[0])}")
    return slope, inter, rms, good

print("CNP-line fits (Vtg vs Vbg):")
s1, b1, rms1, g1 = fit(tg1, clip1, "sr1 T3-T4")
s2, b2, rms2, g2 = fit(tg2, clip2, "sr2 B4-B5")

# --- capacitance: geometry prior + data-calibrated ratio ---
c_tg = stack_capacitance([(15.6, 3)])          # F/m^2 (per device card)
c_bg = stack_capacitance([(12, 3), (0, 3.9)])
print(f"\ngeometry prior: c_tg={c_tg:.4e}  c_bg={c_bg:.4e}  ratio c_bg/c_tg={c_bg/c_tg:.4f}")

# anchor TG at prior, set c_bg from fitted ratio (sr1 = best channel)
ratio = -s1
c_bg_cal = ratio * c_tg
# density offset: n=0 on the fitted line. intercept b1 is Vtg at Vbg=0.
n_at_inter = calc_nD(b1, 0.0, c_tg, c_bg_cal)[0]
n_offset = -n_at_inter
print(f"data-cal: ratio={ratio:.4f}  c_bg_cal={c_bg_cal:.4e}  n_offset={n_offset:.3e} m^-2")

# closure check: n along the fitted ridge should be ~0
nres = []
for i in np.where(g1)[0]:
    n, D = calc_nD(tg1[i], bg[i], c_tg, c_bg_cal)
    nres.append(n + n_offset)
print(f"closure |n| max residual on ridge = {np.max(np.abs(nres)):.3e} m^-2")

# --- figure: per-channel map + ridge + fit ---
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
for k, (V, tgc, sl, inter, nm) in enumerate([(V1, tg1, s1, b1, "sr1 T3-T4 Rxx"),
                                             (V2, tg2, s2, b2, "sr2 B4-B5 Rxx")]):
    R = np.abs(V) / Ibias / 1e3
    im = ax[k].pcolormesh(bg, tg, R.T, shading="nearest", vmax=np.percentile(R, 99))
    ax[k].plot(bg, tgc, "w.", ms=4, label="ridge argmax")
    ax[k].plot(bg, sl*bg+inter, "r-", lw=1, label=f"fit slope={sl:.3f}")
    ax[k].set_xlabel("Vbg (V)"); ax[k].set_ylabel("Vtg (V)"); ax[k].set_title(nm)
    ax[k].legend(loc="upper right", fontsize=8); fig.colorbar(im, ax=ax[k], label="Rxx (kΩ)")
fig.tight_layout(); fig.savefig("hera_scratch/cnp_fit.png", dpi=110)
print("saved hera_scratch/cnp_fit.png")
