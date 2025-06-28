"""Tests for MFL extraction module."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from bdfl.data.mfl_extract.client import MFLClient


class TestMFLClient:
    """Test cases for MFLClient."""
    
    def test_init_with_league_id(self) -> None:
        """Test client initialization with league ID."""
        client = MFLClient(league_id="12345", year="2024")
        assert client.league_id == "12345"
        assert client.year == "2024"
    
    def test_init_without_league_id_raises_error(self) -> None:
        """Test that missing league ID raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="League ID must be provided"):
                MFLClient()
    
    @patch('bdfl.data.mfl_extract.client.requests.get')
    def test_get_rosters_success(self, mock_get: Mock) -> None:
        """Test successful roster retrieval."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "rosters": {
                "franchise": [
                    {
                        "id": "0001",
                        "player": [
                            {
                                "id": "12345",
                                "status": "ROSTER"
                            }
                        ]
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = MFLClient(league_id="65522", year="2024")
        df = client.get_rosters()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]['franchise_id'] == "0001"
        assert df.iloc[0]['player_id'] == "12345"
        assert df.iloc[0]['status'] == "ROSTER"
    
    @patch('bdfl.data.mfl_extract.client.requests.get')
    def test_get_league_info_success(self, mock_get: Mock) -> None:
        """Test successful league info retrieval."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "league": {
                "id": "65522",
                "name": "Test League",
                "year": "2024"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = MFLClient(league_id="65522", year="2024")
        info = client.get_league_info()
        
        assert info["id"] == "65522"
        assert info["name"] == "Test League"
        assert info["year"] == "2024"
    
    @patch('bdfl.data.mfl_extract.client.requests.get')
    def test_get_franchises_success(self, mock_get: Mock) -> None:
        """Test successful franchise retrieval."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "league": {
                "franchises": {
                    "franchise": [
                        {
                            "id": "0001",
                            "name": "Team Alpha",
                            "owner_name": "John Doe",
                            "logo": "logo1.png"
                        },
                        {
                            "id": "0002",
                            "name": "Team Beta",
                            "owner_name": "Jane Smith",
                            "logo": "logo2.png"
                        }
                    ]
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = MFLClient(league_id="65522", year="2024")
        df = client.get_franchises()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert df.iloc[0]['franchise_id'] == "0001"
        assert df.iloc[0]['franchise_name'] == "Team Alpha"
        assert df.iloc[0]['owner_name'] == "John Doe"
        assert df.iloc[1]['franchise_id'] == "0002"
        assert df.iloc[1]['franchise_name'] == "Team Beta"
    
    @patch('bdfl.data.mfl_extract.client.requests.get')
    def test_get_players_success(self, mock_get: Mock) -> None:
        """Test successful players retrieval."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "players": {
                "player": [
                    {
                        "id": "12345",
                        "name": "Wilson, Russell",
                        "position": "QB",
                        "team": "PIT",
                        "birthdate": "1988-11-29",
                        "draft_year": "2012",
                        "rookie_year": "2012"
                    },
                    {
                        "id": "67890",
                        "name": "Barkley, Saquon",
                        "position": "RB",
                        "team": "PHI",
                        "birthdate": "1997-02-09",
                        "draft_year": "2018",
                        "rookie_year": "2018"
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = MFLClient(league_id="65522", year="2024")
        df = client.get_players()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert df.iloc[0]['player_id'] == "12345"
        assert df.iloc[0]['player_name'] == "Wilson, Russell"
        assert df.iloc[0]['position'] == "QB"
        assert df.iloc[0]['team'] == "PIT"
        assert df.iloc[1]['player_id'] == "67890"
        assert df.iloc[1]['player_name'] == "Barkley, Saquon"
        assert df.iloc[1]['position'] == "RB"
    
    @patch('bdfl.data.mfl_extract.client.requests.get')
    def test_get_rosters_with_player_details_success(self, mock_get: Mock) -> None:
        """Test successful enriched rosters retrieval."""
        # Mock responses for multiple API calls
        responses = [
            # First call: get_rosters
            Mock(),
            # Second call: get_players  
            Mock(),
            # Third call: get_franchises
            Mock()
        ]
        
        # Mock roster response
        responses[0].json.return_value = {
            "rosters": {
                "franchise": [
                    {
                        "id": "0001",
                        "player": [
                            {"id": "12345", "status": "ROSTER"},
                            {"id": "67890", "status": "ROSTER"}
                        ]
                    }
                ]
            }
        }
        responses[0].raise_for_status.return_value = None
        
        # Mock players response
        responses[1].json.return_value = {
            "players": {
                "player": [
                    {
                        "id": "12345",
                        "name": "Wilson, Russell",
                        "position": "QB",
                        "team": "PIT"
                    },
                    {
                        "id": "67890",
                        "name": "Barkley, Saquon",
                        "position": "RB",
                        "team": "PHI"
                    }
                ]
            }
        }
        responses[1].raise_for_status.return_value = None
        
        # Mock franchises response
        responses[2].json.return_value = {
            "league": {
                "franchises": {
                    "franchise": [
                        {
                            "id": "0001",
                            "name": "Team Alpha",
                            "owner_name": "John Doe"
                        }
                    ]
                }
            }
        }
        responses[2].raise_for_status.return_value = None
        
        mock_get.side_effect = responses
        
        client = MFLClient(league_id="65522", year="2024")
        df = client.get_rosters_with_player_details()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert df.iloc[0]['franchise_id'] == "0001"
        assert df.iloc[0]['player_id'] == "12345"
        assert df.iloc[0]['player_name'] == "Wilson, Russell"
        assert df.iloc[0]['position'] == "QB"
        assert df.iloc[0]['franchise_name'] == "Team Alpha"
        assert df.iloc[0]['owner_name'] == "John Doe"
        assert df.iloc[0]['status'] == "ROSTER"
    
    @patch('bdfl.data.mfl_extract.client.requests.get')
    def test_get_franchises_empty_response(self, mock_get: Mock) -> None:
        """Test franchise retrieval with empty response."""
        # Mock API response without franchises
        mock_response = Mock()
        mock_response.json.return_value = {
            "league": {}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = MFLClient(league_id="65522", year="2024")
        df = client.get_franchises()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["franchise_id", "franchise_name", "owner_name", "logo"]
    
    @patch('bdfl.data.mfl_extract.client.requests.get')
    def test_get_players_single_player(self, mock_get: Mock) -> None:
        """Test players retrieval with single player (dict instead of list)."""
        # Mock API response with single player
        mock_response = Mock()
        mock_response.json.return_value = {
            "players": {
                "player": {
                    "id": "12345",
                    "name": "Wilson, Russell",
                    "position": "QB",
                    "team": "PIT"
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = MFLClient(league_id="65522", year="2024")
        df = client.get_players()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]['player_id'] == "12345"
        assert df.iloc[0]['player_name'] == "Wilson, Russell"
    
    @patch('bdfl.data.mfl_extract.client.requests.get')
    def test_get_trades_success(self, mock_get: Mock) -> None:
        """Test successful trades retrieval."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "transactions": {
                "transaction": [
                    {
                        "id": "1234567890",
                        "timestamp": "1751033504",
                        "franchise1": "0001",
                        "franchise2": "0002",
                        "franchise1_gave_up": "12345,67890",
                        "franchise2_gave_up": "11111,22222",
                        "expires": "1751637977",
                        "comments": "Test trade"
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = MFLClient(league_id="65522", year="2024")
        df = client.get_trades()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]['trade_id'] == "1234567890"
        assert df.iloc[0]['franchise1_id'] == "0001"
        assert df.iloc[0]['franchise2_id'] == "0002"
        assert df.iloc[0]['franchise1_gave_up'] == "12345,67890"
        assert df.iloc[0]['franchise2_gave_up'] == "11111,22222"
    
    @patch('bdfl.data.mfl_extract.client.requests.get')
    def test_get_trades_empty_response(self, mock_get: Mock) -> None:
        """Test trades retrieval with empty response."""
        # Mock API response without trades
        mock_response = Mock()
        mock_response.json.return_value = {
            "transactions": {}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = MFLClient(league_id="65522", year="2024")
        df = client.get_trades()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        expected_cols = ["trade_id", "timestamp", "franchise1_id", "franchise2_id",
                        "franchise1_gave_up", "franchise2_gave_up", "expires", "comments"]
        assert list(df.columns) == expected_cols
