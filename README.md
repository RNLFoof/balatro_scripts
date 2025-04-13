Some scripts for some Balatro mods I'm working on. Apparently none of them are on my GitHub yet? Wacky.

They both assume that they're placed in a "scripts" directory in the mod root.

- generate_atlases.py: Generates atlas images and a Lua script to load them from individual [card(presumably)] images whose filenames are formatted as `assets/uncombined/ATLAS_NAME/CARD_NAME/CARD_NAME.png` or `assets/uncombined/ATLAS_NAME/CARD_NAME/CARD_NAME/VARIANT_NAME.png`.
- resize.py: Version of [Cryptid's script of the same name](https://github.com/MathIsFun0/Cryptid/blob/main/assets/1x/resize.py) modified to accept globs (so running `py resize.py *.png` should get everything). Generates 2x images from 1x images.
