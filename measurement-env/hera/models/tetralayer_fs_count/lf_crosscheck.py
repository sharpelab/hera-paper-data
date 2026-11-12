#!/usr/bin/env python3
"""
Cross-check our TSV-first FFT pipeline against the PAPER'S OWN analysis code
(`utils/Lf_analysis.py` from the Fermiology-and-the-cCSC repo) on the same raw
sweep (data/1840, the fig3 fan at D = 1 V/nm). The paper's SDR data deposit is
an empty placeholder, so there are no published processed outputs to compare
to — running the repo's code on the mirror sweeps is the only way to get its
n_SdH(n) for a head-to-head.

The repo loads from a hardcoded `../data/raw_sweeps`; we point its module-level
`file_path` at a read-only symlink farm under $HERA_DATA (never writing into the
paper repo or the mirror). Uses the repo's `get_fft` — the correct 1/B FFT whose
axis is normalized to f_nu = n_SdH/n (the quantity the paper's fig3 plots) — and
compares in n_SdH space (n_SdH = f_nu * n) against our absolute-frequency read
(n_SdH = (e/h) * f). (`get_fft_B` is an FFT in B, not 1/B, so it is NOT the SdH
transform and is not used here.)

Run (needs the repo's deps):
  cd hera/models/tetralayer_fs_count
  uv run --no-project --with numpy --with scipy --with matplotlib \
      --with lmfit --with cycler python3 lf_crosscheck.py
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path("/home/zack/sharpelab/Fermiology-and-the-cCSC")
FARM = Path("/data/sharpelab/hera-data/tetralayer-rpl19-validation/raw_sweeps")
OUT = Path("/data/sharpelab/hera-data/tetralayer-rpl19-validation")
_HERE = Path(__file__).resolve().parent

sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / "utils"))


def _load_local(name):
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lf_nsdh(fileid, contact, blims=(0.7, 5.0), cutoff=2.0, order=2, padding=4,
            fnu_search=(0.3, 2.5)):
    """Run the repo's Lf_analysis.get_fft (the 1/B FFT, axis = f_nu = n_SdH/n)
    and return (density, n_SdH_peak) per column — n_SdH = f_nu_peak * n, with the
    peak taken in the fnu_search band."""
    import Lf_analysis as LF
    LF.file_path = str(FARM)                       # redirect the hardcoded path
    from utils import detrend_butterworth
    la = LF.Lf_analysis(fileid, contact)
    ffts, freqs = la.get_fft(detrend_butterworth,
                             {"cutoff": cutoff, "order": order}, padding, blims)
    dens = np.asarray(la.density, dtype=float)
    nsdh = np.full(dens.size, np.nan)
    for i in range(dens.size):
        fnu = freqs[:, i]
        a = np.abs(ffts[:, i])
        band = (fnu >= fnu_search[0]) & (fnu <= fnu_search[1])
        if band.any():
            fnu_pk = fnu[band][np.argmax(a[band])]
            nsdh[i] = fnu_pk * abs(dens[i])
    return dens, nsdh


def main():
    re_ = _load_local("real_eval")
    sf = re_.sf
    rl = re_.rl
    NSDH = re_.NSDH_PER_T

    result = {"fileid": 1840, "blims": [0.7, 5.0], "columns": []}
    for contact in (2, 3):
        _dens, nsdh_lf = lf_nsdh(1840, contact)
        fan = rl.load_fan(1840, contact=contact)
        B, Rxx, n = fan["B"], fan["Rxx"], fan["n"]
        rows = []
        for j in range(n.size):
            nn = float(n[j])
            if nn < 0.6:            # compare on the CQM branch (single tone)
                continue
            FLn = sf.F_L(abs(nn))
            col = re_.analyze_column(B, Rxx[:, j], FLn, 0.7, 5.0)
            ours = col["peaks"][0][0] if col["peaks"] else np.nan
            ns_ours = NSDH * ours if np.isfinite(ours) else np.nan
            ns_lf = float(nsdh_lf[j]) if j < nsdh_lf.size else np.nan
            rows.append(dict(n=round(nn, 3),
                             nsdh_ours=round(ns_ours, 3) if np.isfinite(ns_ours) else None,
                             nsdh_lf=round(ns_lf, 3) if np.isfinite(ns_lf) else None,
                             fnu_ours=round(ns_ours / nn, 3) if np.isfinite(ns_ours) else None,
                             fnu_lf=round(ns_lf / nn, 3) if np.isfinite(ns_lf) else None,
                             rel_diff=(round(abs(ns_ours - ns_lf) / ns_lf, 3)
                                       if np.isfinite(ns_ours) and np.isfinite(ns_lf) and ns_lf > 0 else None)))
        result["columns"].append({"contact": contact, "rows": rows})

    (OUT / "lf_crosscheck.json").write_text(json.dumps(result, indent=2))

    print("Lf_analysis (paper code) vs ours — data/1840 CQM branch (n>=0.6), n_SdH space")
    for cc in result["columns"]:
        rds = [r for r in cc["rows"] if r["rel_diff"] is not None]
        med = float(np.median([r["rel_diff"] for r in rds])) if rds else float("nan")
        print(f"\n contact {cc['contact']}: {len(rds)} comparable cols, "
              f"median |Δn_SdH|/n_SdH = {med*100:.1f}%")
        for r in cc["rows"][:: max(1, len(cc["rows"]) // 6)][:6]:
            print(f"   n={r['n']:+.2f}: n_SdH ours {r['nsdh_ours']} (f_ν {r['fnu_ours']})  "
                  f"Lf {r['nsdh_lf']} (f_ν {r['fnu_lf']})  rel={r['rel_diff']}")


if __name__ == "__main__":
    main()
