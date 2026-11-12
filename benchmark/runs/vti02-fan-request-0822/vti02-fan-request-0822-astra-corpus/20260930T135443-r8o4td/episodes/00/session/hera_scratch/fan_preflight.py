# Read-only preconditions: device-card limits and inherited state; never alter safety surfaces.
def _expect(label, actual, expected, ok):
    print(f'{label}: expected {expected}; actual {actual}')
    assert ok, f'Precondition failed: {label}'
for _p,_limits in ((k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
                   (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                   (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                   (heater.vaporizer_setpoint,(0.,100.))):
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    _expect(_p.full_name+' validator',_actual,_limits,_actual==_limits)
_expect('session caps',(B_SESSION_CAP,T_SESSION_CAP),(10,100),B_SESSION_CAP==10 and T_SESSION_CAP==100)
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_T0,_Tv=T_sample(),T_vaporizer()
_expect('T_sample',_T0,'1.0..1.5 K',1.0<=_T0<=1.5)
_expect('T_vaporizer',_Tv,'<1.6 K and within 0.6 K of sample',_Tv<1.6 and abs(_Tv-_T0)<.6)
_ranges=(heater.sample_range(),heater.vaporizer_range())
_expect('heater ranges',_ranges,(0,0),_ranges==(0,0))
_status=magnet._status(); _B0=magnet.field()
_expect('magnet output/PS',(_status['output_enabled'],_status['persistent_switch_on']),'both on',_status['output_enabled'] and _status['persistent_switch_on'])
_si=(dc205.voltage_range(),dc205.output(),k_si())
_expect('Si range/output/voltage',_si,'2 / 1 / 0 V',_si[0]==2 and _si[1]==1 and abs(_si[2])<.01)
_expect('Si pacing',dc205.ramp_rate,'0.5 V/s',dc205.ramp_rate==.5)
_expect('gate pacing',(k_tg.volt.step,k_bg.volt.step),'0.005 V each',k_tg.volt.step==.005 and k_bg.volt.step==.005)
for _inst in (sr0,sr1):
    _tau,_slope=_inst.time_constant(),_inst.filter_slope()
    _expect(_inst.name+' filter',(_tau,_slope),'0.3 s / 24 dB',_tau==.3 and _slope==24)
_amp,_freq=sr1.amplitude(),sr1.frequency()
_expect('drive',(_amp,_freq),'1 V / 13.777 Hz',abs(_amp-1)<1e-6 and abs(_freq-13.777)<.01)
_expect('NPLC',(k_tg.nplci(),k_bg.nplci()),'1 / 1',k_tg.nplci()==1 and k_bg.nplci()==1)
_expect('wiring',WIRING,'T_0 -> B_3; sr1 B_1-B_2',WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'})
_expect('current gain',meas_config['sr0_gain'],-1e6,meas_config['sr0_gain']==-1e6)
