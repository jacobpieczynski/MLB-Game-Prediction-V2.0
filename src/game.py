from const import *

class Game:
    def __init__(self, data):
        self.sort_data(data)

    def __repr__(self):
        pass

    # 4 different categories of data that must be treated differently
    def sort_data(self, data):
        self.infos, self.start, self.plays, self.data = [], [], [], []
        for line in data:
            if line.startswith('info,') or line.startswith('id,') or line.startswith('version,'):
                self.infos.append(line)
            elif line.startswith('start,'):
                self.start.append(line)
            elif line.startswith('play') or line.startswith('sub') or line.startswith('com') or line.startswith('badj,') or line.startswith('radj,'):
                self.plays.append(line)
            elif line.startswith('data'):
                self.data.append(line)
            else:
                print('Line type not found:')
                print(line)
        self.parse_info()
        self.set_lineup()

    # Takes the info metadata and parses it. Creates a game id and metadata
    def parse_info(self):
        info = dict()
        for line in self.infos:
            line = line.split(',')
            if line[0] == 'id':
                self.date = line[1][3:-1]
            elif line[0] != 'version':
                info[line[1]] = line[2]
        self.id = self.date + info['hometeam'] + info['visteam']
        self.info = info
        self.GameLog = GAMELOG[self.date[:4]][self.id]

    # Takes the 'start' information and sets the lineups based off it
    def set_lineup(self):
        self.home_lineup, self.visitor_lineup, self.players_in_game = [None] * 11, [None] * 11, [] # lineup[0] is none, after that the idx represents their field pos
        for line in self.start:
            line = line.split(',')
            playerid = line[1]
            is_home = int(line[3]) == 0
            field_pos = int(line[5])
            is_pitcher = (field_pos == 1)
            # TODO: Improve this? Seems a bit of a redundant way to do it
            # Adds players into the lineup based on their position - remember, pitchers and players are different objects
            if is_pitcher:
                if is_home:
                    self.home_lineup[field_pos] = PITCHERS[playerid]
                else:
                    self.visitor_lineup[field_pos] = PITCHERS[playerid]
                self.players_in_game.append(PITCHERS[playerid])
            else:
                if is_home:
                    self.home_lineup[field_pos] = PLAYERS[playerid]
                else:
                    self.visitor_lineup[field_pos] = PLAYERS[playerid]
                self.players_in_game.append(PLAYERS[playerid])            

