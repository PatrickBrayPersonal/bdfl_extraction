"""
Module for harmonizing MFL roster data with KTC value histories data.

This module merges player roster information from MyFantasyLeague (MFL) with 
player values from KeepTradeCut (KTC) to create a unified dataset.
"""

import re
from typing import Dict, List, Optional, Tuple
import pandas as pd
from loguru import logger

from .mfl_extract import MFLClient
from .ktc_extract import get_players


def _normalize_name_position_key(name: str, position: str, source: str = 'unknown') -> str:
    """
    Create a normalized composite key from player name and position.

    Args:
        name: Player name (MFL: 'Last, First', KTC: 'First Last')
        position: Player position
        source: Data source ('MFL' or 'KTC')

    Returns:
        Normalized key in format "firstname_lastname_pos"
    """
    if pd.isna(name) or not name:
        return ""

    original_name = str(name).strip()

    # For MFL, convert "Last, First" to "First Last"
    if source == 'MFL' and ',' in original_name:
        parts = [part.strip() for part in original_name.split(',', 1)]
        if len(parts) == 2:
            first_last = f"{parts[1]} {parts[0]}"
        else:
            first_last = original_name
    else:
        first_last = original_name

    # Remove special characters, convert to lowercase, and replace spaces with underscores
    clean_name = re.sub(r'[^a-zA-Z\s]', '', first_last)
    normalized_name = re.sub(r'\s+', '_', clean_name.strip().lower())

    normalized_pos = str(position).strip().lower() if pd.notna(position) else ""

    return f"{normalized_name}_{normalized_pos}"


def _get_mfl_data(league_id: str, year: str) -> pd.DataFrame:
    """
    Get MFL roster data with player details.
    
    Args:
        league_id: MFL league ID
        year: Season year
        
    Returns:
        DataFrame with MFL roster data
    """
    logger.info(f"Fetching MFL roster data for league {league_id}, year {year}")
    
    client = MFLClient(league_id=league_id, year=year)
    mfl_data = client.get_rosters_with_player_details()
    
    # Create composite key for matching
    mfl_data['match_key'] = mfl_data.apply(
        lambda row: _normalize_name_position_key(row['player_name'], row['position'], 'MFL'), 
        axis=1
    )
    
    # Add source identifier
    mfl_data['data_source'] = 'MFL'
    
    logger.info(f"Retrieved {len(mfl_data)} MFL roster entries")
    return mfl_data


def _get_ktc_data() -> pd.DataFrame:
    """
    Get KTC player data with latest values.
    
    Returns:
        DataFrame with KTC player data
    """
    logger.info("Fetching KTC player data")
    
    ktc_data = get_players()
    
    # Create composite key for matching
    ktc_data['match_key'] = ktc_data.apply(
        lambda row: _normalize_name_position_key(row['player_name'], row['position'], 'KTC'), 
        axis=1
    )
    
    # Add source identifier
    ktc_data['data_source'] = 'KTC'
    
    logger.info(f"Retrieved {len(ktc_data)} KTC player entries")
    return ktc_data


def _find_unmatched_players(mfl_data: pd.DataFrame, ktc_data: pd.DataFrame, 
                          max_per_source: int = 10) -> Dict[str, pd.DataFrame]:
    """
    Find players that don't match between MFL and KTC datasets.
    
    Args:
        mfl_data: MFL roster DataFrame
        ktc_data: KTC players DataFrame
        max_per_source: Maximum unmatched players to return per source
        
    Returns:
        Dictionary with 'mfl_unmatched' and 'ktc_unmatched' DataFrames
    """
    mfl_keys = set(mfl_data['match_key'].dropna())
    ktc_keys = set(ktc_data['match_key'].dropna())
    
    # Find unmatched keys
    mfl_unmatched_keys = mfl_keys - ktc_keys
    ktc_unmatched_keys = ktc_keys - mfl_keys
    
    # Get unmatched player data
    mfl_unmatched = mfl_data[mfl_data['match_key'].isin(mfl_unmatched_keys)].head(max_per_source)
    ktc_unmatched = ktc_data[ktc_data['match_key'].isin(ktc_unmatched_keys)].head(max_per_source)
    
    logger.info(f"Found {len(mfl_unmatched_keys)} unmatched MFL players, {len(ktc_unmatched_keys)} unmatched KTC players")
    
    return {
        'mfl_unmatched': mfl_unmatched[['player_name', 'position', 'franchise_name', 'match_key']],
        'ktc_unmatched': ktc_unmatched[['player_name', 'position', 'team', 'value', 'match_key']]
    }


