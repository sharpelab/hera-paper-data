#!/usr/bin/env python3
"""vti-02 fusion artifact: verify the locked transport call against the ana
notebook, and extract the notebook's per-run read cells.

Checks:
 1. transport-call.md's quoted FINAL CALL section is identical (modulo
    trailing whitespace per line) to the final cell of 20260823_ana.ipynb.
 2. Dumps all markdown "Read (run ...)" cells + final cell to
    intermediates/notebook_reads.md for citation.

Run from the fusion dir: python3 artifacts/verify_transport_call.py
"""
import json, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
inputs = root / "inputs"

nb = json.loads((inputs / "20260823_ana.ipynb").read_text())
final_cell = "".join(nb["cells"][-1]["source"])
assert final_cell.startswith("# FINAL CALL"), "last cell is not the final call"

tc = (inputs / "transport-call.md").read_text()
quoted = tc.split("\n---\n", 1)[1].lstrip("\n")

norm = lambda s: "\n".join(line.rstrip() for line in s.strip().splitlines())
match = norm(quoted) == norm(final_cell)
print(f"transport-call.md quoted section == notebook final cell: {match}")
if not match:
    import difflib
    sys.stdout.writelines(difflib.unified_diff(
        norm(quoted).splitlines(True), norm(final_cell).splitlines(True),
        "transport-call.md", "notebook final cell"))

out = root / "intermediates" / "notebook_reads.md"
parts = ["# vti-02 ana notebook — extracted read cells (verbatim)\n"]
for i, c in enumerate(nb["cells"]):
    src = "".join(c["source"])
    if c["cell_type"] == "markdown" and (src.startswith("**Read") or src.startswith("# FINAL CALL")):
        parts.append(f"\n---\n<!-- notebook cell {i} -->\n\n{src}\n")
out.write_text("".join(parts))
print(f"wrote {out} ({len(parts)-1} cells)")
sys.exit(0 if match else 1)
