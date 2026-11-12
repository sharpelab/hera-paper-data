# Runs 6-7: TG linecuts at 10 T, Vbg = 0, Si = 0 vs +25 V. Raw R(Vtg) and drain current.
fig, ax = plt.subplots(1, 2, figsize=(13, 4))
for rid, lab in ((6, "Si = 0"), (7, "Si = +25 V")):
    r = run(rid); mc = r.meta["measurement_config"]
    I = r.col("sr0_X") / float(mc["sr0_gain"]); R = r.col("sr1_X") / I; x = r.col("k_2400_tg_volt"); o = np.argsort(x)
    ax[0].semilogy(x[o], np.abs(R[o]), label=lab); ax[1].plot(x[o], I[o] * 1e9, label=lab)
    print(f"run {rid} {lab}: |R| at Vtg -0.3/-0.2/-0.1/0.0/+0.1/+0.3/+0.6/+1.0 V = " + " / ".join(f"{abs(R[np.argmin(abs(x-v))]):.0f}" for v in (-0.3, -0.2, -0.1, 0.0, 0.1, 0.3, 0.6, 1.0)) + " Ohm")
ax[0].set_xlabel("V_tg [V]"); ax[0].set_ylabel("|R| (B_1-B_2) [Ohm], B = 10 T, V_bg = 0"); ax[0].legend()
ax[1].set_xlabel("V_tg [V]"); ax[1].set_ylabel("I_drain [nA]"); ax[1].legend(); plt.tight_layout(); plt.show()
