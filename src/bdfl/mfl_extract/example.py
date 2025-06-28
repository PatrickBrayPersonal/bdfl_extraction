"""Example usage of MFL client."""

from typing import Optional
import pandas as pd
from loguru import logger

from bdfl.mfl_extract.client import MFLClient


def demo_mfl_client(league_id: Optional[str] = None) -> pd.DataFrame:
    """Demonstrate MFL client functionality.
    
    Args:
        league_id: Optional league ID to override environment variable
        
    Returns:
        DataFrame containing roster data
    """
    try:
        # Initialize client
        client = MFLClient(league_id=league_id)
        
        # Get league info
        logger.info("Fetching league information...")
        league_info = client.get_league_info()
        print(f"\nLeague: {league_info.get('name', 'Unknown')}")
        print(f"ID: {league_info.get('id', 'Unknown')}")
        print(f"Year: {client.year}")
        
        # Get enriched rosters with player names and positions
        logger.info("Fetching enriched rosters...")
        rosters_df = client.get_rosters_with_player_details()
        print(rosters_df)
        
        print(f"\nRosters Summary:")
        print(f"Total roster entries: {len(rosters_df)}")
        print(f"Number of franchises: {rosters_df['franchise_id'].nunique()}")
        print(f"Total players: {rosters_df[rosters_df['player_id'] != ''].shape[0]}")
        
        # Show franchise summary
        franchise_summary = (
            rosters_df[rosters_df['player_id'] != '']
            .groupby(['franchise_id', 'franchise_name'])
            .size()
            .reset_index(name='player_count')
        )
        
        print(f"\nFranchise Player Counts:")
        print(franchise_summary.to_string(index=False))
        
        # Show sample roster data
        if len(rosters_df) > 0:
            print(f"\nSample Roster Data (first 10 rows):")
            sample_df = rosters_df[rosters_df['player_id'] != ''].head(10)
            print(sample_df[['franchise_name', 'player_name', 'position']].to_string(index=False))
        
        # Show position breakdown
        if len(rosters_df) > 0:
            position_summary = (
                rosters_df[rosters_df['player_id'] != '']
                .groupby('position')
                .size()
                .reset_index(name='count')
                .sort_values('count', ascending=False)
            )
            print(f"\nPosition Breakdown:")
            print(position_summary.to_string(index=False))
        
        return rosters_df
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    # Run demo with sample league ID
    demo_mfl_client("65522")
