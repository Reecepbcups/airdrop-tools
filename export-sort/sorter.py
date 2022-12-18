'''
Streams a state_export.json -> sorted groups by their key (auth, authz, ibc, bank, staking, etc)
This is useful for debugging state exports and airdrops
'''

import ijson
import json
import os

from utils import get_keys, get_export_file_location

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
from dotenv import load_dotenv
load_dotenv(os.path.join(parent_dir, ".env"))

# Variables
NAME = os.getenv("SNAPSHOT_CHAIN_PREFIX", "juno")
FILENAME = os.getenv("SNAPSHOT_STATE_EXPORT", "state_export.json")
SNAPSHOT_SORTED_FOLDER = os.getenv("SNAPSHOT_SORTED_FOLDER", f"{NAME}_sorted")
WANTED_SECTION = os.getenv("SNAPSHOT_WANTED_SECTIONS", "").split(",")

exportFileLoc = get_export_file_location(FILENAME)
if len(exportFileLoc) == 0:
    print(f"No state export found for: {FILENAME}. Please ensure it is in the _EXPORTS folder")
    exit(1)


sorted_dir = os.path.join(parent_dir, "_SORTED", SNAPSHOT_SORTED_FOLDER)
os.makedirs(sorted_dir, exist_ok=True)

def main():
    v = get_keys(exportFileLoc, debug=False)
    for idx, obj in v:
        state_key = obj[0]

        if state_key not in WANTED_SECTION:
            print(f"skipping {state_key}...")
            continue

        print(f"{idx}: {state_key}")
        with open(os.path.join(sorted_dir, f"{NAME}_{state_key}.json"), "w") as f:
            json.dump(obj[1], f, indent=1)

if __name__ == "__main__":
    main()