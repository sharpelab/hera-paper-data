"""Two admissibility checks on the ana notebook (parse only):
 (1) does the staged transport-call.md reproduce cell 35 verbatim?
 (2) does any cell mention Raman / ABC-prior / spatial-geometry keywords?
Writes artifacts/nb_checks.txt"""
import json, pathlib, re, difflib

D = pathlib.Path("/data/sharpelab/hera-data/raman-vti-02-20260825-fusion")
nb = json.loads((D/"inputs/20260824_ana.ipynb").read_text())
call = (D/"inputs/transport-call.md").read_text()
out = []

cell35 = "".join(nb["cells"][35]["source"]).strip()
# the staged file's verbatim section starts at the '# THE CALL' header
i = call.find("# THE CALL")
staged = call[i:].strip()
out.append(f"cell35 chars={len(cell35)}  staged-section chars={len(staged)}  identical={cell35==staged}")
if cell35 != staged:
    for line in difflib.unified_diff(cell35.splitlines(), staged.splitlines(), "cell35", "staged", n=1, lineterm=""):
        out.append(line)

KEY = ["raman", "rhombohedr", "ABC-", "ABCA prior", "pre-fab", "prefab", "flake", "parent",
       "micron", "µm", "um)", "GDS", "gds", "optical", "image", "contact", "pad", "Hall bar",
       "hall bar", "L/W", "aspect", "geometry", "domain", "mosaic", "redact"]
out.append("\n--- keyword hits (cell: keyword: line) ---")
for ci, c in enumerate(nb["cells"]):
    src = "".join(c.get("source", []))
    for ln in src.splitlines():
        for k in KEY:
            if k in ln:
                out.append(f"[{ci:3d}] {k!r}: {ln.strip()[:160]}")
                break
txt = "\n".join(out)
(D/"artifacts/nb_checks.txt").write_text(txt+"\n")
print(txt)
