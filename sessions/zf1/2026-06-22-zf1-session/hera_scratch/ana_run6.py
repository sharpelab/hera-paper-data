# --- Run 6: field response (B⊥ kill) at the optimum. RAW Rxx(B). ---
g6 = open_run(Path(file_path)/"6"); print(summarize_run(g6))
mfi=[i for i,c in enumerate(g6.cols) if c=="magnet_field"]
B=(g6.col_at(mfi[-1]))*1e3                    # measured field, mT
Iac=g6.col("sr830_1_X")/(-1e6); Rxx=np.abs((g6.col("sr830_3_X")/100.0)/Iac)
Tk=g6.col("T")*1e3
o=np.argsort(B); B,Rxx,Tk=B[o],Rxx[o],Tk[o]
Rn=Rxx[np.abs(B)>0.7*B.max()].mean(); half=0.5*Rn
Bc=B[(B>0)&(Rxx>=half)].min()
print(f"normal Rxx={Rn:.1f}Ω (flat std/mean={np.std(Rxx[np.abs(B)>0.7*B.max()])/Rn:.2f}); Rxx_min={Rxx.min():.2f}Ω @ {B[np.argmin(Rxx)]:+.2f}mT; B_c⊥(half)≈{Bc:.1f}mT; T={Tk.min():.0f}-{Tk.max():.0f}mK")
fig,ax=plt.subplots(figsize=(7,5))
ax.plot(B,Rxx,".-",ms=4); ax.axhline(Rn,color="grey",ls=":",label=f"normal {Rn:.0f}Ω")
ax.axhline(half,color="orange",ls=":"); ax.axvline(Bc,color="r",ls="--",label=f"B_c⊥≈{Bc:.1f}mT")
ax.set_xlabel("B measured (mT)"); ax.set_ylabel("Rxx (Ω)")
ax.set_title("Run 6 — field-kill: Rxx(B) at SC optimum"); ax.legend(); ax.grid(alpha=.3); plt.show()
