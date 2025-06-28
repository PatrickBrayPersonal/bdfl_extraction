---
tags:
  - tickets
---
Get information on all the trades that have taken place in MFL

~~you'll need to find all the transactions, and only query for trades see the [[mfl_api_docs]]~~

this should be another method in client.py

## Clarifications:

1. **Trade Data Scope**: Start with all the trades that MFL API can return currently

2. **Trade Information Detail**: Include date, franchises, players/picks - capture all trades (both player and draft pick trades)

3. **Data Structure & Integration**: Return as DataFrame and do not enrich (keep as raw trade data initially)

## ✅ **Implementation Complete**

The `get_trades()` method has been successfully added to `MFLClient` in `client.py`:

- **✅ Retrieves all trade transactions** from MFL API using `transactions` endpoint with `TRANS_TYPE=TRADE`
- **✅ Returns DataFrame** with columns: `trade_id`, `timestamp`, `franchise1_id`, `franchise2_id`, `franchise1_gave_up`, `franchise2_gave_up`, `expires`, `comments`
- **✅ Includes caching** to prevent API rate limiting (12-hour expiration)
- **✅ Robust error handling** with proper logging
- **✅ Tested successfully** - retrieved 25 trades from sample league 65522

**Usage:**
```python
from bdfl.data.mfl_extract import MFLClient

client = MFLClient(league_id="65522", year="2025")
trades_df = client.get_trades()
print(f"Retrieved {len(trades_df)} trades")
```

**Sample Output:**
- Trade ID, timestamp, involved franchises
- What each franchise gave up (player IDs, draft picks)
- Trade expiration and comments
- Raw data ready for further analysis or enrichment