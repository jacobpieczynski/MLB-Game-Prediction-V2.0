from const import *
from gamelog import *

# Parse the data from a game log
def parse_log(filename="gl/gl2023.txt", year=2023):
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
