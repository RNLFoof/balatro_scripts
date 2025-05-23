"""Generates a zip file containing only the files necessary to run the mod.
That is, excludes files only needed for development."""

import json
from os.path import normpath
from pathlib import Path
from shutil import copy, make_archive, rmtree
from typing import Dict, Any, Optional

from internal import ansi

RELEASES = Path(".releases")
TEMP = RELEASES / "temp"


def guarantee_path(path: str | Path) -> Path:
    return Path(path)


def get_mod_metadata(mod_root: str | Path = "") -> Optional[Dict[str, Any]]:
    _mod_root: Path = guarantee_path(mod_root)
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
    _relative_to: Path = guarantee_path(relative_to)
    for check in [
        _relative_to,
        _relative_to / "../"
    ]:
        if is_directory_mod_root(check):
            return check
    raise ValueError("Unable to find mod root from given location.")


def get_files_to_include_in_release(relative_to: Path | str):
    _relative_to: Path = guarantee_path(relative_to)
    mod_root = get_mod_root(_relative_to)
    output = set([path for path in mod_root.glob("**/*?.*")])
    removed = set()
    for exclude in [
        ".*/**/*",
        "**/.*/**/*",
        "**/*.yue",
        "**/*test*",
        "assets/uncombined/**/*",
        "scripts/**/*",
    ]:
        to_remove = set([x for x in mod_root.glob(exclude)])
        output -= to_remove
        removed |= to_remove

    worrying_removals = [
        removed_item
        for removed_item
        in removed
        if str(removed_item).endswith(".lua")
    ]
    if worrying_removals:
        print("The following files weren't added to the release, and are worth looking over if you're a human:")
        print("\n".join([f"...{ansi.OKBLUE}\\{worrying_removal.resolve().relative_to((mod_root / '..').resolve())}{ansi.ENDC}" for worrying_removal in worrying_removals]))

    return output


def generate_release(relative_to: str | Path = ""):
    _relative_to: Path = guarantee_path(relative_to)
    mod_root = get_mod_root(_relative_to)
    mod_metadata = get_mod_metadata(mod_root)
    release_name = f"{mod_metadata['id']}_v{mod_metadata['version']}"
    to_copy = get_files_to_include_in_release(mod_root)

    try:
        for source in to_copy:
            if source.is_dir():
                print(f"Huh, {source} is a directory?")
                continue
            destination = mod_root / TEMP / release_name / source.relative_to(mod_root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            copy(source, destination)

        make_archive(str(mod_root / RELEASES / release_name), 'zip', mod_root / TEMP)
    except Exception as e:
        raise e
    finally:
        rmtree(mod_root / TEMP)

    saved_at = (mod_root.absolute() / RELEASES / (release_name+".zip")).resolve().relative_to((mod_root / '..').resolve())
    print(f"Release saved to {ansi.OKBLUE}{saved_at}{ansi.ENDC}")



if __name__ == "__main__":
    generate_release()
