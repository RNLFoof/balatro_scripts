import collections
import os
from os.path import relpath
from textwrap import dedent

import numpy as np
from math import ceil, floor

from PIL import Image

Dimensions = collections.namedtuple("Dimensions", ("width", "height"))
Coordinates = collections.namedtuple("Coordinates", ("x", "y"))

max_grid_width = 8

mod_root_directory = os.path.join("..")
assets_path = os.path.join(mod_root_directory, "assets")
uncombined_path = os.path.join(assets_path, "uncombined")
atlas_output_path = os.path.join(assets_path, "1x")
initialization_file_path = os.path.join(mod_root_directory, "atlases.lua")

def generate_atlas(atlas_name: str) -> str:
    """Returns initialization code."""
    atlas_component_path = os.path.join(uncombined_path, atlas_name)
    card_image_directories = os.listdir(atlas_component_path)  # These don't *have* to be cards, but they *usually* are,
                                            # so I think it makes this more clear (as opposed to just "image filenames")
    number_of_card_images = len(card_image_directories)
    grid_size = np.array([
        min(number_of_card_images, max_grid_width),
        ceil(number_of_card_images / max_grid_width)
    ])

    atlas_image = None
    card_positions = {}
    for card_image_index, card_image_directory in enumerate(card_image_directories):
        card_image_path = os.path.join(atlas_component_path, card_image_directory, f"{card_image_directory}.png")
        card_image = Image.open(card_image_path)
        card_image_size = np.array(card_image.size)

        if not atlas_image:
            atlas_image = Image.new("RGBA", tuple(grid_size * card_image_size))

        card_grid_placement = np.array([
            card_image_index // max_grid_width,
            floor(card_image_index / grid_size[0])
        ])
        card_pixel_placement = card_grid_placement * card_image_size
        atlas_image.paste(card_image, [*card_pixel_placement, *(card_pixel_placement+card_image_size)])
        card_positions[card_image_directory] = card_grid_placement

    atlas_key = f"atlas_{atlas_name}"
    atlas_output_filename = f"{atlas_key}.png"
    atlas_image.save(os.path.join(atlas_output_path, atlas_output_filename))

    card_positions_as_text = ",\n".join(
        f'["{name}"] = {{{position[0]}, {position[1]}}}'\
        for name, position\
        in card_positions.items()
    )

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

def generate_atlases():
    initialization_code_snippets = []

    relative_path_to_this_script = os.path.relpath(
        os.path.realpath(__file__),
        mod_root_directory,
    )
    initialization_code_snippets.append(dedent(f"""
        -- This file is generated in its entirety by "{relative_path_to_this_script}"!
        -- If you make any manual changes they're likely to be MINDLESSLY OVERWRITTEN!!
        -- So don't do that.
    """).strip())

    for atlas_name in os.listdir(uncombined_path):
        output = generate_atlas(atlas_name)
        initialization_code_snippets.append(output)

    with open(initialization_file_path, "w") as initialization_file:
        initialization_file.write("\n\n".join(initialization_code_snippets))

if __name__ == "__main__":
    generate_atlases()