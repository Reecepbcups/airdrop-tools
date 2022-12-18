# State Export sorter

Useful for airdrops from one chain to a new one & debugging any network. All handled from the '.env' file

## Guide

```sh
# copy .env.example to .env
cp .env.example .env

# edit .env to your liking

# Run the sorter script (outputs to _SORTED).
# If you plan to airdrop, ensure you have `SNAPSHOT_WANTED_SECTIONS="bank,staking"` in your .env
python3 sorter.py
```
