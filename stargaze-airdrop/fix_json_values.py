"""
This script fixes your JSON values such as applying 1 description to all, formating names properly, and remioving un-needed keys for stargaze.
"""

import json
import os

JSONS_DIR_NAME = "jsons"
FILENAME_SUFFIX = ".png"
NAME = "Tabulators"  # the name of your collection here (comes out as `Tabulators #id`)
all_desc = "Here is what I put as my description on all of these!"
REMOVE_KEYS = ["compiler"]

# == Logic ==
current_dir = os.path.dirname(os.path.abspath(__file__))
json_dir = os.path.join(current_dir, JSONS_DIR_NAME)

files = os.listdir(json_dir)
files.sort()


for f in files:
    data = open(os.path.join(json_dir, f), "r").read()

    # dict_keys(['name', 'image', 'attributes', 'collectionName', 'description', 'compiler'])
    d = dict(json.loads(data))

    # Tabulators #id for the name
    if NAME not in d["name"]:
        current_id = d["name"]
        d["name"] = f"{NAME} #{current_id}"

    for k in REMOVE_KEYS:
        if k in d.keys():
            del d[k]

    d["description"] = all_desc

    # Dump d to the same file
    with open(os.path.join(json_dir, f), "w") as js:
        json.dump(d, js, indent=4)
