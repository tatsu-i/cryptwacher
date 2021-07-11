expr $(bitcoin-cli getblockchaininfo |jq .mediantime) - $(date -u +%s)
