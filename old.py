# see if I can get anything useful from here, but its messy so prob not.

from ctypes import addressof
from operator import contains
import requests
import ijson # https://pypi.org/project/ijson/#usage JSON as a stream
import json
import re
import os

import src.utils as utils

'''
Snapshot tooling to stream an export to a file for easier handling in the format:
    delegator_address   validator_address   staked_amount

Where staked amount is in the udenom. Divide by 1_000_000 to get the human readable amount

Example:
osmosisd export 3500001 2> osmosis_export.json
# osmosisd export-derive-balances osmosis_export.json balances.json --breakdown-by-pool-ids 1,561 - not neeeded anymore

# Done Automatically:
Compress:
    xz appd_export.json
Download:
    https://reece.sh/exports/<name>_export.json.xz
Decompress
    xz -d appd_export.json.xz
'''

# v46 genesis - https://github.com/notional-labs/craft/blob/master/networks/craft-testnet-1/genesis.json
# app_state.distribution.delegator_starting_infos


sections = {
    "staked_amounts": "app_state.staking.delegations",
    "account_balances": "app_state.bank.balances",
}

# Every section must have .item for the json stream parse
for key in sections:
    if sections[key].endswith('.item') == False:
        sections[key] += '.item'

def main():
    files = {
        "craft": "exports/craft_export.json",
        "osmosis": "exports/osmosis_export.json",
        "akash": "exports/akash_export.json",
        "cosmos": "exports/cosmos_export.json",
        "juno": "exports/juno_export.json",
    }

    output = {
        "craft": "output/craft_staking_values.txt",
        "osmosis": "output/osmosis_staking_values.txt",
        "akash": "output/akash_staking_values.txt",
        "cosmos": "output/cosmos_staking_values.txt",
        "juno": "output/juno_staking_values.txt",
    }
    
    # Downloads files to exports dir if not already there
    # for file in getExportsOnWebsiteIndex():
    #     downloadAndDecompressXZFileFromServer(fileName=file)


    # save_staked_amounts(files['craft'], output['craft'])
    # save_staked_amounts(files['osmosis'], output['osmosis'])
    # save_staked_amounts(files['juno'], output['juno'])


    # Saves an export & all account balances INCLUDING ibc/ tokens if you so choose
    # save_balances(files['osmosis'], 'output/osmosis_balances.json', ignoreNonNativeIBCDenoms=True, ignoreEmptyAccounts=True)
    fairdrop_for_osmosis_pools()




# Move these into their own src files
def getExportsOnWebsiteIndex(link="https://reece.sh/exports/index.html", extensions="(.*xz)") -> list:
    '''
    Returns a list of all .xz files on a website (by default).
    This index.html was generated with the following command on the server:
        apt install tree; tree -H '.' -L 1 --noreport --charset utf-8 -P "*.xz" -o index.html 
    '''
    html = requests.get(link).text
    files = re.findall(f'href="{extensions}"', html)
    return list(x for x in (files))

def downloadAndDecompressXZFileFromServer(baseLink="https://reece.sh/exports", fileName="app_export.json.xz", debug=False):
    # checks if app_export.json.xz exists OR app_export.json, if so skip
    if os.path.exists(f"exports/{fileName}") or os.path.exists(f"exports/{fileName.replace('.xz', '')}"):
        if debug: 
            print(f"{fileName} already exists, skipping")
        return

    os.chdir("exports")
    with open(fileName, 'wb') as f:
        response = requests.get(baseLink + "/" + fileName)
        f.write(response.content)
    print(f"Downloaded {fileName}. Decompressing....")

    # decompress the xz file
    os.system(f"xz -d {fileName}")
    print(f"Decompressed {fileName}")
    os.chdir("..")

def stream_section(fn, key):
    if key not in sections:
        print(f"{key} not in sections")
        return

    key = sections[key]

    with open(fn, 'rb') as input_file:
        parser = ijson.items(input_file, key)
        for idx, obj in enumerate(parser):
            yield idx, obj

