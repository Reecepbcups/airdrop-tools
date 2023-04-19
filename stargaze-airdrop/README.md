# Stargaze NFT Airdrop

This airdrops some collection of values to addresses as requested.

## Steps

```bash
# Download the SG721 contract from mainnet (for testnet upload)
# starsd q wasm code 41 sg721.wasm --node https://stargaze-rpc.polkachu.com:443
# mv sg721.wasm stargaze-airdrop/sg721.wasm
# # upload & get the code id
# # starsd keys add test-user --recover
# starsd tx wasm store ./stargaze-airdrop/sg721.wasm --from reece --gas-prices 0.025ustars --gas-adjustment 1.7 --gas auto
# # get the id
# starsd q tx 5BF8989EF430CEFC526D8C3C74BFF015FC2D278DB9F5CC6F976695992E85D11F

# SG1 Code ID on testnet  (https://docs.stargaze.zone/developers/contract-code-ids)
# this is V1, not sure why V2 is not authorized? weird
CODE_ID=271

# https://github.com/public-awesome/launchpad/blob/main/packages/sg721/src/lib.rs#L105
starsd tx wasm instantiate $CODE_ID '{"name":"Reeces NFT Collection","symbol":"TABTEST","minter":"stars1jx8zl9598dwjwpxf8gyjpjem7r2k44vmsfut4a","collection_info":{"creator":"stars1jx8zl9598dwjwpxf8gyjpjem7r2k44vmsfut4a","description":"ye","image":"https://baseImage.com"}}' --label "Rtest" --admin stars1jx8zl9598dwjwpxf8gyjpjem7r2k44vmsfut4a --from test-user --yes --node https://rpc.elgafar-1.stargaze-apis.com:443 --amount 3000000000ustars

CONTRACT_ADDRESS=stars1xhfg8m92r3ewe0v0mlf80m39vluzdqjwmy2xvt2v0j03c9trt5ls3neq77

# Queries & Txs
# `owner_of`, `approval`, `approvals`, `all_operators`, `num_tokens`, `contract_info`, `nft_info`, `all_nft_info`, `tokens`, `all_tokens`, `minter`
# https://github.com/public-awesome/launchpad/blob/main/packages/sg721/src/lib.rs#L7
```
