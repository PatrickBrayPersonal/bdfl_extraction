"""Combine two KTC value history CSVs, normalize date formats, and remove duplicates."""

import sys
from pathlib import Path

import pandas as pd


PUBLISHED_DIR = Path(__file__).parent.parent / "data" / "published"
OUTPUT_PATH = PUBLISHED_DIR / "ktc_value_histories_combined.csv"


def normalize_date(series: pd.Series) -> pd.Series:
    """Normalize dates to YYYY-MM-DD. Handles both YYYY-MM-DD and YYMMDD formats."""
    sample = series.dropna().iloc[0]
    if "-" in str(sample):
        return pd.to_datetime(series, format="%Y-%m-%d").dt.strftime("%Y-%m-%d")
    else:
        return pd.to_datetime(series.astype(str).str.zfill(6), format="%y%m%d").dt.strftime("%Y-%m-%d")


def load_and_normalize(path: Path) -> pd.DataFrame:
    print(f"Loading {path.name}...")
    df = pd.read_csv(path, dtype=str)
    df["date"] = normalize_date(df["date"])
    print(f"  {len(df):,} rows, date range: {df['date'].min()} → {df['date'].max()}")
    return df


def main() -> None:
    files = sorted(PUBLISHED_DIR.glob("ktc_value_histories_2*.csv"))
    if len(files) < 2:
        print(f"Expected at least 2 source files in {PUBLISHED_DIR}, found {len(files)}")
        sys.exit(1)

    frames = [load_and_normalize(f) for f in files]
    combined = pd.concat(frames, ignore_index=True)
    print(f"\nCombined before dedup: {len(combined):,} rows")

    combined = combined.drop_duplicates(subset=["date", "slug"])
    combined = combined.sort_values(["date", "slug"]).reset_index(drop=True)
    print(f"Combined after dedup:  {len(combined):,} rows")
    print(f"Date range: {combined['date'].min()} → {combined['date'].max()}")

    combined.to_csv(OUTPUT_PATH, index=False)
    print(f"\nWritten to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
