from __future__ import annotations
import sys, importlib, types
from pathlib import Path
from typing import List

def get_wanvideo_scheduler_list() -> List[str]:
    here = Path(__file__).resolve()
    # /workspace/ComfyUI/custom_nodes/comfyui-wanvideo-schedulerloop/test.py
    CUSTOM_NODES = here.parents[1]    # /workspace/ComfyUI/custom_nodes
    COMFY_ROOT   = here.parents[2]    # /workspace/ComfyUI
    WVW_ROOT     = CUSTOM_NODES / "ComfyUI-WanVideoWrapper"

    # Make 'comfy' importable (wanvideo/utils.py imports comfy)
    if str(COMFY_ROOT) not in sys.path:
        sys.path.insert(0, str(COMFY_ROOT))
    import comfy  # sanity: raises if not found

    # If the canonical folder name isn't present (e.g. "-main"), scan once.
    if not (WVW_ROOT / "wanvideo" / "schedulers" / "__init__.py").exists():
        for p in CUSTOM_NODES.iterdir():
            if (p / "wanvideo" / "schedulers" / "__init__.py").exists():
                WVW_ROOT = p
                break
        else:
            raise RuntimeError("WanVideoWrapper not found under custom_nodes.")

    # Mount repo root as a *namespace parent* (PEP 420); do NOT exec repo __init__.py.
    alias = "wanvw"
    for name in list(sys.modules):
        if name == alias or name.startswith(alias + ".") or name == "wanvideo" or name.startswith("wanvideo."):
            del sys.modules[name]
    pkg = types.ModuleType(alias)
    pkg.__path__ = [str(WVW_ROOT)]  # namespace package root
    pkg.__package__ = alias
    sys.modules[alias] = pkg

    # Import parent then submodule (package-aware); relative imports now resolve.
    importlib.import_module(f"{alias}.wanvideo")
    mod = importlib.import_module(f"{alias}.wanvideo.schedulers")  # uses repo’s schedulers/__init__.py

    sched = getattr(mod, "scheduler_list")
    return list(sched() if callable(sched) else sched)