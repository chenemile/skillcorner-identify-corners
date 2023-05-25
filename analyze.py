#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
--------------------------------------------------------------------------
Submission for the SRC FTBL take-home task for the Data Scientist position
--------------------------------------------------------------------------
:author: Emily Chen
:date:   May 2023

Visualizes the output of identify_corner_kicks() as animated gifs
to facilitate tactical analysis
  * RED dot    = ball
  * BLUE dot   = home team
  * ORANGE dot = away team
  * BLACK dot  = unknown team

Script contains one helper function:
  1. get_player_ids() 
       Gets each player's tracking ID and assigns the player
       to either the home team or away team

Outputs a directory '[GAME ID]_analysis' that stores the animated gifs

REQUIREMENTS: pandas, numpy, matplotlib, ffmpeg

USAGE: python3 analyze.py [path-to-dir-containing-match-data]
  e.g. python3 analyze.py data/matches/3442

'''
from identify_corners import identify_corner_kicks

import argparse
import glob
import json
import os
import sys

import pandas as pd
import warnings

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation


# for debugging purposes
#pd.set_option("display.max_columns", None)
#np.set_printoptions(threshold=sys.maxsize)

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)


def get_player_ids(match_info):
    '''
    :param match_info: match_data.json
    :type  match_info: pandas dataframe

    :return: home_players, away_players
    :rtype:  list

    Gets each player's tracking ID stored in "trackable_object"
    and assigns the player to either the home team or away team

    '''
    home_team_id = match_info["home_team"]["id"]
    away_team_id = match_info["away_team"]["id"]

    home_players = []
    away_players = []

    for player in match_info["players"]:
        if player["team_id"] == home_team_id:
            home_players.append(player["trackable_object"])
        elif player["team_id"] == away_team_id:
            away_players.append(player["trackable_object"])

    return home_players, away_players


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('match_dir', help='path to directory containing match_data.json \
                                           and structured_data.json')
    args = parser.parse_args()

    # creates a folder 'analysis' to store output
    dirname = (args.match_dir).rsplit("/", 1)[1] + "_analysis"
    if os.path.exists(dirname):
        for root, dirs, files in os.walk(dirname):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(dirname)
    os.mkdir(dirname)

    # ---------------------------------
    # read in data and identify corners
    # ---------------------------------
    home_team_ids = []
    away_team_ids = [] 

    for jsonfile in glob.glob(args.match_dir + "/*.json"):
        with open(jsonfile, "r") as json_data:

            basename = jsonfile.rsplit("/", 1)[1]

            if basename == "match_data.json":
                match_data = json.load(json_data)
                home_team_ids, away_team_ids = get_player_ids(match_data)

            corner_kicks = []
            if basename == "structured_data.json":
                tracking_data = pd.read_json(json_data)
                corner_kicks  = identify_corner_kicks(tracking_data)

    # ----------------------------------
    # plot corner kicks as animated gifs
    # ----------------------------------

    # assumes a corner kick occurs once per minute, e.g.
    #   the frame at time 1:23:10 is assumed to be the same
    #   corner kick as the frame at time 1:23:80
    prev_min = 0

    for kick in corner_kicks:

        minute = int(kick["time"].split(":")[0])

        # logs the team ('home' or 'away') of each trackable object
        # to assist with color-coding players in animated gif
        team_assignment = pd.DataFrame()

        if prev_min != minute:

            # create dataframes that store the frame, time, and x or y coordinates
            # of all the trackable objects in each frame
            #
            #     Frame  Time      Obj0       Obj1       Obj2       ...
            #     11823  15:45.00  [x-coord]  [x-coord]  [x-coord]  ...
            #     11824  15:45.10  [x-coord]  [x-coord]  [x-coord]  ...
            #
            #     Frame  Time      Obj0       Obj1       Obj2       ...
            #     11823  15:45.00  [y-coord]  [y-coord]  [y-coord]  ...
            #     11824  15:45.10  [y-coord]  [y-coord]  [y-coord]  ...
            #
            # dataframes are used for scatterplotting
            #
            x_positions = pd.DataFrame(columns = ["Frame", "Time"])
            y_positions = pd.DataFrame(columns = ["Frame", "Time"])
    
            frame_number = kick["frame"]
    
            # get the corner kick frame and all frames within 30 seconds after
            df_for_analysis = tracking_data.iloc[frame_number:frame_number+300]
    
            # just in case, for objects with no tracking_id
            no_id_counter = 0
    
            for frame in range(len(df_for_analysis)):
                data = df_for_analysis.iloc[frame]["data"]
    
                # add current frame and time to 'x_positions' and 'y_positions'
                frame_time = {"Frame": df_for_analysis.iloc[frame]["frame"], \
                              "Time": df_for_analysis.iloc[frame]["time"]}
                frame_time_df = pd.DataFrame(frame_time, index=[0])
    
                x_positions = pd.concat([x_positions, frame_time_df])
                y_positions = pd.concat([y_positions, frame_time_df])
    
                # check if there's tracking data and a trackable object
                if data and any("trackable_object" in elem for elem in data):
    
                    # get the id and x-y coordinates of the trackable object
                    for elem in data:
                        if "trackable_object" in elem:
                            tracking_id = elem["trackable_object"]
                        else:
                            tracking_id = "nan" + str(no_id_counter)
                            no_id_counter += 1

                        x_coord = elem["x"]
                        y_coord = elem["y"]
    
                        # update 'x_positions' and 'y_positions'
                        if tracking_id not in x_positions.columns:
                            x_positions[tracking_id] = ''
    
                        if tracking_id not in y_positions.columns:
                            y_positions[tracking_id] = ''
    
                        x_positions.iat[len(x_positions.index)-1, x_positions.columns.get_loc(tracking_id)] = x_coord
                        y_positions.iat[len(y_positions.index)-1, y_positions.columns.get_loc(tracking_id)] = y_coord

                        # update team assignments
                        if tracking_id not in team_assignment.columns:
                            if tracking_id == 55:
                                team_assignment["55"] = ["ball"]
                            elif tracking_id in home_team_ids:
                                team_assignment[tracking_id] = ["home"]
                            elif tracking_id in away_team_ids:
                                team_assignment[tracking_id] = ["away"]
                            else:
                                team_assignment[tracking_id] = ["unknown"]
    
            # convert 'x_positions' and 'y_positions' to numpy arrays,
            # excluding 'Frame' and 'Time' columns
            x_over_time = x_positions[x_positions.columns[2:]].to_numpy()
            y_over_time = y_positions[y_positions.columns[2:]].to_numpy()
    
            x_over_time[x_over_time == ''] = np.nan
            y_over_time[y_over_time == ''] = np.nan

            # map 'team_assignment" to colors
            colors = {"ball": "red", "home": "blue", "away": "orange", "unknown": "black"}
            team_colors = team_assignment.squeeze().map(colors)
    
            # initialize figure for scatterplot and mark x-y axes
            fig = plt.figure()
            ax = plt.axes(xlim=(-52.5,52.5), ylim=(-34,34))

            scatterplot = ax.scatter(x_over_time[0], y_over_time[0], \
                                     s=9, c=team_colors)
    
            def update(frame_number):
                x = x_over_time[frame_number]
                y = y_over_time[frame_number]

                x_y = np.zeros(shape=(len(x), 2))

                for i in range(len(x)):
                    x_y[i] = [x[i], y[i]]

                scatterplot.set_offsets(x_y)
                return scatterplot,
    
            anim = FuncAnimation(fig, update, interval=10)
            anim.save(dirname + "/minute_" + str(minute) + ".gif", writer = "ffmpeg", fps = 10)

            prev_min = minute


if __name__ == "__main__":
    main()
