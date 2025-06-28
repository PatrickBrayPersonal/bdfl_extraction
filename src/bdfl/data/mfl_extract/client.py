"""MFL API client for extracting fantasy football data."""

import os
from typing import Optional, Dict, Any, List
import requests
import pandas as pd
from loguru import logger
from dotenv import load_dotenv
from bdfl.utils.cache import disk_cache

load_dotenv()


@disk_cache("data/cache/mfl_extract/api_requests", expiration=43200)  # 12 hours
def _cached_mfl_request(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a cached request to the MFL API.
    
    Args:
        url: Full URL to request
        params: Optional query parameters
        
    Returns:
        JSON response as dictionary
    """
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


class MFLClient:
    """Client for interacting with MyFantasyLeague.com API.
    
    This class provides methods to extract data from MFL leagues,
    returning results as pandas DataFrames for easy analysis.
    """
    
    def __init__(self, league_id: Optional[str] = None, year: Optional[str] = None) -> None:
        """Initialize MFL client.
        
        Args:
            league_id: MFL league ID. If not provided, will try to load from environment.
            year: League year. If not provided, will try to load from environment or default to current year.
        """
        load_dotenv()
        
        self.league_id = league_id or os.getenv("MFL_LEAGUE_ID")
        self.year = year or os.getenv("MFL_YEAR", "2024")
        self.base_url = "https://api.myfantasyleague.com"
        
        if not self.league_id:
            raise ValueError("League ID must be provided either as parameter or MFL_LEAGUE_ID environment variable")
        
        logger.info(f"Initialized MFL client for league {self.league_id}, year {self.year}")
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the MFL API.
        
        Args:
            endpoint: API endpoint (e.g., 'rosters', 'players')
            params: Optional additional parameters
            
        Returns:
            JSON response as dictionary
        """
        if params is None:
            params = {}
        
        # Add required parameters
        params.update({
            'L': self.league_id,
            'JSON': '1'
        })
        
        # Add endpoint type
        params['TYPE'] = endpoint
        
        url = f"{self.base_url}/{self.year}/export"
        
        logger.debug(f"Making MFL API request: {url} with params: {params}")
        
        try:
            # Use the cached function for the actual HTTP request
            data = _cached_mfl_request(url, params)
            logger.debug(f"Received response with keys: {list(data.keys())}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MFL API request failed: {e}")
            raise
    
    def get_rosters(self, franchise_id: Optional[str] = None, week: Optional[str] = None) -> pd.DataFrame:
        """Get current rosters for all franchises or a specific franchise.
        
        Args:
            franchise_id: Optional franchise ID to get roster for specific team
            week: Optional week number for historical rosters
            
        Returns:
            DataFrame with columns: franchise_id, player_id, status
        """
        params = {}
        if franchise_id:
            params["FRANCHISE"] = franchise_id
        if week:
            params["W"] = week
        
        logger.info(f"Fetching rosters for league {self.league_id}")
        
        try:
            data = self._make_request("rosters", params)
            
            # Debug: Log response structure (commented out to reduce verbosity)
            # logger.debug(f"Full rosters response: {data}")
            
            # Parse the rosters data
            rosters_data = []
            
            if "rosters" in data and "franchise" in data["rosters"]:
                franchises = data["rosters"]["franchise"]
                
                # Handle single franchise vs multiple franchises
                if isinstance(franchises, dict):
                    franchises = [franchises]
                
                logger.debug(f"Found {len(franchises)} franchises")
                
                for franchise in franchises:
                    franchise_id = franchise.get("id", "")
                    
                    # Get players for this franchise
                    if "player" in franchise:
                        players = franchise["player"]
                        
                        # Handle single player vs multiple players
                        if isinstance(players, dict):
                            players = [players]
                        
                        for player in players:
                            rosters_data.append({
                                "franchise_id": franchise_id,
                                "player_id": player.get("id", ""),
                                "status": player.get("status", "")
                            })
            
            df = pd.DataFrame(rosters_data)
            logger.info(f"Retrieved {len(df)} roster entries for {df['franchise_id'].nunique()} franchises")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to get rosters: {e}")
            raise
    
    def get_franchises(self) -> pd.DataFrame:
        """Get franchise information including names and owners.
        
        Returns:
            DataFrame with franchise details
        """
        logger.info(f"Fetching franchise info for league {self.league_id}")
        
        try:
            # Try to get franchise info from league data
            league_data = self._make_request("league")
            
            franchises_data = []
            
            if "league" in league_data and "franchises" in league_data["league"]:
                franchises = league_data["league"]["franchises"]["franchise"]
                
                # Handle single franchise vs multiple franchises
                if isinstance(franchises, dict):
                    franchises = [franchises]
                
                for franchise in franchises:
                    franchises_data.append({
                        "franchise_id": franchise.get("id", ""),
                        "franchise_name": franchise.get("name", ""),
                        "owner_name": franchise.get("owner_name", ""),
                        "logo": franchise.get("logo", "")
                    })
            
            df = pd.DataFrame(franchises_data)
            # Ensure DataFrame has proper columns even when empty
            if df.empty:
                df = pd.DataFrame(columns=["franchise_id", "franchise_name", "owner_name", "logo"])
            logger.info(f"Retrieved {len(df)} franchises")
            return df
            
        except Exception as e:
            logger.error(f"Failed to get franchises: {e}")
            # Return empty DataFrame if franchise info not available
            return pd.DataFrame(columns=["franchise_id", "franchise_name", "owner_name", "logo"])
    
    def get_league_info(self) -> Dict[str, Any]:
        """Get general league information.
        
        Returns:
            Dictionary containing league setup parameters
        """
        logger.info(f"Fetching league info for league {self.league_id}")
        
        try:
            data = self._make_request("league")
            
            if "league" in data:
                league_info = data["league"]
                logger.info(f"Retrieved league info: {league_info.get('name', 'Unknown League')}")
                return league_info
            else:
                logger.warning("No league data found in response")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get league info: {e}")
            raise
    
    def get_rosters_with_player_details(self, franchise_id: Optional[str] = None, week: Optional[str] = None) -> pd.DataFrame:
        """Get rosters with player names and positions by joining roster and player data.
        
        Args:
            franchise_id: Optional franchise ID to get roster for specific team
            week: Optional week number for historical rosters
            
        Returns:
            DataFrame with columns: franchise_id, franchise_name, player_id, player_name, position, status, nfl_team, owner_name
        """
        logger.info(f"Fetching enriched rosters for league {self.league_id}")
        
        try:
            # Get basic roster data (player IDs and franchise assignments)
            rosters_df = self.get_rosters(franchise_id, week)
            
            # Get player details (names, positions, etc.)
            players_df = self.get_players()
            
            # Get franchise details (names, owners, etc.)
            franchises_df = self.get_franchises()
            
            # Join roster data with player details
            enriched_df = rosters_df.merge(
                players_df[['player_id', 'player_name', 'position', 'team']], 
                on='player_id', 
                how='left',
                suffixes=('', '_player')
            )
            
            # Join with franchise details to get franchise names and owner info
            if len(franchises_df) > 0:
                enriched_df = enriched_df.merge(
                    franchises_df[['franchise_id', 'franchise_name', 'owner_name']], 
                    on='franchise_id', 
                    how='left'
                )
            
            # Clean up column names - use player data as primary
            if 'player_name_player' in enriched_df.columns:
                enriched_df['player_name'] = enriched_df['player_name_player']
                enriched_df = enriched_df.drop('player_name_player', axis=1)
            if 'position_player' in enriched_df.columns:
                enriched_df['position'] = enriched_df['position_player']
                enriched_df = enriched_df.drop('position_player', axis=1)
            if 'team_player' in enriched_df.columns:
                enriched_df['nfl_team'] = enriched_df['team_player']
                enriched_df = enriched_df.drop('team_player', axis=1)
            
            logger.info(f"Enriched {len(enriched_df)} roster entries with player and franchise details")
            return enriched_df
            
        except Exception as e:
            logger.error(f"Failed to get enriched rosters: {e}")
            raise
    
    def get_players(self, details: bool = True, since: Optional[str] = None) -> pd.DataFrame:
        """Get all player IDs, names, and positions.
        
        Args:
            details: Whether to include detailed player information
            since: Optional timestamp to get players updated since that time
            
        Returns:
            DataFrame with player information
        """
        params = {}
        if details:
            params["DETAILS"] = "1"
        if since:
            params["SINCE"] = since
        
        logger.info(f"Fetching players for league {self.league_id}")
        
        try:
            data = self._make_request("players", params)
            
            players_data = []
            
            if "players" in data and "player" in data["players"]:
                players = data["players"]["player"]
                
                # Handle single player vs multiple players
                if isinstance(players, dict):
                    players = [players]
                
                for player in players:
                    players_data.append({
                        "player_id": player.get("id", ""),
                        "player_name": player.get("name", ""),
                        "position": player.get("position", ""),
                        "team": player.get("team", ""),
                        "birthdate": player.get("birthdate", ""),
                        "draft_year": player.get("draft_year", ""),
                        "rookie_year": player.get("rookie_year", "")
                    })
            
            df = pd.DataFrame(players_data)
            logger.info(f"Retrieved {len(df)} players")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to get players: {e}")
            raise
    
    def get_trades(self) -> pd.DataFrame:
        """Get all trade transactions for the league.
        
        Returns:
            DataFrame with trade information including:
            - trade_id: Unique identifier for the trade
            - timestamp: When the trade occurred
            - franchise1_id: First franchise involved
            - franchise2_id: Second franchise involved  
            - franchise1_gave_up: What franchise1 traded away
            - franchise2_gave_up: What franchise2 traded away
            - expires: Trade expiration timestamp
            - comments: Trade comments/notes
        """
        logger.info(f"Fetching trades for league {self.league_id}")
        
        try:
            # Get trade transactions using the transactions endpoint
            params = {
                'TRANS_TYPE': 'TRADE'
            }
            
            trade_data = self._make_request('transactions', params)
            
            trades_list = []
            
            # Check if transactions exist
            if 'transactions' not in trade_data:
                logger.info("No transactions found in response")
                return pd.DataFrame(columns=[
                    "trade_id", "timestamp", "franchise1_id", "franchise2_id",
                    "franchise1_gave_up", "franchise2_gave_up", "expires", "comments"
                ])
            
            transactions = trade_data['transactions']
            
            # Handle case where transactions might be a dict (single transaction) or list
            if isinstance(transactions, dict):
                if 'transaction' in transactions:
                    transactions = transactions['transaction']
                    if isinstance(transactions, dict):
                        transactions = [transactions]
                else:
                    transactions = []
            
            logger.debug(f"Found {len(transactions)} transactions")
            
            for transaction in transactions:
                # Extract trade information
                trade_info = {
                    "trade_id": transaction.get("id", ""),
                    "timestamp": transaction.get("timestamp", ""),
                    "franchise1_id": transaction.get("franchise1", ""),
                    "franchise2_id": transaction.get("franchise2", ""),
                    "franchise1_gave_up": transaction.get("franchise1_gave_up", ""),
                    "franchise2_gave_up": transaction.get("franchise2_gave_up", ""),
                    "expires": transaction.get("expires", ""),
                    "comments": transaction.get("comments", "")
                }
                
                trades_list.append(trade_info)
            
            df = pd.DataFrame(trades_list)
            
            # Ensure DataFrame has proper columns even when empty
            if df.empty:
                df = pd.DataFrame(columns=[
                    "trade_id", "timestamp", "franchise1_id", "franchise2_id",
                    "franchise1_gave_up", "franchise2_gave_up", "expires", "comments"
                ])
            
            logger.info(f"Retrieved {len(df)} trades")
            return df
            
        except Exception as e:
            logger.error(f"Failed to get trades: {e}")
            # Return empty DataFrame if trades not available
            return pd.DataFrame(columns=[
                "trade_id", "timestamp", "franchise1_id", "franchise2_id",
                "franchise1_gave_up", "franchise2_gave_up", "expires", "comments"
            ])
