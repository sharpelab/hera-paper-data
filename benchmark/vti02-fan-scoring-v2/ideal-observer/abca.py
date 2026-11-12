"""ABCA single-pocket table (F_total, m*) on the electron side from hera/models/tetralayer_fs_count (read-only import).
-> abca_table.json: n (1e12 cm^-2, actual frame), F (T), m* (m_e). Built once; interpolated at call time."""
import sys, json, time, importlib.util
from pathlib import Path
import numpy as np
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OUT = HERE / 'abca_table.json'
FS = Path('/home/zack/sharpelab/measurement-env/hera/models/tetralayer_fs_count/synth_fan.py')

if __name__ == '__main__':
    spec = importlib.util.spec_from_file_location('synth_fan', FS)
    sf = importlib.util.module_from_spec(spec); spec.loader.exec_module(sf)
    t0 = time.time()
    f = sf.orbits_for('ABCA', +1)
    print('table built', round(time.time() - t0, 1), 's')
    ns = np.round(np.arange(0.25, 3.651, 0.05), 3)
    rows = []
    for n in ns:
        (F, m, lab), = f(float(n))
        rows.append((float(n), float(F), float(m)))
        print(f'n {n:.2f}  F {F:7.3f}  F_L {10.3392*n:7.3f}  m* {m:.4f}')
    json.dump(dict(rows=rows, source=str(FS) + " orbits_for('ABCA', +1), ud = 0"), open(OUT, 'w'), indent=1)
