import sys, pickle, time
import numpy as np
import io_core as C
D = {d['label']: d for d in pickle.load(open('designs.pkl', 'rb'))}
labs = sys.argv[1:] or ['live 0822-r8', 'live 0825-r8', 'live 0821-r8', 'live 0824-r4']
for lab in labs:
    d = dict(D[lab]); sel = (d['n'] >= C.N_LO) & (d['n'] <= C.N_HI); n = d['n'][sel]; d['nc'] = n.size
    t, Brc = C.timing(d); w = C.weights(d)
    RB = C.clean_map(Brc, n, 'B', {}); RR = C.clean_map(Brc, n, 'R', {})
    I = d['I']; muB, muR = C.blur(RB * I, w), C.blur(RR * I, w)
    var = C.noise_var(d, Brc, RB, n)
    tones = C.hb_tones(n, {})
    for M, Qe, cl in [(4, 2, False), (4, 2, True), (6, 2, True), (4, 1, True), (4, 3, True)]:
        kl, pat, cr = C.tone_kl(muB, muR, var, Brc, n, tones, w, M=M, Qe=Qe, clutter=cl)
        capd = {sa: C.capped_kl(pat, kl, sa) for sa in (0.5, 1.0)}
        print(f"{lab:14s} M{M} Q{Qe} clutter {cl!s:5s}: KL {kl.sum():9.1f} med/col {np.median(kl):7.2f} clutter/noise med {np.median(cr):8.1f} | cap sa0.5 {capd[0.5][0]:7.2f} sa1 {capd[1.0][0]:6.2f} n_eff {capd[1.0][1]:5.1f}")
