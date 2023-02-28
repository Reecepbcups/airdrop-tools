# HOW-TO-EXPORT

To airdrop, you will need a state export file. These come from a full node that is synced up to the network and stopped.
These nodes typically only hold 30 days' worth of data, so ensure you take an export between now and 30 days ago. You can ensure your height is within this time by checking [Mintscan](https://hub.mintscan.io/).

If you need a snapshot, use Notional's snapshot provider
<https://snapshots.notional.ventures/>

I am working on a tool to auto-pull, grab, convert to PebbleDB, and export the state for you.
<https://github.com/Reecepbcups/cosmosia-chain-sync>

Once you have this data, you can export this data by running the following command:

```bash
# Always export in your home directory, some don't configure wasm correctly if they use a forked Cosmos SDK.
cd ~/.osmosis/
osmosisd export 3500001 2> osmosis_state_export.json

cd ~/.juno/
junod export 6600000 > juno_state_export.json
```

**Please note** Some exports require > and others require 2>, this is due to an SDK bug that outputs it to STDERR.
This can take upwards of 30 minutes to complete, so be patient.

If you see it spewing out the text to your screen, try using the other ">" or "2>" operator. We want it to get formatted into the file.

Once the command exits, check your file size. It should be large. If it only shows 4KB, then you have not exported the state correctly due to an issue with height or version.
This will have been output in the file itself, so follow the error to fix the reason it could not export correctly.

You can check the file size like so in UNIX:

```bash
du -sh osmosis_state_export.json
```

Then check to ensure the file is valid and no extra logs got into your JSON. If the below fails, there is likely text at the top of your file that you need to remove from logs.

```bash
cat osmosis_state_export.json | python -c "import sys,json;json.loads(sys.stdin.read());print 'OK'"
```

Once the above is complete, you are ready to follow the other guides and scripts to parse, edit, and get the data into a format of your liking :)

**EXTRA**
<https://exports.reece.sh/>

You can compress these with the [`xz`](https://www.geeksforgeeks.org/xz-lossless-data-compression-tool-in-linux-with-examples/) command for max compression.

These can be placed on an Nginx server for easy download. Use the following command to generate an index.html file:
`apt install tree; tree -H '.' -L 1 --noreport --charset utf-8 -P "*.xz" -o index.html`
After doing so, you can easily download all the files with the main function
