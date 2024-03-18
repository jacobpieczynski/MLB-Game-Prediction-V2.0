import csv
from const import *
from stat_calc import calc_whisnant
"""
STAT GATHERING FUNCTIONS

All stats to collect:
Team batting averageXX
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
Fielding Independent PitchingXX
"""

"""
Stats to measure:
TB
XBH
Recent Success 
"""
# STATS: DPythag, DPythag_10d, DOBP, DOBP_10d, DSLG, DSLG_10d, DLog5, DERA, DWHIP, DWHIP_10d, DFIP, DWhisnant, DSP_ERA, DRA_Var
# STATS: DWhisnant, DRA_Var
# TODO: Once all stats calculated, search through all calculateable stats and remove calculations for unused ones
#fieldnames = ['Date', 'Home', 'Visitor', 'GameID', 'Year', 'WinDiff', 'HomeAdv', 'WPctDiff', 'Log5', 'RunDiff', 'RADiff', 'RPGDiff', 'H2H', 'AVG', 'SLG', 'OBP', 'ISO', 'OPS', 'DER', 'PythagDiff', 'ERA', 'WHIP', 'BB9', 'K9', 'HR9', 'FIP', 'HWin']
fieldnames = ['Date', 'Home', 'Visitor', 'GameID', 'Year', 'WinDiff', 'HomeAdv', 'WPctDiff', 'RunDiff', 'RPGDiff', 'RADiff', 'PythagDiff', 'Log5', 'PythagDiff_10d', 'Whisnant', 'OBP', 'SLG', 'AVG', 'ISO', 'OBP_10d', 'SLG_10d', 'AVG_10d', 'ISO_10d', 'SP_ERA', 'SP_WHIP', 'SP_FIP', 'ERA', 'WHIP', 'FIP', 'H2H', 'WHIP_10d', 'ERA_10d', 'FIP_10d', 'OPS', 'OPS_10d', 'SP_BB9', 'SP_HR9', 'SP_K9', 'BB9', 'K9', 'HR9', 'BB9_10d', 'K9_10d', 'HR9_10d', 'HWin']
train, test = [], []
checked = []

def log_games():
    for year in GAMES:
        for team in GAMES[year]:
            for gameid in GAMES[year][team]:
                game = GAMES[year][team][gameid]
                # Checks that both teams have played at least 7 games
                if gameid not in checked and above_threshold(game):
                    data = {'Date': game.date, 'Home': game.home, 'Visitor': game.visitor, 'GameID': game.id, 'Year': int(game.year)}
                    team_stats = game.get_team_records()
                    data['PythagDiff'] = team_stats['PythagDiff']
                    data['Log5'] = team_stats['Log5']
                    data['WinDiff'] = team_stats['WinDiff'] ##
                    data['HomeAdv'] = team_stats['HomeAdv'] ##
                    data['WPctDiff'] = team_stats['WPctDiff'] ##
                    data['RunDiff'] = team_stats['RunDiff'] ##
                    data['RPGDiff'] = team_stats['RPGDiff'] ##
                    data['RADiff'] = team_stats['RADiff'] ##

                    home_start, visitor_start = get_prior_gameids(game.home, get_prior_date(game.date))[0][:8], get_prior_gameids(game.visitor, get_prior_date(game.date))[0][:8]
                    team_stats_10d = game.get_team_records(home_start, visitor_start)
                    data['PythagDiff_10d'] = team_stats_10d['PythagDiff']
                    
                    batting_stats = game.team_batting_stats()
                    data['OBP'] = batting_stats['OBP']
                    data['SLG'] = batting_stats['SLG']
                    data['AVG'] = batting_stats['AVG'] ##
                    data['ISO'] = batting_stats['ISO'] ##
                    data['OPS'] = batting_stats['OPS'] ##

                    batting_stats_10d = game.team_batting_stats(home_start, visitor_start)
                    data['OBP_10d'] = batting_stats_10d['OBP']
                    data['SLG_10d'] = batting_stats_10d['SLG']
                    data['AVG_10d'] = batting_stats_10d['AVG'] ##
                    data['ISO_10d'] = batting_stats_10d['ISO'] ##
                    data['OPS_10d'] = batting_stats_10d['OPS'] ##

                    pitcher_stats = game.comp_sps()
                    data['SP_ERA'] = pitcher_stats['ERA']
                    data['SP_WHIP'] = pitcher_stats['WHIP']
                    data['SP_FIP'] = pitcher_stats['FIP'] ##
                    data['SP_BB9'] = pitcher_stats['BB9'] ##
                    data['SP_K9'] = pitcher_stats['K9'] ##
                    data['SP_HR9'] = pitcher_stats['HR9'] ##

                    team_pitcher_stats = game.comp_pitchers()
                    data['ERA'] = team_pitcher_stats['ERA']
                    data['WHIP'] = team_pitcher_stats['WHIP']
                    data['FIP'] = team_pitcher_stats['FIP']
                    data['BB9'] = team_pitcher_stats['BB9'] ##
                    data['K9'] = team_pitcher_stats['K9'] ##
                    data['HR9'] = team_pitcher_stats['HR9'] ##

                    h2h = game.head_to_head()
                    data['H2H'] = h2h['HWins'] - h2h['VWins'] ##

                    team_pitcher_stats_10d = game.comp_pitchers(home_start, visitor_start)
                    data['WHIP_10d'] = team_pitcher_stats_10d['WHIP']
                    data['ERA_10d'] = team_pitcher_stats_10d['ERA'] ##
                    data['FIP_10d'] = team_pitcher_stats_10d['FIP'] ##
                    data['BB9_10d'] = team_pitcher_stats_10d['BB9'] ##
                    data['K9_10d'] = team_pitcher_stats_10d['K9'] ##
                    data['HR9_10d'] = team_pitcher_stats_10d['HR9'] ##

                    data['Whisnant'] = calc_whisnant(team_stats['HRPG'], team_stats['VRPG'], batting_stats['HSLG'], batting_stats['VSLG'])

                    data['HWin'] = game.home_win
                    if data['Year'] > 2021:
                        test.append(data)
                    else:
                        train.append(data)
                    checked.append(gameid)
                    print(f'{game.id} Added')
        
    with open('train.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in train:
            writer.writerow(result)
    with open('test.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in test:
            writer.writerow(result)
    with open('combined.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in test:
            writer.writerow(result)
        for result in train:
            writer.writerow(result)
    return True

"""
def log_games():
    for year in GAMES:
        for gameid in GAMES[year]:
            game = GAMES[year][gameid]
            # Checks that both teams have played at least 7 games
            if above_threshold(game):
                data = {'Date': game.date, 'Home': game.home, 'Visitor': game.visitor, 'GameID': game.id, 'Year': int(game.year)}
                team_stats = game.get_team_records()
                #print(f'{game.id} {team_stats}')
                for stat in team_stats:
                    if stat != 'Total Games':
                        data[stat] = team_stats[stat]
                h2h = game.head_to_head()
                data['H2H'] = h2h['HWins'] - h2h['VWins']
                batting_stats = game.batting_stats
                for stat in batting_stats:
                    data[stat] = batting_stats[stat]
                pitcher_stats = game.comp_results
                for stat in pitcher_stats:
                    data[stat] = pitcher_stats[stat]
                data['HWin'] = game.home_win
                results.append(data)
                print(f'{game.id} Added')
        
    with open('stats2.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow(result)
    return True
"""