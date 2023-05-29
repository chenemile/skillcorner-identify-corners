#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
--------------------------------------------------------------------------
Submission for the SRC FTBL take-home task for the Data Scientist position
--------------------------------------------------------------------------
:author: Emily Chen
:date:   May 2023

Identifies frames and times of possible corner kicks in the SkillCorner dataset

Script contains two helper functions:
  1. identify_corner_kicks()
       A rule-based model that identifies the frames and times of
       possible corner kicks, given the x-y coordinates of the ball
       or number of players in the 18-yard box

  2. write_out_to_csv()
       Writes the output of identify_corner_kicks() to a three-column
       csv file, listing the frame, time, and corner-taking team

Outputs a directory 'corners' that stores the csv file for each game

REQUIREMENTS: pandas

USAGE: python3 identify_corners.py
       Assumes the SkillCorner dataset 'data' is in the same folder

'''
import csv
import glob
import json
import os

import pandas as pd


# for debugging purposes
#pd.set_option('display.max_columns', None)

def identify_corner_kicks(df):
    '''
    :param df: all the data stored in 'structured_data.json'
    :type  df: pandas dataframe

    :return: possible_corners
    :rtype:  list of pandas dataframes

    A rule-based model that identifies the frames and times of
    possible corner kicks, given the x-y coordinates of the ball
    or number of players in the 18-yard box

    '''
    possible_corners = []

    for frame in range(len(df)):
    
        tracking_data = df["data"].iloc[frame]
    
        # check if there's tracking data
        if tracking_data and any("trackable_object" in elem for elem in tracking_data):
    
            num_obj = 0

            # check if there's a trackable object and if object is the ball
            for elem in tracking_data:
                if "trackable_object" in elem and elem["trackable_object"] == 55:
    
                    # absolute value of the x-y coordinates of the ball
                    x_coord = abs(elem["x"])
                    y_coord = abs(elem["y"])
                    if "z" in elem:
                        z_coord = elem["z"]
                    radius  = 1.2

                    # pythagorean theorem for circles
                    #   checks if the ball is within radius of corner arc 
                    #   with some leeway given to include radius of the ball
                    if (x_coord - 52.5)**2 + (y_coord - 34)**2 <= radius:
                        if z_coord > 1:
                            break
                        possible_corners.append(df.iloc[frame])

                # check number of trackable objects within 18-yard box
                if "trackable_object" in elem:
                    x_coord = abs(elem["x"])
                    y_coord = abs(elem["y"])

                    if x_coord >= 36 and x_coord <= 52.5 and \
                       y_coord >= 0  and y_coord <= 21.16:
                        num_obj += 1

            if num_obj >= 16:
                possible_corners.append(df.iloc[frame])

    return possible_corners


def write_out_to_csv(dirname, match_data, corners):
    '''
    :param dirname: path to folder in which to store csv
    :type  dirname: str
    :param match_data: all the data stored in 'match_data.json'
    :type  match_data: pandas dataframe
    :param corners: possible corner kick situations
    :type  corners: list of pandas dataframes

    Writes the output of identify_corner_kicks() to a three-column csv file,
    listing the 'frame', the corner-taking 'team', and the 'time'

    '''
    date      = str(match_data["date_time"])
    home_team = match_data["home_team"]["name"].replace(" ","_")
    away_team = match_data["away_team"]["name"].replace(" ","_")
    match_id  = str(match_data["id"])
   
    filename  = dirname + "/" + match_id + "_" + home_team + "(H)_" + \
               away_team + "(A)_" + date + ".csv"

    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Frame", "Team", "Time"])

        for df in corners:
            if df["possession"]["group"] == "home team":
                writer.writerow([df["frame"], home_team, df["time"]])
            elif df["possession"]["group"] == "away team":
                writer.writerow([df["frame"], away_team, df["time"]])
            else:
                writer.writerow([df["frame"], "n/a", df["time"]])


def main():

    # creates a folder 'corners' to store output, i.e.
    #   csv files listing frames and time stamps of
    #   the corner kicks from each game
    dirname = "corners"
    if os.path.exists(dirname):
        for root, dirs, files in os.walk(dirname):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(dirname)
    os.mkdir(dirname)

    for jsonfile in glob.glob("data/matches/*/*.json"):
        with open(jsonfile, 'r') as json_data:

            basename = jsonfile.rsplit("/", 1)[1]

            if basename == "match_data.json":
                match_data = json.load(json_data)
    
            corner_kicks = []
            if basename == "structured_data.json":
                tracking_data = pd.read_json(json_data)
                corner_kicks  = identify_corner_kicks(tracking_data)
            
            write_out_to_csv(dirname, match_data, corner_kicks)


if __name__ == "__main__":
    main()
