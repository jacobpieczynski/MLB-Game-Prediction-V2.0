from const import *
# Classes
from pitcher import *
from player import *
from gamelog import *

# Parse the roster information
def parse_roster(filename='ros/2023/ANA2023.ROS', year='2023'):
    try:
        with open(filename) as file:
            for line in file:
                if (line[-1] == 'P'):
                    pitcher = Pitcher(line)
                    if pitcher.id not in PITCHERS:
                        PITCHERS[pitcher.id] = pitcher
                    print(pitcher)
                else:
                    player = Player(line)
                    if player.id not in PLAYERS:
                        PLAYERS[player.id] = player
                    print(player)
    except:
        return False
    return True

# Parse the data from a game log
def parse_log(filename="gl/gl2023.txt", year='2023'):
    GAME_LOGS.setdefault(year, {})

    try:
        with open(filename) as file:
            for line in file:
                game = GameLog(line.rstrip('\n'))
                GAME_LOGS[year].setdefault(game.date, [])
                GAME_LOGS[year][game.date].append(game)
    except:
        return False
    return True
