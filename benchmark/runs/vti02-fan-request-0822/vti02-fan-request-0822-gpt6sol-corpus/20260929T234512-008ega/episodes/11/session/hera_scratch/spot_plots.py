from hera.analysis import open_run, plot_raw, sdh_fft
import matplotlib.pyplot as plt
import numpy as np

for i in (6, 7):
    r = open_run(f'data/{i}')
    plot_raw(r).savefig(f'hera_scratch/spot_{i}_raw.png', dpi=130)
    plt.close('all')
    B = r.col('magnet_field')
    I = r.col('sr0_X') / -1e6
    R = r.col('sr1_X') / I
    print(i,'current nA',np.nanquantile(I*1e9,[0,.01,.5,.99,1]),'R ohm',np.nanquantile(R,[0,.01,.5,.99,1]))
    fig, axs=plt.subplots(2,1,figsize=(10,7))
    axs[0].plot(B,R,lw=.6)
    axs[0].set(xlabel='B (T)',ylabel='Rxx (ohm)',title=f'run {i}: raw Rxx')
    for lo in (.7,1.,1.5,2.,2.5,3.):
        if lo>=B.max(): continue
        f,S=sdh_fft(R[:,None],B,b_range=(lo,10),nfft=1024,bg_degree=5,log=False)
        axs[1].plot(f,S[0]/np.max(S[0]),label=f'{lo}-10T')
    axs[1].set(xlim=(0,45),ylim=(0,1.1),xlabel='F (T)',ylabel='norm FFT')
    axs[1].legend(ncol=3)
    fig.tight_layout();fig.savefig(f'hera_scratch/spot_{i}_fft.png',dpi=130)
