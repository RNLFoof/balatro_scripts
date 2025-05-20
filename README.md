Some general purpose Python scripts for some Balatro mods I'm working on.
Intended to be placed in a "scripts" directory in the mod root.

- `generate_atlases.py`: Generates atlas images and a Lua script to load them from individual [card(presumably)] images whose filenames are formatted as `assets/uncombined/ATLAS_NAME/CARD_NAME/CARD_NAME.png` or `assets/uncombined/ATLAS_NAME/CARD_NAME/CARD_NAME/VARIANT_NAME.png`.
- `generate_release.py`: Generates a zip file containing only the files necessary to run the mod. That is, excludes files only needed for development.
- `resize.py`: Generates 2x images from 1x images. Stole this from [Cryptid](https://github.com/MathIsFun0/Cryptid/blob/main/assets/1x/resize.py) (much love) and modified to accept globs. (so running `py resize.py *.png` should get everything)