import json,sys
for p in sys.argv[1:]:
    d=json.load(open(p))
    print('=====',p)
    print('columns',d['columns'])
    print('mc',json.dumps(d['measurement_config'])[:1500])
    print('type',d['type'],'function',d.get('function'),'slow_delay',d['slow_delay'],'fast_delay',d['fast_delay'],'slow_params',d['slow_params'],'fast_params',d['fast_params'],'interrupted',d['interrupted'], d['start_time'], d.get('end_time'))
    print('comments',d['comments'])
    for name,ins in d['instruments'].items():
        pars=ins.get('snapshot',{}).get('parameters',{})
        if 'sensitivity' in pars or 'time_constant' in pars:
            keys=['sensitivity','time_constant','filter_slope','amplitude','frequency','reserve','input_config','input_coupling','sync_filter','harmonic','notch_filter','input_shield']
            print(' ',name,{k:pars[k].get('value') for k in keys if k in pars})
        elif name not in ('k_2400_tg','k_2400_bg'):
            print(' ',name, {k:v.get('value') for k,v in pars.items() if k in ('field','ramp_rate','amplitude','gain','sensitivity')})
