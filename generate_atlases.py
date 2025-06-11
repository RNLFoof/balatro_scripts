"""Generates atlas images and a Lua script to load them from individual [card(presumably)] images whose filenames are
formatted as `assets/uncombined/ATLAS_NAME/CARD_NAME/CARD_NAME.png` or
`assets/uncombined/ATLAS_NAME/CARD_NAME/CARD_NAME/VARIANT_NAME.png`.

Assumes that it's in `MOD_ROOT/scripts`."""

import os
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Generator

import PIL.Image
import numpy as np
from math import ceil, floor

from PIL import Image

import resize
from internal import paths, ansi

max_grid_width = 8

MOD_ROOT_DIRECTORY = paths.get_mod_root()


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


@dataclass
class ImageMetadata:
    atlas_name: str
    card_name: str
    path: Path
    is_variant: bool = False
    prescaled: bool = False

    def position_path(self):
        output = []
        if self.is_variant:
            output.append(self.card_name)
        output.append(self.path.stem)
        return output

    def image(self, scale: int = 1) -> PIL.Image:
        output = PIL.Image.open(self.path)
        if not self.prescaled:
            output = output.resize([x*scale for x in output.size])
        return output


def card_images_within(atlas_name: str, scale: int) -> Generator[ImageMetadata, None, None]:
    # atlas_component_path = paths.UNCOMBINED_ASSETS / atlas_name
    card_names = get_immediate_subdirectories(paths.UNCOMBINED_ASSETS / atlas_name)  # These don't *have* to be cards,
    #                                         # but they *usually* are,
    #                                         # so I think it makes this more clear (as opposed to just "image names")
    # card_image_directories = list(filter(
    #     lambda x: os.path.exists(
    #         os.path.join(
    #             atlas_component_path,
    #             x,
    #             f"{x}.png"
    #         )
    #     ) or os.path.exists(
    #         os.path.join(
    #             atlas_component_path,
    #             x,
    #             x
    #         )
    #     ),
    #     card_image_directories
    # ))

    for card_name in card_names:
        found_card_name = False
        for pattern, kwargs in [
            (paths.UNCOMBINED_ASSETS / atlas_name / card_name / f"{card_name}.png", {}),
            (paths.UNCOMBINED_ASSETS / atlas_name / card_name / card_name / "*.png", {"is_variant": True}),
            (paths.UNCOMBINED_ASSETS / atlas_name / card_name / f"{scale}x" / f"{card_name}.png", {"prescaled": True}),
            (paths.UNCOMBINED_ASSETS / atlas_name / card_name / f"{scale}x" / card_name / "*.png", {"is_variant": True, "prescaled": True}),
        ]:
            for path in Path("").glob(str(pattern)):
                print(f"\t{scale}x: Adding {ansi.OKBLUE}{path}{ansi.ENDC}")
                yield ImageMetadata(atlas_name, card_name, path, **kwargs)
                found_card_name = True
        if not found_card_name:
            print(f"\t{ansi.WARNING}{scale}x: Unable to find anything for {card_name}, if you care{ansi.ENDC}")
    # 
    # for image_path_metadata in image_path_metadatas:
    #     yield image_path_metadata
        # yield card_image_key_path, card_image_path
        #
        # found_anything = False
        # if os.path.exists(card_image_path):
        #     card_image_key_path = [card_image_directory]
        #     yield card_image_key_path, card_image_path
        #     found_anything = True
        # elif os.path.exists(card_variant_images_path):
        #     for image in os.listdir(card_variant_images_path):
        #         if image.endswith(".png"):
        #             card_image_key_path = [card_image_directory, os.path.splitext(image)[0]]
        #             card_image_path = os.path.join(atlas_component_path, card_image_directory, card_image_directory, image)
        #             yield card_image_key_path, card_image_path
        #             found_anything = True
        #
        # if not found_anything:
        #     print(f"No usable images found in {card_image_directory}, if you care")
        #     continue


