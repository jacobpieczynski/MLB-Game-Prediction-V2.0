from const import *
# Classes
from game import Game
from gamelog import GameLog
from pitcher import Pitcher
from player import Player

# Parse the roster information
def parse_roster(filename='ros/2023/ANA2023.ROS'):
    try:
        with open(filename) as file:
            for line in file:
                line = line.strip('\n')
                if (line[-1] == 'P'):
                    pitcher = Pitcher(line)
                    if pitcher.id not in PITCHERS:
                        PITCHERS[pitcher.id] = pitcher
                        PLAYERS[pitcher.id] = pitcher
                else:
                    player = Player(line)
                    if player.id not in PLAYERS:
                        PLAYERS[player.id] = player
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
                game = Game(data)
                print(f'for game created {game.id}')
                GAMES[game.id] = game
                data = []
                data.append(line.strip('\n'))
            else:
                data.append(line.strip('\n'))
        # To append final game
        print('new game {game.id}')
        game = Game(data)
        print('game created')
        GAMES[game.id] = game
    #except:
     #   return False
    return True