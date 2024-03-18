from const import *
# Classes
from game import Game
from gamelog import GameLog
from player import Player

# Parse the roster information
def parse_roster(filename='ros/2023/ANA2023.ROS'):
    try:
        year = filename[4:8]
        team = filename[9:12]
        with open(filename) as file:
            for line in file:
                line = line.strip('\n')
                player = Player(line)
                if player.id not in PLAYERS:
                    PLAYERS[player.id] = player
                if year not in TEAM_ROS:
                    TEAM_ROS[year] = dict()
                if team not in TEAM_ROS[year]:
                    TEAM_ROS[year][team] = []
                TEAM_ROS[year][team].append(player)
    except:
        return False
    return True

# Parse the data from a game log
def parse_log(filename="gl/gl2023.txt", year='2023'):
    GAMELOG.setdefault(year, {})
    try:
        with open(filename) as file:
            for line in file:
                game = GameLog(line.rstrip('\n'))
                GAMELOG[year].setdefault(game.id, {})
                GAMELOG[year][game.id] = game
    except:
        return False
    return True

# Parse PBP Files
def parse_pbp(filename='pbp/2023/2023ARI.EVN'):
    data = []
    #try:
    with open(filename) as file:
        for line in file:
            # All games begin with the 'id,' line
            if line[0:3] == 'id,' and data != []:
                year = filename[4:8]
                if year not in GAMES:
                    GAMES[year] = dict()
                game = Game(data)
                if game.home not in GAMES[year]:
                    GAMES[year][game.home] = dict()
                if game.visitor not in GAMES[year]:
                    GAMES[year][game.visitor] = dict()
                GAMES[year][game.home][game.id] = game
                GAMES[year][game.visitor][game.id] = game
                print(f'game created {game.id}')
                data = []
                data.append(line.strip('\n'))
            else:
                data.append(line.strip('\n'))
        # To append final game
        game = Game(data)
        GAMES[year][game.home][game.id] = game
        GAMES[year][game.visitor][game.id] = game
        print(f'game created {game.id}')
    #except:
     #   return False
    print('test')
    print(len(GAMES['2023']['ARI']))
    print(len(GAMES['2023']['ANA']))
    print(len(GAMES['2023']['LAN']))
    print(len(GAMES['2023']['WAS']))
    return True