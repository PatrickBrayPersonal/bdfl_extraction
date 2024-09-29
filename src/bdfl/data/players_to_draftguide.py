from datetime import datetime

import pandas as pd

players = pd.read_parquet("data/raw/ktc_players.parquet")

players = players.drop(columns=["superflexValues"])


players = pd.concat(
    [players.drop(["oneQBValues"], axis=1), players["oneQBValues"].apply(pd.Series)],
    axis=1,
)

players["age"] = (
    datetime.now().timestamp() - players["birthday"].fillna(0).astype(int)
) / (365.25 * 24 * 60 * 60)
players["selected"] = ""
players["notes"] = ""

opinion_cols = [
    "value",
    "rookieRank",
    "rookieTier",
    "rookiePositionalRank",
    "rookiePositionalTier",
    "positionalRank",
    "positionalTier",
]
players.rename(columns={col: f"{col}_ktc" for col in opinion_cols}, inplace=True)


players = players[
    [
        "playerName",
        "selected",
        "value_ktc",
        "position",
        "rookieRank_ktc",
        "rookieTier_ktc",
        "rookiePositionalRank_ktc",
        "rookiePositionalTier_ktc",
        "age",
        "team",
        "college",
        "positionalRank_ktc",
        "positionalTier_ktc",
        "pickRound",
        "pickNum",
        "seasonsExperience",
        "rookie",
    ]
]


players.to_csv("data/processed/ktc_players.csv", index=False)
