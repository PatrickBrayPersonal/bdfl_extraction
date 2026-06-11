# Troubleshooting Guide

This guide helps you resolve common issues when using BDFL.

## Installation Issues

### Poetry Not Found

**Error**: `poetry: command not found`

**Solutions**:
```bash
# Install Poetry via pip
pip install poetry

# Or install via official installer
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH (macOS/Linux)
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
poetry --version
```

### Python Version Compatibility

**Error**: `This project requires Python ^3.10`

**Solutions**:
```bash
# Check current Python version
python --version

# Install Python 3.10+ using pyenv
pyenv install 3.10.0
pyenv local 3.10.0

# Or use system package manager
# macOS: brew install python@3.10
# Ubuntu: sudo apt install python3.10
```

### Permission Errors

**Error**: `[Errno 13] Permission denied`

**Solutions**:
```bash
# Make scripts executable
chmod +x src/bdfl/data/*.py

# Check directory permissions
ls -la data/

# Create directories if missing
mkdir -p data/{raw,processed,cache}
```

## Runtime Issues

### Network Connection Problems

**Error**: `requests.exceptions.ConnectionError`

**Symptoms**:
- Scripts fail to connect to KeepTradeCut
- Timeout errors during data collection

**Solutions**:
1. **Check internet connection**
2. **Verify KeepTradeCut is accessible**:
   ```bash
   curl -I https://keeptradecut.com
   ```
3. **Add retry logic** (for developers):
   ```python
   import time
   import requests
   from requests.adapters import HTTPAdapter
   from urllib3.util.retry import Retry
   
   session = requests.Session()
   retry_strategy = Retry(total=3, backoff_factor=1)
   adapter = HTTPAdapter(max_retries=retry_strategy)
   session.mount("http://", adapter)
   session.mount("https://", adapter)
   ```

### HTML Parsing Failures

**Error**: `AttributeError: 'NoneType' object has no attribute`

**Symptoms**:
- Scripts fail when parsing KeepTradeCut HTML
- Empty or malformed data returned

**Causes**:
- KeepTradeCut website structure changed
- JavaScript content not loading properly
- Rate limiting by the website

**Solutions**:
1. **Check website manually** in browser
2. **Inspect HTML structure** for changes
3. **Add delays between requests**:
   ```python
   import time
   time.sleep(1)  # Wait 1 second between requests
   ```
4. **Update parsing logic** if website changed

### Configuration Errors

**Error**: `KeyError: 'columns'`

**Symptoms**:
- Scripts fail to load configuration
- Missing required configuration keys

**Solutions**:
1. **Verify YAML syntax**:
   ```bash
   python -c "import yaml; yaml.safe_load(open('configs/get_draftguide.yaml'))"
   ```
2. **Check required keys exist**:
   ```yaml
   # get_draftguide.yaml must have:
   columns: [...]
   out:
     path: "..."
   ```
3. **Use default configurations** as templates

### Cache Issues

**Error**: Cache files corrupted or taking too much space

**Solutions**:
```bash
# Clear all cache
rm -rf data/cache/*

# Clear specific function cache
rm -rf data/cache/_get_player_value_hist/

# Check cache size
du -sh data/cache/
```

## Data Quality Issues

### Missing Player Data

**Symptoms**:
- Fewer players than expected
- Key players missing from results

**Debugging**:
```python
# Check total players
players = get_players()
print(f"Total players: {len(players)}")

# Check for specific player
player_name = "Player Name"
matches = players[players['player_name'].str.contains(player_name, case=False)]
print(matches[['player_name', 'position', 'team']])

# Check data types
print(players.dtypes)
print(players.isnull().sum())
```

### Incorrect Age Calculations

**Symptoms**:
- Negative ages
- Unrealistic age values

**Debugging**:
```python
# Check birthday data
print(players['birthday'].describe())
print(players[players['age'] < 0][['player_name', 'age', 'birthday']])

# Manual age calculation
from datetime import datetime
current_timestamp = datetime.now().timestamp()
players['age_check'] = (current_timestamp - players['birthday']) / (365.25 * 24 * 60 * 60)
```

### Value History Gaps

**Symptoms**:
- Missing historical data for some players
- Incomplete value histories

**Debugging**:
```python
# Check value history coverage
value_hist = get_value_hist(players, relevant_cols=['player_name'], head=10)
coverage = value_hist.groupby('slug')['date'].count()
print(f"Average data points per player: {coverage.mean():.1f}")
print(f"Players with < 10 data points: {(coverage < 10).sum()}")
```

## Performance Issues

### Slow Data Collection

**Symptoms**:
- Scripts take very long to complete
- High memory usage

**Solutions**:
1. **Use head parameter** to limit players:
   ```yaml
   # configs/get_valuehist.yaml
   get_value_hist:
     head: 100  # Process only top 100 players
   ```

2. **Check cache utilization**:
   ```bash
   ls -la data/cache/_get_player_value_hist/
   ```

3. **Monitor memory usage**:
   ```bash
   # Run with memory monitoring
   /usr/bin/time -v poetry run python src/bdfl/data/get_valuehist.py
   ```

### Large Output Files

**Solutions**:
```python
# Use compression
import pandas as pd
df.to_csv('output.csv.gz', compression='gzip', index=False)

# Filter data before export
df_filtered = df[df['value'] > 1000]  # Only valuable players
```

## Development Issues

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'bdfl'`

**Solutions**:
```bash
# Ensure you're in the poetry environment
poetry shell

# Install in development mode
poetry install

# Check Python path
python -c "import sys; print(sys.path)"
```

### Test Failures

**Error**: Tests fail after changes

**Solutions**:
```bash
# Run specific test
pytest tests/test_specific.py -v

# Run with coverage
pytest --cov=src/bdfl tests/

# Update test data if needed
pytest --update-snapshots
```

## Getting Help

### Debug Information to Collect

When reporting issues, include:

1. **Environment info**:
   ```bash
   python --version
   poetry --version
   poetry show  # List installed packages
   ```

2. **Error messages** (full traceback)

3. **Configuration files** being used

4. **Sample data** that reproduces the issue

5. **Network connectivity** test results

### Log Analysis

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use loguru (already in dependencies)
from loguru import logger
logger.add("debug.log", level="DEBUG")
```

### Common Debugging Commands

```bash
# Test network connectivity
curl -v https://keeptradecut.com/dynasty-rankings

# Validate YAML files
python -c "import yaml; print(yaml.safe_load(open('configs/get_players.yaml')))"

# Check file permissions
ls -la src/bdfl/data/
ls -la data/

# Monitor disk space
df -h
du -sh data/
```

### When to Seek Help

Contact maintainers when:
- Website structure has fundamentally changed
- Configuration options need expansion
- New features are needed
- Performance optimization is required
- Security concerns arise
