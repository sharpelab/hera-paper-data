from scipy.signal import find_peaks
from hera.analysis import sdh_fft, luttinger_frequency
r = run(6); ch = {x.cid: x for x in resolve_channels(r.meta)}
B = r.col('magnet_field'); I = r.col('sr0_X')/ch['sr0'].gain
R = (r.col('sr1_X')/ch['sr1'].gain)/I
f, spec = sdh_fft(R[:,None], B, b_range=(1,10), nfft=4096, bg_degree=5, log=False)
y=spec[0]; pk,_=find_peaks(y); pk=[i for i in pk if 3<f[i]<40]
pk=sorted(pk,key=lambda i:-y[i])[:6]
print('data/6 FFT 1–10 T peaks:', ', '.join(f'{f[i]:.1f} T' for i in pk))
print(f"Geometry-anchored full-density F_L(3.2e12) = {luttinger_frequency(3.2e16):.1f} T")
plt.figure(figsize=(7,3.5)); plt.plot(f,y); plt.xlim(0,40); plt.xlabel('SdH frequency (T)'); plt.ylabel('FFT magnitude (arb.)')
for i in pk[:4]: plt.axvline(f[i],ls=':',alpha=.5); plt.text(f[i],y[i],f'{f[i]:.1f}',fontsize=8)
plt.title('data/6 signed Rxx FFT, B=1–10 T'); plt.tight_layout(); plt.show()
