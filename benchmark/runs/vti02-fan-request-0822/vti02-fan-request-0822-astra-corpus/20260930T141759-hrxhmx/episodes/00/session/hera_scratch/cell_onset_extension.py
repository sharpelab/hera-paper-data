# Read-only preflight: gate B and state inherited from the handoff.
for _p, _expected in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
 (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
 (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
 _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
 print(_p.full_name,'validator expected',_expected,'actual',_actual)
 assert _actual==_expected
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
for _name,_param in [('T_sample',T_sample),('T_vaporizer',T_vaporizer)]:
 assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv=T_sample(),T_vaporizer()
print('expected base sample 1.0-1.5 K, vaporizer <1.6 K; actual',_Ts,_Tv)
assert 1.0<=_Ts<=1.5 and _Tv<1.6 and abs(_Tv-_Ts)<0.6
_ranges=(heater.sample_range(),heater.vaporizer_range());print('heater ranges expected 0,0 actual',_ranges);assert _ranges==(0,0)
_B=magnet.field();print('B expected near 0 T; actual',_B);assert abs(_B)<0.05
assert magnet.persistent_switch_on() and magnet.output_enabled()
_si=dc205.voltage();print('Si expected 0 V, actual',_si);assert abs(_si)<0.01 and dc205.voltage_range()==2 and dc205.output()==1
assert dc205.ramp_rate==0.5 and k_tg.volt.step==0.005 and k_bg.volt.step==0.005
assert k_tg.nplci()==1 and k_bg.nplci()==1
print('drive expected 1 V,13.777 Hz actual',sr1.amplitude(),sr1.frequency())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<0.01
for _li in [sr0,sr1]:
 print(_li.name,'tau/slope expected .3 s/24, actual',_li.time_constant(),_li.filter_slope())
 assert _li.time_constant()==0.3 and _li.filter_slope()==24
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB
CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-0.0894,D_offset=-0.013)
vt,vb=calc_gate_voltages(3.2,0.,**CAL)
assert -0.3<=vt<=1 and -1.3<=vb<=2
B_vec=field_invB(0.4,2.0,241)
assert np.max(np.abs(np.diff(1/B_vec)))<=1/(3*40)+1e-12
sr1.sensitivity(50e-6)
mc=dict(meas_config);mc.update({'Si (V)':0.,'sample_temperature:':_Ts,'comments':'electron onset extension n_A=3.2e12 D_A=0; B 0.4->2T uniform inverse B; 241 pts, 3s delay, run5 calibration','calibration':CAL})
s=sweep.AsyncStation(mc);s.add_comment('sdh-spot-check')
s.add_comment('Onset extension: n_A=+3.2e12 cm^-2 D_A=0 V/nm Si=0; B=0.4->2 T, 241 uniform-inverse-B points; 3s delay, sr1=50uV tau=.3s slope24')
s.ramp(k_bg.volt,vb);s.ramp(k_tg.volt,vt)
interruptible_sleep(3)
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr).fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
for _p in [T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P]:s.plot(magnet.field,_p)
def onset_guard(station,data):
 # time, B, Ts,Tv,Itg,Ibg,Ix,Ip,Vx,Vp
 if abs(data[4])>1e-9 or abs(data[5])>1e-9 or not 1<=data[2]<=1.5 or abs(data[8])>=0.9*50e-6:
  print('CHECKPOINT STOP: leakage, temperature, or range',data);station.interrupt_requested=True
s.register_run_after(onset_guard,())
s.sweep(magnet.field,B_vec,delay=3.0)
print('ONSET EXTENSION finished; actual B,gates',magnet.field(),k_tg.volt(),k_bg.volt())
