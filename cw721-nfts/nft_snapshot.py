"""
Loops over all JSON files in CW20s folder, then converts out the actual balances
"""

import asyncio
import base64
import datetime
import json
import os

import httpx
from httpx import AsyncClient

# from dotenv import load_dotenv
# load_dotenv()


# cosmos.directory for Stargaze. This query is VERY taxing on the node, so be careful. Use your own node if you have it (non rate limited)
REST_API_NODE = "https://stargaze-api.polkachu.com"

# Adora NFTs
CONTRACT_ADDRESS = "stars1uj5wruqnez8klwxp88e5m6vt7n5wpa7qu6983pv43rsy78wzmuyqp826mg"

# Token IDs
START_IDX = 1
END_IDX = 1_000


current_dir = os.path.dirname(os.path.realpath(__file__))
NFTs = os.path.join(current_dir, "SNAPSHOTS")
os.makedirs(NFTs, exist_ok=True)

## == HELPERS ==
headers = {
    "accept": "application/json",
}


def encode_base64(string: str) -> str:
    return base64.b64encode(string.encode()).decode()


def get_contract_info(contract_addr: str) -> dict:
    url = f"""{REST_API_NODE}/cosmwasm/wasm/v1/contract/{contract_addr}"""
    response = httpx.get(url, headers=headers)
    return response.json()


def get_url(contract_addr, idx) -> str:
    value = '{"owner_of":{"token_id":"TOKEN"}}'.replace("TOKEN", str(idx))
    query = encode_base64(value).replace("=", "%3D")
    url = f"""{REST_API_NODE}/cosmwasm/wasm/v1/contract/{contract_addr}/smart/{query}"""
    return url


def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# == MAIN LOGIC ==
async def fetch_data(
    client: AsyncClient, url: str, key: str, results: dict, errors: dict
):
    # async with httpx.AsyncClient() as client:
    print(f"Fetching {key} from {url}")

    response = await client.get(url)

    if response.status_code == 200:
        results[key] = response.json()

    else:
        # TODO: Add a check which goes through every 100-1 to see if the NFT exists on start? Then lower END_IDX automatically
        print(
            f"Error fetching {key}: {response.status_code} status. This NFT may not exist. Possibly lower your END_IDX from {END_IDX}"
        )
        errors[key] = response.text


async def async_holders():
    results = {}
    errors: dict[int, str] = {}

    urls = {}
    for i in range(START_IDX, END_IDX + 1):
        urls[i] = get_url(CONTRACT_ADDRESS, i)

    async with AsyncClient(timeout=30.0) as client:
        tasks = [
            fetch_data(client, url, key, results, errors) for key, url in urls.items()
        ]
        await asyncio.gather(*tasks)

    # Save holders to file in an easier to digest format
    holders: dict[str, list[int]] = {}

    for k, v in results.items():
        owner = v.get("data", {}).get("owner", None)
        if owner is None:
            continue

        if owner not in holders:
            holders[owner] = []

        holders[owner].append(k)

    # get parent contract info
    info = get_contract_info(CONTRACT_ADDRESS)

    #  save holders to a file
    with open(
        os.path.join(NFTs, f"{CONTRACT_ADDRESS}_{START_IDX}-{END_IDX}.json"), "w"
    ) as f:
        print("Saving results to file")
        json.dump(
            {
                "contract": {
                    "address": CONTRACT_ADDRESS,
                    "name": info.get("contract_info", {}).get("label", None),
                    "code_id": info.get("contract_info", {}).get("code_id", None),
                },
                "time": get_current_time(),
                "range": {"start": START_IDX, "end": END_IDX},
                "holders": holders,
            },
            f,
            indent=4,
        )


if __name__ == "__main__":
    asyncio.run(async_holders())
