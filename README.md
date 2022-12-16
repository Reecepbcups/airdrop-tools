# cosmos airdrop tools

This repo houses many tools to quickly airdrop in a variety of ways to other addresses.

## Prerequisites

Please ensure you install the requirements from the requirements.txt file before continuing.

```bash
python3 -m pip install -r requirements.txt
```

## How To Export a Snapshot

[EXPORT-GUIDE](./HOW-TO-EXPORT.md)

## Tools in this repo

- state export sorter (extract more manageable files)
- Get all CW20 balances
- Osmosis LP Airdrop (TODO)

- Fairdrop (same amount to a subset of accounts)
- Formula Drop (airdrop based on conditions, ex: minimum of X staked, not to CeXs, etc.)

### Other

- [SoftSlash repayment from export](https://github.com/Reecepbcups/chandra-station-canto-repayment-script)
- [CW20 Merkle Airdrop](https://github.com/CosmWasm/cw-tokens/tree/main/contracts/cw20-merkle-airdrop)
- [CW20 to new TokenFactory Contracts](https://github.com/Reecepbcups/cw20-to-tokenfactory)
