# Runs 6-7: raw gain-divided MR, no background removal (raw before interpretation)
run6, run7 = run(6), run(7)
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for a, r, lab in ((ax[0], run6, "run 6: electron n=+3.2e12, B 0->10 T"),
                  (ax[1], run7, "run 7: hole n=-1.2e12, B 10->0.3 T")):
    B = r.col("magnet_field")
    amp = r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]
    I = amp / r.meta["measurement_config"]["bias_resistor"]
    R = r.col("sr1_X") / I
    a.plot(B, R, lw=0.5)
    a.set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=lab)
    print(f"{lab}: I_bias {I*1e9:.1f} nA, R {np.nanmin(R):.0f}..{np.nanmax(R):.0f} Ohm, "
          f"T {np.nanmin(r.col('T_sample')):.3f}-{np.nanmax(r.col('T_sample')):.3f} K, "
          f"|I_tg|max {np.nanmax(np.abs(r.col('k_2400_tg_curr')))*1e12:.0f} pA, "
          f"|I_bg|max {np.nanmax(np.abs(r.col('k_2400_bg_curr')))*1e12:.0f} pA")
fig.tight_layout()
