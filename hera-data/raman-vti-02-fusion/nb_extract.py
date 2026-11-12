"""Extract the vti-02 ana notebook (inputs/20260821_ana.ipynb) without executing it:
full cell sources, stream outputs, and embedded PNGs -> nb-extract/.
Run: uv run --no-project python nb_extract.py
"""
import base64, json
from pathlib import Path

here = Path(__file__).resolve().parent
nb = json.load(open(here / "inputs" / "20260821_ana.ipynb"))
out = here / "nb-extract"
out.mkdir(exist_ok=True)
lines = []
for i, c in enumerate(nb["cells"]):
    src = "".join(c["source"])
    lines.append(f"\n{'='*20} cell {i} [{c['cell_type']}] meta={json.dumps(c.get('metadata', {}))} {'='*20}\n{src}\n")
    for j, o in enumerate(c.get("outputs", [])):
        if o.get("output_type") == "stream":
            lines.append(f"--- cell {i} stream output {j} ---\n{''.join(o.get('text', ''))}\n")
        elif "data" in o:
            d = o["data"]
            if "text/plain" in d:
                lines.append(f"--- cell {i} data output {j} text/plain ---\n{''.join(d['text/plain'])}\n")
            if "image/png" in d:
                p = out / f"cell{i:02d}_out{j}.png"
                p.write_bytes(base64.b64decode(d["image/png"]))
                lines.append(f"--- cell {i} data output {j} image/png -> {p.name}\n")
(out / "ana_notebook_dump.md").write_text("".join(lines))
print("wrote", out / "ana_notebook_dump.md", "and", len(list(out.glob("*.png"))), "png files")
