# API Reference

This document provides detailed information about BDFL's functions, classes, and modules.

## Data Collection Module (`bdfl.data`)

### get_players.py

#### `get_players() -> pd.DataFrame`

Scrapes current dynasty player rankings from KeepTradeCut.

**Returns**:
- `pd.DataFrame`: Player data with standardized column names

**Columns Returned**:
- `player_name`: Player's full name
- `slug`: URL-friendly player identifier
- `position`: Player position (QB, RB, WR, TE)
- `team`: Current NFL team
- `age`: Player age (calculated)
- `value`: Current dynasty value
- `rookie`: Boolean indicating rookie status
- `birthday`: Unix timestamp of birth date
- `height_feet`, `height_inches`: Physical measurements
- `weight`: Player weight in pounds
- `draft_year`: NFL draft year
- `pick_round`, `pick_num`: Draft position
- `college`: College attended
- Various ranking fields (`rookie_rank`, `positional_rank`, etc.)

**Example**:
```python
from bdfl.data.get_players import get_players

players = get_players()
print(f"Found {len(players)} players")
print(players[['player_name', 'position', 'team', 'value']].head())
```

#### `_one_qb_values_only(players: pd.DataFrame) -> pd.DataFrame`

Internal function that processes raw player data to extract one-QB values.

**Parameters**:
- `players`: Raw player DataFrame from KeepTradeCut

**Returns**:
- `pd.DataFrame`: Processed DataFrame with one-QB values only

### get_draftguide.py

#### `get_draft_guide(players: pd.DataFrame, columns: list) -> pd.DataFrame`

Generates a rookie draft guide from player data.

**Parameters**:
- `players`: Player DataFrame from `get_players()`
- `columns`: List of column names to include in the guide

**Returns**:
- `pd.DataFrame`: Filtered DataFrame with rookie players only

**Processing**:
- Calculates current age from birthday timestamps
- Adds empty `selected` and `notes` columns for draft tracking
- Filters to rookie players only (`rookie == True`)
- Returns only specified columns

**Example**:
```python
from bdfl.data.get_players import get_players
from bdfl.data.get_draftguide import get_draft_guide

players = get_players()
columns = ['player_name', 'position', 'value', 'rookie_rank']
draft_guide = get_draft_guide(players, columns)
```

### get_valuehist.py

#### `get_value_hist(players: pd.DataFrame, relevant_cols: list, head: int = 0) -> pd.DataFrame`

Collects historical value data for players.

**Parameters**:
- `players`: Player DataFrame from `get_players()`
- `relevant_cols`: Player metadata columns to include
- `head`: Number of top players to process (0 = all)

**Returns**:
- `pd.DataFrame`: Historical value data merged with player metadata

**Columns Returned**:
- `date`: Historical date
- `value`: Player value on that date
- `slug`: Player identifier
- All columns specified in `relevant_cols`

**Example**:
```python
from bdfl.data.get_players import get_players
from bdfl.data.get_valuehist import get_value_hist

players = get_players()
relevant_cols = ['player_name', 'position', 'team']
value_hist = get_value_hist(players, relevant_cols, head=50)
```

#### `_get_player_value_hist(player_slug: str) -> pd.DataFrame`

Internal cached function that scrapes individual player value history.

**Parameters**:
- `player_slug`: URL-friendly player identifier

**Returns**:
- `pd.DataFrame`: Historical values for single player

**Caching**:
- Results cached for 24 hours using `@disk_cache` decorator
- Cache location: `data/cache/_get_player_value_hist/`

## Utility Modules

### pandas_io (`bdfl.utils.pandas_io`)

#### `write(df: pd.DataFrame, path: str, add_datetime: bool = False, **kwargs)`

Standardized DataFrame writing with optional timestamp.

**Parameters**:
- `df`: DataFrame to write
- `path`: Output file path
- `add_datetime`: Whether to append timestamp to filename
- `**kwargs`: Additional arguments passed to `pd.DataFrame.to_csv()`

**Example**:
```python
from bdfl.utils import pandas_io

pandas_io.write(df, "output.csv", add_datetime=True, index=False)
# Creates: output_20250627-155330.csv
```

#### `@snake_case_columns`

Decorator that converts DataFrame column names to snake_case.

**Usage**:
```python
@pandas_io.snake_case_columns
def my_function() -> pd.DataFrame:
    # Function returns DataFrame with any column naming
    return df  # Columns automatically converted to snake_case
```

#### `columns_to_snake(df: pd.DataFrame) -> pd.DataFrame`

Converts DataFrame column names to snake_case format.

**Parameters**:
- `df`: Input DataFrame

**Returns**:
- `pd.DataFrame`: DataFrame with snake_case column names

### cache (`bdfl.utils.cache`)

#### `@disk_cache(cache_dir: str, expiration: int = 86400)`

Decorator for caching function results to disk.

**Parameters**:
- `cache_dir`: Directory to store cache files
- `expiration`: Cache expiration time in seconds (default: 24 hours)

**Usage**:
```python
from bdfl.utils.cache import disk_cache

@disk_cache("data/cache/my_function", expiration=3600)
def expensive_function(param):
    # Expensive computation
    return result
```

## Configuration Loading

### OmegaConf Integration

All scripts use OmegaConf for configuration loading:

```python
from omegaconf import OmegaConf

# Load configuration
cfg = OmegaConf.load("configs/script_name.yaml")

# Access nested values
output_path = cfg.out.path
columns = cfg.columns
```

## Error Handling

### Common Exceptions

**Network Errors**:
```python
requests.exceptions.RequestException
```

**Parsing Errors**:
```python
bs4.FeatureNotFound
ValueError  # When parsing JavaScript data
```

**Configuration Errors**:
```python
KeyError  # Missing configuration keys
yaml.scanner.ScannerError  # Invalid YAML syntax
```

**File System Errors**:
```python
FileNotFoundError  # Missing directories or files
PermissionError  # Insufficient file permissions
```

## Data Types

### Player DataFrame Schema

Standard player DataFrame contains these columns with expected types:

```python
{
    'player_name': str,
    'slug': str,
    'position': str,  # 'QB', 'RB', 'WR', 'TE'
    'team': str,
    'age': float,
    'value': int,
    'rookie': bool,
    'birthday': int,  # Unix timestamp
    'height_feet': int,
    'height_inches': int,
    'weight': int,
    'draft_year': int,
    'pick_round': int,
    'pick_num': int,
    'college': str,
    # ... additional ranking columns
}
```

### Value History DataFrame Schema

```python
{
    'date': str,      # Date string
    'value': int,     # Player value
    'slug': str,      # Player identifier
    # ... player metadata columns
}
```

## Performance Notes

- **Caching**: Value history collection uses intelligent caching
- **Rate Limiting**: Natural delays through processing time
- **Memory Usage**: Large datasets may require chunking for processing
- **Network**: Scripts make multiple HTTP requests; consider connection stability
