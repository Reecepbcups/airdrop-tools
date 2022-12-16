import os, json, bech32

'''
Hi Reece- apologies for the late reply, but the tea, have been busy.  
we are game developers who have created a virtual world using Unity3d. 
Currently we have a login method which users email\password. 
We now are looking at how we can integrate different wallets with our "metaverse".   
looking for developer that can help us navigate this, the first step being the airdrop which we have promised our userbase.  

are you able to provide "Anyone staking 30 Atom, 30 Juno or 50 Osmo on 23/10/2022 (snapshot date)"

Snapshot Blocks: (staking only)
- osmosis 6570000
- cosmos 12560000
- juno 5360000
'''

current_dir = os.path.dirname(os.path.abspath(__file__))
csvs = os.path.join(current_dir, "csvs")
os.makedirs(csvs, exist_ok=True)
os.chdir(current_dir)

# exclude CEXs - https://github.com/notional-labs/craft-airdrop/blob/main/src/airdrop_data.py#L18
# https://www.mintscan.io/cosmos/validators
BLACKLISTED_CENTRAL_EXCHANGES = {
    'cosmosvaloper18ruzecmqj9pv8ac0gvkgryuc7u004te9rh7w5s': "Binance Node",
    'cosmosvaloper156gqf9837u7d4c4678yt3rl4ls9c5vuursrrzf': "Binance Staking",
    'cosmosvaloper1a3yjj7d3qnx4spgvjcwjq9cw9snrrrhu5h6jll': "Coinbase Custody",
    'cosmosvaloper1nm0rrq86ucezaf8uj35pq9fpwr5r82clzyvtd8': "Kraken",
}

files = {
    "juno": 'juno_staking.json',
    "cosmos": 'cosmos_staking.json',
    "osmosis": 'osmosis_staking.json'
}
min_requirements = {
    "juno": 30,
    "cosmos": 30,
    "osmosis": 50
}

# This was not used here for this, but can be in the future.
conversion_rate = {
    "juno": 1, # 1 CW20 for 1
    "cosmos": 3, # 4 CW20 per 1 ATOM
    "osmosis": 0.5 # 0.5 CW20 per 1 OSMO
}

# convert rate? ex 1atom -> 1 of their CW20 token or something

FINAL_ADDRESSES_AMOUNTS = {} # address: amount


def convert_address_to_juno(address, new_prefix="juno") -> str:
    _, data = bech32.bech32_decode(address)
    return bech32.bech32_encode(new_prefix, data)

def get_new_token_amount(amount, token):
    '''
    Converts an old token (atom, osmo, juno) to the new rate for the CW20 / genesis udenom
    '''
    return amount * conversion_rate[token]


addrs = {k: {} for k in files.keys()}
for token in files:
    print(f"Processing {token}")
    
    rate = conversion_rate[token]
    min_req = min_requirements[token]
    with open(files[token], 'r') as f:
        data = json.load(f)['delegations']
        '''
        {
            "delegator_address": "juno1twrgyxhra09v8k95g60tge4mdqle8q5y8cwnmp",
            "shares": "1000000.000000000000000000",
            "validator_address": "junovaloper1twrgyxhra09v8k95g60tge4mdqle8q5yc9cuqc"
        },
        '''

    for d in data:
        val = d['validator_address']
        addr = d['delegator_address']            
        full_token = int(float(d['shares']) / 1000000) # from say 1_000_000uatom -> 1atom for example

        if val in BLACKLISTED_CENTRAL_EXCHANGES:
            continue # ignore CEXs
        if full_token < min_req:
            continue # ignore people with not enough staked
        
        if addr not in addrs[token].keys():
            addrs[token][addr] = None

        # juno_addr = convert_address_to_juno(addr)
        # if juno_addr not in FINAL_ADDRESSES_AMOUNTS:
        #     FINAL_ADDRESSES_AMOUNTS[juno_addr] = 999

        # FINAL_ADDRESSES_AMOUNTS[juno_addr] += get_new_token_amount(full_token, token)

# save FINAL_ADDRESSES_AMOUNTS to file as final_output.json
# with open('final_output.json', 'w') as f:
#     json.dump(FINAL_ADDRESSES_AMOUNTS, f, indent=2)    



# save all Juno -> cvs
# sort FINAL_ADDRESSES_AMOUNTS  by keys alphabetically
# FINAL_ADDRESSES_AMOUNTS = dict(sorted(FINAL_ADDRESSES_AMOUNTS.items(), key=lambda item: item[0]))
# # save to csv file
# with open('final_output.csv', 'w') as f:
#     f.write(f"address,amount\n")
#     for addr, amount in FINAL_ADDRESSES_AMOUNTS.items():
#         f.write(f"{addr},{amount}\n")


# save every key to its own csv, up to 50k per file
for token in addrs:

    l = len(addrs[token].keys())
    print(f"{token}={l}")
    # continue

    maximum = 50000-2
    if l < maximum:
        maximum = l

    groups = [list(addrs[token].keys())[i:i + maximum] for i in range(0, l, maximum)]    
    for i, group in enumerate(groups):
        with open(f"csvs/{token}_{i}.csv", 'w') as f:
            f.write(f"address\n")
            for addr in group:
                f.write(f"{addr}\n")
        
            
        