# === Diagnostic: resolve SdH bias current (sr0 read 10.9 nA vs expected 50 nA) ===
# Hypothesis: sr0 sens was 0.01 V (10 mV FS); a true 50 nA -> 50 mV at the Ithaco
# x1e6 -> overloads sr0 -> garbage readback. Coarsen sr0 to 0.1 V and re-measure;
# sweep amplitude to confirm the (linear) amplitude->current transfer (100 MOhm bias).
# Field sits at 0.74 T (interrupted); current bias is B-independent so this is valid.
print('state: B=', round(magnet.mag(),3), 'T ; sr1.amplitude=', sr1.amplitude(),
      'V ; f=', sr1.frequency(), 'Hz ; sr0.sens(old)=', sr0.sensitivity())
sr0.sensitivity(0.1)            # 100 mV FS: headroom for 50 nA * 1e6 = 50 mV
time.sleep(2)
for amp in (0.5, 1.0, 2.0, 5.0):
    sr1.amplitude(amp); time.sleep(3.0)
    I = sr0.X()/(-1e6)
    print(f'amp={amp:.2f}V -> I_drain={I*1e9:7.2f} nA (expect {amp/1e8*1e9:5.1f} nA) '
          f'| sr0_X={sr0.X()*1e3:+.2f} mV | Rxx_sr1={sr1.X()/I:6.1f} ohm | sr0 ovld={sr0.sensitivity()}')
print('left at amp=5 V')
