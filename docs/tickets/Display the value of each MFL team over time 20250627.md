---
tags:
  - tickets
---
# Steps

## Pull data from MFL API about a league
create a new section of the bdfl.data module called `mfl_extract`
have functions that allow other parts of the python package to use to get information about a given league.

Use best practices here, I think a class makes the most sense.

Methods should return tabular data as pandas dataframes

The MFL api docs are available at [[mfl_api_docs]]

SAMPLE_LEAGUE_ID=65522

