# Configuration Guide

BDFL uses YAML configuration files to customize data extraction behavior. All configuration files are located in the `configs/` directory.

## Configuration Files

### get_players.yaml

Controls the output settings for player data extraction.

```yaml
out:
  path: data/raw/ktc_players.csv
  index: false
```

**Parameters**:
- `out.path`: Output file location
- `out.index`: Whether to include DataFrame index in CSV (typically false)

### get_draftguide.yaml

Defines which columns to include in the rookie draft guide.

```yaml
columns:
  - player_name
  - selected
  - notes
  - value
  - rookie_rank
  - rookie_tier
  - rookie_positional_rank
  - rookie_positional_tier
  - positional_rank
  - positional_tier
  - position
  - age
  - team
  - college
  - pick_round
  - pick_num
out:
  path: data/processed/draft_guide.csv
  add_datetime: true
```

**Parameters**:
- `columns`: List of player attributes to include in the draft guide
- `out.path`: Base output file path (timestamp will be added)
- `out.add_datetime`: Whether to append timestamp to filename

**Available Columns**:
- **Identity**: `player_name`, `slug`, `position`, `team`
- **Physical**: `age`, `height_feet`, `height_inches`, `weight`
- **Draft Info**: `pick_round`, `pick_num`, `draft_year`, `college`
- **Rankings**: `value`, `rookie_rank`, `rookie_tier`, `positional_rank`
- **Tracking**: `selected`, `notes` (added by script for draft management)

### get_valuehist.yaml

Controls player filtering and output for historical value collection.

```yaml
get_value_hist:
  head: 0
  relevant_cols:
    - player_name
    - slug
    - position
    - team
    - age
    - birthday
    - height_feet
    - height_inches
    - weight
    - draft_year
    - seasons_experience
    - pick_round
    - pick_num
out:
  path: data/processed/ktc_value_histories.csv
  add_datetime: true
```

**Parameters**:
- `get_value_hist.head`: Number of top players to process (0 = all players)
- `get_value_hist.relevant_cols`: Player metadata columns to include with historical data
- `out.path`: Output file location
- `out.add_datetime`: Whether to append timestamp to filename

## Configuration Patterns

### Output Configuration

All scripts support consistent output configuration:

```yaml
out:
  path: "output/file/path.csv"      # Required: output file path
  add_datetime: true                # Optional: append timestamp
  index: false                      # Optional: include DataFrame index
```

**Timestamp Format**: `YYYYMMDD-HHMMSS`
**Example**: `draft_guide_20250627-155330.csv`

### Column Selection

Scripts that support column filtering use list format:

```yaml
columns:
  - column_name_1
  - column_name_2
  - column_name_3
```

### Nested Configuration

Complex scripts use nested configuration:

```yaml
script_name:
  parameter_1: value
  parameter_2: 
    - list_item_1
    - list_item_2
out:
  path: output.csv
```

## Customization Examples

### Custom Draft Guide

Create a minimal draft guide with only essential information:

```yaml
# configs/get_draftguide.yaml
columns:
  - player_name
  - position
  - team
  - value
  - rookie_rank
  - selected
  - notes
out:
  path: data/processed/simple_draft_guide.csv
  add_datetime: true
```

### Top Players Value History

Track only the top 100 players by value:

```yaml
# configs/get_valuehist.yaml
get_value_hist:
  head: 100
  relevant_cols:
    - player_name
    - position
    - team
    - value
out:
  path: data/processed/top100_value_history.csv
  add_datetime: true
```

### Raw Player Data with Index

Include DataFrame index in player data export:

```yaml
# configs/get_players.yaml
out:
  path: data/raw/ktc_players_with_index.csv
  index: true
```

## Configuration Best Practices

### File Organization
- Keep original configs as templates
- Create custom configs for specific use cases
- Use descriptive filenames for custom configs

### Column Selection
- Include `player_name` and `slug` for data joining
- Add `position` and `team` for filtering and analysis
- Include relevant metadata based on your analysis needs

### Output Paths
- Use `data/raw/` for unprocessed data
- Use `data/processed/` for filtered/transformed data
- Enable timestamps for historical tracking

### Performance Optimization
- Use `head` parameter in `get_valuehist.yaml` to limit API calls
- Cache results are automatically managed (24-hour expiration)
- Consider player filtering based on position or value thresholds

## Validation

Configuration files are validated at runtime. Common errors:

**Missing required fields**:
```
KeyError: 'out'
```

**Invalid YAML syntax**:
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**File path issues**:
```
FileNotFoundError: [Errno 2] No such file or directory
```

## Environment-Specific Configs

For different environments, create separate config files:

```
configs/
├── get_players.yaml          # Default
├── get_players_dev.yaml      # Development
├── get_players_prod.yaml     # Production
└── get_players_test.yaml     # Testing
```

Load specific configs:
```python
cfg = OmegaConf.load("configs/get_players_dev.yaml")
```
