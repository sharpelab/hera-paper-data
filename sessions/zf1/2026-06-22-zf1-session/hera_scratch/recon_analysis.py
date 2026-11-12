import sys, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

rid = sys.argv[1] if len(sys.argv) > 1 else "1"
run = open_run(f"data/{rid}")
print(summarize_run(run))
print("cols:", run.cols)
print("interrupted:", run.interrupted)

t   = run.col("time")
vtg = run.col_at(run.cols.index("k_tg_volt"))      # first k_tg_volt (slow axis)
# fast axis bg, and currents
def c(name): return run.col(name)
vbg = run.col_at(2)                                 # k_bg_volt (fast axis; also fp'd at 6)
itg = c("k_tg_curr"); ibg = c("k_bg_curr")
I   = c("sr830_1_X")/(-1e6)                         # measured device current (A)
v2  = c("sr830_2_X")/100.0                          # 2T volts
v3  = c("sr830_3_X")/100.0                          # 4T volts

print(f"\nleakage: |I_tg|max={np.abs(itg).max():.2e} A  |I_bg|max={np.abs(ibg).max():.2e} A")
print(f"current: I med={np.median(I)*1e9:.3f} nA  min={I.min()*1e9:.3f}  max={I.max()*1e9:.3f}")

# clip check: sensitivity was 0.5 V on voltage channels -> lock-in input = V*100
clip2 = np.abs(run.col("sr830_2_X")).max()/0.5
clip3 = np.abs(run.col("sr830_3_X")).max()/0.5
print(f"clip frac (|X|max/sens): sr2={clip2:.3f}  sr3={clip3:.3f}  (>~0.9 => clipping)")

# timing
dt = np.diff(t)
print(f"timing: {len(t)} pts, wall={(t[-1]-t[0]):.0f}s, per-pt med={np.median(dt):.3f}s mean={np.mean(dt):.3f}s")

# per-row CNP (Rxx max in BG)
tg_vals = np.unique(np.round(vtg, 3))
print("\n--- per-TG-row CNP (4T Rxx=v3/I) ---")
cnp_bg = {}; fig, ax = plt.subplots(1, 2, figsize=(11,4))
for tv in tg_vals:
    m = np.isclose(vtg, tv, atol=1e-3)
    bg = vbg[m]; R = (v3[m]/I[m]); order = np.argsort(bg)
    bg, R = bg[order], R[order]
    # smooth then argmax for ridge
    from scipy.ndimage import gaussian_filter1d
    Rs = gaussian_filter1d(np.nan_to_num(R), 1.5)
    k = np.argmax(Rs); cnp_bg[tv] = bg[k]
    edge = (k <= 1 or k >= len(bg)-2)
    print(f"  TG={tv:+.2f}: CNP @ Vbg={bg[k]:+.3f} V  Rpeak={R[k]/1e3:.1f} kOhm  Imin={I[m].min()*1e9:.3f} nA{'  [EDGE-CLIPPED ROW]' if edge else ''}")
    ax[0].plot(bg, R/1e3, label=f"TG={tv:+.1f}")
    ax[0].axvline(bg[k], ls=":", alpha=0.4)
ax[0].set_xlabel("V_bg (V)"); ax[0].set_ylabel("R_4T (kOhm)"); ax[0].set_title(f"recon run {rid}: 4T Rxx vs BG"); ax[0].legend()

# 3-pt cap-ratio preview: fit Vbg_cnp vs Vtg  -> slope dVbg/dVtg; c_bg/c_tg = -1/slope
tgs = np.array(sorted(cnp_bg)); bgs = np.array([cnp_bg[t_] for t_ in tgs])
if len(tgs) >= 2:
    slope, b0 = np.polyfit(tgs, bgs, 1)
    print(f"\nCNP line: Vbg = {slope:+.3f}*Vtg {b0:+.3f}")
    print(f"  dVbg/dVtg = {slope:+.3f}  ->  c_bg/c_tg = -1/slope = {(-1/slope):+.3f}  (PREVIEW; geom prior ratio = 1/1.18={1/1.18:.3f})")
    ax[1].plot(tgs, bgs, "o-"); ax[1].set_xlabel("V_tg (V)"); ax[1].set_ylabel("V_bg at CNP"); ax[1].set_title("CNP line (3-pt preview)")
fig.tight_layout(); fig.savefig(f"hera_scratch/recon_run{rid}.png", dpi=110)
print(f"\nsaved hera_scratch/recon_run{rid}.png")
