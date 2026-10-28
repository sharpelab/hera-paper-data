# Set SR830 voltage-channel sensitivities for the 5 nA / unity-gain config.
# Full scale R = sens / I_bias.  200 uV -> 40 kohm full scale (25-50k target).
# sr0 = current channel (Ithaco) — leave it alone.
I_bias = 5e-9
for sr in (sr1, sr2, sr3):
    sr.sensitivity(2e-4)   # 200 uV
for nm, sr in [("sr0(curr)", sr0), ("sr1", sr1), ("sr2", sr2), ("sr3", sr3)]:
    s = sr.sensitivity()
    print(f"{nm}: sensitivity = {s:.2e} V" + ("" if nm.startswith("sr0") else f"  -> full scale {s/I_bias:.0f} ohm"))
# refresh meas_config sens metadata so future runs record correctly
meas_config["sr1_sens"] = sr1.sensitivity()
meas_config["sr2_sens"] = sr2.sensitivity()
meas_config["sr3_sens"] = sr3.sensitivity()
print("meas_config sens updated")
