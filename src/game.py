from const import *

class Game:
    def __init__(self, data):
        self.reset_stats()
        self.info_lines, self.start_lines, self.pbp_lines, self.data_lines = [], [], [], []
        self.home_lineup, self.visitor_lineup = dict(), dict() # Dicts linking to the player object
        self.home_fielders, self.visitor_fielders = [None] * 11, [None] * 11 # Ordered by position map e.g. home_fielders[2] will represent the catcher, [10] will rep DH, [1] pitcher
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
            bat_pos = int(line[4])
            pos = int(line[5])
            # Pitchers
            if bat_pos == 0 and is_home:
                self.home_starter = PITCHERS[playerid]
                self.home_starter.reset_temp_stats()
                self.home_fielders[pos] = PITCHERS[playerid]
            elif bat_pos == 0:
                self.visitor_starter = PITCHERS[playerid]
                self.visitor_starter.reset_temp_stats()
                self.visitor_fielders[pos] = PITCHERS[playerid]
            # Batting starting lineup
            elif is_home:
                self.home_lineup[playerid] = PLAYERS[playerid]
                PLAYERS[playerid].reset_temp_stats()
                self.home_fielders[pos] = PLAYERS[playerid]
            else:
                self.visitor_lineup[playerid] = PLAYERS[playerid]
                PLAYERS[playerid].reset_temp_stats()
                self.visitor_fielders[pos] = PLAYERS[playerid]

    def simulate_game(self):
        self.reset_sim_attributes()
        # Initial variables
        for line in self.pbp_lines:
            if line.startswith('play,'):
                info = line.split(',')
                home_at_bat = bool(info[2] == '0')
                #print(line)
                #print(home_at_bat)
                id = info[3]
                pitch_count = info[4]
                pitches = info[5]
                play = info[6]
                # Change to one "Batters" dict?
                if home_at_bat:
                    print(self.home_lineup)
                    if id not in self.home_lineup:
                        self.home_lineup[id] = PLAYERS[id]
                    self.current_batter = self.home_lineup[id]
                else:
                    if id not in self.visitor_lineup:
                        self.visitor_lineup[id] = PLAYERS[id]
                    self.current_batter = self.visitor_lineup[id]
                self.current_batter.add_temp_stat('PA', 1)
                self.current_pitcher.add_temp_stat('BF', 1)
                # MISC LOGIC
                # ...
                # ...
                # Swaps pitchers at the end of the inning
                if self.inn_outs == 3:
                    if home_at_bat:
                        self.current_pitcher = self.home_pitcher
                    else:
                        self.current_pitcher = self.visitor_pitcher
                    self.inn_outs = 0
            elif line.startswith('sub,'):
                pass

    def reset_sim_attributes(self):
        self.bases = [None, None, None]
        self.inn_outs = 0
        self.game_outs = 0
        self.inning = 1
        """
        self.current_batter = self.home_lineup[0]
        self.next_home_batter = self.home_lineup[1]
        self.next_visitor_batter = self.visitor_lineup[0]
        """
        self.current_pitcher = self.visitor_starter
        self.visitor_pitcher = self.current_pitcher
        self.home_pitcher = self.home_starter

    def reset_stats(self):
        # Add all variables here to reset
        pass

    def __repr__(self):
        return f"Game Object for {self.id} - {self.visitor} at {self.home} on {self.date}"#\nHome Starting lineup: {self.home_lineup}, Visitor Starting lineup: {self.visitor_lineup}\n Home Fielding Order {self.home_fielders}, Visitor fielders {self.visitor_fielders}"