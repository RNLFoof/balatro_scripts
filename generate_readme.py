"""Generates README.md based on the docstrings of the other scripts.
Is presumably of very little use to anybody besides me.
Including [EXCLUDE FROM README] in the docstring does what it says on the tin."""
# It would probably be a bit cleaner for [EXCLUDE FROM README] to be a comment but uuugghhh idc man

import ast
from pathlib import Path
from textwrap import dedent
from typing import Optional, Dict

from internal import paths
from internal.misc import ensure_path

STARTING_TEXT = dedent("""
    Some general purpose Python scripts for some Balatro mods I'm working on.
    Intended to be placed in a "scripts" directory in the mod root.
""").strip()


@ensure_path
def get_script_docstring(script_filename: str | Path) -> Optional[str]:
    module = ast.parse(script_filename.read_bytes())
    if module is None:
        return
    if len(module.body) == 0:
        return
    first_entry = module.body[0]
    if "value" not in first_entry.__dict__:
        return
    potential_docstring = module.body[0].value.value
    if type(potential_docstring) is str:
        return potential_docstring


def get_script_docstrings() -> Dict[Path, str]:
    output = {
        script_filename: get_script_docstring(script_filename)
        for script_filename
        in Path().glob("*.py")
    }
    output = {
        script_filename: docstring
        for script_filename, docstring
        in output.items()
        if docstring is not None
    }
    return output


def first_paragraph(multiline_string: str) -> str:
    return multiline_string.split("\n\n")[0]


def flatten(multiline_string: str) -> str:
    return multiline_string.replace("\n", " ")


def get_script_bullet_points() -> str:
    return "\n".join([
        f"- `{script_filename}`: {flatten(first_paragraph(docstring))}"
        for script_filename, docstring
        in get_script_docstrings().items()
        if "[EXCLUDE FROM README]" not in docstring
    ])


def generate_readme_text() -> str:
    return STARTING_TEXT + "\n\n" + get_script_bullet_points()


def generate_readme():
    paths.README.write_text(generate_readme_text())


if __name__ == "__main__":
    generate_readme()
