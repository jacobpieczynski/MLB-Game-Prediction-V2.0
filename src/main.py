from const import *
from parse import *

def main():
    # Loads the roster files
    print('-' * 50)
    print('LOADING ROSTERS')
    for year in ROS_FILES:
        for ros in ROS_FILES[year]:
            if not parse_roster(ros, ros[6:10]):
                print(f'FAILED TO OPEN ROSTER {ros}')
                print('-' * 50, end='\n\n')
                return False
            print(ros)
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

main()