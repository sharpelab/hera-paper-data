import csv, numpy as np
rows = [r for r in csv.DictReader(open('pfit.csv')) if r['Te'] == '1.2']
f = lambda r, k: float(r[k])
print("rec      n     F_l   s_l(se)      s_h(se)      s_FL(se)     s_l+s_h  s_l/s_h  m_l/m_h  A0_l/A0_h")
bins = {}
for r in rows:
    if r['rec'] not in ('0825-r8','0822-r8','0821-r5','0822-r6','0824-r5','0825-r7','0824-r4'): continue
    ok = f(r,'sse_light') < 0.8 and f(r,'sse_heavy') < 0.8
    line = f"{r['rec']} {f(r,'n'):5.2f} {f(r,'F_light'):5.2f} {f(r,'s_light'):5.2f}({f(r,'sse_light'):.2f}) {f(r,'s_heavy'):6.2f}({f(r,'sse_heavy'):.2f}) {f(r,'s_FL'):6.2f}({f(r,'sse_FL'):.2f}) {f(r,'s_light')+f(r,'s_heavy'):7.2f} {f(r,'s_light')/f(r,'s_heavy'):7.2f} {f(r,'m_light')/f(r,'m_heavy'):7.2f} {f(r,'A0_light')/max(1e-9,f(r,'A0_heavy')):7.2f}"
    if r['rec'] in ('0825-r8', '0822-r8'):
        if int(r['col']) % 4 == 0: print(line + ('' if ok else '  *'))
        b = (r['rec'], round(f(r,'n')*2)/2)
        if ok: bins.setdefault(b, []).append((f(r,'s_light'), f(r,'s_heavy'), f(r,'s_FL'), f(r,'A0_light')/f(r,'A0_heavy')))
    else: print(line + ('' if ok else '  *'))
print("\nbinned (good fits): rec, n-bin, N, med s_l, med s_h, med s_FL, med s_l/s_h, med A_l/A_h")
for b, L in sorted(bins.items()):
    a = np.array(L); print(b, len(L), *[round(float(np.median(a[:, k])), 2) for k in range(3)], round(float(np.median(a[:,0]/a[:,1])),2), round(float(np.median(a[:,3])),2))