def save_staked_amounts(input_file, output_file, excludeCentralExchanges=True):
    output = ""
    # totalAccounts = 0
    for idx, obj in stream_section(input_file, 'staked_amounts'):
        delegator = str(obj['delegator_address'])
        valaddr = str(obj['validator_address'])
        stake = str(obj['shares'])        

        # totalAccounts += 1
        if idx % 10_000 == 0:
            print(f"{idx} accounts processing...")

        if excludeCentralExchanges == True and valaddr in utils.BLACKLISTED_CENTRAL_EXCHANGES:
            # print(f"Skipping {delegator} because they are on a central exchange holder {valaddr}")
            continue

        bonus = 1.0 # no bonus by default for now. Look back at notes for how to implement properly
        if valaddr in utils.GENESIS_VALIDATORS.keys():
            bonus = utils.GENESIS_VALIDATORS[valaddr] # 'akashvaloper1lxh0u07haj646pt9e0l2l4qc3d8htfx5kk698d': 1.2,
    
        if bonus > 1.0:
            print(f"{delegator} got a bonus of {bonus}x for delegating to genesis validator {valaddr}")

        output += f"{delegator} {valaddr} {float(stake)}\n"

    print(f"{idx} accounts processed from {input_file}")
    with open(output_file, 'w') as o:
        o.write(output)


def save_balances(input_file, output_file, ignoreNonNativeIBCDenoms=True, ignoreEmptyAccounts=True):
        accounts = {}
        for idx, obj in stream_section(input_file, 'account_balances'):
            address = str(obj['address'])
            coins = obj['coins']

            outputCoins = {}
            for coin in coins:
                denom = coin['denom']
                amount = coin['amount']

                if ignoreNonNativeIBCDenoms and str(denom).startswith('ibc/'):
                    continue # ignore any non native ibc tokens held by the account

                outputCoins[denom] = amount # {'uion': 1000000, 'uosmo': 1000000}

            if idx % 10_000 == 0:
                print(f"{idx} accounts processed")

            if ignoreEmptyAccounts and len(outputCoins) == 0:
                continue

            # print(f"{address} {outputCoins}")
            # output += f"{address} {outputCoins}\n"
            accounts[address] = outputCoins
            
        print(f"{idx} accounts processed from {input_file}")
        with open(output_file, 'w') as o:
            o.write(json.dumps(accounts))
        

craft_airdrop_amounts = {}
def add_airdrop_to_account(craft_address, amount):
    global craft_airdrop_amounts
    if craft_address not in craft_airdrop_amounts:
        craft_airdrop_amounts[craft_address] = 0
    craft_airdrop_amounts[craft_address] += amount
    pass

def fairdrop_for_osmosis_pools():
    '''Group #2 - LPs for pool #1 and #561 (luna/osmo)'''
    # TODO: POOL #1 & #561 (luna/osmo) - not done
    
    filePath = "output/osmosis_balances.json"
    # Ensure output/osmosis_balances.json exists
    if not os.path.exists(filePath):
        print(f"{filePath} does not exist, exiting")
        print("Be sure it is not commented out in main() & you ran it at least once")
        return

    # Load the balances file
    with open(f"{filePath}", 'r') as f:
        osmosis_balances = json.loads(f.read())

    poolHolders = {}
    totalSupply = {"gamm/pool/1": 0, "gamm/pool/561": 0}

    for acc in osmosis_balances:
        address = acc
        coins = osmosis_balances[acc]
        # print(address, coins)

        for denom in coins:
            amount = coins[denom]
            # print(f"{address} has {amount} {denom}") # shows all balances

            if denom in ["gamm/pool/561", "gamm/pool/1"]: # atom/osmo, luna/osmo
                if address not in poolHolders:
                    pools = {"gamm/pool/1": 0, "gamm/pool/561": 0}
                    poolHolders[address] = pools

                poolHolders[address][denom] = amount
                totalSupply[denom] += int(amount) # add to total supply for stats
                # print(poolHolders)

    # save poolHolders to a pool.json file in the output directory
    with open("output/pool.json", 'w') as o:
        o.write(json.dumps(poolHolders))

    print(f"LPs\nLength of poolHolders: {len(poolHolders)}")
    print(f"Total supply: {totalSupply}")


            

                
    




def DEBUG_get_keys(fn, stopLoopIter=10_000):
    '''
    Gets all json keys from a file up to a select height (useful if the file is large like osmosis)
    You can also just look at the geneisis file to get the keys
    '''
    with open(fn, 'rb') as input_file:
        parser = ijson.parse(input_file)
        foundParents = []
        foundDataTypes = {}
        loops = 0
        for parent, data_type, value in parser:
            # print('parent={}, data_type={}, value={}'.format(parent, data_type, value))
            if parent not in foundParents:
                foundParents.append(parent)
            loops+=1

            if loops >= stopLoopIter:
                break
        print(f"{foundParents}=")
        print(f"{foundDataTypes}=")



if __name__ == "__main__":
    main()