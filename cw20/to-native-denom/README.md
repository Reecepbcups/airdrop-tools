# CW20 -> Native Denom

[old repo - cw20-to-native](https://github.com/Reecepbcups/cw20-to-native)

This tool will allow you to take a CW20 snapshot AND/OR convert a CW20 -> a chain's native denomination via an x/tokenfactory module.
or to a new app chain if you're going down that route

This does **NOT** require a [state export](../../HOW-TO-EXPORT.md) as we grab the information directly from chain via the RPC query.

## TODO

Convert the shell script to python and only require 1 file call.

## Usage

```bash
cp .env.example .env
# edit .env with the data you want for your CW20 convert.

sh script1.sh
# wait for it to save all to CW20s/ folder
# For now only standard CW20s are supported.
# For forked support, contact 
#- Discord: Reece#3307 / Twitter: @Reecepbcups_ 

python3 script2.py

# Done! Double check balance.json looks right and then finally mint the tokens to their addresses
sh factory_mint.sh
```

## Note

You could also update the TOKEN_FACTORY_MINT_COMMAND (.env) to be an `simd add-genesis-account` command as well (If you want to move your CW20 to its own chain).
