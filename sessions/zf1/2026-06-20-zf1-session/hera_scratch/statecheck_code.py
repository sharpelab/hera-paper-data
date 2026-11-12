# Post-error device state check. Run 2 gatemap crashed on a transient SR830
# SNAP read at row 44/61; the cell's finally should have parked gates to 0.
print("T          :", temperature(), "K")
print("magnet B   :", magnet.field(), "T")
print("k_tg.volt  :", k_tg.volt(), "V")
print("k_bg.volt  :", k_bg.volt(), "V")
print("k_tg.curr  :", k_tg.curr(), "A")
print("k_bg.curr  :", k_bg.curr(), "A")
for sr in (sr830_1, sr830_2, sr830_3, sr830_4):
    print(f"{sr.name}: X={sr.X():.4e}  P={sr.P():.2f}")

# re-park if the finally didn't (or partially) land
if abs(k_tg.volt()) > 1e-3 or abs(k_bg.volt()) > 1e-3:
    print(">> gates not at 0 — re-parking")
    k_tg.volt(0)
    k_bg.volt(0)
    print("   k_tg.volt:", k_tg.volt(), " k_bg.volt:", k_bg.volt())
else:
    print(">> gates parked at 0 (finally ran OK)")
