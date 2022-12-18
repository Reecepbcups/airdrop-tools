'''
Reece Williams | Oct 31st 2022

Example script on how to read the genesis data from the state export
'''

import json, os

from utils import bech32encode, bech32decode

from dotenv import load_dotenv
load_dotenv()  

current_dir = os.path.dirname(os.path.realpath(__file__))

SNAPSHOT_SORTED_FOLDER = os.getenv('SNAPSHOT_SORTED_FOLDER', 'juno_sorted')
sorted_dir = os.path.join(os.path.dirname(current_dir), "_SORTED", SNAPSHOT_SORTED_FOLDER)
commands_dir = os.path.join(os.path.dirname(current_dir), "_AIRDROP_COMMANDS")
os.makedirs(sorted_dir, exist_ok=True)
os.makedirs(commands_dir, exist_ok=True)

SNAPSHOT_CHAIN_PREFIX = os.getenv('SNAPSHOT_CHAIN_PREFIX', "juno")
SNAPSHOT_CHAIN_TOKEN = os.getenv('SNAPSHOT_CHAIN_TOKEN', "ujuno")

# Cosmostation:junovaloper1t8ehvswxjfn3ejzkjtntcyrqwvmvuknzmvtaaa,
SNAPSHOT_IGNORED_VALIDATORS = os.getenv('SNAPSHOT_IGNORED_VALIDATORS', None)

if SNAPSHOT_IGNORED_VALIDATORS is not None:
    temp = {}
    for x in SNAPSHOT_IGNORED_VALIDATORS.split(','):
        s = x.split(':')
        if len(s) != 2:
            continue
        name, valoper = s
        temp[valoper] = name
    SNAPSHOT_IGNORED_VALIDATORS = temp # {'junovaloper1t8ehvswxjfn3ejzkjtntcyrqwvmvuknzmvtaaa': 'Cosmostation'}

# New Chain Airdrop logic
SNAPSHOT_IGNORE_CONTRACTS = os.getenv('SNAPSHOT_IGNORE_CONTRACTS', 'false').lower().startswith('t')
SNAPSHOT_BALANCE_MINIMUM = int(os.getenv('SNAPSHOT_BALANCE_MINIMUM', '0'))
SNAPSHOT_STAKING_MINIMUM = int(os.getenv('SNAPSHOT_BALANCE_MINIMUM', '0')) 

NEW_CHAIN_PREFIX = os.getenv('NEW_CHAIN_PREFIX', 'cosmos')
NEW_CHAIN_TOKEN = os.getenv('NEW_CHAIN_TOKEN', 'uatom')

NEW_CHAIN_FORMULA_BALANCES = os.getenv('NEW_CHAIN_FORMULA_BALANCES', 'AMT')
NEW_CHAIN_FORMULA_STAKING = os.getenv('NEW_CHAIN_FORMULA_STAKING', 'AMT')

GENESIS_CMD_FORMAT = os.getenv('NEW_CHAIN_CMD_FORMAT', 'eved add-genesis-account ADDR COIN --append')

airdrop_amounts = {} # 'addr': uamount

def main():
    global airdrop_amounts

    # if SNAPSHOT_IGNORE_CONTRACTS=True, we ignore any addresses which are longer than 39+len(SNAPSHOT_CHAIN_PREFIX)
    title = f'{SNAPSHOT_CHAIN_PREFIX}_to_{NEW_CHAIN_PREFIX}'
    balance_airdrop()
    save_commands_to_file(f'{title}_balances.sh')
    balances_airdroped = len(airdrop_amounts)
    
    staking_airdrop()
    save_commands_to_file(f'{title}_staking.sh')
    stakers_airdroped = len(airdrop_amounts)
    
    print(f"\nTotal of {balances_airdroped:,} bank balances and {stakers_airdroped:,} stakers airdropped to {NEW_CHAIN_PREFIX}!")
    print(f"Commands saved to '{commands_dir}'")

