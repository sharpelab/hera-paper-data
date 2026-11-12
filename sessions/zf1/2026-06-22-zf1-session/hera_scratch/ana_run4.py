# --- Run 4: confirm candidate, pin optimum, resolve floor @ 200 µV. RAW. ---
g4 = open_run(Path(file_path)/"4"); print(summarize_run(g4))
v = np.load("hera_scratch/confirm_vectors.npz"); vtg=v["vtg"]; vbg=v["vbg"]; seg=v["seg"]
N4 = cal.density(vtg,vbg)/1e15; D4 = cal.displacement_field(vtg,vbg)/1e9
I4 = g4.col("sr830_1_X")/(-1e6); R4 = np.abs(g4.col("sr830_3_X")/100.0/I4)
m=min(len(R4),len(seg)); R4,N4,D4,seg=R4[:m],N4[:m],D4[:m],seg[:m]
fig,ax=plt.subplots(1,2,figsize=(13,5))
for D0 in (-0.55,-0.60,-0.65):
    s=np.isclose(D4,D0,atol=0.01); o=np.argsort(N4[s])
    ax[0].plot(N4[s][o],R4[s][o],marker=".",ms=4,label=f"D={D0:+.2f}")
    print(f"  D={D0:+.2f}: Rxx min={R4[s].min():.2f} Ω @ n={N4[s][o][np.argmin(R4[s][o])]:+.2f}e11")
ax[0].set_xlabel("n (1e11 cm⁻²)"); ax[0].set_ylabel("R_4T (Ω)"); ax[0].axhline(0,color="k",lw=.5)
ax[0].set_title("Run 4 — confirm linecuts (200 µV): Rxx→0 at D=−0.65"); ax[0].legend(); ax[0].grid(alpha=.3)
se=seg=="edge"; o=np.argsort(D4[se])
ax[1].plot(D4[se][o],R4[se][o],"o-",ms=4,color="purple")
ax[1].set_xlabel("D (V/nm)"); ax[1].set_ylabel("R_4T (Ω)"); ax[1].set_title("edge sweep (BG=+4.198): Rxx vs D"); ax[1].grid(alpha=.3)
print(f"  edge: Rxx min={R4[se].min():.2f} Ω @ D={D4[se][np.argmin(R4[se])]:+.3f}")
plt.show()
print(f"GLOBAL min Rxx = {R4.min():.2f} Ω")
