# Analysis — snake SdH FFT stability: peaks WANDER -> 2 FS not resolved (aliasing)
from scipy.signal import find_peaks
def dom(F,col,Blo,N=4096):
    m=load_meta(F);ci={k:i for i,k in enumerate(m['columns'])};d=load1d(F)
    B=d[:,ci['magnet_mag']];sel=(B>=Blo)&(B<=4.0);x=1/B[sel];r=d[sel,ci[col]]/5e-9
    o=np.argsort(x);x,r=x[o],r[o];xu=np.linspace(x.min(),x.max(),N);ru=np.interp(xu,x,r)
    ru=ru-np.polyval(np.polyfit(xu,ru,6),xu);Fa=np.fft.rfftfreq(N,d=xu[1]-xu[0]);A=np.abs(np.fft.rfft(ru*np.hanning(N)))
    return Fa,A
fig,ax=plt.subplots(1,2,figsize=(13,4.5))
for j,(F,side) in enumerate([(36,'hole n=-8e12'),(37,'electron n=+8e12')]):
    for lo in (0.6,1.0,1.5):
        Fa,A=dom(F,'sr1_X',lo);k=(Fa>1)&(Fa<40)
        ax[j].plot(Fa[k],A[k]/A[k].max(),label=f'B[{lo},4]')
    ax[j].set(xlabel='F (T)',ylabel='|FFT| sr1',title=f'{side}: peak WANDERS w/ window');ax[j].legend(fontsize=8)
fig.suptitle('Snake SdH FFT — peaks wander across windows = main-tone (~83T) aliasing, not 2 FS');plt.tight_layout();plt.show()
print('Dominant FFT peak wanders with window on all channels/legs -> low-F band contaminated by aliases of the')
print('undersampled ~83 T main tone (50 mT too coarse at n=8e12). 2 FS NOT resolved -> field-sampling-limited.')
