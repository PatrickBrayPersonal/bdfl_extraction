# Installation Guide

This guide will help you set up BDFL on your system.

## Prerequisites

- **Python 3.12+**: BDFL requires Python 3.12 or higher
- **Poetry**: Package and dependency management
- **Git**: For cloning the repository

## Installing Poetry

If you don't have Poetry installed:

```bash
# Install Poetry
pip install poetry

# Verify installation
poetry --version
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd bdfl_extraction
```

### 2. Set Up Environment

```bash
# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### 3. Verify Installation

```bash
# Run tests to verify everything works
pytest .

# Check if scripts can be imported
python -c "from bdfl.data.get_players import get_players; print('Installation successful!')"

# Test the Streamlit UI (optional)
inv ui
```

The Streamlit UI should open in your browser at `http://localhost:8501`.

## Development Installation

For development work, install additional dev dependencies:

```bash
# Install with dev dependencies (already included in poetry install)
poetry install

# Install pre-commit hooks (if available)
pre-commit install
```

## Directory Setup

After installation, ensure the following directories exist:

```bash
# Create data directories if they don't exist
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/cache
```

## Environment Variables

Currently, BDFL doesn't require any environment variables. All configuration is handled through YAML files in the `configs/` directory.

## Troubleshooting Installation

### Common Issues

**Poetry not found:**
```bash
# Add Poetry to PATH (macOS/Linux)
export PATH="$HOME/.local/bin:$PATH"

# Or install via curl
curl -sSL https://install.python-poetry.org | python3 -
```

**Python version issues:**
```bash
# Check Python version
python --version

# Use pyenv to manage Python versions if needed
pyenv install 3.12.0
pyenv local 3.12.0
```

**Permission errors:**
```bash
# Make scripts executable
chmod +x src/bdfl/data/*.py
```

## Next Steps

After successful installation:

1. Read the [Data Scripts Guide](data-scripts.md)
2. Review [Configuration Options](configuration.md)
3. Try running your first data extraction script
4. Launch the Streamlit UI with `inv ui` for interactive data analysis
