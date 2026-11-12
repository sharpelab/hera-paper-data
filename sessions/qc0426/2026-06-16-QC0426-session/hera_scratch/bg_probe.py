import time
print("step:", k_bg.volt.step, " inter_delay:", getattr(k_bg.volt,'inter_delay',None))
for _ in range(5):
    print("k_bg.volt() =", k_bg.volt())
print("-- set 0 --")
k_bg.volt.set(0)
for _ in range(4):
    print("k_bg.volt() =", k_bg.volt())
