'''
Streams a state_export.json -> sorted groups by their key (auth, authz, ibc, bank, staking, etc)
This is useful for debugging state exports and airdrops
'''

import ijson
import json
import os


NAME = "juno"
FILENAME = "state_export.json"
FOLDERNAME = f"{NAME}_sorted"
WANTED_SECTION = ['bank', 'staking'] # gov, staking, upgrade, transfer, mint, vesting, ibc, interchainaccounts, liquidity

current_dir = os.path.dirname(os.path.realpath(__file__))
os.makedirs(os.path.join(current_dir, FOLDERNAME), exist_ok=True)


sections = { 
    # locations within the genesis file
    # for ijson, every section MUST end with .item to grab the values
    "app_state": "app_state",
    "staked_amounts": "app_state.staking.delegations.item",
    "account_balances": "app_state.bank.balances.item",
    "total_supply": "app_state.bank.supply.item",
    "validators_info": "app_state.staking.validators.item", # useful to get like, a validator bonded status. Is a list
}  

def stream_section(fileName, key, debug=False):
    '''
        Given a fileName and a json key location,
        it will stream the jso objects in that section 
        and yield them as:
        -> index, object        
    '''
    if key not in sections:
        print(f"{key} not in sections")
        return

    key = sections[key]

    with open(fileName, 'rb') as input_file:
        parser = ijson.items(input_file, key)
        for idx, obj in enumerate(parser):
            if debug: print(f"stream_section: {idx}: {obj}")
            yield idx, obj

def get_keys(fileName, debug=False):
    '''
        Streams the state_export.json's Key Value pairs
    '''
    with open(fileName, 'rb') as input_file:
        parser = ijson.kvitems(input_file, sections["app_state"])
        for idx, obj in enumerate(parser):
            if debug: print(f"stream_section: {idx}: {obj}")
            yield idx, obj

def main():
    v = get_keys(os.path.join(current_dir, FILENAME), debug=False)
    for idx, obj in v:
        state_key = obj[0]

        if state_key not in WANTED_SECTION:
            print("Skipping", state_key, "since it is not wanted")
            continue

        print(f"{idx}: {state_key}")
        with open(os.path.join(os.path.join(current_dir, FOLDERNAME), f"{NAME}_{state_key}.json"), "w") as f:
            json.dump(obj[1], f, indent=2)

if __name__ == "__main__":
    main()