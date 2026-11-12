# === SdH spot check, electron side (`sdh-spot-check`): n = +3.2e12 at D = 0 (region-A calibration), B 0 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# --- session calibration from run 5 (cnp-and-dline-calibration; ratio data-calibrated, scale = geometry prior) ---
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_spot, D_spot = 3.2, 0.0                       # 1e12 cm^-2, V/nm
Vtg_spot, Vbg_spot = calc_gate_voltages(n_spot, D_spot, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot: n = {n_spot:+.2f}e12, D = {D_spot:+.2f} V/nm -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V; "
      f"roundtrip n,D = {calc_nD(Vtg_spot, Vbg_spot, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])}")

# --- inherited state and Gate B, reads only ---
for p, expected in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
 (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
 (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
    actual=(float(p.vals._min_value),float(p.vals._max_value))
    print(p.full_name, 'expected validator',expected,'actual',actual)
    assert actual == expected
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
for name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
_T0, _Tv, _B0, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
print('Expected base T 1–1.5 K, vaporizer <1.6 K, field 0±0.05 T, Si 0±0.01 V:',_T0,_Tv,_B0,_Si)
assert 1 <= _T0 <= 1.5 and _Tv < 1.6 and abs(_Tv-_T0)<0.6 and abs(_B0)<0.05 and abs(_Si)<0.01
print('Expected heater ranges 0,0:',heater.sample_range(),heater.vaporizer_range())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert dc205.voltage_range()==2 and dc205.output()==1
assert WIRING == {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('Expected drive 1 V, 13.777 Hz:',sr1.amplitude(),sr1.frequency())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<.01
for li in (sr0,sr1):
    print(li.name,'expected tau .3 s / 24 dB:',li.time_constant(),li.filter_slope())
    assert li.time_constant()==.3 and li.filter_slope()==24
assert magnet.settle_s >= 3
assert k_tg.volt.step==.005 and k_bg.volt.step==.005
print('Expected NPLC=1:',k_tg.nplci(),k_bg.nplci())
assert k_tg.nplci()==1 and k_bg.nplci()==1
B_vec = field_invB(0.3,1.5,335)
assert np.max(np.abs(np.diff(1/B_vec))) <= 1/(3*39.704)
sr1.sensitivity(50e-6)
mc=dict(meas_config)
mc.update({'Si (V)':_Si,'sample_temperature:':_T0,'comments':'electron onset extension n=+3.2e12 D~0, run-5 cal; B .3->1.5 T uniform invB 335 pts, sr1 50 uV, tau .3 s, 24dB, dwell=3s driver settle'})
s=sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(mc['comments'])
s.ramp(k_bg.volt,Vbg_spot); s.ramp(k_tg.volt,Vtg_spot)
interruptible_sleep(10)
follow=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P]
for p in follow:
    s.fp(p); s.plot('time',p)
# layout time, B, Ts, Tv, Itg, Ibg, X0, P0, X1, P1
_ext_checks={'points':0}
def extension_guard(station,data):
    _ext_checks['points']+=1
    bad=(not np.all(np.isfinite(data)) or not 1<=data[2]<=1.5 or data[3]>=1.6
         or abs(data[4])>1e-9 or abs(data[5])>1e-9
         or abs(data[6])>=.018 or abs(data[8])>=45e-6)
    if bad:
        print('SAFETY TRIP: onset extension',data); station.interrupt_requested=True
    if _ext_checks['points']%20==0:
        for name in ('T_sample','T_vaporizer'):
            assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
s.register_run_after(extension_guard,())
result=s.sweep(magnet.field,B_vec,delay=0)
print('Extension finished; interrupted:',result.metadata.get('interrupted'))
print('Actual held state:',magnet.field(),k_tg.volt(),k_bg.volt(),T_sample())
