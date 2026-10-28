import sys
sys.path.insert(0, "/home/zack/sharpelab/measurement-env/hera/models/raman_stacking")
from raman_io import load_wip
import witio

for name in ("04_3LGr.wip", "05_3LGr-stack.wip"):
    path = f"/data/sharpelab/hera-data/raman-qc0426/{name}"
    print("#"*72); print("FILE:", name)
    p = witio.read(path)
    for d in p.data:
        try:
            arr = d.array(); shape = getattr(arr, "shape", None)
        except Exception as e:
            shape = f"(no array: {type(e).__name__})"
        print(f"  item: {d.caption!r:50s} shape={shape}")
    ds = load_wip(path)
    for d in ds:
        m = d["meta"] or {}
        keys = ["Excitation Wavelength [nm]", "Laser Power [mW]", "Power [mW]",
                "Integration Time [s]", "Start Date", "Start Time",
                "Points per Line", "Lines per Image", "Scan Width [µm]", "Scan Height [µm]"]
        print("-"*60)
        print("  spectral:", d["caption"], f"nx,ny=({d['nx']},{d['ny']})",
              "wn %.0f..%.0f" % (d["wn"].min(), d["wn"].max()))
        for k, v in sorted(m.items()):
            s = str(v)
            print(f"    {k} = {s[:120]}")
