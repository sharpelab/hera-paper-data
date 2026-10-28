# Gate C analysis — gate-current-sanity-check runs 0-3 (scratch)
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run

SR0_GAIN = -1e6      # Ithaco, V/A
I_BIAS = 1e-9        # 10 mV / 10 MOhm

runs = {i: open_run(f"data/{i}") for i in range(4)}
legs = {0: ("TG", "k_2400_tg", "+0.8"), 1: ("TG", "k_2400_tg", "-0.8"),
        2: ("BG", "k_2400_bg", "+5"), 3: ("BG", "k_2400_bg", "-5")}

# --- Fig 1: raw gate I-V (swept gate current vs its own V), all legs ---
fig, axs = plt.subplots(1, 2, figsize=(11, 4.5))
for i, (gname, inst, ep) in legs.items():
    r = runs[i]
    v = r.col(f"{inst}_volt")
    icurr = r.col(f"{inst}_curr")
    ax = axs[0] if gname == "TG" else axs[1]
    ax.plot(v, icurr * 1e12, ".", ms=2, label=f"run {i}: 0 -> {ep} V")
for ax, t in zip(axs, ["TG (k_2400_tg): I_tg vs V_tg", "BG (k_2400_bg): I_bg vs V_bg"]):
    ax.set_title(t); ax.set_xlabel("V (V)"); ax.set_ylabel("I_gate (pA)")
    ax.axhline(0, color="gray", lw=0.5); ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("hera_scratch/gatec_gate_iv.png", dpi=110)

# --- numbers: offset, excess vs offset, 100 pA crossing, endpoint ---
print("=== gate I-V numbers ===")
for i, (gname, inst, ep) in legs.items():
    r = runs[i]
    v, icurr = r.col(f"{inst}_volt"), r.col(f"{inst}_curr")
    o = np.argsort(np.abs(v)); v, icurr = v[o], icurr[o]
    i0 = np.median(icurr[np.abs(v) < 0.05 * np.abs(v).max()])
    excess = np.abs(icurr - i0)
    # smooth excess a touch for crossing detection
    k = 7; ex_s = np.convolve(excess, np.ones(k)/k, mode="same")
    cross = v[ex_s > 100e-12]
    vc = cross[np.argmin(np.abs(cross))] if len(cross) else np.nan
    # local conductance over last 20% of leg
    n = len(v); sl = slice(int(0.8*n), n)
    g = np.polyfit(v[sl], icurr[sl], 1)[0]
    print(f"run {i} {gname} 0->{ep}V: offset {i0*1e12:+.1f} pA, endpoint {icurr[-1]*1e12:+.1f} pA "
          f"(excess {excess[-1]*1e12:.1f} pA), |excess|>100pA beyond V={vc:+.3f} V, "
          f"local G(last 20%) = {g*1e12:.1f} pS")

# --- Fig 2: drain current + parked-gate current per leg ---
fig, axs = plt.subplots(1, 2, figsize=(11, 4.5))
for i, (gname, inst, ep) in legs.items():
    r = runs[i]
    v = r.col(f"{inst}_volt")
    idr = r.col("sr0_X") / SR0_GAIN
    axs[0].plot(v, np.abs(idr) * 1e12, ".", ms=2, label=f"run {i}: {gname} -> {ep} V")
    parked = "k_2400_bg" if gname == "TG" else "k_2400_tg"
    axs[1].plot(v, r.col(f"{parked}_curr") * 1e12, ".", ms=2, label=f"run {i}: parked {parked[-2:]}")
axs[0].set_title("|I_drain| (sr0/gain) vs swept gate V"); axs[0].set_ylabel("|I_drain| (pA)")
axs[0].axhline(I_BIAS*1e12, color="r", ls="--", lw=0.8, label="I_bias 1 nA")
axs[1].set_title("parked-gate current"); axs[1].set_ylabel("I (pA)")
for ax in axs: ax.set_xlabel("swept V (V)"); ax.legend(fontsize=7); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("hera_scratch/gatec_drain_parked.png", dpi=110)

print()
print("=== drain / liveness ===")
for i, (gname, inst, ep) in legs.items():
    r = runs[i]
    idr = r.col("sr0_X") / SR0_GAIN
    print(f"run {i} {gname}->{ep}V: |I_drain| med {np.median(np.abs(idr))*1e12:.1f} pA "
          f"(of {I_BIAS*1e12:.0f} pA driven) -> R_SD_tot ~ {0.010/np.median(np.abs(idr))/1e6:.0f} MOhm; "
          f"T_sample med {np.median(r.col('T_sample')):.3f} K")

# --- Rxx channels: signal vs noise (are 4T probes established?) ---
print()
print("=== Rxx channels (V/I_bias, nominal 1 nA) ===")
for i, (gname, inst, ep) in legs.items():
    r = runs[i]
    out = []
    for ch in ("sr1", "sr2", "sr3"):
        x = r.col(f"{ch}_X")
        out.append(f"{ch}: med {np.median(x)*1e9:+.1f} nV rms-dev {np.std(x)*1e9:.1f} nV")
    print(f"run {i} {gname}->{ep}V: " + " | ".join(out))
