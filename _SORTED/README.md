# Sorted

Here is the location for processed and organized data after running export-sort/sorter.py

The structure is like so:

```md
_SORTED/
    ├── README.md
    ├── {CHAIN}_sorted/
        ├── {CHAIN}_bank.json
        ├── {CHAIN}_staking.json
        ├── {CHAIN}_*.json

Where CHAIN is the 'SNAPSHOT_CHAIN_PREFIX' from '.env'
```
