# Session cleanup: ramp magnet 7.95 T -> 0 T (campaign concluding, device idle).
print("B before:", magnet.field(), "T")
magnet.field(0.0)   # ~58 min blocking ramp
print("B after :", magnet.field(), "T")
