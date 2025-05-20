"""Generates atlas images and a Lua script to load them from individual [card(presumably)] images whose filenames are
formatted as `assets/uncombined/ATLAS_NAME/CARD_NAME/CARD_NAME.png` or `assets/uncombined/ATLAS_NAME/CARD_NAME/CARD_NAME/VARIANT_NAME.png`.
Assumes that it's in `MOD_ROOT/scripts`"""

import os
import json
from textwrap import dedent

import numpy as np
from math import ceil, floor

from PIL import Image

max_grid_width = 8

MOD_ROOT_DIRECTORY = os.path.join("..")
ASSETS_PATH = os.path.join(MOD_ROOT_DIRECTORY, "assets")
UNCOMBINED_PATH = os.path.join(ASSETS_PATH, "uncombined")
ATLAS_OUTPUT_PATH = os.path.join(ASSETS_PATH, "1x")
INITIALIZATION_FILE_PATH = os.path.join(MOD_ROOT_DIRECTORY, "atlases.lua")

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def card_images_within(atlas_name):
    atlas_component_path = os.path.join(UNCOMBINED_PATH, atlas_name)
    card_image_directories = get_immediate_subdirectories(atlas_component_path)  # These don't *have* to be cards, but they *usually* are,
                                            # so I think it makes this more clear (as opposed to just "image filenames")
    card_image_directories = list(filter(
        lambda x: os.path.exists(
            os.path.join(
                atlas_component_path, 
                x, 
                f"{x}.png"
            )
        ) or os.path.exists(
            os.path.join(
                atlas_component_path, 
                x, 
                x
            )
        ),
        card_image_directories
    ))
    for card_image_index, card_image_directory in enumerate(card_image_directories):
        card_image_path = os.path.join(atlas_component_path, card_image_directory, f"{card_image_directory}.png")
        card_variant_images_path = os.path.join(atlas_component_path, card_image_directory, card_image_directory)
        found_anything = False
        if os.path.exists(card_image_path):
            card_image_key_path = [card_image_directory]
            yield card_image_key_path, card_image_path
            found_anything = True
        elif os.path.exists(card_variant_images_path):
            for image in os.listdir(card_variant_images_path):
                if image.endswith(".png"):
                    card_image_key_path = [card_image_directory, os.path.splitext(image)[0]]
                    card_image_path = os.path.join(atlas_component_path, card_image_directory, card_image_directory, image)
                    yield card_image_key_path, card_image_path
                    found_anything = True
        
        if not found_anything:
            print(f"No usable images found in {card_image_directory}, if you care")
            continue

def generate_atlas(atlas_name: str) -> str:
    """Returns initialization code."""
    card_images = list(card_images_within(atlas_name))
    number_of_card_images = len(card_images)
    grid_size = np.array([
        min(number_of_card_images, max_grid_width),
        ceil(number_of_card_images / max_grid_width)
    ])

    atlas_image = None
    card_positions = {}
    # card_positions_as_text = ""
    for card_image_index, (card_image_key_path, card_image_path) in enumerate(card_images):
        card_image = Image.open(card_image_path)
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
        # card_positions_as_text += f'\n{" " * 8}'
        for card_image_key in card_image_key_path[:-1]:
            working.setdefault(card_image_key, {})
            working = working[card_image_key]
            # card_positions_as_text += f'["{card_image_key}"]'
        working[card_image_key_path[-1]] = card_grid_placement
        # card_positions_as_text += f'["{card_image_key_path[-1]}"] = {{x={card_grid_placement[0]}, y={card_grid_placement[1]}}},'

    atlas_key = f"atlas_{atlas_name}"
    atlas_output_filename = f"{atlas_key}.png"
    atlas_image.save(os.path.join(ATLAS_OUTPUT_PATH, atlas_output_filename))
    card_positions_as_texts = [""]
    def traverse_tree_and_make_jsonable(working, indent=2):  # I swear 2 is correct. trust me
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
    # card_positions_as_text = json.dumps(card_positions, indent = 4)
    # card_positions_as_text = card_positions_as_text.replace(":", "=")
    card_positions_as_text = "\n".join(card_positions_as_texts)[8:]  # The 8 trims extra indentation that gets readded below

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
        MOD_ROOT_DIRECTORY,
    )
    initialization_code_snippets.append(dedent(f"""
        -- This file is generated in its entirety by "{relative_path_to_this_script}"!
        -- If you make any manual changes they're likely to be MINDLESSLY OVERWRITTEN!!
        -- So don't do that.
    """).strip())

    for atlas_name in os.listdir(UNCOMBINED_PATH):
        output = generate_atlas(atlas_name)
        initialization_code_snippets.append(output)

    with open(INITIALIZATION_FILE_PATH, "w") as initialization_file:
        initialization_file.write("\n\n".join(initialization_code_snippets))

if __name__ == "__main__":
    generate_atlases()