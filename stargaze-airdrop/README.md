# Stargaze NFT Airdrop

This airdrops some collection of values to addresses as requested.

## Steps

- Run fix_json_values.json to format names, description, and fix any attribute errors

- Create a 1/1 collection on testnet or mainnet to a single wallet.
  - mainnet: <https://studio.stargaze.zone/>
  - testnet: <https://studio.publicawesome.dev/>

- Get a list of stargaze addresses. If you have another address (ex: juno, osmo, or cosoms) you can convert with: <https://bech32.scrtlabs.com/>.

- Edit the main.py file to include all the data for your collection, setting the ids range to your range you want to airdrop to holders.
  - If you want to airdrop specific attributes to these wallets, use `list_of_ids_from_attributes.py` to get these ids, and copy-paste in `main.py`.