'''
Reece Williams | Oct 31st 2022

Example script on how to read the genesis data from the state export
'''

import json, os, bech32 # pip install bech32

current_dir = os.path.dirname(os.path.realpath(__file__))
FOLDER = 'genesis_sorted'

# Snapshot Data
SNAPSHOT_CHAIN_PREFIX = 'juno'
SNAPSHOT_CHAIN_TOKEN = 'ujuno'
SNAPSHOT_IGNORED_VALIDATORS = {
    "junovaloper1t8ehvswxjfn3ejzkjtntcyrqwvmvuknzmvtaaa": "Cosmostation", # example
}

# new Chain Logic
SNAPSHOT_IGNORE_CONTRACTS = True
SNAPSHOT_BALANCE_MINIMUM = 10 * (10**6) # 10juno
SNAPSHOT_STAKING_MINIMUM = 10 * (10**6) # 10 JUNO STAKED

NEW_CHAIN_PREFIX = 'eve' # ex: if snapshot is from cosmos, we want to convert to 'eve1xxxxxx' address. Only 118 cointypes
NEW_CHAIN_TOKEN = 'ueve'

GENESIS_CMD_FORMAT = 'eved add-genesis-account ADDR COIN --append'

airdrop_amounts = {} # 'addr': uamount

def main():
    global airdrop_amounts

    # if SNAPSHOT_IGNORE_CONTRACTS=True, we ignore any addresses which are longer than 39+len(SNAPSHOT_CHAIN_PREFIX)
    balance_airdrop()
    save_commands_to_file('balance_commands.sh')    
    
    staking_airdrop()
    save_commands_to_file('staking_commands.sh')

def balance_airdrop():
    global airdrop_amounts
    print("Resetting Airdrop Amounts...")
    airdrop_amounts = {} # reset it
    print("Reading Genesis Account balances...")
    balances = json.load(open(os.path.join(current_dir, FOLDER, 'genesis_bank.json'), 'r'))['balances']

    # loop through bank
    for account in balances: # {'address': 'cosoms1...', 'coins': [{'amount': '1000000', 'denom': 'utoken'}]}
        addr = account['address']

        if SNAPSHOT_IGNORE_CONTRACTS and len(addr) > 39+len(SNAPSHOT_CHAIN_PREFIX):
            continue # normal public key = length of 39. So prefix+39 = 44. Contracts are longer

        coins = account['coins']
        for coin in coins:
            if coin['denom'] == SNAPSHOT_CHAIN_TOKEN:
                snapshot_amt = coin['amount']
                if int(snapshot_amt) < SNAPSHOT_BALANCE_MINIMUM:
                    continue

                # save as the new address
                _, data = bech32decode(addr)
                new_addr = bech32encode(NEW_CHAIN_PREFIX, data)
                airdrop_amounts[new_addr] = snapshot_amt


def staking_airdrop(): # {'delegator_address': 'cosoms1...', 'shares': '11458136.000000000000000000', 'validator_address': 'cosmosvaloper1xxxx'}
    global airdrop_amounts
    print("Resetting Airdrop Amounts...")
    airdrop_amounts = {} # reset it
    print("Reading Genesis Account staked amounts...")
    
    staking = json.load(open(os.path.join(current_dir, FOLDER, 'genesis_staking.json'), 'r'))['delegations']

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

        if shares < SNAPSHOT_STAKING_MINIMUM: continue

        if new_addr in airdrop_amounts.keys():
            airdrop_amounts[new_addr] = int(shares) + int(airdrop_amounts[new_addr])
        else:
            airdrop_amounts[new_addr] = int(shares)



def save_commands_to_file(filename='commands.sh'):
    with open(os.path.join(current_dir, filename), 'w') as f:
        output = []
        for addr, amount in airdrop_amounts.items():        
            s = GENESIS_CMD_FORMAT.replace('ADDR', addr).replace('COIN', f'{amount}{NEW_CHAIN_TOKEN}')
            output.append(s)
        f.write('\n'.join(output))


# ==================
def bech32encode(prefix, data):    
    return bech32.bech32_encode(prefix, bech32.convertbits(data, 8, 5, True))

def bech32decode(address):
    prefix, data = bech32.bech32_decode(address)        
    return prefix, bech32.convertbits(data, 5, 8, False)

if __name__ == '__main__':
    # hrp, converted = bech32decode('cosmos10r39fueph9fq7a6lgswu4zdsg8t3gxlqvvvyvn')
    # print(hrp, converted)
    # print(bech32encode('osmo', converted))
    
    main()