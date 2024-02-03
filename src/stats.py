import csv
from const import *
"""
STAT GATHERING FUNCTIONS

All stats to collect:
Team batting averageXX
HBP
ISO (isolated power)XX
On Base PercentageXX
Times on bases
OPSXX
ERAXX
FIPXX
K/9XX
HR/9XX
BB/9XX
GBF (ground ball fly ball ratio)
A_HR - at bats per home run
HRH - home runs per hits
TB - Total bases
SLGXX
XBH - extra base hits
IPXX
WHIPXX
Defence-Independent Component ERA
KBB - strikeouts to walk ratio
Total Runs ScoredXX
Stolen Bases
Team Wins/LossesXX
Save Pct
Double Plays Turned
Recent Success
Fielding Percentage
WAR
Defensive Efficiency Ratio (DER)
Home vs Away wins (subtract home team's home wins from visiting teams away wins)XX
"""

"""
Stats to measure:
TB
XBH
Recent Success 
"""

# TODO: Once all stats calculated, search through all calculateable stats and remove calculations for unused ones
fieldnames = ['Date', 'Home', 'Visitor', 'GameID', 'WinDiff', 'HomeAdv', 'WPctDiff', 'RunDiff', 'RPGDiff', 'H2H', 'AVG', 'SLG', 'OBP', 'ISO', 'OPS', 'ERA', 'WHIP', 'BB9', 'K9', 'HR9', 'FIP']
results = []

def log_games():
    for gameid in GAMES:
        game = GAMES[gameid]
        # Checks that both teams have played at least 7 games
        if above_threshold(game):
            data = {'Date': game.date, 'Home': game.home, 'Visitor': game.visitor, 'GameID': game.id}
            team_stats = game.team_stats
            for stat in team_stats:
                if stat != 'Total Games':
                    data[stat] = team_stats[stat]
            data['H2H'] = game.h2h_totals['HWins'] - game.h2h_totals['VWins']
            batting_stats = game.batting_stats
            for stat in batting_stats:
                data[stat] = batting_stats[stat]
            pitcher_stats = game.comp_results
            for stat in pitcher_stats:
                data[stat] = pitcher_stats[stat]
            results.append(data)
            print(f'{game.id} Added')
        
    with open('stats2.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow(result)
    return True
