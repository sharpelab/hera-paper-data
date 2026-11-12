from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset
import numpy as np

for rid in (6, 7):
    r = open_run(f'data/{rid}')
    print('\nRUN', rid, 'columns', r.cols)
    print('times', r.meta['start_time'], r.meta['end_time'], 'duration min', (r.meta['end_time']-r.meta['start_time'])/60)
    print('config', {k:v for k,v in r.meta['measurement_config'].items() if k in ('sr0_gain','sr1_gain','bias_resistor','bias_channel','sr1','sr0')})
    channels = resolve_channels(r.meta)
    print('channels', channels)
    c = current_channel(channels)
    I = r.col(c.col)/c.gain
    v = next(x for x in channels if x.cid=='sr1')
    R = np.abs((r.col(v.col)/v.gain)/I)
    B = r.col('magnet_field')
    for name, a in [('B',B), ('I_nA',I*1e9), ('R_ohm',R), ('Itg_pA',r.col('k_2400_tg_curr')*1e12),('Ibg_pA',r.col('k_2400_bg_curr')*1e12),('T',r.col('T_sample'))]:
        print(name, 'min/median/max',np.nanmin(a),np.nanmedian(a),np.nanmax(a))
    order = np.argsort(B)
    Bs, Rs = B[order], R[order]
    for br in [(2,10),(3,10),(4,10),(5,10)]:
        freqs,spec=sdh_fft(Rs[:,None], Bs, b_range=br, nfft=2048,bg_degree=4)
        mask=(freqs>2)&(freqs<90)
        inds=np.argsort(spec[0,mask])[-8:][::-1]
        print('FFT',br,[(round(float(freqs[mask][i]),2),round(float(spec[0,mask][i]),2)) for i in inds])
    try:
        print('ONSET',sdh_onset(Rs,Bs,b_lo=0.3,b_hi=10,r_full_scale=5000).summary())
    except Exception as e:
        print('ONSET ERROR',type(e).__name__,str(e))
