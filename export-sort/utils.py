import ijson, os, bech32

current_dir = os.path.dirname(os.path.realpath(__file__))
exports_folder = os.path.join(os.path.dirname(current_dir), "_EXPORTS")

sections = { 
    # locations within the genesis file for ijson, every section MUST end with .item to grab the values
    "app_state": "app_state",
    "staked_amounts": "app_state.staking.delegations.item",
    "account_balances": "app_state.bank.balances.item",
    "total_supply": "app_state.bank.supply.item",
    # useful to get like, a validator bonded status. Is a list
    "validators_info": "app_state.staking.validators.item",
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

def get_keys(file_path, debug=False):
    '''
    Streams the state_export.json's Key Value pairs
    '''
    with open(file_path, 'rb') as input_file:
        parser = ijson.kvitems(input_file, sections["app_state"])
        for idx, obj in enumerate(parser):
            if debug: print(f"stream_section: {idx}: {obj}")
            yield idx, obj


def get_exports() -> list[str]:
    return os.listdir(exports_folder)

def get_export_file_location(filename: str) -> str:
    '''
    Returns the file path of the export file if it is found,
    else: ""
    '''
    if filename not in get_exports():
        print(f"{filename} not in exports folder")
        return ""
    
    return os.path.join(exports_folder, filename)


def bech32encode(prefix, data):    
    return bech32.bech32_encode(prefix, bech32.convertbits(data, 8, 5, True))

def bech32decode(address):
    prefix, data = bech32.bech32_decode(address)        
    return prefix, bech32.convertbits(data, 5, 8, False)

# print(get_export_file_location("test.txt"))