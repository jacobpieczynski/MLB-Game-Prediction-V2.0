from const import *

class Game:
    def __init__(self, data):
        #self.reset_stats() # TODO: Is this necessary?
        self.info_lines, self.start_lines, self.pbp_lines, self.data_lines = [], [], [], [] # TODO: add these as return for sort_info and use as arguments for their resp. funcs?
        self.home_lineup, self.visitor_lineup = dict(), dict() # Dicts linking to the player object
        self.home_fielders, self.visitor_fielders = [None] * 11, [None] * 11 # Ordered by position map e.g. home_fielders[2] will represent the catcher, [10] will rep DH, [1] pitcher
        self.sort_info(data)
        self.GameLog = GAMELOG[self.year][self.id] # Links to GameLog for this game
        self.GameLog.connect_game(self)

    # Takes a play by play log (pbp) and categorizes the information within
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
        # Now that the info is categorized, we can take the "start" info and set the lineups
        self.set_lineups()
        # All necssary beginning info has been assigned, we can now simulate the game to get statistics
        self.simulate_game()
        return True
    
    # Loops through the 'start' data in a pbp file to set the starting lineups for each team
    def set_lineups(self):
        for line in self.start_lines:
            line = line.split(',')
            print('\n\n')
            print(line)
            print(self.id)
            playerid = line[1]
            is_home = int(line[3]) == 0
            bat_pos = int(line[4])
            pos = int(line[5])
            # Pitchers have a bat_pos of 0
            if pos == 1 and is_home:
                self.home_starter = PITCHERS[playerid]
                self.home_starter.reset_temp_stats()
                self.home_fielders[pos] = PITCHERS[playerid]
            elif pos == 1:
                self.visitor_starter = PITCHERS[playerid]
                self.visitor_starter.reset_temp_stats()
                self.visitor_fielders[pos] = PITCHERS[playerid]
            # Batting starting lineup - both fielders arrays are set up so that the arr idx corresponds to the position in the field played
            elif is_home:
                self.home_lineup[playerid] = PLAYERS[playerid]
                PLAYERS[playerid].reset_temp_stats()
                self.home_fielders[pos] = PLAYERS[playerid]
            else:
                self.visitor_lineup[playerid] = PLAYERS[playerid]
                PLAYERS[playerid].reset_temp_stats()
                self.visitor_fielders[pos] = PLAYERS[playerid]

    # Simulates a game based on PBP files to collect specific game-level statistics
    def simulate_game(self):
        self.reset_sim_attributes()
        # Initial variables
        for line in self.pbp_lines:
            if line.startswith('play,') and 'NP' not in line:
                info = line.split(',')
                home_at_bat = bool(info[2] == '0')
                #print(line)
                #print(home_at_bat)
                id = info[3]
                pitch_count = info[4]
                pitches = info[5]
                play = info[6]
                print(info)
                # Change to one "Batters" dict?
                if home_at_bat:
                    #print(self.home_lineup)
                    if id not in self.home_lineup:
                        self.home_lineup[id] = PLAYERS[id]
                    self.current_batter = self.home_lineup[id]
                else:
                    if id not in self.visitor_lineup:
                        self.visitor_lineup[id] = PLAYERS[id]
                    self.current_batter = self.visitor_lineup[id]
                # 'NP' occurs when there is a substitute in the game, do not inc stats
                #if play != 'NP': # TODO: Replace 'np' when you decide how to deal with it
                self.current_batter.add_temp_stat('PA', 1)
                self.current_pitcher.add_temp_stat('BF', 1)
                # Makes sure that all players are included in the players_in_game. They will later be called to increase their temp stats.
                if self.current_batter.id not in self.players_in_game:
                    self.players_in_game[self.current_batter.id] = self.current_batter
                if self.current_batter.id not in self.players_in_game:
                    self.players_in_game[self.current_batter.id] = self.current_batter
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
                # TODO: Add player to players_in_game and make sure to reset their temp stats
                # If side = 0, and pos = 0, change home_pitcher
                # If side = 1 and pos = 0, change visiting_pitcher
                # Else: add player to their respective slot in the lineup/fielding positions
                info = line.split(',')
                playerid = info[1]
                is_home = int(info[3]) == 0
                bat_ord = int(info[4])
                if bat_ord >= 10:
                    bat_ord = 10
                pos = int(info[5])
                # New pitcher
                if pos == 1 and is_home:
                    self.home_pitcher = self.get_player(id)
                    self.players_in_game[id] = self.home_pitcher
                    # TODO: END PITCHER OUTING
                elif pos == 1:
                    self.visitor_pitcher = self.get_player(id)
                    self.players_in_game[id] = self.visitor_pitcher
                elif is_home:
                    self.home_lineup[id] = self.get_player(id)
                    self.players_in_game[id] = PLAYERS[id]
                else:
                    self.visitor_lineup[id] = self.get_player(id)
                    self.players_in_game[id] = PLAYERS[id]

        self.attribute_stats()

    # Plays are very complex with many edge cases
    def parse_play(self, play):
        pass

    # Resets statistics and attributes linked to simulating a specific game
    def reset_sim_attributes(self):
        self.bases = [None, None, None] # The player at 1st, 2nd, and 3rd bases
        self.inn_outs = 0 # TODO: Fix this, it's inefficient I think
        self.game_outs = 0
        self.inning = 1
        self.players_in_game = dict()
        """
        self.current_batter = self.home_lineup[0]
        self.next_home_batter = self.home_lineup[1]
        self.next_visitor_batter = self.visitor_lineup[0]
        """
        self.current_pitcher = self.visitor_starter
        self.visitor_pitcher = self.current_pitcher
        self.home_pitcher = self.home_starter

    # Loops through every player involved in the game and attributes their "temp" stats to their permenant ones
    def attribute_stats(self):
        for player in self.players_in_game:
            self.players_in_game[player].inc_total_stats() # Function name is the same for both pitchers and players so no discernment needed

    def get_player(self, id):
        if id in PITCHERS:
            return PITCHERS[id]
        elif id in PLAYERS:
            return PLAYERS[id]
        else:
            print("Player could not be found, get_player(id)")
            return None

    def __repr__(self):
        return f"Game Object for {self.id} - {self.visitor} at {self.home} on {self.date}"#\nHome Starting lineup: {self.home_lineup}, Visitor Starting lineup: {self.visitor_lineup}\n Home Fielding Order {self.home_fielders}, Visitor fielders {self.visitor_fielders}"