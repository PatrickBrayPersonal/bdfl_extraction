# BDFL Documentation

Welcome to the BDFL (Fantasy Football Data Extraction) documentation. This package provides tools for scraping and analyzing fantasy football data from KeepTradeCut (KTC).

```{toctree}
:maxdepth: 2
:caption: Contents:

installation
data-scripts
configuration
api-reference
troubleshooting
```

## What is BDFL?

BDFL is a Python package designed for fantasy football enthusiasts who want to:
- Extract current dynasty player rankings
- Generate customizable rookie draft guides
- Track historical player value changes
- Analyze fantasy football trends and patterns

## Key Features

- **Web Scraping**: Automated data collection from KeepTradeCut
- **Configurable Extraction**: YAML-based configuration system
- **Smart Caching**: Reduces API calls with 24-hour cache expiration
- **Data Processing**: Snake case standardization and CSV export
- **Extensible Architecture**: Modular design for easy expansion

## Data Sources

The primary data source is [KeepTradeCut](https://keeptradecut.com), which provides:
- Dynasty player rankings
- Historical value tracking
- Player metadata (age, position, team, etc.)
- Rookie-specific information

## Project Structure

```
src/bdfl/
├── data/           # Data extraction scripts
├── model/          # ML models and analysis
├── ui/             # User interface components
└── utils/          # Utility functions and helpers

configs/            # YAML configuration files
docs/               # Documentation
data/
├── raw/            # Raw scraped data
├── processed/      # Cleaned and processed data
└── cache/          # Cached API responses
```

## Quick Start

1. **Installation**: See {doc}`installation`
2. **Data Scripts**: Learn about {doc}`data-scripts`
3. **Configuration**: Understand {doc}`configuration`
4. **API Reference**: Browse the {doc}`api-reference`
5. **Troubleshooting**: Get help with {doc}`troubleshooting`
