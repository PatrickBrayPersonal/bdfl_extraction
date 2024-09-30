import ast

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from bdfl.utils import pandas_io
from omegaconf import OmegaConf
from bdfl.data.get_players import get_players


def _get_player_value_hist(player_slug: str):
    # Send a GET request to the website
    response = requests.get(
        f"https://keeptradecut.com/dynasty-rankings/players/{player_slug}"
    )
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract the desired information
    # Find the <script> tag within the <body> tag
    script = soup.select_one("body > script").string

    adjacent_players = script.split("var playerOneQB = ")[1].split(";\r\n")[0]
    adjacent_players = adjacent_players.replace("false", "False").replace(
        "true", "True"
    )

    adjacent_players = ast.literal_eval(adjacent_players)
    hist = adjacent_players["overallValue"]

    hist_df = pd.DataFrame(hist)
    hist_df["slug"] = player_slug
    hist_df = hist_df.rename(columns={"d": "date", "v": "value"})
    return hist_df


def get_value_hist(players: pd.DataFrame, relevant_cols: list, head: int = 0):
    if head > 0:
        players = players.head(head)
    value_hists = [
        _get_player_value_hist(slug)
        for slug in tqdm(players["slug"], desc="Processing players")
    ]
    value_hists = pd.concat(value_hists)
    output = value_hists.merge(players[relevant_cols], on="slug")
    return output


if __name__ == "__main__":
    cfg = OmegaConf.load("configs/players_to_value_hist.yaml")
    players = get_players()
    value_hist = get_value_hist(players, **cfg.get_value_hist)
    pandas_io.write(value_hist, **cfg.out)
