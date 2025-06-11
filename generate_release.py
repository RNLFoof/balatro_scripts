"""Generates a zip file containing only the files necessary to run the mod.
That is, excludes files only needed for development."""

import json
from os.path import normpath
from pathlib import Path
from shutil import copy, make_archive, rmtree
from typing import Dict, Any, Optional

from internal import ansi, paths
from internal.paths import guarantee_is_path

RELEASES = paths.MOD_ROOT / ".releases"
TEMP = RELEASES / "temp"


def get_files_to_include_in_release(relative_to: Path | str):
    _relative_to: Path = guarantee_is_path(relative_to)
    
    output = set([path for path in paths.MOD_ROOT.glob("**/*?.*")])
    removed = set()
    for exclude in [
        ".*/**/*",
        "**/.*/**/*",
        "**/*.yue",
        "**/*test*",
        "assets/uncombined/**/*",
        "scripts/**/*",
    ]:
        to_remove = set([x for x in paths.MOD_ROOT.glob(exclude)])
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
        print("\n".join(
            [f"...{ansi.OKBLUE}\\{worrying_removal.resolve().relative_to((paths.MOD_ROOT / '..').resolve())}{ansi.ENDC}" for
             worrying_removal in worrying_removals]))

    return output


def generate_release(relative_to: str | Path = ""):
    _relative_to: Path = guarantee_is_path(relative_to)
    
    mod_metadata = paths.get_mod_metadata(paths.MOD_ROOT)
    release_name = f"{mod_metadata['id']}_v{mod_metadata['version']}"
    to_copy = get_files_to_include_in_release(paths.MOD_ROOT)

    try:
        for source in to_copy:
            if source.is_dir():
                print(f"Huh, {source} is a directory?")
                continue
            destination = paths.MOD_ROOT / TEMP / release_name / source.relative_to(paths.MOD_ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            copy(source, destination)

        make_archive(str(RELEASES / release_name), 'zip', paths.MOD_ROOT / TEMP)
    except Exception as e:
        raise e
    finally:
        rmtree(paths.MOD_ROOT / TEMP)

    saved_at = (paths.MOD_ROOT.absolute() / RELEASES / (release_name + ".zip")).resolve().relative_to(
        (paths.MOD_ROOT / '..').resolve())
    print(f"Release saved to {ansi.OKBLUE}{saved_at}{ansi.ENDC}")


if __name__ == "__main__":
    generate_release()
