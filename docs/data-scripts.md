# Data Collection Scripts

BDFL provides three main data collection scripts for extracting fantasy football data from KeepTradeCut.

## Overview

All scripts are located in `src/bdfl/data/` and can be run independently. Each script:
- Uses configuration files from `configs/`
- Outputs timestamped CSV files
- Follows consistent data processing patterns

## Scripts

### 1. get_players.py

**Purpose**: Scrape current dynasty player rankings and metadata from KeepTradeCut.

**Usage**:
```bash
poetry run python src/bdfl/data/get_players.py
```

**What it does**:
- Fetches the main dynasty rankings page
- Extracts player data from embedded JavaScript
- Processes one-QB values (removes superflex data)
- Standardizes column names to snake_case
- Exports to `data/raw/ktc_players.csv`

**Key Features**:
- Automatic column name standardization
- One-QB value focus (superflex values removed)
- Raw player data with all available attributes

**Configuration**: `configs/get_players.yaml`

### 2. get_draftguide.py

**Purpose**: Generate a customizable rookie draft guide with selected player attributes.

**Usage**:
```bash
poetry run python src/bdfl/data/get_draftguide.py
```

**What it does**:
- Loads player data using `get_players()`
- Calculates current age from birthday timestamps
- Filters to rookie players only
- Adds empty columns for draft tracking (`selected`, `notes`)
- Exports customizable columns to `data/processed/draft_guide_YYYYMMDD-HHMMSS.csv`

**Key Features**:
- Age calculation from timestamps
- Rookie-only filtering
- Customizable column selection
- Draft tracking fields (selected, notes)

**Configuration**: `configs/get_draftguide.yaml`

### 3. get_valuehist.py

**Purpose**: Collect historical value data for players with intelligent caching.

**Usage**:
```bash
poetry run python src/bdfl/data/get_valuehist.py
```

**What it does**:
- Loads current player data
- Optionally filters to top N players by value
- Scrapes individual player pages for historical values
- Caches results for 24 hours to minimize requests
- Merges historical data with player metadata
- Exports to `data/processed/ktc_value_histories.csv`

**Key Features**:
- Smart caching (24-hour expiration)
- Progress tracking with tqdm
- Configurable player filtering
- Historical value tracking

**Configuration**: `configs/get_valuehist.yaml`

## Script Architecture

### Common Patterns

All scripts follow similar patterns:

```python
# 1. Configuration loading
cfg = OmegaConf.load("configs/script_name.yaml")

# 2. Data collection
data = collect_data_function()

# 3. Data processing
processed_data = process_data(data, **cfg.processing_params)

# 4. Output
pandas_io.write(processed_data, **cfg.out)
```

### Utility Functions

Scripts leverage shared utilities:
- `pandas_io.write()`: Standardized CSV output with timestamps
- `pandas_io.snake_case_columns`: Column name standardization
- `disk_cache`: Intelligent caching decorator
- `get_players()`: Shared player data collection

## Data Flow

```
KeepTradeCut Website
        ↓
    Web Scraping
        ↓
   Raw Data Processing
        ↓
    Configuration Filtering
        ↓
    CSV Export with Timestamps
```

## Output Files

### File Naming Convention
- **Raw data**: `data/raw/filename.csv`
- **Processed data**: `data/processed/filename_YYYYMMDD-HHMMSS.csv`
- **Cache**: `data/cache/_function_name/`

### Typical Outputs
- `ktc_players.csv`: Complete player dataset
- `draft_guide_20250627-155330.csv`: Rookie draft guide
- `ktc_value_histories.csv`: Historical value tracking

## Performance Considerations

### Caching Strategy
- **get_valuehist.py** uses disk caching to avoid repeated API calls
- Cache expires after 24 hours
- Individual player pages cached separately

### Rate Limiting
- Scripts include natural delays through processing time
- Consider adding explicit delays for large datasets
- Monitor KeepTradeCut's terms of service

## Error Handling

Scripts include basic error handling for:
- Network connectivity issues
- HTML parsing failures
- Configuration file problems

For debugging, check:
1. Network connectivity
2. KeepTradeCut website structure changes
3. Configuration file syntax
4. Output directory permissions
