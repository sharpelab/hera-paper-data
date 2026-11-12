#!/usr/bin/env python
"""Parse (never execute) inputs/20260821_ana.ipynb for the vti-02 fusion run.

Produces artifacts/ana_inventory.md:
  - cell inventory (index, type, first line, exec_count, metadata stamps)
  - verbatim text of the call cell (index 29) for byte-comparison against
    inputs/transport-call.md
  - independence grep: any occurrence of raman / rhombohedral / ABC-lean
    vocabulary anywhere in the notebook (sources + outputs)
  - geometry grep: contact / pad / µm / gds / image mentions usable as
    frame bridges for registration
"""
import json, re, sys, pathlib

RUN = pathlib.Path("/data/sharpelab/hera-data/raman-vti-02-20260821-fusion")
nb = json.loads((RUN / "inputs" / "20260821_ana.ipynb").read_text())
cells = nb["cells"]

out = []
out.append(f"# ana notebook inventory — {len(cells)} cells\n")
out.append("| idx | type | exec | appended_at | first line |")
out.append("|---|---|---|---|---|")
for i, c in enumerate(cells):
    src = "".join(c.get("source", []))
    first = src.strip().splitlines()[0][:90] if src.strip() else "(empty)"
    first = first.replace("|", "\\|")
    meta = c.get("metadata", {})
    stamp = meta.get("appended_at", "")
    out.append(f"| {i} | {c['cell_type']} | {c.get('execution_count','')} | {stamp} | {first} |")

# --- call cell (29) verbatim ---
call_src = "".join(cells[29]["source"]) if len(cells) > 29 else "(no cell 29)"
out.append("\n## Cell 29 (claimed call cell) — verbatim source\n")
out.append("```")
out.append(call_src)
out.append("```")

# byte-compare against transport-call.md section (after the '---' separator)
tc = (RUN / "inputs" / "transport-call.md").read_text()
sec = tc.split("\n---\n", 1)[1].lstrip("\n") if "\n---\n" in tc else ""
match = call_src.strip() == sec.strip()
out.append(f"\n**Byte-comparison vs transport-call.md body (whitespace-stripped): "
           f"{'MATCH' if match else 'MISMATCH'}**")
if not match:
    out.append(f"- call cell len {len(call_src.strip())}, contract body len {len(sec.strip())}")

# --- independence grep ---
pat_ind = re.compile(r"raman|rhombo|\bABC\b|ABCA|pre[- ]?fab|flake.?map|stacking prior|expect.*ABC",
                     re.IGNORECASE)
# --- geometry grep ---
pat_geo = re.compile(r"\bgds\b|optical|image|contact map|\bpad\b|micron|\bum\b|µm|geometry|footprint",
                     re.IGNORECASE)

def scan(pat, title):
    hits = []
    for i, c in enumerate(cells):
        texts = ["".join(c.get("source", []))]
        for o in c.get("outputs", []) or []:
            if "text" in o:
                texts.append("".join(o["text"]))
            for k, v in (o.get("data") or {}).items():
                if k.startswith("text/"):
                    texts.append("".join(v) if isinstance(v, list) else str(v))
        for t in texts:
            for line in t.splitlines():
                if pat.search(line):
                    hits.append((i, line.strip()[:160]))
    out.append(f"\n## {title} — {len(hits)} line hits\n")
    for i, line in hits:
        out.append(f"- cell {i}: `{line}`")
    return hits

ind_hits = scan(pat_ind, "Independence grep (raman/rhombo/ABC/prior vocabulary)")
geo_hits = scan(pat_geo, "Geometry grep (gds/optical/pad/µm frame-bridge vocabulary)")

(RUN / "artifacts" / "ana_inventory.md").write_text("\n".join(out) + "\n")
print(f"cells={len(cells)} call29_match={match} "
      f"independence_hits={len(ind_hits)} geometry_hits={len(geo_hits)}")
print("wrote artifacts/ana_inventory.md")
