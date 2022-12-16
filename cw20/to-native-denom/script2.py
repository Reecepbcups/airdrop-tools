'''
Loops over all JSON files in CW20s folder, then converts out the actual balances
'''

import os
import json
import base64
import bech32

from dotenv import load_dotenv
load_dotenv()

TOKEN_FACTORY_DENOM = os.getenv("TOKEN_FACTORY_DENOM", "factory/addr/denom")
WALLET_PREFIX = os.getenv("WALLET_PREFIX", "juno")
NEW_WALLET_PREFIX = os.getenv("NEW_WALLET_PREFIX", "juno")
TOKEN_FACTORY_MINT_COMMAND = os.getenv("TOKEN_FACTORY_MINT_COMMAND", "eved tx tokenfactory mint-and-send-tokens {TOKEN_FACTORY_DENOM} {balance} {address} --node {NEW_CHAIN_NODE}")
NEW_CHAIN_NODE = os.getenv("NEW_CHAIN_NODE", "http://localhost:26657")

JUST_SNAPSHOT = os.getenv("JUST_SNAPSHOT", False)


current_dir = os.path.dirname(os.path.realpath(__file__))
CW20s = os.path.join(current_dir, 'CW20s')

def hex_string_to_uft8(hex_string):
    return bytearray.fromhex(hex_string).decode()

def base64_to_uft8(base64_string):
    return base64.b64decode(base64_string).decode()

# public keys
def bech32_encode(hrp, data):    
    converted = bech32.convertbits(data, 8, 5, True)
    return bech32.bech32_encode(hrp, converted)
def bech32_decode(bech):    
    hrp, data = bech32.bech32_decode(bech)
    if data is None:
        return hrp,False
    converted = bech32.convertbits(data, 5, 8, False)
    return hrp,converted
def test_bech32wallet(): # only works for 118 -> 118 cointypes
    hrp, decoded_pubkey = bech32_decode("cosmos10r39fueph9fq7a6lgswu4zdsg8t3gxlqvvvyvn")
    new_wallet = bech32_encode("osmo", decoded_pubkey)    
    assert new_wallet == "osmo10r39fueph9fq7a6lgswu4zdsg8t3gxlqyhl56p"    
test_bech32wallet()

balances = {}
total_balances = 0

for file in os.listdir(CW20s):
    # read the file
    with open(os.path.join(CW20s, file), 'r') as f:
        data = json.load(f)

        # get models key if found
        if 'models' not in data:
            continue

        modules = list(data['models'])

        for m in modules:
            key = hex_string_to_uft8(m['key'])
            if 'balance' not in key:
                break
            
            # TODO: clean this mess up yuck
            # remove balance from the string
            address = str(key.replace('balance', '')) # balancejuno1000xz25ydz8h9rwgnv30l9p0x500dvj0s9yyc9 -> juno1000xz25ydz8h9rwgnv30l9p0x500dvj0s9yyc9
            address = WALLET_PREFIX + key.split(WALLET_PREFIX)[1]
            balance = int(base64_to_uft8(m['value']).replace('"', '')) # TODO: try catch

            # print(f'{address} - {balance}')
            if balance <= 0:
                continue

            balances[address] = balance
            total_balances += balance

# save balances to a file as JSON
with open(os.path.join(current_dir, 'balances.json'), 'w') as f:
    balances = {k: v for k, v in sorted(balances.items(), key=lambda x: x[1], reverse=True)}
    json.dump(balances, f, indent=2)
    print("Balances saved to balances.json. Total Value: {total_balances:.0f}")

if JUST_SNAPSHOT:
    print("Just snapshot per .env file, your file balances.json is done & sorted :)")
    exit()

# loop through balances
output = []
for address, balance in balances.items():
    new_address = bech32_encode(NEW_WALLET_PREFIX, bech32_decode(address)[1]) # bech32 convert requires the pubkey of the old wallet addr + the new prefix 
    output.append(TOKEN_FACTORY_MINT_COMMAND.format(TOKEN_FACTORY_DENOM=TOKEN_FACTORY_DENOM, balance=balance, address=new_address, NEW_CHAIN_NODE=NEW_CHAIN_NODE))

# save to file
script='factory_mint.sh'
with open(os.path.join(current_dir, script), 'w') as f:
    f.write('\n'.join(output))
    print(f"Token Factory commands saved to {script}")