#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
--------------------------------------------------------------------------
Submission for the SRC FTBL take-home task for the Data Scientist position
--------------------------------------------------------------------------
:author: Emily Chen
:date:   May 2023

Evaluates the rule-based model identify_corner_kicks() using precision
and recall as the evaluation metrics.

Script contains one helper function:
  1. counts_for_prf()
       Counts the number of true positives, false positive, and false
       negative for precision/recall calculations.

USAGE: python3 eval.py

'''
from statistics import mean, median


def counts_for_prf(true, pred):
    '''
    :param true: actual minutes when corners kicks occurred  
    :type  true: list
    :param pred: model-predicted minutes 
    :type  pred: list

    :return: true_pos, false_pos, false_neg 
    :rtype:  int

    Counts the number of true positives, false positive, and false
    negative for precision/recall calculations.

    '''
    true_pos  = 0
    false_pos = 0
    false_neg = 0

    for idx, val in enumerate(true):
        if val in pred:
            true_pos += 1
            pred.remove(val)
        else:
            false_neg += 1

    false_pos = len(pred)

    return true_pos, false_pos, false_neg


def main():

    # if multiple corners take place within a single minute, only counted once
    #   e.g. '3442', two corners take place within the 2nd minute and
    #        two take place within the 56th minute
    true = {"2068": [2, 16, 38, 451, 64, 69, 77, 89, 90],
            "2269": [3, 6, 17, 30, 51, 64, 80, 89],
            "2417": [11, 27, 31],
            "2440": [2, 5, 22, 29, 33, 35, 48, 49, 53, 54, 58, 59, 67, 72, 75, 92],
            "2841": [17, 26, 29, 36, 45, 54, 87],
            "3442": [2, 7, 35, 48, 56, 57, 69, 76],
            "3518": [7, 8, 21, 27, 38, 48, 65, 82, 86],
            "3749": [8, 24, 31, 41, 46, 59, 62],
            "4039": [48, 50, 51, 65, 88, 93]
           }

    pred = {"2068": [16, 35, 38, 63, 65, 70, 77, 89],
            "2269": [6, 7, 41, 56, 64, 89],
            "2417": [11, 44, 62, 79],
            "2440": [2, 34, 35, 58],
            "2841": [17, 18, 19, 24, 26, 29, 46, 54, 63, 87, 89],
            "3442": [7, 35, 48, 56, 57, 69, 76],
            "3518": [8, 21, 25, 27, 34, 81, 82, 86],
            "3749": [40],
            "4039": [14, 48, 88]
           }

    num_corners_per_game = {}
    all_true = []
    all_pred = []
    for key in true.keys():
        if key not in num_corners_per_game:
            num_corners_per_game[key] = len(true[key])

        all_true.extend(true[key])
        all_pred.extend(pred[key])

    print("mean num corners per game: "   + str(mean(num_corners_per_game.values())))
    print("median num corners per game: " + str(median(num_corners_per_game.values())))

    tp, fp, fn = counts_for_prf(all_true, all_pred)

    print("precision: " + str(float(tp/(tp + fp))))
    print("recall: "    + str(float(tp/(tp + fn))))


if __name__ == "__main__":
    main()
