from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def datadir() -> Path:
    return Path("tests/data/regressions")


@pytest.fixture(scope="session")
def original_datadir() -> Path:
    return Path("tests/data/regressions")
