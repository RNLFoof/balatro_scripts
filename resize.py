# Stole this from Cryptid. much love
# modified to accept globs

import sys
from glob import iglob

from PIL import Image
import os
import time

def upscale_pixel_art(input_image, output_directory, input_image_path):
    # Double the size
    new_size = (input_image.width * 2, input_image.height * 2)
    resized_image = input_image.resize(new_size, Image.NEAREST)  # NEAREST resampling preserves pixelation

    # Save the resized image
    filename = os.path.basename(input_image_path)
    output_image_path = os.path.join(output_directory, filename)
    resized_image.save(output_image_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py resize.py <input_image>")
        sys.exit(1)

    input_directory = os.path.join(os.path.realpath(__file__), "..", "..", "assets", "1x")
    did_anything = False
    for filename in iglob(sys.argv[1], root_dir=input_directory):
        did_anything = True
        print(f"Resizing {filename}...")
        input_image_path = os.path.join(input_directory, filename)
        input_image = Image.open(input_image_path)

        output_directory = os.path.join(input_directory, "../2x/")
        upscale_pixel_art(input_image, output_directory, input_image_path)

    if did_anything:
        print("Done! :)")
    else:
        print("I didn't find anything that matched the path provided :(")