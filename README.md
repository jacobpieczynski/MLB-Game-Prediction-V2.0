Version 2.0 of my MLB Game Prediction model
------------------------------------

This began as my final project for CS50 and has evolved into a research project I'm currently writing a paper on.
V1.0 had a maximum accuracy of 57.2%, compared to student averages of 55-56% with a logistic regression model.
Target accuracy is up to 59-60%, bringing in data from the past decade worth of seasons.

Executables:
------------------------------------
Main.py
------------------------------------
Main.py searches through the roster, gamelog, and pbp (Play-by-Play) data to create combined.csv, test.csv, and train.csv. Test and train are the same data as combined, just split into prior to 2022 and after 2022 for train and test respectively.

Train.py
------------------------------------
Train.py accesses data in combined.csv, or test/train.csv (depending on the configuration in log_games.py), builds a Linear Regresion model off of it and tests it.




Disclaimer:
 The information used here was obtained free of
 charge from and is copyrighted by Retrosheet.  Interested
 parties may contact Retrosheet at "www.retrosheet.org".
