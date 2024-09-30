import ast

import pandas as pd
import requests
from bs4 import BeautifulSoup
from bdfl.utils import pandas_io
from omegaconf import OmegaConf


@pandas_io.snake_case_columns
def get_players() -> pd.DataFrame:
    response = requests.get("https://keeptradecut.com/dynasty-rankings")
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract the desired information
    # Find the <script> tag within the <body> tag
    script = soup.select_one("body > script").string
    player_string = script.split("\n")[2]
    player_string = player_string.split("playersArray = ")[1]
    player_string = player_string[0:-2]
    player_string = player_string.replace("false", "False")
    player_string = player_string.replace("true", "True")

    players = pd.DataFrame(ast.literal_eval(player_string))
    return players


if __name__ == "__main__":
    cfg = OmegaConf.load("configs/get_players.yaml")
    players = get_players()
    pandas_io.write(players, **cfg.out)
