# Park back gate to 0 — finally-block left it at ~-0.44 V (within validators).
print("BG before:", k_bg.volt(), "V")
k_bg.volt(0)
print("BG after :", k_bg.volt(), "V")
