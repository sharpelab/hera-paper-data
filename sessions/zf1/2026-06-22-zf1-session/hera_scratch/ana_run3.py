# --- Run 3: fine n-linecuts at fixed D. CANDIDATE search (raw Rxx(n)). ---
g3 = open_run(Path(file_path)/"3"); print(summarize_run(g3))
lc = np.load("hera_scratch/linecut_vectors.npz"); Dl=lc["D"]; nl=lc["n"]; Ds=lc["Ds"]
I3 = g3.col("sr830_1_X")/(-1e6); R3 = np.abs(g3.col("sr830_3_X")/100.0/I3)
m = min(len(R3), len(Dl)); R3,Dl2,nl2 = R3[:m],Dl[:m],nl[:m]
fig, ax = plt.subplots(figsize=(8,5))
for D0 in Ds:
    s=np.isclose(Dl2,D0); o=np.argsort(nl2[s])
    ax.plot(nl2[s][o], R3[s][o], marker=".", ms=4, label=f"D={D0:+.2f}")
    print(f"  D={D0:+.2f}: Rxx min={R3[s].min():.1f} Ω @ n={nl2[s][np.argmin(R3[s])]:+.2f}e11")
ax.set_xlabel("n (1e11 cm⁻²)"); ax.set_ylabel("R_4T (Ω)"); ax.axhline(0,color="k",lw=.5)
ax.set_title("Run 3 — fine n-linecuts: Rxx(n) at fixed D  (dip at D=−0.65, n≈−4.8)")
ax.legend(); ax.grid(alpha=.3); plt.show()
