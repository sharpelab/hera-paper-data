# Gate C read — leakage profile per leg, offset-corrected.
# Flat instrument offsets (parked-gate reads): BG channel ~ -100 pA, TG ~ +20 pA (nplci=10).
for rid, vcol, icol, leg in [
        (0, 'k_2400_tg_volt', 'k_2400_tg_curr', 'TG +'),
        (1, 'k_2400_tg_volt', 'k_2400_tg_curr', 'TG -'),
        (2, 'k_2400_bg_volt', 'k_2400_bg_curr', 'BG +'),
        (3, 'k_2400_bg_volt', 'k_2400_bg_curr', 'BG -')]:
    r = run(rid)
    v, i = r.col_at(1), r.col(icol)  # swept axis via col_at (fp duplicate)
    i0 = np.median(i[np.abs(v) < 0.5])           # offset near 0 V
    exc = i - i0
    hot = np.abs(exc) > 1e-10                    # >100 pA above offset
    v_end = v[np.abs(v).argmax()]
    leak_end = exc[np.abs(v).argmax()]
    if hot.any():
        v_on = v[hot][np.abs(v[hot]).argmin()]   # smallest |V| exceeding 100 pA
        note = f'|I-I0| > 100 pA beyond {v_on:+.2f} V'
    else:
        note = 'clean (<100 pA above offset everywhere)'
    print(f'run {rid} ({leg}): offset {i0*1e12:+5.0f} pA | at {v_end:+.1f} V leak {leak_end*1e12:+6.0f} pA | {note}')