def balance_airdrop():
    global airdrop_amounts    
    airdrop_amounts = {}
    print(f"Reading {SNAPSHOT_CHAIN_PREFIX} balance amounts...")

    bankJSON = os.path.join(sorted_dir, f'{SNAPSHOT_CHAIN_PREFIX}_bank.json')

    if not os.path.exists(bankJSON):
        print(f"\tERROR: '{SNAPSHOT_CHAIN_PREFIX}_bank.json' is not found, so no balances to airdrop too. If this is a mistake ensure you ran sorter.py...")
        print(f"\tand that .env has SNAPSHOT_WANTED_SECTIONS=\"bank\"\n")
        return

    balances = json.load(open(bankJSON, 'r'))['balances']

    # loop through bank
    for account in balances: # {'address': 'cosoms1...', 'coins': [{'amount': '1000000', 'denom': 'utoken'}]}
        addr = account['address']

        if SNAPSHOT_IGNORE_CONTRACTS and len(addr) > 39+len(SNAPSHOT_CHAIN_PREFIX):
            continue # normal public key = length of 39. So prefix+39 = 44. Contracts are longer

        coins = account['coins']
        for coin in coins:
            if coin['denom'] == SNAPSHOT_CHAIN_TOKEN:
                amt = coin['amount']
                if int(amt) < SNAPSHOT_BALANCE_MINIMUM:
                    continue

                # save as the new address
                _, data = bech32decode(addr)
                new_addr = bech32encode(NEW_CHAIN_PREFIX, data)
                
                updated_amt = int(eval(NEW_CHAIN_FORMULA_BALANCES.replace('AMT', str(amt))))
                airdrop_amounts[new_addr] = updated_amt


def staking_airdrop(): 
    # {'delegator_address': 'cosoms1...', 'shares': '11458136.000000000000000000', 'validator_address': 'cosmosvaloper1xxxx'}
    global airdrop_amounts    
    airdrop_amounts = {}
    print(f"Reading {SNAPSHOT_CHAIN_PREFIX} staked amounts...")
    
    stakingJSON = os.path.join(sorted_dir, f'{SNAPSHOT_CHAIN_PREFIX}_staking.json')
    if not os.path.exists(stakingJSON):
        print(f"\tERROR: '{SNAPSHOT_CHAIN_PREFIX}_staking.json' is not found, so no stakers to airdrop too. If this is a mistake ensure you ran sorter.py...")
        print(f"\tand that .env has SNAPSHOT_WANTED_SECTIONS=\"staking\"\n")
        return

    staking = json.load(open(stakingJSON, 'r'))['delegations']

    for staker in staking:
        addr = staker['delegator_address']
        shares = staker['shares']
        validator = staker['validator_address']
        if SNAPSHOT_IGNORE_CONTRACTS and len(addr) > 39+len(SNAPSHOT_CHAIN_PREFIX):
            continue

        if validator in SNAPSHOT_IGNORED_VALIDATORS.keys():
            continue

        # save as the new address
        _, data = bech32decode(addr)
        new_addr = bech32encode(NEW_CHAIN_PREFIX, data)

        # LOGIC HERE
        # round shares up to 0 decimal places
        shares = int(float(shares))
        if shares == 0: continue

        if shares < SNAPSHOT_STAKING_MINIMUM: 
            continue

        updated_shares = int(eval(NEW_CHAIN_FORMULA_STAKING.replace('AMT', str(shares))))

        if new_addr not in airdrop_amounts.keys():
            airdrop_amounts[new_addr] = 0

        airdrop_amounts[new_addr] = int(airdrop_amounts[new_addr]) + int(updated_shares)

# ====================
def save_commands_to_file(filename='commands.sh'):
    if len(airdrop_amounts) == 0:
        # print("No airdrop amounts to save!")
        return

    with open(os.path.join(commands_dir, filename), 'w') as f:
        output = []
        for addr, amount in airdrop_amounts.items():                      
            s = GENESIS_CMD_FORMAT.replace('ADDR', addr).replace('COIN', f'{amount}{NEW_CHAIN_TOKEN}')            
            output.append(s)
        f.write('\n'.join(output))

def test():
    hrp, converted = bech32decode('cosmos10r39fueph9fq7a6lgswu4zdsg8t3gxlqvvvyvn')
    print(hrp, converted)
    print(bech32encode('osmo', converted))

if __name__ == '__main__':
    # test()
    main()    