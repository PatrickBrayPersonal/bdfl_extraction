from bdfl.data.get_players import get_players
from bdfl.data.get_draftguide import get_draft_guide
from omegaconf import OmegaConf
import pandas as pd


def test_get_draftguide():
    cfg = OmegaConf.load("configs/get_draftguide.yaml")
    players = get_players()
    draft_guide = get_draft_guide(players, columns=cfg.columns)
    assert isinstance(draft_guide, pd.DataFrame)
