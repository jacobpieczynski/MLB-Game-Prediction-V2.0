from const import *
from parse import *
from stats import log_games

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
        if year > '2000':
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
    #print(GAMES['20230830LANARI'].comp_sps())
    #print(GAMES['20230920ARISFN'].get_team_records())
    #print(GAMES['20230830LANARI'].team_batting_stats())
    #print(PLAYERS['judga001'].get_totals(END_2022, START_2022))

main()