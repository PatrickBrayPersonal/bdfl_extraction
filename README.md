# BDFL - Fantasy Football Data Extraction

**Author:** Patrick Bray  
**Purpose:** Extract and analyze useful data for fantasy football decision-making

## Overview

BDFL is a Python package that scrapes and processes fantasy football data from KeepTradeCut (KTC), providing tools for dynasty league analysis, draft preparation, and player valuation tracking.

## Features

### Data Collection Scripts
- **Player Data**: Scrape current dynasty rankings and player information from KTC
- **Draft Guide**: Generate rookie draft guides with customizable player attributes
- **Value History**: Track historical player value changes over time with caching

### Key Capabilities
- Web scraping with BeautifulSoup and requests
- Configurable data extraction via YAML configs
- Automatic data caching to minimize API calls
- CSV export with timestamped filenames
- Snake case column standardization

## Prerequisites
- Python 3.10+
- Poetry package manager
  - Install: `pip install poetry`

## Installation

1. **Set up environment:**
   ```bash
   poetry install
   poetry shell
   ```

2. **Test installation:**
   ```bash
   pytest .
   ```

## Usage

### Data Extraction Scripts

Run individual data collection scripts:

```bash
# Get current player rankings and data
poetry run python src/bdfl/data/get_players.py

# Generate rookie draft guide
poetry run python src/bdfl/data/get_draftguide.py

# Collect player value histories (with caching)
poetry run python src/bdfl/data/get_valuehist.py
```

### Configuration

Customize data extraction via YAML configs in `configs/`:

- `get_players.yaml`: Output settings for player data
- `get_draftguide.yaml`: Column selection for draft guides
- `get_valuehist.yaml`: Player filtering and output for value histories

### Invoke Commands

This repository uses [invoke](https://www.pyinvoke.org/) for task management:

```bash
# See available commands
inv -l

# Format code with ruff
inv format

# Generate VS Code launch config
inv launch
```

## Data Sources

- **KeepTradeCut**: Dynasty player rankings and historical values
- **Output**: Processed CSV files in `data/processed/` with timestamps
- **Caching**: Player value histories cached in `data/cache/` (24hr expiration)

## Project Structure

```
src/bdfl/
├── data/           # Data extraction scripts
├── model/          # ML models and analysis
├── ui/             # User interface components
└── utils/          # Utility functions and helpers

configs/            # YAML configuration files
data/
├── raw/            # Raw scraped data
├── processed/      # Cleaned and processed data
└── cache/          # Cached API responses
```

## Dependencies

**Core:** pandas, requests, beautifulsoup4, tqdm, omegaconf, hydra-core  
**Dev:** pytest, ruff, invoke, jupyter  
**UI:** streamlit, seaborn, plotly

Manage dependencies with Poetry:
```bash
poetry add <package-name>
```
