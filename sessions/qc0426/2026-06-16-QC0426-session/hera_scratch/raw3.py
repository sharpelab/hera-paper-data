m=load_meta(3);ci={c:i for i,c in enumerate(m['columns'])};d=load1d(3)
nf=36;nr=d.shape[0]//nf;g=d[:nr*nf].reshape(nr,nf,-1);B=g[:,0,ci['magnet_mag']];Ib=5e-9
absn=np.abs(np.linspace(-1.4e12,-5.0e12,nf))/1e12
fig,ax=plt.subplots(1,3,figsize=(16,4.5))
for k,(nm,c,cm) in enumerate([('sr1 Rxx','sr1_X','viridis'),('sr3 Rxy','sr3_X','seismic')]):
    R=g[:,:,ci[c]]/Ib;vm=np.percentile(np.abs(R),98)
    im=ax[k].pcolormesh(absn,B,R,shading='auto',cmap=cm,vmin=(-vm if k else 0),vmax=vm)
    fig.colorbar(im,ax=ax[k],label='ohm');ax[k].set(xlabel='|n| (1e12)',ylabel='B (T)',title=nm)
I=g[:,:,ci['sr0_X']]/m['measurement_config']['sr0_gain'];im=ax[2].pcolormesh(absn,B,I*1e9,shading='auto',cmap='inferno')
fig.colorbar(im,ax=ax[2],label='I (nA)');ax[2].set(xlabel='|n| (1e12)',ylabel='B (T)',title='drain I')
fig.suptitle('Raw — file 3: Landau fan (D=0 hole, sens 2mV)');plt.tight_layout();plt.show()
