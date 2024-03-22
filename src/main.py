from const import *
from parse import *
from log_games import log_games

import cProfile

def main():
    # Loads the roster files
    print('-' * 50)
    print('LOADING ROSTERS')
    for year in ROS_FILES:
        for ros in ROS_FILES[year]:
            if not parse_roster(ros):
                print(f'FAILED TO OPEN ROSTER {ros}')
                print('-' * 50, end='\n\n')
                return False
            print(ros)
    # SHOHEI RULE
    #tmp = Pitcher('ohtas001,Ohtani,Shohei,L,R,ANA,DH')
    #PLAYERS[tmp.id] = tmp
    print('\nLOADED')
    print('-' * 50, end='\n\n')

    # Loads the GL files
    print('-' * 50)
    print('LOADING GAME LOGS')
    for gl in GL_FILES:
        if not parse_log(gl, gl[5:9]):
            print(f'FAILED TO OPEN FILE {gl}')
            print('-' * 50, end='\n\n')
            return False
        print(gl)
    print('\nLOADED')
    print('-' * 50, end='\n\n')

    # Loads the PBP files
    print('-' * 50)
    print('LOADING PBPs')
    for year in PBP_FILES:
        if year > '2022':
            for pbp in PBP_FILES[year]:
                if not parse_pbp(pbp):
                    print(f'FAILED TO OPEN FILE {pbp}')
                    print('-' * 50, end='\n\n')
                    return False
                print(pbp)

    print('\nLOADED')
    print('-' * 50, end='\n\n')

    # Writes the Data
    print('-' * 50)
    print('LOADING DATA')
    if not log_games():
       print(f'FAILED TO LOG GAMES')
       print('-' * 50, end='\n\n')
       return False
    
    print('\nLOADED')
    print('-' * 50, end='\n\n')
    # Testing
    
    """home_ros = GAMES['2023']['ARI']['20230510ARIMIA'].home_starting_lineup[2:]
    vis_ros = GAMES['2023']['MIA']['20230510ARIMIA'].visitor_starting_lineup[2:]
    print(len(home_ros))
    print(vis_ros)
    home_hits, home_abs = 0, 0
    vis_hits, vis_abs = 0, 0
    GAMES['2023']['ARI']['20230510ARIMIA'].team_batting_stats()
    for player in home_ros:
        print(f'MAIN: {player.name} {player.id} {player.get_totals("ARI", "20230509")}')
        home_hits += player.get_totals("ARI", "20230509")['H']
        home_abs += player.get_totals("ARI", "20230509")['AB']
    for player in vis_ros:
        print(f'{player.name} {player.id} {player.get_totals("MIA", "20230509")}')
        vis_hits += player.get_totals("MIA", "20230509")['H']
        vis_abs += player.get_totals("MIA", "20230509")['AB']
    print(f"{PLAYERS['carrc005'].get_totals('ARI', '20230510')}")
    print(f'ARI: {home_hits} hits in {home_abs} at bats, batting average of {home_hits / home_abs}')
    print(f'MIA: {vis_hits} hits in {vis_abs} at bats, batting average of {vis_hits / vis_abs}')
    print(f'BA DIFF = {(home_hits / home_abs) - (vis_hits / vis_abs)}')
    """
    """
    for i in range(2019,2024):
        print(f'{PLAYERS["gallz001"].name} {i} pitching totals: ', end="")
        totals = PLAYERS['gallz001'].get_totals(str(i) + '1231', str(i) + '0101')
        print(f'ER: {totals["ER"]}, IP: {totals["IP"]}, Hits: {totals["Hp"]}, Ks: {totals["Kp"]}')
    for i in range(2010,2024):
        print(f'{PLAYERS["chapa001"].name} {i} pitching totals: ', end="")
        totals = PLAYERS['chapa001'].get_totals(str(i) + '1231', str(i) + '0101')
        print(f'ER: {totals["ER"]}, IP: {totals["IP"]}, Hits: {totals["Hp"]}, Ks: {totals["Kp"]}')
    for i in range(2017,2024):
        print(f'{PLAYERS["hadej001"].name} {i} pitching totals: ', end="")
        totals = PLAYERS['hadej001'].get_totals(str(i) + '1231', str(i) + '0101')
        print(f'ER: {totals["ER"]}, IP: {totals["IP"]}, Hits: {totals["Hp"]}, Ks: {totals["Kp"]}')
    """
#main()

cProfile.run('main()')