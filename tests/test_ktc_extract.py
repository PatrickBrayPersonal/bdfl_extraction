"""Tests for KTC (KeepTradeCut) extraction module."""

import os
import pandas as pd
from omegaconf import OmegaConf
from bdfl.data.ktc_extract import get_players, get_draft_guide, get_value_hist


class TestKTCExtract:
    """Test cases for KTC extraction functions."""
    
    def test_get_players(self) -> None:
        """Test players retrieval from KTC."""
        players = get_players()
        assert isinstance(players, pd.DataFrame)
        assert len(players) > 0
        # Check for expected columns
        expected_cols = ['slug', 'player_name', 'position', 'team', 'value']
        for col in expected_cols:
            assert col in players.columns, f"Missing column: {col}"
    
    def test_get_draft_guide(self) -> None:
        """Test draft guide generation."""
        # Get a small sample of players for testing
        players = get_players()
        test_columns = ['player_name', 'position', 'team', 'value', 'age', 'selected', 'notes']
        
        draft_guide = get_draft_guide(players, columns=test_columns)
        assert isinstance(draft_guide, pd.DataFrame)
        
        # Check that only rookie players are included
        # Note: This assumes the 'rookie' column exists in players data
        if 'rookie' in players.columns:
            assert len(draft_guide) <= len(players[players['rookie']])
        
        # Check that all requested columns are present
        for col in test_columns:
            assert col in draft_guide.columns, f"Missing column: {col}"
    
    def test_get_value_hist_small_sample(self) -> None:
        """Test value history retrieval with small sample."""
        # Disable caching for testing
        os.environ["CACHE"] = "false"
        
        players = get_players()
        # Use only top 2 players for faster testing
        relevant_cols = ['slug', 'player_name', 'position', 'team']
        
        value_hist = get_value_hist(players, relevant_cols=relevant_cols, head=2)
        assert isinstance(value_hist, pd.DataFrame)
        assert len(value_hist) > 0
        
        # Check for expected columns
        expected_cols = ['date', 'value', 'slug', 'player_name', 'position', 'team']
        for col in expected_cols:
            assert col in value_hist.columns, f"Missing column: {col}"
