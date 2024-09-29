import ast

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Send a GET request to the website
response = requests.get("https://keeptradecut.com/dynasty-rankings")
# Get the HTML content from the resPponse
html = response.text

# Create a BeautifulSoup object
soup = BeautifulSoup(html, "html.parser")

# Extract the desired information
# Find the <script> tag within the <body> tag
script = soup.select_one("body > script").string
player_string = script.split("\n")[2]
player_string = player_string.split("playersArray = ")[1]
player_string = player_string[0:-2]
player_string = player_string.replace("false", "False")
player_string = player_string.replace("true", "True")

players = pd.DataFrame(ast.literal_eval(player_string))

print(players)
players.to_parquet("data/raw/ktc_players.parquet")
players.to_csv("data/raw/ktc_players.csv")
