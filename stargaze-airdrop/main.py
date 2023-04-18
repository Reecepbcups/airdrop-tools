# Original From
# https://github.com/Reecepbcups/craft/blob/master/nft-cw/scripts/src/Mint_Images.py

"""
This script mints an entire collection to a set wallet.


Testnet:
- https://docs.stargaze.zone/developers/testnet
- https://rpc.elgafar-1.stargaze-apis.com:443


"""

import sys

sys.dont_write_bytecode = True
import json
import os

import requests

# from dotenv import load_dotenv
# load_dotenv()


START_IDX = 1  # put at 1 for mainnet mint
# addresses = requests.get("https://api.crafteconomy.io/v1/nfts/get_contract_addresses").json()
# ADDR721 = addresses['ADDR721_REALESTATE']
# ADDR721IMAGES = addresses['ADDR721_IMAGES']
# ADDRM = addresses['MARKETPLACE']
# DAO_MULTISIG = "craft1n3a53mz55yfsa2t4wvdx3jycjkarpgkf07zwk7" # dao account for now. They should be the one who inited the 721 contract (DAO)
# CRAFTD_REST = "https://craft-rest.crafteconomy.io"
GAS_LIMIT = 10_000_000

# Links to the images, use IPFS
links = [
    "https://ipfs.io/ipfs/QmNLoezbXkk37m1DX5iYADRwpqvZ3yfu5UjMG6sndu1AaQ",
    "https://ipfs.io/ipfs/QmNLjZSFV3GUMcusj8keEqVtToEE3ceTSguNom7e4S6pbJ",
    "https://ipfs.io/ipfs/QmNLijobERK4VhSDZdKjt5SrezdRM6k813qcSHd68f3Mqg",
    "https://i.imgur.com/sqmreSn.png",
]

# the wallet which gets all of the NFTs minted to them
MAIN_WALLET = "stars10r39fueph9fq7a6lgswu4zdsg8t3gxlqcsme8z"

# Stargaze wallet address
CONTRACT_ADDRESS = ""

current_dir = os.path.dirname(os.path.abspath(__file__))


def main():
    part1_mintToAdminAccount()
    # part2_sendToMarketplace()


def _saveToFile(msgFmt, filename):
    p = os.path.join(current_dir, "mint_nfts")
    os.makedirs(p, exist_ok=True)
    with open(os.path.join(p, filename), "w") as f:
        json.dump(msgFmt, f, indent=4)


def part1_mintToAdminAccount():
    msgFmt = {
        "body": {
            "messages": [],
            "memo": "minting stargaze images",
            "timeout_height": "0",
            "extension_options": [],
            "non_critical_extension_options": [],
        },
        "auth_info": {
            "signer_infos": [],
            "fee": {
                "amount": [],
                "gas_limit": f"{GAS_LIMIT}",
                "payer": "",
                "granter": "",
            },
            "tip": None,
        },
        "signatures": [],
    }
    for idx, link in enumerate(links, START_IDX):
        msgFmt["body"]["messages"].append(
            {
                "@type": "/cosmwasm.wasm.v1.MsgExecuteContract",
                "sender": f"{MAIN_WALLET}",  # wallet who can mint (DAO multisig)
                "contract": f"{CONTRACT_ADDRESS}",
                "msg": {
                    "mint": {
                        "token_id": f"{idx}",
                        "owner": f"{MAIN_WALLET}",  # dao owns all images it mints
                        "token_uri": f"{link}",
                    }
                },
                "funds": [],
            }
        )

    _saveToFile(msgFmt, "mint_images.json")


if __name__ == "__main__":
    main()
    print("Ensure you are in the images folder")
    print("craftd tx sign mint_images.json --from dao &> signed_mint_images.json")
    print(
        "craftd tx sign images_to_marketplace.json --from dao &> signed_images_marketplace.json"
    )
    print()
    print("craftd tx broadcast signed_mint_images.json")
    print("craftd tx broadcast signed_images_marketplace.json")