def harmonize_datasets(league_id: str, year: str = "2024") -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Merge MFL roster data with KTC value data.
    
    Args:
        league_id: MFL league ID
        year: Season year (default: "2024")
        
    Returns:
        Tuple of (merged_data, unmatched_players)
        - merged_data: DataFrame with combined MFL and KTC data
        - unmatched_players: Dict with unmatched players from each source
    """
    logger.info(f"Starting data harmonization for league {league_id}, year {year}")
    
    # Get data from both sources
    mfl_data = _get_mfl_data(league_id, year)
    ktc_data = _get_ktc_data()
    
    # Find unmatched players before merging
    unmatched = _find_unmatched_players(mfl_data, ktc_data)
    
    # Debug: Show sample keys from both datasets
    logger.debug(f"Sample MFL keys: {list(mfl_data['match_key'].dropna().head(5))}")
    logger.debug(f"Sample KTC keys: {list(ktc_data['match_key'].dropna().head(5))}")
    
    # Merge datasets on the composite key
    merged_data = mfl_data.merge(
        ktc_data[['match_key', 'value', 'rookie', 'age', 'team']],  # Select relevant KTC columns
        on='match_key',
        how='inner',
        suffixes=('_mfl', '_ktc')
    )
    
    # Clean up the merged data
    merged_data = merged_data.drop(['match_key'], axis=1)
    
    logger.info(f"Successfully merged {len(merged_data)} players")
    logger.info(f"Merge rate: {len(merged_data) / len(mfl_data) * 100:.1f}% of MFL players matched")
    
    return merged_data, unmatched


def generate_unmatched_report(unmatched_players: Dict[str, pd.DataFrame]) -> str:
    """
    Generate a formatted report of unmatched players.
    
    Args:
        unmatched_players: Dictionary with unmatched player DataFrames
        
    Returns:
        Formatted string report
    """
    report = []
    
    report.append("## Unmatched Players Report\n")
    
    # MFL unmatched players
    mfl_unmatched = unmatched_players['mfl_unmatched']
    report.append(f"### MFL Players Not Found in KTC ({len(mfl_unmatched)} shown):\n")
    if len(mfl_unmatched) > 0:
        report.append("```")
        for _, player in mfl_unmatched.iterrows():
            report.append(f"{player['player_name']} ({player['position']}) - {player['franchise_name']} - Key: {player['match_key']}")
        report.append("```\n")
    else:
        report.append("No unmatched MFL players found.\n")
    
    # KTC unmatched players
    ktc_unmatched = unmatched_players['ktc_unmatched']
    report.append(f"### KTC Players Not Found in MFL ({len(ktc_unmatched)} shown):\n")
    if len(ktc_unmatched) > 0:
        report.append("```")
        for _, player in ktc_unmatched.iterrows():
            report.append(f"{player['player_name']} ({player['position']}) - {player['team']} - Value: {player['value']} - Key: {player['match_key']}")
        report.append("```\n")
    else:
        report.append("No unmatched KTC players found.\n")
    
    return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    league_id = os.getenv("MFL_LEAGUE_ID", "65522")  # Default to sample league
    year = os.getenv("MFL_YEAR", "2025")
    
    # Harmonize the datasets
    merged_data, unmatched = harmonize_datasets(league_id, year)
    
    # Print summary
    print(f"\nHarmonization Summary:")
    print(f"- Total merged players: {len(merged_data)}")
    print(f"- MFL unmatched: {len(unmatched['mfl_unmatched'])}")
    print(f"- KTC unmatched: {len(unmatched['ktc_unmatched'])}")
    
    # Generate and print unmatched report
    report = generate_unmatched_report(unmatched)
    print(f"\n{report}")
    
    # Show sample of merged data
    print("\nSample merged data:")
    if len(merged_data) > 0:
        # Use available columns (team_ktc instead of team after merge)
        sample_cols = ['player_name', 'position', 'franchise_name', 'team_ktc', 'value']
        available_cols = [col for col in sample_cols if col in merged_data.columns]
        print(merged_data[available_cols].head(10))
    else:
        print("No merged data to display.")
