"""
Loads JSON files from a repo you set. Then you give it a Cutoff id, and it will iterate through all JSON, get the id, and put into a list.
Useful for airdropping specific traits to a select group of wallets

In this folder (stargaze-airdrop) you need to make a folder jsons/ which holds all your JSONs to use this script by default
"""

import json
import os

# == CONFIG ==
JSONS_DIR_NAME = "jsons"
# Assuming we have 1 - 10,000, we only want 1-9001
CUTOFF_ID = 9001
# Capitalization matters!
TRAIT_TYPE = "Head"
TRAIT_VALUE = "Umee"
FILENAME_SUFFIX = ".png"

# == Logic ==
current_dir = os.path.dirname(os.path.abspath(__file__))
jsons_dir = os.path.join(current_dir, JSONS_DIR_NAME)

files = os.listdir(jsons_dir)


ids = set()
for file in files:
    with open(os.path.join(jsons_dir, file)) as f:
        data = json.load(f)

    found = False

    for attr in reversed(list(data["attributes"])):
        if attr["trait_type"] == TRAIT_TYPE and attr["value"] == TRAIT_VALUE:
            found = True
            break

    if found:
        _id = int(data["image"].replace(FILENAME_SUFFIX, ""))

        # Custom ids we do not want
        if _id >= CUTOFF_ID:
            continue

        ids.add(_id)

# Returns a printed list to the terminal of the values here.
# Then you can copy paste into the main airdrop scripts for stargaze
print(sorted(ids))
