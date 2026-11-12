"""Print the source (and optionally text outputs) of selected notebook cells. Parse only."""
import json, sys, pathlib
NB = pathlib.Path("/data/sharpelab/hera-data/raman-vti-02-20260825-fusion/inputs/20260824_ana.ipynb")
nb = json.loads(NB.read_text())
want_out = "--out" in sys.argv
idxs = [int(a) for a in sys.argv[1:] if not a.startswith("--")]
for i in idxs:
    c = nb["cells"][i]
    print(f"\n===== CELL {i} ({c['cell_type']}, exec={c.get('execution_count')}) =====")
    print("".join(c.get("source", [])))
    if want_out:
        for o in c.get("outputs", []):
            if o.get("output_type") == "stream":
                print("--- stream ---"); print("".join(o.get("text", [])))
            elif o.get("output_type") in ("execute_result", "display_data"):
                d = o.get("data", {})
                if "text/plain" in d:
                    print("--- result ---"); print("".join(d["text/plain"]))
                for k in d:
                    if k.startswith("image"):
                        print(f"--- [{k}, {len(d[k])} B] ---")
            elif o.get("output_type") == "error":
                print("--- error ---"); print("\n".join(o.get("traceback", []))[:2000])
