from const import *
from player import Player
from stat_calc import *

class Game:
    def __init__(self, data):
        self.com = False # TEMP
        self.sort_data(data)

    def __repr__(self):
        if self.id:
            return f'Game object: {self.id} on {self.date} - {self.info["visteam"]} at {self.info["hometeam"]}. Home Lineup {self.home_starting_lineup}'

    # 4 different categories of data that must be treated differently
    def sort_data(self, data):
        self.infos, self.start, self.plays = [], [], []
        for line in data:
            if line.startswith('info,') or line.startswith('id,') or line.startswith('version,'):
                self.infos.append(line)
            elif line.startswith('start,'):
                self.start.append(line)
            elif line.startswith('play') or line.startswith('sub') or line.startswith('com') or line.startswith('badj,') or line.startswith('radj,') or line.startswith('data,'):
                self.plays.append(line)
            else:
                print(line)
                print('Line type not found:')
        self.parse_info()
        self.set_lineup()
        self.simulate_game()

    # Takes the info metadata and parses it. Creates a game id and metadata
    def parse_info(self):
        info = dict()
        for line in self.infos:
            line = line.split(',')
            if line[0] == 'id':
                if line[1][-1] != '0':
                    self.factor = line[1][-1]
                else:
                    self.factor = ''
                self.date = line[1][3:-1]
            elif line[0] != 'version':
                info[line[1]] = line[2]
        self.id = self.date + info['hometeam'] + info['visteam']
        self.year = self.date[0:4]
        self.home = info['hometeam']
        self.visitor = info['visteam']
        self.field = info['site']
        self.info = info
        self.GameLog = GAMELOG[self.date[:4]][self.id]
        self.hscore = int(self.GameLog.home_score)
        self.vscore = int(self.GameLog.visitor_score)
        self.home_win = self.hscore > self.vscore
        self.id += self.factor
        

    # Takes the 'start' information and sets the lineups based off it
    def set_lineup(self):
        self.home_lineup, self.visitor_lineup, self.players_in_game = [None] * 11, [None] * 11, dict() # lineup[0] is none, after that the idx represents their field pos
        self.player_stats = dict()
        for line in self.start:
            line = line.split(',')
            playerid = line[1]
            is_home = int(line[3]) == 1
            field_pos = int(line[5])
            is_pitcher = (field_pos == 1)
            # TODO: Improve this? Seems a bit of a redundant way to do it
            # TODO: How do we treat years? Will players be able to fit into a general PLAYERS roster or do we need to sort by year?
            # Adds players into the lineup based on their position - remember, pitchers and players are different objects
            if is_home:
                self.home_lineup[field_pos] = PLAYERS[playerid]
            else:
                self.visitor_lineup[field_pos] = PLAYERS[playerid]
            PLAYERS[playerid].reset_game_stats()
            self.player_stats[playerid] = {'PA': 0, 'AB': 0, 'H': 0, 'S': 0, 'D': 0, 'T': 0, 'HR': 0, 'BB': 0, 'K': 0, 'RBI': 0, 'SB': 0, 'CS': 0, 'SF': 0, 'SH': 0, 'HBP': 0, 'ROE': 0, 'G': 0, 'S': 0, 'IP': 0, 'OP': 0, 'ER': 0, 'HR': 0, 'BB': 0, 'H': 0, 'R': 0, 'HBP': 0, 'K': 0, 'BF': 0, 'P': 0, 'HBPp': 0, 'HRp': 0, 'Kp': 0, 'BBp': 0, 'Hp': 0}
            if is_pitcher:
                PLAYERS[playerid].inc_game_stat(self, ['G', 'S'], [1, 1])
            self.players_in_game[playerid] = PLAYERS[playerid]
        #self.home_starting_lineup, self.visitor_starting_lineup = [], []
        #for h in self.home_lineup:
         #   self.home_starting_lineup.append(h)
        #for v in self.visitor_lineup:
        #    self.visitor_starting_lineup.append(v)
        self.home_starting_lineup = self.home_lineup.copy()
        self.visitor_starting_lineup = self.visitor_lineup.copy()

    # Loops through the plays and parses them/collects statistics accordingly
    def simulate_game(self):
        self.bases = [None] * 4
        self.op, self.inning, self.side = 0, 0, 0
        radj = False
        # Makes sure players don't have existing stats
        for player in self.players_in_game:
            self.players_in_game[player].reset_game_stats()   

        for line in self.plays:
            line = line.split(',')
            # 3 types of play info
            if line[0] == 'play' and line[-1] != 'NP': #TODO: NP will always (?) preceed a sub/adj, can ignore those lines
                # TODO: Account for a new inning
                is_home = int(line[2]) == 1
                playerid = line[3]
                pitch_count = line[4]
                total_pitches = int(pitch_count[0]) + int(pitch_count[1])
                pitches_thrown = line[5]
                play = line[6]
                if playerid not in PLAYERS:
                    for player in PLAYERS:
                        print(player)
                    print(f'FUCK {line}')
                batter = PLAYERS[playerid]
                # TODO: How to treat new innings
                inning, side = int(line[1]), int(line[2])
                if self.inning != inning or self.side != side: # self.op == 3 or 
                    self.inning = inning
                    self.side = side
                    if not radj:
                        self.bases = [None] * 4
                    self.op = 0

                if is_home:
                    pitcher = PLAYERS[self.visitor_lineup[1].id]
                else:
                    pitcher = PLAYERS[self.home_lineup[1].id]
                if pitcher.id not in self.players_in_game:
                    self.players_in_game[pitcher.id] = pitcher

                pitcher.inc_game_stat(self, ['P'], [total_pitches])
                self.parse_play(play, batter, pitcher)
                # Hacky way to fix a FC error 
                # TODO: Look at game 20230620SFNSDN, Anthony Descalfani is given 4 outs in the 3rd inning
                if self.op >= 4:
                    pitcher.inc_game_stat(self, ['OP'], [-1])
                    self.op = 3
                radj = False

            # When a player is substituted for another
            elif line[0] == 'sub':
                # The numbers are in the standard notation, with designated hitters being identified as position 10. On sub records 11 indicates a pinch hitter and 12 is used for a pinch runner. 
                # When a player pinch hits or pinch runs for the DH, that player automatically becomes the DH, so no 'sub' record is included to identify the new DH.
                #['sub', 'gonzv001', '"Victor Gonzalez"', '1', '0', '1']
                playerid = line[1]
                playername = line[2]
                is_home = int(line[3]) == 1
                bat_pos = int(line[4])
                field_pos = int(line[5])
                # TODO: TEMP - adjust to account for pinch runners and hitters
                if field_pos >= 10:
                    field_pos = 10
                # Checks for pitchers being subbed as players
                if playerid not in PLAYERS:
                    PLAYERS[playerid] = Player(f'{playerid},{playername.split(" ")[1]},{playername.split(" ")[0]},,,,{field_pos}')
                if playerid not in self.player_stats:
                    self.player_stats[playerid] = {'PA': 0, 'AB': 0, 'H': 0, 'S': 0, 'D': 0, 'T': 0, 'HR': 0, 'BB': 0, 'K': 0, 'RBI': 0, 'SB': 0, 'CS': 0, 'SF': 0, 'SH': 0, 'HBP': 0, 'ROE': 0, 'G': 0, 'S': 0, 'IP': 0, 'OP': 0, 'ER': 0, 'HR': 0, 'BB': 0, 'H': 0, 'R': 0, 'HBP': 0, 'K': 0, 'BF': 0, 'P': 0, 'HBPp': 0, 'HRp': 0, 'Kp': 0, 'BBp': 0, 'Hp': 0}
                if field_pos == 1:
                        PLAYERS[playerid].inc_game_stat(self, ['G'], [1])
                if is_home:
                    self.home_lineup[field_pos] = PLAYERS[playerid]
                else:
                    self.visitor_lineup[field_pos] = PLAYERS[playerid]
                self.players_in_game[playerid] = PLAYERS[playerid] 
            elif line[0] == 'com':
                if self.com:
                    #print(f'com? {line}')
                    pass
            # Tracks a the ER of each pitcher
            elif line[0] == 'data':
                PLAYERS[line[2]].inc_game_stat(self, ['ER'], [int(line[3])])
            # Runner Adjustment, for when an inning starts with someone on base (extra innings rule)
            elif line[0] == 'radj':
                radj = True
                self.bases[int(line[2])] = PLAYERS[line[1]]
            else:
                # TODO: Account for badj
                if line[-1] != 'NP' : print(f'badj? {line}')
                pass
        for player in self.players_in_game:
            self.players_in_game[player].add_game_stats(self)
            self.players_in_game[player].reset_game_stats()        
            
    def parse_play(self, play, batter, pitcher):
        self.com = False # TODO: TEMP
        # 'Simple Plays'
        simple = play.split('/')[0]
        mods, runners = list(), [None]
        if '/' in play:
            mods = play.split('.')[0].split('/')[1:]
        if '.' in play:
            runners = play.split('.')[1:]

        # Number beginning a simple play represents a ground/line out
        if simple[0].isnumeric():
            # Parenthesis represents a double play, with the character inside the parenthesis representing the baserunner out
            if '(' in simple:
                runner = simple.split(')')[0][-1]
                # 'B' - If the putout is made at a base not normally covered by the fielder the base runner, batter in this example, is given explicitly.
                # If the last digit is a number, it represents a double play
                if simple[-1].isnumeric():
                    if runner.isnumeric():
                        self.bases[int(runner)] = None
                    pitcher.inc_game_stat(self, ['OP', 'BF'], [2, 1])
                    self.op += 2
                # If there are two () it is also a double (or triple!) play
                elif simple.count('(') > 1:
                  ##print((f'Lined into play, {runner} out as well as batter - {play}')
                    pitcher.inc_game_stat(self, ['OP', 'BF'], [int(simple.count('(')), 1])
                    self.op += int(simple.count('('))
                else:
                    # Runner in parenthesis represents a force out - B in parenthesis is the batter, so empty base is implied
                    if runner.isnumeric():
                        self.bases[int(runner)] = None
                    #else:
                      ##print((f'Unusual fo, batter out - {play}')
                    pitcher.inc_game_stat(self, ['OP', 'BF'], [1, 1])
                    self.op += 1
            # Other numeric entries represent a simple pop/lineout
            else:
                pitcher.inc_game_stat(self, ['OP', 'BF'], [1, 1])
                self.op += 1
            # Records sacrifice hits - sacs don't count as an at bat, just a plate appearance
            if '/SF' in play:
                batter.inc_game_stat(self, ['PA', 'SF'], [1, 1])
            elif  '/SH' in play:
                batter.inc_game_stat(self, ['PA', 'SH'], [1, 1])
            else:
                batter.inc_game_stat(self, ['PA', 'AB'], [1, 1])
        # Defensive indifference, runner allowed to steal
        elif simple.startswith("DI"):
            # TODO: treat defensive indifference, advance runner
            pass
        # Interference by a player resulting in batter going to 1 and all others advancing
        elif 'C/E' in play:
            batter.inc_game_stat(self, ['PA'], [1])
            pitcher.inc_game_stat(self, ['BF'], [1])
        # Single
        elif simple.startswith('S') and not simple.startswith('SB'):
            batter.inc_game_stat(self, ['S', 'PA', 'AB', 'H'], [1, 1, 1, 1])
            pitcher.inc_game_stat(self, ['Hp', 'BF'], [1, 1])
        # Double
        elif simple.startswith('D') or simple.startswith('DGR'):
            batter.inc_game_stat(self, ['D', 'PA', 'AB', 'H'], [1, 1, 1, 1])
            pitcher.inc_game_stat(self, ['Hp', 'BF'], [1, 1])
        # Triple
        elif simple.startswith('T'):
            batter.inc_game_stat(self, ['T', 'PA', 'AB', 'H'], [1, 1, 1, 1])
            pitcher.inc_game_stat(self, ['Hp', 'BF'], [1, 1])
        # Fielding Error
        elif simple.startswith('E') and simple[1].isnumeric():
            batter.inc_game_stat(self, ['PA', 'AB', 'ROE'], [1, 1, 1])
            pitcher.inc_game_stat(self, ['BF'], [1])
        # Fielders choice - batter goes to first, another runner is attempted to get out
        elif simple.startswith('FC'):
            batter.inc_game_stat(self, ['AB', 'PA'], [1, 1])
            # Any of these cases means that a FC was attempted but no runner put out
            if runners != [None] and (('B-1' in runners[0] and 'E' in runners[0]) or ('X' not in runners)):
                pitcher.inc_game_stat(self, ['BF'], [1])
            else:
                pitcher.inc_game_stat(self, ['BF', 'OP'], [1, 1])
                self.op += 1
        # Home Run
        elif 'H/' in play or simple.startswith('HR'):
            batter.inc_game_stat(self, ['HR', 'AB', 'PA', 'H'], [1, 1, 1, 1])
            pitcher.inc_game_stat(self, ['HRp', 'Hp', 'BF'], [1, 1, 1])
        # Hit by Pitch
        elif simple.startswith('HP'):
            batter.inc_game_stat(self, ['HBP', 'PA'], [1, 1])
            pitcher.inc_game_stat(self, ['HBPp', 'BF'], [1, 1])
        # K + something represents a strikout plus another event
        elif simple.startswith('K+') or (simple.startswith('K') and '+' in simple):
            # TODO: Treat strikeout edge cases
            op = 1
            for mod in mods:
                # One of the edge cases, 'DP' in mod represents a double play in this case
                if 'DP' in mod:
                    op = 2
            batter.inc_game_stat(self, ['K', 'PA', 'AB'], [1, 1, 1])
            pitcher.inc_game_stat(self, ['Kp', 'OP', 'BF'], [1, op, 1])
            self.op += op
        # Strikeout
        elif simple.startswith('K'):
            batter.inc_game_stat(self, ['K', 'PA', 'AB'], [1, 1, 1])
            pitcher.inc_game_stat(self, ['Kp', 'OP', 'BF'], [1, 1, 1])
            self.op += 1
        elif simple.startswith('PB') or simple.startswith('WP'):
            #TODO: passed ball/wild pitch, not a batter stat but runners may have advanced.
            pass
        elif simple.startswith('W+') or (simple.startswith('W') and '+' in simple):
            # TODO: treat walk edge cases (for baserunning (?))
            batter.inc_game_stat(self, ['BB', 'PA'], [1, 1])
            pitcher.inc_game_stat(self, ['BBp', 'BF'], [1, 1])
        # Intentional Walk
        elif simple.startswith('I') or simple.startswith('IW') or simple.startswith('W'):
            batter.inc_game_stat(self, ['BB', 'PA'], [1, 1])
            pitcher.inc_game_stat(self, ['BBp', 'BF'], [1, 1])
        # Balk
        elif simple.startswith('BK'):
            # TODO: treat balks, advance all runners
            pass
        # Player caught stealing
        elif simple.startswith('CS'):
            base = simple[2]
            if base == 'H':
                base = 3
            else:
                base = int(base) - 1
            # TODO: treat caught stealing, general base running
            if 'E' not in simple and self.bases[base] != None:
                self.bases[base].inc_game_stat(self, ['CS'], [1])
            else:
                pass
            pitcher.inc_game_stat(self, ['OP'], [1])
            self.op += 1
        # Pickoff cases
        elif simple.startswith('PO'):
            # Error, runner advances
            if '(E' in simple:
                # TODO: account for the error
                pass
            # Picked off and changed with caught stealing
            elif simple.startswith('POCS'):
                base = simple[4] 
                # TODO: Picked off, caught stealing
                """
                if base == 'H':
                    self.bases[3].inc_game_stat(self, ['CS'], [1])
                    self.bases[3] = None
                else:
                    self.bases[int(base) - 1].inc_game_stat(self, ['CS'], [1])
                    self.bases[int(base) - 1] = None
                """
                pitcher.inc_game_stat(self, ['OP'], [1])
                self.op += 1
            # Runner picked off, base represets the base they were at
            else:
                base = simple[2]
                if base == 'H':
                    self.bases[3] = None
                else:
                    self.bases[int(base) - 1] = None
                pitcher.inc_game_stat(self, ['OP'], [1])
                self.op += 1
        # Stolen Base
        # TODO: Fix this (get rid of 1 ==2 ) when adv_bases works
        elif simple.startswith('SB'):
            if 1 == 2:
                steals = simple.split('.')[0].split(';')
                for steal in steals:
                    base = steal[2]
                    if base == 'H':
                        self.bases[3].inc_game_stat(self, ['SB'], [1])
                        # TODO: Account for run scored ??
                    else:
                        self.bases[int(base) - 1].inc_game_stat(self, ['SB'], [1])
        # Fielding error on fly ball
        elif simple.startswith('FLE'):
            # TODO: if we track fielding stats, update with this. Otherwise, ignore/pass
            pass
        # Other action
        # TODO: Deal with other action if necessary
        elif simple.startswith('OA'):
            self.com = True
        else:
            pass
        if runners != [None]:
            for runner in runners:
                if 'X' in runner:
                    pitcher.inc_game_stat(self, ['OP'], [1])
                    self.op += 1
        
        #self.adv_bases(batter, simple, runners[0], play)

    # Statistics Functions
    def get_team_records(self, home_start=None, visitor_start=None):
        end_date = get_prior_date(self.date)
        if home_start == None or visitor_start == None:
            home_start, visitor_start = end_date[:4] + '0101', end_date[:4] + '0101' # Jan 1 of the year of the game
        home_wins, home_hwins, home_vwins, visitor_wins, visitor_hwins, visitor_vwins, home_ra, visitor_ra, h_pyth, v_pyth = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        home_losses, visitor_losses = 0, 0
        home_runs, visitor_runs = 0, 0
        hwpct, vwpct = 0, 0
        """
        for gameid in GAMES[self.year]:
            game = GAMES[self.year][gameid]
            #if game.date == '20231001':
                #print(f'{self.id}, gdate = {game.date}, end_date = {end_date}, comp = {game.date <= end_date}, comp 2 = {game.date >= start_date}')
            if game.date <= end_date and (((self.home in (game.home, game.visitor)) and game.date >= home_start) or ((self.visitor in (game.home, game.visitor)) and game.date >= visitor_start)):
            #if game.date <= end_date and game.date >= start_date and (self.home in (game.home, game.visitor) or self.visitor in (game.home, game.visitor)):
                # Checks that the team is in the game and won
                if self.home == game.home and game.home_win:
                    home_wins += 1
                    home_hwins += 1
                elif self.home == game.visitor and not game.home_win:
                    home_wins += 1
                    home_vwins += 1
                elif self.home in (game.home, game.visitor):
                    home_losses += 1

                if self.visitor == game.home and game.home_win:
                    visitor_wins += 1
                    visitor_hwins += 1
                elif self.visitor == game.visitor and not game.home_win:
                    visitor_wins += 1
                    visitor_vwins += 1
                elif self.visitor in (game.home, game.visitor):
                    visitor_losses += 1

                # To add to total runs
                if self.home == game.home:
                    home_runs += game.hscore
                    home_ra += game.vscore
                elif self.home == game.visitor:
                    home_runs += game.vscore
                    home_ra += game.hscore
                if self.visitor == game.visitor:
                    visitor_runs += game.vscore
                    visitor_ra += game.hscore
                elif self.visitor == game.home:
                    visitor_runs += game.hscore
                    visitor_ra += game.vscore
                #print(f'Add Win {game.id}, {visitor_wins}, home wins {home_wins} Win Diff = {home_wins - visitor_wins}')
        """
                
        # Sorts through every game the home team played in
        for gameid in GAMES[self.year][self.home]:
            game = GAMES[self.year][self.home][gameid]
            # Makes sure the game is within the proper date
            if game.date <= end_date and game.date >= home_start:
                # Tallies wins, losses, and runs
                if self.home == game.home and game.home_win:
                    home_wins += 1
                    home_hwins += 1
                elif self.home == game.visitor and not game.home_win:
                    home_wins += 1
                    home_vwins += 1
                elif self.home in (game.home, game.visitor):
                    home_losses += 1
                if self.home == game.home:
                    home_runs += game.hscore
                    home_ra += game.vscore
                elif self.home == game.visitor:
                    home_runs += game.vscore
                    home_ra += game.hscore
        for gameid in GAMES[self.year][self.visitor]:
            game = GAMES[self.year][self.visitor][gameid]
            if game.date <= end_date and game.date >= visitor_start:
                if self.visitor == game.home and game.home_win:
                    visitor_wins += 1
                    visitor_hwins += 1
                elif self.visitor == game.visitor and not game.home_win:
                    visitor_wins += 1
                    visitor_vwins += 1
                elif self.visitor in (game.home, game.visitor):
                    visitor_losses += 1
                if self.visitor == game.visitor:
                    visitor_runs += game.vscore
                    visitor_ra += game.hscore
                elif self.visitor == game.home:
                    visitor_runs += game.hscore
                    visitor_ra += game.vscore
        
        if home_wins > 0:
            hwpct = round(home_wins / (home_wins + home_losses), 3)
        if visitor_wins > 0:
            vwpct = round(visitor_wins / (visitor_wins + visitor_losses), 3)

        # RPG - Runs per game
        hrpg, vrpg = 0, 0
        if (home_wins + home_losses) > 0:
            hrpg = round(home_runs / (home_wins + home_losses), 2)
        if (visitor_wins + visitor_losses) > 0:
            vrpg = round(visitor_runs / (visitor_wins + visitor_losses), 2)

        if home_ra > 0:
            h_pyth = calc_pythag(home_runs, home_ra)
        if visitor_ra > 0:
            v_pyth = calc_pythag(visitor_runs, visitor_ra)
        home_stats = {'Wins': home_wins, 'Losses': home_losses, 'Games': home_wins + home_losses, 'HomeWins': home_hwins, 'AwayWins': home_vwins, 'WPct': hwpct, 'Runs': home_runs, 'RPG': hrpg, 'Pythag': h_pyth, 'RA': home_ra}
        visitor_stats = {'Wins': visitor_wins, 'Losses': visitor_losses, 'Games': visitor_wins + visitor_losses, 'HomeWins': visitor_hwins, 'AwayWins': visitor_vwins, 'WPct': vwpct, 'Runs': visitor_runs, 'RPG': vrpg, 'Pythag': v_pyth, 'RA': visitor_ra}
        team_stats = {'WinDiff': home_stats['Wins'] - visitor_stats['Wins'], 'HomeAdv': home_stats['HomeWins'] - visitor_stats['AwayWins'], 'WPctDiff': round(home_stats['WPct'] - visitor_stats['WPct'], 3), 'Log5': calc_log5(home_stats['WPct'], visitor_stats['WPct']), 'RunDiff': home_stats['Runs'] - visitor_stats['Runs'], 'RPGDiff': round(home_stats['RPG'] - visitor_stats['RPG'], 2), 'Total Games': min(home_stats['Games'], visitor_stats['Games']), 'PythagDiff': home_stats['Pythag'] - visitor_stats['Pythag'], 'RADiff': home_stats['RA'] - visitor_stats['RA'], 'HRPG': hrpg, 'VRPG': vrpg}
        return team_stats
    
    # Compares the head to head record of the two teams
    def head_to_head(self):
        end_date = get_prior_date(self.date)
        start_date = end_date[:4] + '0101'
        home_wins, visitor_wins = 0, 0
        """
        for gameid in GAMES[self.year]:
            game = GAMES[self.year][gameid]
            if game.date <= end_date and game.date >= start_date:
                if self.home in (game.home, game.visitor) and self.visitor in (game.home, game.visitor):
                    if self.home == game.home and game.home_win:
                        home_wins += 1
                    elif self.home == game.visitor and not game.home_win:
                        home_wins += 1

                    if self.visitor == game.home and game.home_win:
                        visitor_wins += 1
                    elif self.visitor == game.visitor and not game.home_win:
                        visitor_wins += 1
        """

        for gameid in GAMES[self.year][self.home]:
            game = GAMES[self.year][self.home][gameid]
            if game.date <= end_date and game.date >= start_date:
                if self.home == game.home and game.home_win:
                    home_wins += 1
                elif self.home == game.visitor and not game.home_win:
                    home_wins += 1
                """
                if self.visitor == game.home and game.home_win:
                    visitor_wins += 1
                elif self.visitor == game.visitor and not game.home_win:
                    visitor_wins += 1
                """
        for gameid in GAMES[self.year][self.visitor]:
            game = GAMES[self.year][self.visitor][gameid]
            if game.date <= end_date and game.date >= start_date:
                if self.visitor == game.home and game.home_win:
                    visitor_wins += 1
                elif self.visitor == game.visitor and not game.home_win:
                    visitor_wins += 1

        h2h_totals = {'HWins': home_wins, 'VWins': visitor_wins}
        return h2h_totals
    
    def team_batting_stats(self, home_start=None, visitor_start=None):
        home_stats, visitor_stats, results = dict(), dict(), dict()
        end_date = get_prior_date(self.date)
        if home_start == None or visitor_start == None:
            home_start, visitor_start = self.year + '0101', self.year + '0101'
        # Goes through each player in the STARTING lineup
        #checked = {self.home: [], self.visitor: []}
        #print(f'In game {self.id}, home_starting_lineup = {self.home_starting_lineup}, visitor_starting_lineup = {self.visitor_starting_lineup}')
        for i in range(len(self.home_starting_lineup)):
            # 0 is None, 1 is the pitcher
            if i > 1 and self.home_starting_lineup[i] != None and self.visitor_starting_lineup[i] != None:
                # Collects batting totals
                #checked[self.home].append(self.home_starting_lineup[i])
                #checked[self.visitor].append(self.visitor_starting_lineup[i])
                #print(f'Home Start: {home_start}, end_date {end_date}')
                htotals, vtotals = self.home_starting_lineup[i].get_totals(self.home, end_date, home_start), self.visitor_starting_lineup[i].get_totals(self.visitor, end_date, visitor_start)
                #print(f'IN GAME: {self.home_starting_lineup[i].id}, htotals = {htotals}')
                # Sums each statistic
                for hstat, vstat in zip(htotals, vtotals):
                    if hstat not in home_stats:
                        home_stats[hstat] = 0
                    if vstat not in visitor_stats:
                        visitor_stats[vstat] = 0
                    home_stats[hstat] += htotals[hstat] 
                    visitor_stats[vstat] += vtotals[vstat]
        #print(f'IN game {self.id}, checked = {checked}, total of {len(checked[self.home])} players home and total of {len(checked[self.visitor])} players visitor')
        #print(f'In game {self.id}, home stats = {home_stats}, visitor stats = {visitor_stats}')
        home_stats['AVG'], visitor_stats['AVG'] = calc_avg(home_stats['H'], home_stats['AB']), calc_avg(visitor_stats['H'], visitor_stats['AB'])
        home_stats['SLG'], visitor_stats['SLG'] = calc_slg(home_stats['S'], home_stats['D'], home_stats['T'], home_stats['HR'], home_stats['AB']), calc_slg(visitor_stats['S'], visitor_stats['D'], visitor_stats['T'], visitor_stats['HR'], visitor_stats['AB'])
        home_stats['OBP'], visitor_stats['OBP'] = calc_obp(home_stats['H'], home_stats['BB'], home_stats['HBP'], home_stats['AB'], home_stats['SF']), calc_obp(visitor_stats['H'], visitor_stats['BB'], visitor_stats['HBP'], visitor_stats['AB'], visitor_stats['SF'])
        home_stats['ISO'], visitor_stats['ISO'] = calc_iso(home_stats['SLG'], home_stats['AVG']), calc_iso(visitor_stats['SLG'], visitor_stats['AVG'])
        home_stats['OPS'], visitor_stats['OPS'] = calc_ops(home_stats['SLG'], home_stats['AVG']), calc_ops(visitor_stats['SLG'], visitor_stats['AVG'])
        # TODO: THIS is a defense stat, not a batting stat 
        #home_stats['DER'], visitor_stats['DER'] = calc_der(home_stats['H'], home_stats['ROE'], home_stats['HR'], home_stats['PA'], home_stats['BB'], home_stats['K'], home_stats['HBP']), calc_der(visitor_stats['H'], visitor_stats['ROE'], visitor_stats['HR'], visitor_stats['PA'], visitor_stats['BB'], visitor_stats['K'], visitor_stats['HBP'])
        results['AVG'] = round(home_stats['AVG'] - visitor_stats['AVG'], 3)
        results['SLG'] = round(home_stats['SLG'] - visitor_stats['SLG'], 3)
        results['OBP'] = round(home_stats['OBP'] - visitor_stats['OBP'], 3)
        results['ISO'] = round(home_stats['ISO'] - visitor_stats['ISO'], 3)
        results['OPS'] = round(home_stats['OPS'] - visitor_stats['OPS'], 3)
        results['HSLG'] = home_stats['SLG']
        results['VSLG'] = visitor_stats['SLG']
        results['HBA'] = home_stats['AVG']
        results['VBA'] = visitor_stats['AVG']
        #results['DER'] = round(home_stats['DER'] - visitor_stats['DER'], 3)
        # Find difference between home and away stats
        """
        for i in home_stats:
            if i not in results:
                results[i] = 0
            results[i] = home_stats[i] - visitor_stats[i]
        """
        return results
    
    def comp_sps(self):
        end_date = get_prior_date(self.date)
        results = dict()
        """
        year = self.date[:4]
        home_stats, visitor_stats = dict(), dict()
        for h in TEAM_ROS[year][self.home]:
            if h.pos == 'P':
                stats = h.get_totals(end_date)
                for stat in stats:
                    if stat not in home_stats:
                        home_stats[stat] = 0
                    home_stats[stat] += stats[stat]
        for v in TEAM_ROS[year][self.visitor]:
            if v.pos == 'P':
                stats = v.get_totals(end_date)
                for stat in stats:
                    if stat not in visitor_stats:
                        visitor_stats[stat] = 0
                    visitor_stats[stat] += stats[stat]
        """
        home_stats, visitor_stats = self.home_starting_lineup[1].get_totals(self.home, end_date), self.visitor_starting_lineup[1].get_totals(self.visitor, end_date)
        results['ERA'] = round(calc_era(home_stats['ER'], home_stats['IP']) - calc_era(visitor_stats['ER'], visitor_stats['IP']), 2)
        results['WHIP'] = round(calc_whip(home_stats['Hp'], home_stats['BBp'], home_stats['OP']) - calc_whip(visitor_stats['Hp'], visitor_stats['BBp'], visitor_stats['IP']), 2)
        results['BB9'] = round(calc_bb9(home_stats['BBp'], home_stats['IP']) - calc_bb9(visitor_stats['BBp'], visitor_stats['IP']), 2)
        results['K9'] = round(calc_k9(home_stats['Kp'], home_stats['IP']) - calc_k9(visitor_stats['Kp'], visitor_stats['IP']), 2)
        results['HR9'] = round(calc_hr9(home_stats['HRp'], home_stats['IP']) - calc_hr9(visitor_stats['HRp'], visitor_stats['IP']), 2)
        results['FIP'] = round(calc_fip(home_stats['HRp'], home_stats['BBp'], home_stats['HBPp'], home_stats['Kp'], home_stats['IP']) - calc_fip(visitor_stats['HRp'], visitor_stats['BBp'], visitor_stats['HBPp'], visitor_stats['Kp'], visitor_stats['IP']), 2)
        return results
    
    def comp_pitchers(self, home_start=None, visitor_start=None):
        end_date = get_prior_date(self.date)
        results = dict()
        year = str(self.year)
        home_stats, visitor_stats = dict(), dict()
        if home_start == None:
            home_start = year + '0101'
        if visitor_start == None:
            visitor_start = year + '0101'
        for h in TEAM_ROS[year][self.home]:
            if h.pos == 'P':
                stats = h.get_totals(self.home, end_date, home_start)
                for stat in stats:
                    if stat not in home_stats:
                        home_stats[stat] = 0
                    home_stats[stat] += stats[stat]
        for v in TEAM_ROS[year][self.visitor]:
            if v.pos == 'P':
                stats = v.get_totals(self.visitor, end_date, visitor_start)
                for stat in stats:
                    if stat not in visitor_stats:
                        visitor_stats[stat] = 0
                    visitor_stats[stat] += stats[stat]
        results['ERA'] = round(calc_era(home_stats['ER'], home_stats['IP']) - calc_era(visitor_stats['ER'], visitor_stats['IP']), 2)
        results['WHIP'] = round(calc_whip(home_stats['Hp'], home_stats['BBp'], home_stats['OP']) - calc_whip(visitor_stats['Hp'], visitor_stats['BBp'], visitor_stats['IP']), 2)
        results['BB9'] = round(calc_bb9(home_stats['BBp'], home_stats['IP']) - calc_bb9(visitor_stats['BBp'], visitor_stats['IP']), 2)
        results['K9'] = round(calc_k9(home_stats['Kp'], home_stats['IP']) - calc_k9(visitor_stats['Kp'], visitor_stats['IP']), 2)
        results['HR9'] = round(calc_hr9(home_stats['HRp'], home_stats['IP']) - calc_hr9(visitor_stats['HRp'], visitor_stats['IP']), 2)
        results['FIP'] = round(calc_fip(home_stats['HRp'], home_stats['BBp'], home_stats['HBPp'], home_stats['Kp'], home_stats['IP']) - calc_fip(visitor_stats['HRp'], visitor_stats['BBp'], visitor_stats['HBPp'], visitor_stats['Kp'], visitor_stats['IP']), 2)
        return results
    
    