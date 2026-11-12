import asyncio, sys
from pathlib import Path
from jupyter_nbmodel_client import NbModelClient, get_jupyter_notebook_websocket_url
from tools.nb_collab import _resolve_server

WANT = {"f4e429e6f405468dbf09c0e63504b07d":"MAGNET",
        "be03d02525164736b6f7e3469827b54e":"HEATER/TEMPS",
        "b5fce8e8b1d34a0e95d8dafcebd26745":"DC205",
        "ad4a04d542e04c7884da8c8928433b1a":"SAFETIES"}

def text_of(out):
    t=out.get("text","")
    if isinstance(t,list): t="".join(t)
    if not t and "data" in out:
        d=out["data"].get("text/plain","")
        t="".join(d) if isinstance(d,list) else d
    return t

async def main(nb_path):
    p=Path(nb_path); server_url,token,root=_resolve_server(p)
    rel=p.resolve().relative_to(Path(root).resolve()).as_posix()
    ws=get_jupyter_notebook_websocket_url(server_url,rel,token)
    async with NbModelClient(ws,path=rel) as client:
        for idx in range(len(client)):
            c=client[idx]
            if c.get("id") in WANT:
                print(f"\n===== {WANT[c['id']]} (cell {idx}) =====")
                outs=c.get("outputs",[]) or []
                if not outs: print("(no output)")
                for o in outs:
                    tx=text_of(o).strip()
                    if tx: print(tx[:600])
asyncio.run(main(sys.argv[1]))
