"""Index the ana notebook: cell number, type, exec count, first lines, size.
Parse only - never execute. Writes artifacts/nb_index.txt."""
import json, sys, pathlib

NB = pathlib.Path("/data/sharpelab/hera-data/raman-vti-02-20260825-fusion/inputs/20260824_ana.ipynb")
OUT = pathlib.Path("/data/sharpelab/hera-data/raman-vti-02-20260825-fusion/artifacts/nb_index.txt")

nb = json.loads(NB.read_text())
lines = []
lines.append(f"nbformat {nb.get('nbformat')}.{nb.get('nbformat_minor')}  ncells={len(nb['cells'])}")
lines.append(f"metadata keys: {sorted(nb.get('metadata', {}).keys())}")
for i, c in enumerate(nb["cells"]):
    src = "".join(c.get("source", []))
    head = " | ".join(src.splitlines()[:3])[:180]
    nout = len(c.get("outputs", []))
    obytes = len(json.dumps(c.get("outputs", [])))
    lines.append(f"[{i:3d}] {c['cell_type']:8s} exec={c.get('execution_count')} src={len(src):6d}B out={nout} ({obytes}B) :: {head}")
OUT.write_text("\n".join(lines) + "\n")
print("\n".join(lines))
