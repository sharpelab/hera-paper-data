# Gate C (part 1) — route provided contact configuration via ContactMux.
print("pre  | T:", heater.sample_temperature(), "K  B:", magnet.field(), "T  "
      "BG:", k_bg.volt(), "V  Si:", k_si.volt(), "V")

mux.select({"source": "T2", "drain": "B7",
            "sr1+": "T3", "sr1-": "T4",
            "sr2+": "B4", "sr2-": "B5",
            "sr3+": "T5", "sr3-": "B6"})
print("contacts selected: source=T2 drain=B7 | sr1=T3-T4 sr2=B4-B5 sr3=T5-B6(Hall)")

# Raw lock-in read-back (gain-uncorrected) to confirm contacts are live.
for nm, sr in [("sr0(I)", sr0), ("sr1", sr1), ("sr2", sr2), ("sr3", sr3)]:
    print(f"  {nm}: X={sr.X():.4e}  P={sr.P():.2f} deg  sens={sr.sensitivity()}")
