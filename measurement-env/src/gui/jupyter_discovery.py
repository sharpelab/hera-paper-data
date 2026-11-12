"""Find a running JupyterLab server by its notebook root dir.

Toolkit-neutral (no tkinter/Qt): used as the ManagedProcess ready_check by
both the tkinter toploader Jupyter panel and the Qt shared Jupyter panel.
"""

import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from gui.utils import _log


def find_server_url(notebook_dir_str):
    """Return the /lab?token= URL of a running Jupyter server rooted at
    *notebook_dir_str*, or None if there isn't one."""
    try:
        from jupyter_core.paths import jupyter_runtime_dir

        runtime_dir = Path(jupyter_runtime_dir())
    except ImportError:
        _log("jupyter", "find_server_url: jupyter_core not available")
        return None

    _log("jupyter", f"find_server_url: scanning {runtime_dir}")
    for server_file in runtime_dir.glob("jpserver-*.json"):
        try:
            info = json.loads(server_file.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        root_dir = info.get("root_dir") or info.get("notebook_dir", "")
        if Path(root_dir).resolve() != Path(notebook_dir_str).resolve():
            continue
        base = info.get("url", "")
        if base:
            try:
                urlopen(f"{base}api/status", timeout=2)
            except HTTPError:
                pass  # 403 etc = server is alive
            except URLError:
                continue  # Connection refused = server is dead
        token = info.get("token", "")
        url = f"{base.rstrip('/')}/lab?token={token}" if base and token else None
        _log("jupyter", f"find_server_url: matched {server_file.name} url={url}")
        return url
    _log("jupyter", "find_server_url: no server found")
    return None
