from bdfl.data.get_players import get_players
import pandas as pd


def test_get_players():
    players = get_players()
    assert isinstance(players, pd.DataFrame)
