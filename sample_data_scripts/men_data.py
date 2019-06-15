# -*- coding: utf-8 -*-
"""
Tony Silva
CrossFit Games Open 2019 API Data Project
"""

import requests
import pandas as pd
import csv
from datetime import date

# ping the CF Games Open leaderboard and store the JSON as csv to be used in analysis

entrants = []
leaderboard_scores = []
failed_pages = []


url = 'https://games.crossfit.com/competitions/api/v1/competitions/open/2019/leaderboards?division=1&' \
    'region=0&scaled=0&sort=0&occupation=0&page=1'
response = requests.get(url)
json_output = response.json()

# Pull the total number pages in the API so we know how many pages we should iterate through
for key, value in json_output.items():
    if key == 'pagination':
        totalPages = value['totalPages']
        break
    else:
        continue


for i in range(1, totalPages+1):
    # Attempt to get the JSON data, if not then log that it failed in a list
    try:
        url = 'https://games.crossfit.com/competitions/api/v1/competitions/open/2019/leaderboards?division=1&region=0&scaled=0&sort=0&occupation=0&page=' + str(
            i)
        response = requests.get(url)
        json_output = response.json()
        # Athletes is a list of JSON athletes files
        athletes = json_output["leaderboardRows"]
        print(i)
    except:
        print(i, " - failed to process page")
        failed_pages.append(i)
        continue

    # The athlete object is a dictionary containing entrant information and scores
    # scores are stored in a list of dictionaries for each score.

    for athlete in athletes:
        entrant = athlete["entrant"]
        scores = athlete["scores"]

        # change weight from kilos to pounds
        if "kg" in entrant["weight"]:
            lbs = entrant["weight"].split()
            lb = int(lbs[0])
            lb = round(lb * 2.20462)
            entrant["weight"] = lb
        elif "lb" in entrant["weight"]:
            lbs = entrant["weight"].split()
            lb = int(lbs[0])
            entrant["weight"] = lb

        # Change height from centimeters to inches
        if "cm" in entrant["height"]:
            height = entrant["height"].split()
            h = int(height[0])
            h = round(h * 0.393701)
            entrant["height"] = h
        elif "in" in entrant["height"]:
            height = entrant["height"].split()
            h = int(height[0])
            entrant["height"] = h

        # Iterate through the scores and create new variables for each
        # scores will be integers of either reps, seconds, or weight (lbs)
        # create the "goal" of the workout, will be used to measure if someone
        # beat a time cap or not.
        for score in scores:
            score["competitorId"] = entrant["competitorId"]
            if "reps" in score["scoreDisplay"]:
                reps = score["scoreDisplay"].split()
                s = int(reps[0])
                score["cf_score"] = s
                score["type"] = 'reps'
            if ":" in score["scoreDisplay"]:
                try:
                    score["cf_score"] = score["time"]
                except:
                    try:
                        x = score["scoreDisplay"].split(':')
                        t = int(x[0]) * 60 + int(x[1])
                        score["cf_score"] = t
                    except:
                        score["cf_score"] = ""
                score["type"] = 'time'
            if "lb" in score["scoreDisplay"]:
                lbs = score["scoreDisplay"].split()
                lb = int(lbs[0])
                score["cf_score"] = lb
                score["type"] = 'weight'
            elif "kg" in score["scoreDisplay"]:
                lbs = score["scoreDisplay"].split()
                lb = int(lbs[0])
                lb = round(lb * 2.20462)
                score["cf_score"] = lb
                score["type"] = 'weight'

            # Pending 2019 Open work outs release
            # Wod types, utlimate goal of the workout
            # if score["ordinal"] == 1:
            #     score["wod_type"] = 'reps'
            # elif score["ordinal"] == 2:
            #     score["wod_type"] = 'time'
            # elif score["ordinal"] == 3:
            #     score["wod_type"] = 'weight'
            # elif score["ordinal"] == 4:
            #     score["wod_type"] = 'time'
            # elif score["ordinal"] == 5:
            #     score["wod_type"] = 'time'
            # elif score["ordinal"] == 6:
            #     score["wod_type"] = 'reps'

        entrants.append(entrant)
        leaderboard_scores = leaderboard_scores + scores

entrants_csv = pd.DataFrame(entrants)
scores_csv = pd.DataFrame(leaderboard_scores)

today = str(date.today())
entrants_csv.to_csv('~/Data/athletes_men_2019_'+today+'.csv', index=False)
scores_csv.to_csv('~/Data/scores_men_2019_'+today+'.csv', index=False)

# with open('~/Data/failed_pages_women.csv', 'w') as myfile:
#     wr = csv.writer(myfile, lineterminator='\n')
#     for page in failed_pages:
#         wr.writerow([page])
