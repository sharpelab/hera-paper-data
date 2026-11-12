# Runs 0-3 — Gate C reduction: gate I-V, drain current, Rxx resolution
SR0_GAIN = -1e6   # Ithaco (device card)
I_BIAS = 1e-9     # 10 mV drive / 10 MOhm bias resistor

legs = {0: ("TG", "k_2400_tg", "+0.8"), 1: ("TG", "k_2400_tg", "-0.8"),
        2: ("BG", "k_2400_bg", "+5"), 3: ("BG", "k_2400_bg", "-5")}

fig, axs = plt.subplots(1, 3, figsize=(15, 4.2))
for i, (gname, inst, ep) in legs.items():
    g = run(i)
    v = g.col(f"{inst}_volt")
    ax = axs[0] if gname == "TG" else axs[1]
    ax.plot(v, g.col(f"{inst}_curr") * 1e12, ".", ms=2, label=f"run {i}: 0 → {ep} V")
    axs[2].plot(v, np.abs(g.col("sr0_X") / SR0_GAIN) * 1e12, ".", ms=2,
                label=f"run {i}: {gname} → {ep} V")
axs[0].set_title("TG gate current"); axs[1].set_title("BG gate current")
axs[2].set_title("|I_drain| (sr0/gain); driven 1000 pA")
axs[2].axhline(1000, color="r", ls="--", lw=0.8)
for ax in axs:
    ax.set_xlabel("swept gate V (V)"); ax.set_ylabel("I (pA)")
    ax.grid(alpha=0.3); ax.legend(fontsize=7)
fig.tight_layout(); plt.show()

print("=== gate I-V ===")
for i, (gname, inst, ep) in legs.items():
    g = run(i)
    v, ic = g.col(f"{inst}_volt"), g.col(f"{inst}_curr")
    o = np.argsort(np.abs(v)); v, ic = v[o], ic[o]
    i0 = np.median(ic[np.abs(v) < 0.05 * np.abs(v).max()])
    ex = np.abs(ic - i0)
    ex_s = np.convolve(ex, np.ones(7) / 7, mode="same")
    cross = v[ex_s > 100e-12]
    vc = f"{cross[np.argmin(np.abs(cross))]:+.2f} V" if len(cross) else "never"
    gloc = np.polyfit(v[int(0.8 * len(v)):], ic[int(0.8 * len(v)):], 1)[0]
    print(f"run {i} {gname} 0→{ep} V: offset {i0*1e12:+.0f} pA, endpoint {ic[-1]*1e12:+.0f} pA "
          f"(excess {ex[-1]*1e12:.0f} pA), excess>100 pA beyond {vc}, "
          f"local G(top 20%) {gloc*1e12:.0f} pS")

print()
print("=== drain / 4T ===")
for i, (gname, inst, ep) in legs.items():
    g = run(i)
    idr = np.median(np.abs(g.col("sr0_X") / SR0_GAIN))
    x1, x2, x3 = (np.median(g.col(f"{c}_X")) for c in ("sr1", "sr2", "sr3"))
    print(f"run {i} {gname}→{ep} V: |I_drain| {idr*1e12:.0f} pA -> R_SD ~ {0.010/idr/1e6:.0f} MOhm | "
          f"sr1/2/3 med {x1*1e9:+.0f}/{x2*1e9:+.0f}/{x3*1e9:+.0f} nV (ADC-LSB multiples: unresolved)")
