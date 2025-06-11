"""Generates 2x images from 1x images. Stole this from
[Cryptid](https://github.com/MathIsFun0/Cryptid/blob/main/assets/1x/resize.py) (much love) and modified to accept globs.
(so running `py resize.py *.png` should get everything)

Assumes that it's in `MOD_ROOT/scripts`"""

import sys
from glob import iglob
from pathlib import Path

from PIL import Image
import os
import time

from internal.misc import ensure_path


def upscale_pixel_art(input_image, output_directory, input_image_path):
    # Double the size
    new_size = (input_image.width * 2, input_image.height * 2)
    resized_image = input_image.resize(new_size, Image.NEAREST)  # NEAREST resampling preserves pixelation

    # Save the resized image
    filename = os.path.basename(input_image_path)
    output_image_path = os.path.join(output_directory, filename)
    resized_image.save(output_image_path)


@ensure_path
def upscale_pixel_art_at(input_image_filename: Path | str):
    input_image_filename: Path
    print(f"Resizing {input_image_filename.name}...")
    input_image = Image.open(input_image_filename)

    output_directory = os.path.join(input_image_filename, "../../2x/")
    upscale_pixel_art(input_image, output_directory, input_image_filename)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py resize.py <input_image>")
        sys.exit(1)

    input_directory = os.path.join(os.path.realpath(__file__), "..", "..", "assets", "1x")
    did_anything = False
    for filename in iglob(sys.argv[1], root_dir=input_directory):
        did_anything = True
        input_image_filename = os.path.join(input_directory, filename)
        upscale_pixel_art_at(input_image_filename)

    if did_anything:
        print("Done! :)")
    else:
        print("I didn't find anything that matched the path provided :(")