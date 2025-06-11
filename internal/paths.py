import json
from pathlib import Path
from typing import Optional, Dict, Any


def guarantee_is_path(path: str | Path) -> Path:
    return Path(path)


# This is more of a misc.py function, but it's needed here, and I won't want spaghetti
def get_mod_metadata(mod_root: str | Path = "") -> Optional[Dict[str, Any]]:
    _mod_root: Path = guarantee_is_path(mod_root)
    for json_path in _mod_root.glob("*.json"):
        json_contents = json.loads(json_path.read_text())
        if "id" not in json_contents:
            continue
        if json_path.stem == json_contents["id"]:
            return json_contents
    return None


def is_directory_mod_root(directory: str | Path = "") -> bool:
    return get_mod_metadata(directory) is not None


def get_mod_root(relative_to: str | Path = ""):
    _relative_to: Path = guarantee_is_path(relative_to)
    for check in [
        _relative_to,
        _relative_to / "../"
    ]:
        if is_directory_mod_root(check):
            return check
    raise ValueError("Unable to find mod root from given location.")


# I don't want to lock off the ability to ever access these guys independently of the mod root
# but, realistically, they're mostly needed relative to the mod root
# so use this: regexr.com/8fbgu
ROOTLESS_README = Path("README.md")
ROOTLESS_ASSETS = Path("assets")
ROOTLESS_UNCOMBINED_ASSETS = ROOTLESS_ASSETS / "uncombined"
ROOTLESS_ASSETS_1X = ROOTLESS_ASSETS / "1x"
ROOTLESS_ASSETS_2X = ROOTLESS_ASSETS / "2x"
ROOTLESS_ATLAS_INITIALIZATION_FILE = Path("atlases.lua")

MOD_ROOT = get_mod_root()

README = MOD_ROOT / ROOTLESS_README
ASSETS = MOD_ROOT / ROOTLESS_ASSETS
UNCOMBINED_ASSETS = MOD_ROOT / ROOTLESS_UNCOMBINED_ASSETS
ASSETS_1X = MOD_ROOT / ROOTLESS_ASSETS_1X
ASSETS_2X = MOD_ROOT / ROOTLESS_ASSETS_2X
ATLAS_INITIALIZATION_FILE = MOD_ROOT / ROOTLESS_ATLAS_INITIALIZATION_FILE
