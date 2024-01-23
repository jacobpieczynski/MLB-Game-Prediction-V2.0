from const import *

class Game:
    def __init__(self, data):
        self.reset_stats()
        self.info_lines, self.start_lines, self.pbp_lines, self.data_lines = [], [], [], []
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
        # RULE - DO NOT WORK WITH DATA UNTIL NECESSARY
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
        return True

    def reset_stats(self):
        # Add all variables here to reset
        pass

    def __repr__(self):
        return f"Game Object for {self.id} - {self.visitor} at {self.home} on {self.date}"