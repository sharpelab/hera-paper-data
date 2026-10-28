"""Corpus-model ABAB electron-side table: F_light, F_heavy, m_light, m_heavy vs n (1e12 cm^-2)."""
import sys, json, importlib.util, numpy as np
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('sf', '/home/zack/sharpelab/measurement-env/hera/models/tetralayer_fs_count/synth_fan.py')
sf = importlib.util.module_from_spec(spec); spec.loader.exec_module(sf)
f = sf.orbits_for('ABAB', +1)
rows = []
for n in np.round(np.arange(0.2, 8.501, 0.05), 3):
    os_ = f(n)
    d = {lab: (F, m) for F, m, lab in os_}
    rows.append([float(n), d.get('light', (np.nan,))[0], d['heavy'][0], d.get('light', (0, np.nan))[1], d['heavy'][1], len(os_)])
    if len(os_) != 2: print(n, os_)
json.dump(dict(cols=['n', 'F_light', 'F_heavy', 'm_light', 'm_heavy', 'n_orbits'], rows=rows), open('../corpus_abab_table.json', 'w'), indent=0)
for r in rows[::10]: print(np.round(r, 4))
