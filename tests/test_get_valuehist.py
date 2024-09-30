import pandas as pd
from omegaconf import OmegaConf
from bdfl.data.get_players import get_players
from bdfl.data.get_valuehist import get_value_hist


def test_get_value_hist():
    cfg = OmegaConf.load("configs/get_valuehist.yaml")
    cfg.get_value_hist.head = 2
    players = get_players()
    value_hist = get_value_hist(players, **cfg.get_value_hist)
    assert isinstance(value_hist, pd.DataFrame)
