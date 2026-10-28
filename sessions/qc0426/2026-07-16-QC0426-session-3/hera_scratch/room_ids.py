import asyncio, sys
from pathlib import Path
from jupyter_nbmodel_client import NbModelClient, get_jupyter_notebook_websocket_url
from tools.nb_collab import _resolve_server

async def main(nb_path):
    p = Path(nb_path)
    server_url, token, root = _resolve_server(p)
    rel = p.resolve().relative_to(Path(root).resolve()).as_posix()
    ws = get_jupyter_notebook_websocket_url(server_url, rel, token)
    async with NbModelClient(ws, path=rel) as client:
        print(f"connected room cells={len(client)}")
        for idx in range(len(client)):
            c = client[idx]
            ctype = c.get("cell_type")
            src = c.get("source","")
            if isinstance(src, list): src="".join(src)
            first = next((l for l in src.splitlines() if l.strip()), "")
            print(f"{idx:2d} {ctype:8} id={c.get('id')} | {first[:50]}")

asyncio.run(main(sys.argv[1]))
