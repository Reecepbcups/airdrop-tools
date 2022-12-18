# Airdrop Commands

This directory will contain any commands that need to be run for your genesis.json
You must run the export-sort sorter.py first to get the base information out from the state export

Once completed, you run the airdrop.py. It reads all the logic from the .env file in the export-sort directory.
This ALSO includes formulas that are useful for changing new chain airdrop amounts or doing fair drops to each wallet.

**Fair drop definition**: every wallet gets the same amount no matter the amount staked / their balance in the snapshot
