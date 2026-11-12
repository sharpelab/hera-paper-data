import json, numpy as np
from hera.analysis import field_invB
fan_B = np.concatenate(([0.0,0.7,1.0,1.25], field_invB(1.5,4.0,61), np.linspace(4.2,10.0,30)))
out = {
 "status":"extracted","landed":"fan","form":"2d_megasweep","field_mode":"stitched",
 "B_values":[round(float(x),6) for x in fan_B],
 "n_min_cm2":-1.2e12,"n_max_cm2":3.2e12,"n_columns":111,"D":0.0,
 "slow_axis":"B","slow_delay_s":3.0,"fast_delay_s":3.0,
 "lockins":[
  {"name":"sr0","sensitivity_V":2e-2,"sensitivity_set_in_answer":True,"time_constant_s":0.3,"time_constant_set_in_answer":False},
  {"name":"sr1","sensitivity_V":1e-4,"sensitivity_set_in_answer":True,"time_constant_s":0.3,"time_constant_set_in_answer":False}],
 "gate_current_reads":[
  {"name":"k_2400_tg_curr","nplc":1.0,"nplc_set_in_answer":False},
  {"name":"k_2400_bg_curr","nplc":1.0,"nplc_set_in_answer":False}],
 "excitation_V":1.0,"bias_resistor_ohm":1e8,"n_fans":1,"stated_wall_clock_h":12.0,
 "flags":[],
 "notes":"cell 48: s.multimegasweep([magnet.field],[fan_B],[k_tg.volt,k_bg.volt],[fan_tg,fan_bg],slow_delay=3,fast_delay=3). fan_B = concat([0,0.7,1.0,1.25], field_invB(1.5,4.0,61), linspace(4.2,10.0,30)) = 95 stitched setpoints (4 low-B controls, an inverse-B leg 1.5-4 T, then a uniform 0.2 T leg to 10 T). Densities are the cell's own fan_n = np.linspace(-1.2, 3.2, 111) in 1e12 cm^-2 at D = 0 via calc_gate_voltages with the run-5 FAN_CAL (TG -0.2770..+0.9836 V, BG -0.4650..+1.1663 V); the cell calls the absolute scale a geometry prior and D=0 a symmetry estimate. sr0/sr1 sensitivities are set in the appended cell; tau 0.3 s, slope 24 dB/oct, NPLC 1/1, drive 1.0 V and the 100 MOhm bias resistor are inherited and only asserted/read there. 12 h is the markdown's stated budget."
}
json.dump(out, open('/grade-run/output.json','w'), indent=1)
print("ok")
