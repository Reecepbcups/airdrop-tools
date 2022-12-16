## Reece Williams - September 2022
## Goal: Convert a CW20 from ANY cosmos network -> an Eve x/TokenFactory native denom
# HOW: 
# - Run this script to query ALL keys of the CW20 contract
# - save each to their own file
# - Run the python script to sort through and get the exact balances, then outputs into an easy way to format for later
# NOTE: This script will make MANY files in the directory it is run.

# validate dependencies are installed
command -v jq > /dev/null 2>&1 || { echo >&2 "jq not installed. More info: https://stedolan.github.io/jq/download/"; exit 1; }

# switch to files current dir
cd "$(dirname "$0")"

# check if .env file exists, if not exit
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found, please create one with 'cp .env.example .env'. Then edit to your liking."
    exit 1
fi

# load env vars from .env file
export $(grep -v '^#' .env | xargs)

# check if any of the following env variables are empty, if so exit
if [ -z "$BINARY" ] || [ -z "$CW20_CONTRACT" ] || [ -z "$CW20_QUERY_PER_LIMIT" ] || [ -z "$RPC_NODE" ]; then
  echo "Please fill out the .env file with the correct values"
  exit 1
fi

# BINARY="junod"
# CW20_CONTRACT="juno15u3dt79t6sxxa3x3kpkhzsy56edaa5a66wvt3kxmukqjz2sx0hes5sn38g"
# LIMIT="500"
# RPC_NODE="https://rpc.juno.strange.love:443"

# make dir CW20s if not already made
mkdir -p CW20s

next_pag_key=""

# Loop through until we dont have any more pages
while true; do
    # get a random UUID for this file
    UUID=$(uuidgen)
    FILENAME="CW20s/cw20-$UUID.json"

    # check if next_pag_key is empty
    if [[ -z $next_pag_key ]]; then
        echo "no key = 1st run"
        $BINARY q wasm contract-state all $CW20_CONTRACT --output json --limit $CW20_QUERY_PER_LIMIT --node $RPC_NODE > $FILENAME
    else
        echo "Running with page key: $next_pag_key"
        $BINARY q wasm contract-state all $CW20_CONTRACT --output json --limit $CW20_QUERY_PER_LIMIT --page-key $next_pag_key --node $RPC_NODE > $FILENAME
    fi

    # $BINARY q wasm contract-state all $CW20_CONTRACT --output json --node $RPC_NODE > $FILENAME

    # get FILENAME json, and get the pagentation section using jq

    # echo "Getting all keys from $FILENAME"
    next_pag_key=`jq -r '.pagination.next_key' $FILENAME`
    # if next_pag_key if null, then we are done
    if [[ $next_pag_key == "null" ]]; then
        echo "No more pages, Finished!"
        break
    fi
done

echo "Please run script2.py now to convert the CW20s folder files -> balances.json"