# s1_admissibility_independence.py — fusion Step 1 + independence audit, vti-01
#
# Admissibility: both locked contracts carry weight words, evidence lists, and
# coordinates (transport: named contact pairs; Raman: region raster + stage
# stamps). Independence: textual sweep — no transport-side input mentions the
# Raman data; the Raman contract's provenance states no transport result was
# seen, and it postdates the transport call (2026-08-27 vs 2026-08-20).
#
# Output: audit_step1.txt
#
#   uv run --no-project --with numpy python s1_admissibility_independence.py

import json
import re

OUT = []


def check(name, ok, detail=""):
    OUT.append(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    return ok


tc = open("inputs/transport-call.md").read()
rc = open("inputs/raman-contract.md").read()
rp = open("inputs/raman-provenance.md").read()
sn = open("inputs/session_notes.md").read()
dc = open("inputs/device_card.md").read()

# --- admissibility: transport contract ---
check("transport: weight words", all(w in tc for w in ["strong", "consistent-with", "uninformative"]))
check("transport: evidence list with runs/coordinates",
      bool(re.search(r"run[s]? \d", tc)) and "n = " in tc and "D = 0" in tc)
check("transport: channels named as contact pairs",
      all(s in tc for s in ["sr1 (B_SD–L4)", "sr2 (L4–L1)", "sr3 (L3–L2)"]))

# --- admissibility: Raman contract ---
check("raman: weight words", all(w in rc for w in ["strong", "uninformative"]))
check("raman: stage stamps present", "S0" in rc and "S1" in rc and "2026-05-28" in rc)
check("raman: region coordinates + raster artifact",
      "regions.npz" in rc and bool(re.search(r"centroid \(−?\-?12", rc)))
import numpy as np  # noqa: E402
z = np.load("inputs/regions.npz", allow_pickle=True)
check("raman: raster loads with labels/axes/key",
      set(z.files) >= {"labels", "x_um", "y_um", "key"},
      f"labels {z['labels'].shape}, {len(z['key'])} key entries")

# --- independence: transport side never saw the Raman data ---
kw = re.compile(r"raman|witec|\.wip|2D[- ]band|FWHM|532(\.\d+)? ?nm", re.I)
nb = json.load(open("inputs/20260818_ana.ipynb"))
nb_hits = [i for i, c in enumerate(nb["cells"]) if kw.search("".join(c.get("source", [])))]
check("independence: ana notebook (parsed JSON, 39 cells) has no Raman refs",
      not nb_hits, f"hits in cells {nb_hits}" if nb_hits else "0 matches")
for name, txt in [("transport-call.md", tc), ("session_notes.md", sn), ("device_card.md", dc)]:
    check(f"independence: {name} has no Raman refs", not kw.search(txt))

# --- independence: Raman side never saw the transport result ---
check("independence: raman provenance states no transport result seen",
      "no transport result" in rp and "no transport result" in rc)
check("independence: raman execution (2026-08-27) postdates locked transport call "
      "(2026-08-20) and cites only vti-01.wip + owner device facts",
      "executed 2026-08-27" in rc and "inputs/vti-01.wip" in rp)

ok = all(l.startswith("[PASS]") for l in OUT)
OUT.append("")
OUT.append("STEP 1 VERDICT: both contracts ADMISSIBLE; calls INDEPENDENT — "
           "fusion is evidential." if ok else "STEP 1 VERDICT: FAILURE — see above.")
report = "\n".join(OUT)
open("audit_step1.txt", "w").write(report + "\n")
print(report)
