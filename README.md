# cosmos airdrop tools

This repo houses many tools to quickly airdrop in a variety of ways to other addresses.

## Prerequisites

Please ensure you install the requirements from the requirements.txt file before continuing.

```bash
python3 -m pip install -r requirements.txt
```

---

## How To Export a Snapshot

[EXPORT-GUIDE](./HOW-TO-EXPORT.md)

or use my free tool

[https://snapshots.reece.sh/](https://snapshots.reece.sh/)

---

## Tools in this repo

- [Automatic CosmWasm NFT Snapshots (stargaze)](https://github.com/Reecepbcups/stargaze-nft-snapshots)
- [State Export Sort](./export-sort/)
- [Airdrop from CHAIN-A to NEW-CHAIN w/ formulas & excluded validators (for both bank & staking)](./native-airdrop/)
- [CW20 balances to CSV](./cw20/to-other-cw20/)
- [CW20 balances to new chain](./cw20/to-native-denom/)

### Other

- [SoftSlash repayment from export](https://github.com/Reecepbcups/chandra-station-canto-repayment-script)
- [CW20 Merkle Airdrop](https://github.com/CosmWasm/cw-tokens/tree/main/contracts/cw20-merkle-airdrop)
- [CW20 to new TokenFactory Contracts](https://github.com/Reecepbcups/cw20-to-tokenfactory)
