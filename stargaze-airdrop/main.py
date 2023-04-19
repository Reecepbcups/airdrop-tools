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
# {BINARY}_REST = "https://craft-rest.crafteconomy.io"
GAS_LIMIT = 10_000_000

# Links to the images, use IPFS ERC721 / OPensea supported metadata format here
links = [
    "https://pbs.twimg.com/profile_images/1641181817976901636/9SPaHVIi_400x400.jpg",
    "https://pbs.twimg.com/profile_banners/1633958116193882112/1678897381/1500x500",
]

BINARY = "starsd"

# the wallet which gets all of the NFTs minted to them
FROM_ACCOUNT_NAME = "test-user"  # keyring os
MAIN_WALLET = "stars1jx8zl9598dwjwpxf8gyjpjem7r2k44vmsfut4a"

# Stargaze wallet address
# https://studio.publicawesome.dev/contracts/sg721/?contractAddress=stars1xhfg8m92r3ewe0v0mlf80m39vluzdqjwmy2xvt2v0j03c9trt5ls3neq77
CONTRACT_ADDRESS = "stars1xhfg8m92r3ewe0v0mlf80m39vluzdqjwmy2xvt2v0j03c9trt5ls3neq77"

current_dir = os.path.dirname(os.path.abspath(__file__))


def main():
    part1_mintToAdminAccount()
    # part2_sendToMarketplace() # send to select holders function? To map specific Ids to wallets from airdrop / employees


def _saveToFile(msgFmt, filename):
    p = os.path.join(current_dir, "mint_nfts")
    os.makedirs(p, exist_ok=True)
    with open(os.path.join(p, filename), "w") as f:
        json.dump(msgFmt, f, indent=4)


def part1_mintToAdminAccount():
    msgFmt = {
        "body": {
            "messages": [],
            "memo": "",
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
        },
        "signatures": [],
    }
    for idx, link in enumerate(links, START_IDX):
        # https://studio.stargaze.zone/contracts/sg721/execute/
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
                        "extension": {},  # TODO: Metadata here? or?
                    }
                },
                "funds": [],
            }
        )

    _saveToFile(msgFmt, "mint_images.json")


def airdrop_ids():
    # For a one off send, you can just use https://studio.publicawesome.dev/contracts/sg721/execute/ -> Send NFT

    # TODO:
    # - open a airdrop.csv file. Foramt: stargaze_addr,nft_id
    # iterate through all values, and ensure the main wallet owns all of these NFTs. If not, error.
    # generate messages to send to each user wallet
    # sign and generate done woo
    pass


def get_chain_id():
    res = os.popen(f"{BINARY} config chain-id").read().strip()
    return res


if __name__ == "__main__":
    main()

    print("\n\nEnsure you are in the images folder\n")
    print(
        f"{BINARY} tx sign mint_images.json --from {FROM_ACCOUNT_NAME} --chain-id={get_chain_id()} &> signed_mint_images.json"
    )
    # print(
    #     f"{BINARY} tx sign images_to_marketplace.json --from {FROM_ACCOUNT_NAME} &> signed_images_marketplace.json"
    # )
    print(f"{BINARY} tx broadcast signed_mint_images.json")
    # print(f"{BINARY} tx broadcast signed_images_marketplace.json")

    # then we can query
    # starsd q wasm contract-state smart stars1xhfg8m92r3ewe0v0mlf80m39vluzdqjwmy2xvt2v0j03c9trt5ls3neq77 '{"nft_info":{"token_id":"1"}}'
