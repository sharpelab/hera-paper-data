# Kernel-binding probe (read-only) — confirm nb-collab now reaches the
# instrument-connected kernel before any measure cell. No hardware writes.
names = ["magnet","heater","sr0","sr1","sr2","sr3","k_bg","k_2410",
         "k_tg","dc205_volt","mux","async_station","np"]
missing = [n for n in names if n not in globals()]
print("missing names:", missing)
print("B =", magnet.mag(), "T ;  T =", heater.sample_temperature(), "K")
print("kernel OK" if not missing else "KERNEL STILL WRONG")
