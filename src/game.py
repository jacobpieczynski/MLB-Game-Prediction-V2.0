from const import *

class Game:
    def __init__(self, data):
        self.reset_stats()
        self.info_lines, self.start_lines, self.pbp_lines, self.data_lines = [], [], [], []
        self.home_lineup, self.visitor_lineup = [], [] # Array linking to the player object
        self.sort_info(data)
        self.GameLog = GAMELOG[self.year][self.id] # Links to GameLog for this game
        self.GameLog.connect_game(self)

    def sort_info(self, data):
        # Creates an ID from the ID line (first line)
        self.home = data[0][3:6]
        self.visitor = data[2].split(',')[-1]
        self.date = data[0][6:-1]
        self.id = self.date + self.home + self.visitor
        self.year = data[0][6:10]

        # Sorts lines based on data type - each will be treated differently
        for line in data:
            if line.startswith('id,'):
                pass
            elif line.startswith('version,'):
                self.version = line[-1]
            elif line.startswith('info,'):
                self.info_lines.append(line)
            elif line.startswith('start,'):
                self.start_lines.append(line)
            elif line.startswith('play,') or line.startswith('com,') or line.startswith('sub,') or line.startswith('radj,') or line.startswith('badj'):
                self.pbp_lines.append(line)
            elif line.startswith('data,'):
                self.data_lines.append(line)
            else:
                print(f"Line : {line} could not be processed")
                return False
        self.set_lineups()
        # SIMULATE GAME
        self.simulate_game()
        return True
    
    def set_lineups(self):
        for line in self.start_lines:
            line = line.split(',')
            playerid = line[1]
            is_home = int(line[3]) == 0
            pos = int(line[4])
            # Pitchers
            if pos == 0 and is_home:
                self.home_starter = PITCHERS[playerid]
            elif pos == 0:
                self.visitor_starter = PITCHERS[playerid]
            # Batting starting lineup
            elif is_home:
                self.home_lineup.append(PLAYERS[playerid])
            else:
                self.visitor_lineup.append(PLAYERS[playerid])

    def simulate_game(self):
        # Initial variables
        pass

    def clear_bases(self):
        self.bases = [0, 0, 0] # 1st 2nd 3rd

    def reset_stats(self):
        # Add all variables here to reset
        pass

    def __repr__(self):
        return f"Game Object for {self.id} - {self.visitor} at {self.home} on {self.date}"