def generate_atlas(atlas_name: str, scale: int) -> str:
    """Returns initialization code."""
    image_metadatas = list(card_images_within(atlas_name, scale))
    number_of_card_images = len(image_metadatas)
    grid_size = np.array([
        min(number_of_card_images, max_grid_width),
        ceil(number_of_card_images / max_grid_width)
    ])

    atlas_image = None
    card_positions = {}
    for card_image_index, image_metadata in enumerate(image_metadatas):
        card_image_index: int
        image_metadata: ImageMetadata
        card_image = image_metadata.image(scale)
        card_image_size = np.array(card_image.size)

        if not atlas_image:
            atlas_image = Image.new("RGBA", tuple(grid_size * card_image_size))

        card_grid_placement = np.array([
            card_image_index % max_grid_width,
            floor(card_image_index / grid_size[0])
        ])
        card_pixel_placement = card_grid_placement * card_image_size
        atlas_image.paste(card_image, [*card_pixel_placement, *(card_pixel_placement+card_image_size)])

        working = card_positions
        for card_image_key in image_metadata.position_path()[:-1]:
            working.setdefault(card_image_key, {})
            working = working[card_image_key]
        working[image_metadata.position_path()[-1]] = card_grid_placement

    atlas_key = f"atlas_{atlas_name}"
    atlas_output_filename = f"{atlas_key}.png"
    output_dir = paths.ASSETS / f"{scale}x"
    atlas_image.save(output_dir / atlas_output_filename)
    card_positions_as_texts = [""]

    def traverse_tree_and_make_jsonable(working, indent=3):  # I swear 3 is correct. trust me
        for key, value in working.items():
            card_positions_as_texts[-1] += "    " * indent + f'["{key}"]'
            if type(value) is dict:
                card_positions_as_texts[-1] += " = {"
                indent += 1
                card_positions_as_texts.append("")
                traverse_tree_and_make_jsonable(value, indent=indent)
                indent -= 1
                card_positions_as_texts[-1] += "    " * indent + "},"
                card_positions_as_texts.append("")
            else:
                card_positions_as_texts[-1] += f' = {{x={value[0]}, y={value[1]}}},'
                card_positions_as_texts.append("")
                # working[key] = {
                #     "x": int(value[0]),
                #     "y": int(value[1]),
                # }
    traverse_tree_and_make_jsonable(card_positions)
    card_positions_as_texts = card_positions_as_texts[:-1]  # It should always end with one empty entry
    card_positions_as_text = "\n".join(card_positions_as_texts)[12:]  # the 12 trims extra indentation that gets readded below

    if scale == 1:
        return dedent(f"""
        --- {atlas_name.upper()} ---
        
        {atlas_key} = SMODS.Atlas {{
            key = "{atlas_key}",
            path = "{atlas_output_filename}",
            px = {card_image_size[0]},
            py = {card_image_size[1]}
        }}
        
        {atlas_key}_positions = {{
            {
                card_positions_as_text
            }
        }}
        """).strip()


def generate_atlases_for_name(atlas_name: str) -> str:
    print(f"Generating {ansi.OKGREEN}{atlas_name}{ansi.ENDC}:")
    generate_atlas(atlas_name, 2)
    return generate_atlas(atlas_name, 1)

def generate_all_atlases():
    initialization_code_snippets = []

    relative_path_to_this_script = os.path.relpath(
        os.path.realpath(__file__),
        MOD_ROOT_DIRECTORY,
    )
    initialization_code_snippets.append(dedent(f"""
        -- This file is generated in its entirety by "{relative_path_to_this_script}"!
        -- If you make any manual changes they're likely to be MINDLESSLY OVERWRITTEN!!
        -- So don't do that.
    """).strip())

    for atlas_name in os.listdir(paths.UNCOMBINED_ASSETS):
        output = generate_atlases_for_name(atlas_name)
        initialization_code_snippets.append(output)

    with open(paths.ATLAS_INITIALIZATION_FILE, "w") as initialization_file:
        initialization_file.write("\n\n".join(initialization_code_snippets))


if __name__ == "__main__":
    generate_all_atlases()
