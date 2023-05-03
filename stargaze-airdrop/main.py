import base64
import json
import os
import random as r
import time

import httpx

"""
# How to sign & broadcast via CLI after running this script
rm airdrop_to_users_*.json
rm signed_airdrop.json
starsd tx sign airdrop_to_users_*.json --from tabu-testnet --chain-id=elgafar-1 &> signed_airdrop.json

starsd tx broadcast signed_airdrop.json --node https://rpc.elgafar-1.stargaze-apis.com:443
"""

# Gas for the messages, (stargaze has -1 so put any amount here)
GAS = "2000000"

REST_API_NODE = "https://rest.elgafar-1.stargaze-apis.com"
# REST_API_NODE = "https://stargaze-api.polkachu.com" # mainnet

# Wallet which owns the NFTs from the 1/1 collection
MASTER_WALLET = "stars160a6rd8hm9ydt86enhf48f2x2260wq0qfkq35p"
# the 1/1 collection (SG721 from stargaze studio mint)
ADDR721 = "stars1y9g9qs40p6gksd29fm08j3jpy0cnvx0zg0987cq8s8c4lezexwpsys256j"
# How many NFTs to randomly mint to them
nfts_to_give = 1
# list of wallets which get the airdrop
airdrop_list: list[str] = [
    "stars10r39fueph9fq7a6lgswu4zdsg8t3gxlqcsme8z",
    "stars1q3scuwfpapydfzrkfssxuwccspewlp6sgnel53",
]
COLLECTION_SIZE = 10_000
# Ids to airdrop to users. You can use list_of_ids_from_attributes.py to get a specific attr list, or use a range of ids here
# If you do not own an id in this list, a new random id is chosen.
# If you run out of Ids which you can give in this range, it will error out. (ex: trying to give 50 NFTs but you only own 49)
ids_range: list[int] = list(range(1, 41))

# == LOGIC ==
current_dir = os.path.dirname(os.path.abspath(__file__))
if str(REST_API_NODE).endswith("/"):
    REST_API_NODE = REST_API_NODE[:-1]


def main():
    airdropNFTs()


def encode_base64(string: str) -> str:
    return base64.b64encode(string.encode()).decode()


def get_master_wallet_holdings():
    value = '{"tokens":{"owner":"ADDRESS","start_after":"1","limit":COLLECTION_SIZE}}'.replace(
        "ADDRESS", MASTER_WALLET
    ).replace(
        "COLLECTION_SIZE", str(COLLECTION_SIZE)
    )

    headers = {
        "accept": "application/json",
    }

    query = encode_base64(value).replace("=", "%3D")
    url = f"""{REST_API_NODE}/cosmwasm/wasm/v1/contract/{ADDR721}/smart/{query}"""
    res = httpx.get(
        url,
        timeout=60,
        headers=headers,
    ).json()

    v = res["data"]["tokens"]
    return [int(x) for x in list(sorted(v, key=lambda x: int(x)))]


holdings = get_master_wallet_holdings()


def get_random_nft_id_in_holdings(_counter=0) -> int:
    # get a random id in ids_range, if not in holdings, try again
    v = r.choice(ids_range)
    if _counter >= 250:
        print(
            "Error: No more NFTs to airdrop in this range based off our master wallet holdings"
        )
        print(f"{ids_range=}")
        print(f"{holdings=}")
        exit(1)

    if v not in holdings:
        return get_random_nft_id_in_holdings(_counter + 1)

    # remove v from holdings & ids_range
    holdings.remove(v)
    ids_range.remove(v)
    return v


def airdropNFTs():
    global ids_range

    # This is what we will sign
    current_time = time.strftime("%H-%M-%S")
    fileName = f"airdrop_{current_time}.json"

    msgFmt = {
        "body": {
            "messages": [],
            "memo": f"{fileName}",
            "timeout_height": "0",
            "extension_options": [],
            "non_critical_extension_options": [],
        },
        "auth_info": {
            "signer_infos": [],
            "fee": {"amount": [], "gas_limit": f"{GAS}", "payer": "", "granter": ""},
        },
        "signatures": [],
    }

    for addr in list(airdrop_list):
        # Give multiple NFTs to users if desired.
        for i in range(nfts_to_give + 1):
            randomId = get_random_nft_id_in_holdings()

            msgFmt["body"]["messages"].append(
                {
                    "@type": "/cosmwasm.wasm.v1.MsgExecuteContract",
                    "sender": f"{MASTER_WALLET}",  # wallet who can mint, holder of all NFts which were minted via the stargaze studio created 1/1 collection
                    "contract": f"{ADDR721}",
                    "msg": {
                        "transfer_nft": {
                            "recipient": f"{addr}",
                            "token_id": f"{randomId}",
                        }
                    },
                    "funds": [],
                }
            )

    # save msgFmt to file
    with open(os.path.join(current_dir, f"{fileName}"), "w") as sendF:
        sendF.write(json.dumps(msgFmt, indent=4))

    print(f"You can now airdrop. {fileName}.")


if __name__ == "__main__":
    main()
