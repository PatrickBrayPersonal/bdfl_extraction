from datetime import datetime

import pandas as pd
from omegaconf import OmegaConf
from bdfl.data.get_players import get_players
from bdfl.utils import pandas_io


def get_draft_guide(players: pd.DataFrame, columns: list):
    players = players.copy()
    players = players.drop(columns=["superflexValues"])

    players = pd.concat(
        [
            players.drop(["oneQBValues"], axis=1),
            players["oneQBValues"].apply(pd.Series),
        ],
        axis=1,
    )

    players["age"] = (
        datetime.now().timestamp() - players["birthday"].fillna(0).astype(int)
    ) / (365.25 * 24 * 60 * 60)
    players["selected"] = ""
    players["notes"] = ""

    players = players[players["rookie"]]

    return players[columns]


if __name__ == "__main__":
    cfg = OmegaConf.load("configs/players_to_draftguide.yaml")
    players = get_players()
    draft_guide = get_draft_guide(players, columns=cfg.columns)
    pandas_io.write(draft_guide, **cfg.out)
