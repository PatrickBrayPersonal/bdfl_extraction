import ast

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from bdfl.utils import pandas_io


def get_value_history(player_slug: str):
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
    return hist_df


if __name__ == "__main__":
    interim_path = "data/processed/history_cache.csv"
    hist_path = "data/processed/ktc_value_histories_20240929.csv"
    players = pandas_io.file_to_df("data/raw/ktc_players.csv").head(3)
    relevant_cols = [
        "player_name",
        "slug",
        "position",
        "team",
        "age",
        "birthday",
        "height_feet",
        "height_inches",
        "weight",
        "draft_year",
        "seasons_experience",
        "pick_round",
        "pick_num",
    ]
    try:
        value_hists = pd.read_csv(interim_path)
    except Exception as e:
        print(e)
        value_hists = [
            get_value_history(slug)
            for slug in tqdm(players["slug"], desc="Processing players")
        ]
        value_hists = pd.concat(value_hists)
        value_hists.to_csv(interim_path, index=False)

    value_hists = value_hists.rename(columns={"d": "date", "v": "value"})
    output = value_hists.merge(players[relevant_cols], on="slug")
    output.to_csv("data/processed/ktc_player_value_histories_20240929.csv", index=False)
    print(output)
