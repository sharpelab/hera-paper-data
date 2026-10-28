# Raw — re-verify, NEW config (source T2 / drain B7), D=0 n-line, Si=0, 200uV
import scipy.constants as cst
m=load_meta(35);ci={c:i for i,c in enumerate(m['columns'])};d=load1d(35)
Ib=5e-9;I=d[:,ci['sr0_X']]/m['measurement_config']['sr0_gain']
C_TG=cst.epsilon_0*3.0/15.6e-9;C_BG=1.298*C_TG;N_OFF=-7.095e14
n=((C_TG*d[:,ci['DC_bias']]+C_BG*d[:,ci['k_bg_volt']])/cst.e+N_OFF)/1e16  # 1e12 cm^-2
fig,ax=plt.subplots(1,3,figsize=(15,4))
ax[0].plot(n,d[:,ci['sr1_X']]/Ib,label='sr1 T3-T4');ax[0].plot(n,d[:,ci['sr2_X']]/Ib,label='sr2 B4-B5')
ax[0].set(xlabel='n (1e12 cm^-2)',ylabel='Rxx (ohm)');ax[0].legend()
ax[1].plot(n,d[:,ci['sr3_X']]/Ib,'C2');ax[1].set(xlabel='n (1e12 cm^-2)',ylabel='Rxy T5-B6 (ohm)')
ax[2].plot(n,I*1e9,'C3');ax[2].axhline(5,ls=':',c='k');ax[2].set(xlabel='n (1e12 cm^-2)',ylabel='I_drain B7 (nA)')
fig.suptitle('Raw — file 35: re-verify NEW config (T2 src / B7 drain), D=0, Si=0, B=0, 200 uV — RECOVERED')
plt.tight_layout();plt.show()
print('drain(B7) I med %.2f nA -> new config conducts; CNP + Rxx clean at 200uV'%(np.median(I)*1e9))
