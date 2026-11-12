from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft
from scipy.signal import find_peaks
file_path = Path.cwd() / "data"
assert (file_path / "6" / "metadata.json").is_file(), str(file_path)
spot_records=[]
for rid in (6,7):
    r=open_run(Path(file_path)/str(rid))
    channels=resolve_channels(r.meta)
    ci=current_channel(channels); cv=next(c for c in channels if c.cid=='sr1')
    B=r.col('magnet_field'); I=r.col(ci.col)/ci.gain; V=r.col(cv.col)/cv.gain
    R=V/I; order=np.argsort(B)
    fig, ax=plt.subplots(2,3,figsize=(13,7))
    for a,y,label in zip(ax.flat,[V*1e6,I*1e9,R,r.col('sr1_P'),r.col('k_2400_tg_curr')*1e12,r.col('k_2400_bg_curr')*1e12],['raw Vxx (uV)','drain I (nA)','signed V/I (ohm)','sr1 phase (deg)','TG current (pA)','BG current (pA)']):
        a.plot(B,y,lw=0.8); a.set(xlabel='B setpoint (T)',ylabel=label)
    fig.suptitle(f'data/{rid}: raw signals and measured-current resistance');fig.tight_layout();plt.show()
    print(f'data/{rid}: {r.rows} points, {(r.meta["end_time"]-r.meta["start_time"])/60:.1f} min; R {R.min():.2f}..{R.max():.2f} ohm; I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA; T {r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K; voltage <= {np.max(np.abs(V))/50e-6:.3f} of 50 uV FS')
    print('max abs gate current (pA):',*[f'{c}: {np.max(np.abs(r.col(c)))*1e12:.1f}' for c in ['k_2400_tg_curr','k_2400_bg_curr']])
    spot_records.append((rid,B[order],R[order]))
# Analysis follows all raw plots. Signed linear-R FFT avoids log-floor artifacts at negative R.
fig,ax=plt.subplots(1,2,figsize=(12,4))
for a,(rid,B,R) in zip(ax,spot_records):
    for lo,hi in [(1.5,10),(1.5,5),(2,10)]:
        f,spec=sdh_fft(R[:,None],B,b_range=(lo,hi),bg_degree=3,log=False,nfft=4096)
        a.plot(f,spec[0]/max(spec[0]),label=f'{lo}-{hi} T')
        peaks,_=find_peaks(spec[0]); peaks=sorted([p for p in peaks if 3<f[p]<70],key=lambda p:-spec[0,p])[:4]
        print(f'data/{rid} [{lo},{hi}] T: peaks {[round(float(f[p]),2) for p in peaks]} T; independent resolution {1/(1/lo-1/hi):.2f} T')
    a.set(xlim=(0,60),xlabel='F (T)',ylabel='normalized FFT amplitude',title=f'data/{rid}, signed R, cubic B background');a.legend()
fig.tight_layout();plt.show()
