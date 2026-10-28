"""Model ABAB cyclotron masses (u_D=0) vs signed n (1e12 cm^-2): light, heavy, and the F_L sum-orbit mass m_l+m_h."""
import sys, json, numpy as np, importlib.util
spec = importlib.util.spec_from_file_location('fb', '/home/zack/sharpelab/measurement-env/hera/models/tetralayer_fs_count/fs_count_b0.py')
fb = importlib.util.module_from_spec(spec); sys.dont_write_bytecode = True; spec.loader.exec_module(fb)
out = {}
for n in np.round(np.r_[np.arange(-3.2, -0.29, 0.1), np.arange(0.3, 3.31, 0.1)], 2):
    ms = fb.abab_mstar(n * 1e16)
    ms = sorted(ms)   # by F: light first
    if len(ms) >= 2:
        out[f"{n:.1f}"] = dict(F_l=ms[0][0], m_l=ms[0][1], F_h=ms[-1][0], m_h=ms[-1][1], all=[list(map(float, x)) for x in ms])
json.dump(out, open('masses.json', 'w'), indent=1)
for k, v in out.items():
    if abs(float(k)) >= 0.9 and round(float(k)*10) % 2 == 0:
        print(k, f"F_l {v['F_l']:.2f} m_l {v['m_l']:.4f}  F_h {v['F_h']:.2f} m_h {v['m_h']:.4f}  ratio {v['m_l']/v['m_h']:.3f}  norb {len(v['all'])}")
