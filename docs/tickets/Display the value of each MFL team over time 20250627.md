---
tags:
  - tickets
---
# Steps

## Pull data from MFL API about a league
create a new section of the bdfl module called `mfl_extract`
have functions that allow other parts of the python package to use to get information about a given league.

Use best practices here, I think a class makes the most sense.

Methods should return tabular data as pandas dataframes

The MFL api docs are available at [[mfl_api_docs]]

SAMPLE_LEAGUE_ID=65522

## Allow connection through the frontend
Populate the frontend from 

User enters their MFL league ID and the app hits the MFL API and returns the name of the league which is rendered in the app.


## Connect the MFL data to the KTC data
Could be useful to merge on the player slug combined with the position as an ID

User sees the cumulative value of their entire team right now

## Collect data on historical rosters of each team
Use the historical trades to infer what the rosters of each team in the league was throughout all years available

Present this data as a 