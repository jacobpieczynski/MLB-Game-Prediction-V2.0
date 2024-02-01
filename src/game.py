from const import *
from pitcher import Pitcher
from player import Player

class Game:
    def __init__(self, data):
        self.com = False # TEMP
        self.sort_data(data)

    def __repr__(self):
        if self.id:
            return f'Game object: {self.id} on {self.date} - {self.info["visteam"]} at {self.info["hometeam"]}'

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
                print('Line type not found:')
        self.simulate_game()
        self.get_team_records()
        self.head_to_head()
        self.team_batting_stats

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
        self.home = info['hometeam']
        self.visitor = info['visteam']
        self.info = info
        self.GameLog = GAMELOG[self.date[:4]][self.id]
        self.hscore = int(self.GameLog.home_score)
        self.vscore = int(self.GameLog.visitor_score)
        self.home_win = self.hscore > self.vscore
        self.id += self.factor
        

    # Takes the 'start' information and sets the lineups based off it
    def set_lineup(self):
        self.home_lineup, self.visitor_lineup, self.players_in_game = [None] * 11, [None] * 11, dict() # lineup[0] is none, after that the idx represents their field pos
        for line in self.start:
            line = line.split(',')
            playerid = line[1]
            is_home = int(line[3]) == 1
            field_pos = int(line[5])
            is_pitcher = (field_pos == 1)
            # TODO: Improve this? Seems a bit of a redundant way to do it
            # TODO: How do we treat years? Will players be able to fit into a general PLAYERS roster or do we need to sort by year?
            # Adds players into the lineup based on their position - remember, pitchers and players are different objects
            if is_pitcher:
                if is_home:
                    self.home_lineup[field_pos] = PITCHERS[playerid]
                else:
                    self.visitor_lineup[field_pos] = PITCHERS[playerid]
                PITCHERS[playerid].reset_game_stats()
                PITCHERS[playerid].inc_game_stat(['G', 'S'], [1, 1])
                self.players_in_game[playerid] = PITCHERS[playerid]
            else:
                if is_home:
                    self.home_lineup[field_pos] = PLAYERS[playerid]
                else:
                    self.visitor_lineup[field_pos] = PLAYERS[playerid]
                PLAYERS[playerid].reset_game_stats()
                self.players_in_game[playerid] = PLAYERS[playerid] 
        self.home_starting_lineup = self.home_lineup.copy()
        self.visitor_starting_lineup = self.visitor_lineup.copy()

    # Loops through the plays and parses them/collects statistics accordingly
    def simulate_game(self):
        self.parse_info()
        self.set_lineup()
        self.bases = [None] * 4
        self.op, self.inning, self.side = 0, 0, 0
        radj = False
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
                    pitcher = PITCHERS[self.visitor_lineup[1].id]
                else:
                    pitcher = PITCHERS[self.home_lineup[1].id]
                if pitcher.id not in self.players_in_game:
                    self.players_in_game[pitcher.id] = pitcher

                pitcher.inc_game_stat(['P'], [total_pitches])
                self.parse_play(play, batter, pitcher)
                # Hacky way to fix a FC error 
                # TODO: Look at game 20230620SFNSDN, Anthony Descalfani is given 4 outs in the 3rd inning
                if self.op >= 4:
                    pitcher.inc_game_stat(['OP'], [-1])
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

                # Field pos 1 is a pitcher
                if field_pos == 1:
                    # Checks for players being subbed as pitchers
                    if playerid not in PITCHERS:
                        PITCHERS[playerid] = Pitcher(f'{playerid},{playername.split(" ")[1]},{playername.split(" ")[0]},,,,{field_pos}')
                    # If being subbed in as a pitcher, the bat pos will be 0, otherwise they are subbed in as both a pitcher and batter (usually extra innings)
                    if bat_pos != 0:
                        if playerid not in PLAYERS:
                            PLAYERS[playerid] = Player(f'{playerid},{playername.split(" ")[1]},{playername.split(" ")[0]},,,,{field_pos}')
                        if is_home:
                            self.home_lineup[bat_pos] = PLAYERS[playerid]
                        else:
                            self.visitor_lineup[bat_pos] = PLAYERS[playerid]
                    # Regardless, they will be subbed in as a pitcher
                    if is_home:
                        self.home_lineup[1] = PITCHERS[playerid]
                    else:
                        self.visitor_lineup[1] = PITCHERS[playerid]
                    self.players_in_game[playerid] = PITCHERS[playerid]
                    PITCHERS[playerid].inc_game_stat(['G'], [1])
                else:
                    # Checks for pitchers being subbed as players
                    if playerid not in PLAYERS:
                        PLAYERS[playerid] = Player(f'{playerid},{playername.split(" ")[1]},{playername.split(" ")[0]},,,,{field_pos}')
                    if is_home:
                        self.home_lineup[field_pos] = PLAYERS[playerid]
                    else:
                        self.visitor_lineup[field_pos] = PLAYERS[playerid]
                    self.players_in_game[playerid] = PLAYERS[playerid]
            elif line[0] == 'com':
                if self.com:
                    #print(line)
                    pass
            # Tracks a the ER of each pitcher
            elif line[0] == 'data':
                PITCHERS[line[2]].inc_game_stat(['ER'], [int(line[3])])
            # Runner Adjustment, for when an inning starts with someone on base (extra innings rule)
            elif line[0] == 'radj':
                radj = True
                self.bases[int(line[2])] = PLAYERS[line[1]]
            else:
                # TODO: Account for badj
                pass
        for player in self.players_in_game:
            self.players_in_game[player].add_game_stats()
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
                    self.bases[int(runner)] = None
                    pitcher.inc_game_stat(['OP', 'BF'], [2, 1])
                    self.op += 2
                # If there are two () it is also a double (or triple!) play
                elif simple.count('(') > 1:
                  ##print((f'Lined into play, {runner} out as well as batter - {play}')
                    pitcher.inc_game_stat(['OP', 'BF'], [int(simple.count('(')), 1])
                    self.op += int(simple.count('('))
                else:
                    # Runner in parenthesis represents a force out - B in parenthesis is the batter, so empty base is implied
                    if runner.isnumeric():
                        self.bases[int(runner)] = None
                    #else:
                      ##print((f'Unusual fo, batter out - {play}')
                    pitcher.inc_game_stat(['OP', 'BF'], [1, 1])
                    self.op += 1
            # Other numeric entries represent a simple pop/lineout
            else:
                pitcher.inc_game_stat(['OP', 'BF'], [1, 1])
                self.op += 1
            # Records sacrifice hits - sacs don't count as an at bat, just a plate appearance
            if '/SF' in play or '/SH' in play:
                batter.inc_game_stat(['PA', 'Sac'], [1, 1])
            else:
                batter.inc_game_stat(['PA', 'AB'], [1, 1])
        # Defensive indifference, runner allowed to steal
        elif simple.startswith("DI"):
            # TODO: treat defensive indifference, advance runner
            pass
        # Interference by a player resulting in batter going to 1 and all others advancing
        elif 'C/E' in play:
            batter.inc_game_stat(['PA'], [1])
            pitcher.inc_game_stat(['BF'], [1])
        # Single
        elif simple.startswith('S') and not simple.startswith('SB'):
            batter.inc_game_stat(['S', 'PA', 'AB', 'H'], [1, 1, 1, 1])
            pitcher.inc_game_stat(['H', 'BF'], [1, 1])
        # Double
        elif simple.startswith('D') or simple.startswith('DGR'):
            batter.inc_game_stat(['D', 'PA', 'AB', 'H'], [1, 1, 1, 1])
            pitcher.inc_game_stat(['H', 'BF'], [1, 1])
        # Triple
        elif simple.startswith('T'):
            batter.inc_game_stat(['T', 'PA', 'AB', 'H'], [1, 1, 1, 1])
            pitcher.inc_game_stat(['H', 'BF'], [1, 1])
        # Fielding Error
        elif simple.startswith('E') and simple[1].isnumeric():
            batter.inc_game_stat(['PA', 'AB'], [1, 1])
            pitcher.inc_game_stat(['BF'], [1])
        # Fielders choice - batter goes to first, another runner is attempted to get out
        elif simple.startswith('FC'):
            batter.inc_game_stat(['AB', 'PA'], [1, 1])
            # Any of these cases means that a FC was attempted but no runner put out
            if ('B-1' in runners[0] and 'E' in runners[0]) or ('X' not in runners):
                pitcher.inc_game_stat(['BF'], [1])
            else:
                pitcher.inc_game_stat(['BF', 'OP'], [1, 1])
                self.op += 1
        # Home Run
        elif 'H/' in play or simple.startswith('HR'):
            batter.inc_game_stat(['HR', 'AB', 'PA', 'H'], [1, 1, 1, 1])
            pitcher.inc_game_stat(['HR', 'H', 'BF'], [1, 1, 1])
        # Hit by Pitch
        elif simple.startswith('HP'):
            batter.inc_game_stat(['HBP', 'PA'], [1, 1])
            pitcher.inc_game_stat(['HBP', 'BF'], [1, 1])
        # K + something represents a strikout plus another event
        elif simple.startswith('K+') or (simple.startswith('K') and '+' in simple):
            # TODO: Treat strikeout edge cases
            op = 1
            for mod in mods:
                # One of the edge cases, 'DP' in mod represents a double play in this case
                if 'DP' in mod:
                    op = 2
            batter.inc_game_stat(['K', 'PA', 'AB'], [1, 1, 1])
            pitcher.inc_game_stat(['K', 'OP', 'BF'], [1, op, 1])
            self.op += op
        # Strikeout
        elif simple.startswith('K'):
            batter.inc_game_stat(['K', 'PA', 'AB'], [1, 1, 1])
            pitcher.inc_game_stat(['K', 'OP', 'BF'], [1, 1, 1])
            self.op += 1
        elif simple.startswith('PB') or simple.startswith('WP'):
            #TODO: passed ball/wild pitch, not a batter stat but runners may have advanced.
            pass
        elif simple.startswith('W+') or (simple.startswith('W') and '+' in simple):
            # TODO: treat walk edge cases (for baserunning (?))
            batter.inc_game_stat(['BB', 'PA'], [1, 1])
            pitcher.inc_game_stat(['BB', 'BF'], [1, 1])
        # Intentional Walk
        elif simple.startswith('I') or simple.startswith('IW') or simple.startswith('W'):
            batter.inc_game_stat(['BB', 'PA'], [1, 1])
            pitcher.inc_game_stat(['BB', 'BF'], [1, 1])
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
                self.bases[base].inc_game_stat(['CS'], [1])
            else:
                pass
            pitcher.inc_game_stat(['OP'], [1])
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
                    self.bases[3].inc_game_stat(['CS'], [1])
                    self.bases[3] = None
                else:
                    self.bases[int(base) - 1].inc_game_stat(['CS'], [1])
                    self.bases[int(base) - 1] = None
                """
                pitcher.inc_game_stat(['OP'], [1])
                self.op += 1
            # Runner picked off, base represets the base they were at
            else:
                base = simple[2]
                if base == 'H':
                    self.bases[3] = None
                else:
                    self.bases[int(base) - 1] = None
                pitcher.inc_game_stat(['OP'], [1])
                self.op += 1
        # Stolen Base
        # TODO: Fix this (get rid of 1 ==2 ) when adv_bases works
        elif simple.startswith('SB'):
            if 1 == 2:
                steals = simple.split('.')[0].split(';')
                for steal in steals:
                    base = steal[2]
                    if base == 'H':
                        self.bases[3].inc_game_stat(['SB'], [1])
                        # TODO: Account for run scored ??
                    else:
                        self.bases[int(base) - 1].inc_game_stat(['SB'], [1])
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
                    pitcher.inc_game_stat(['OP'], [1])
                    self.op += 1
        
        #self.adv_bases(batter, simple, runners[0], play)

    # TODO: This function doesn't work whatsoever at the moment
    def adv_bases(self, batter, simple, runners=None, play=None):
        if 'OA' in simple and 'X' in runners:
            return False

        if runners == None:
            if (simple.startswith('S') or simple.startswith('HP') or simple.startswith('W') or simple.startswith('IW')) and not simple.startswith('SB') and not simple.startswith('W+'):
                self.bases[1] = batter
            elif simple.startswith('D'):
                self.bases[2] = batter
            elif simple.startswith('T'):
                self.bases[3] = batter
            elif (simple[0].isnumeric() or simple.startswith('K') or simple.startswith('HR')) and not simple.startswith('K+') and 'E' not in simple:
                pass
            elif simple.startswith('SB'):
                bases = simple.split(';')
                for base in bases:
                    if base[-1] == 'H':
                        self.bases[3] = None
                    else:
                        self.bases[int(base[-1])] = self.bases[int(base[-1]) - 1]
            elif 'SB' in simple:
                if simple.startswith('W+'):
                    self.bases[1] = batter
                bases = simple[2:].split(';')
                for base in bases:
                    if base[-1] == 'H':
                            self.bases[3] = None
                    else:
                        self.bases[int(base[-1])] = self.bases[int(base[-1]) - 1]
            elif simple.startswith('POCS'):
                self.bases[int(simple[4]) - 1] = None
            elif simple.startswith('PO'):
                self.bases[int(simple[2])] = None
            elif 'E' in simple:
                self.bases[1] = batter
            else:
                pass
        else:
            if 'B' in runners:
                runners = runners.split(';')
                for runner in runners:
                    # TODO: Fix this
                    if runners != None and 'X' in runner:
                        if 'E' in runner:
                            start = runner[0]
                            end = runner[2]
                            if start == 'B':
                                self.bases[int(end)] = batter
                            elif end == 'H':
                                self.bases[int(start)] = None
                            else:
                                self.bases[int(end)] = self.bases[int(start)]
                    else:
                        start = runner[0]
                        end = runner.split('-')[1][0]
                        if start != end:
                            if end == 'H' and start !='B':
                                self.bases[int(start)] = None
                            elif end == 'H' and start == 'B':
                                # Do nothing, batter doesn't end up on a base
                                # TODO: Wherever ends in "H" and doesn't include 'UR', batter gets an rbi
                                # TODO: Deal with outs
                                pass
                            elif start == 'B':
                                self.bases[int(end)] = batter
                            else:
                                self.bases[int(end)] = self.bases[int(start)]
                                self.bases[int(start)] = None
            else:
                runners = runners.split(';')
                for runner in runners:
                    # TODO: Fix this
                    if 'X' in runner:
                        pass
                    else:
                        start = runner[0]
                        end = runner.split('-')[1][0]
                        if start != end:
                            if end == 'H':
                                self.bases[int(start)] = None
                            else:
                                self.bases[int(end)] = self.bases[int(start)]
                                self.bases[int(start)] = None
                if (simple.startswith('S') or simple.startswith('HP') or simple.startswith('W') or simple.startswith('IW')) and not simple.startswith('SB') and not simple.startswith('WP'):
                    self.bases[1] = batter
                elif simple.startswith('D'):
                    self.bases[2] = batter
                elif simple.startswith('T'):
                    self.bases[3] = batter
                elif (simple[0].isnumeric() or simple.startswith('K') or simple.startswith('HR')) and not simple.startswith('K+') and 'E' not in simple:
                    pass
                elif simple.startswith('SB') or (simple.startswith('K+') and 'SB' in simple):
                    # TODO: Check that stolen bases are being measured correctly
                    if simple.startswith('K+'):
                        simple = simple[2:]
                    bases = simple.split('.')[0].split(';')
                    for base in bases:
                        base = base[-1]
                        if base == 'H':
                            pass
                        elif self.bases[int(base) - 1] != None:
                            self.bases[int(base)] = self.bases[int(base) - 1]
                            self.bases[int(base) - 1] = None
                        
                    pass
                elif simple.startswith('WP'):
                    # TODO: make sure wild pitches are being measured correctly
                    pass
                elif 'E' in simple:
                    self.bases[1] = batter
                else:
                    pass
        # TODO: Make sure to record when players are forced out

        """
        If no run log,
        Treat accordingly 


        If run log
        If b in run log, go through each run log

        If b not in run log,
        Treat run
        """

    # Statistics Functions
    def get_team_records(self):
        end_date = get_prior_date(self.date)
        start_date = end_date[:4] + '0101' # Jan 1 of the year of the game
        home_wins, visitor_wins = 0, 0
        home_losses, visitor_losses = 0, 0
        home_runs, visitor_runs = 0, 0
        hwpct, vwpct = 0, 0
        for gameid in GAMES:
            game = GAMES[gameid]
            #if game.date == '20231001':
                #print(f'{self.id}, gdate = {game.date}, end_date = {end_date}, comp = {game.date <= end_date}, comp 2 = {game.date >= start_date}')
            if game.date <= end_date and game.date >= start_date and (self.home in (game.home, game.visitor) or self.visitor in (game.home, game.visitor)):
                # Checks that the team is in the game and won
                if self.home == game.home and game.home_win:
                    home_wins += 1
                elif self.home == game.visitor and not game.home_win:
                    home_wins += 1
                elif self.home in (game.home, game.visitor):
                    home_losses += 1

                if self.visitor == game.home and game.home_win:
                    visitor_wins += 1
                elif self.visitor == game.visitor and not game.home_win:
                    visitor_wins += 1
                elif self.visitor in (game.home, game.visitor):
                    visitor_losses += 1

                # To add to total runs
                if self.home == game.home:
                    home_runs += game.hscore
                elif self.home == game.visitor:
                    home_runs += game.vscore
                if self.visitor == game.visitor:
                    visitor_runs += game.vscore
                #print(f'Add Win {game.id}, {visitor_wins}')
        if home_wins > 0:
            hwpct = round(home_wins / (home_wins + home_losses), 3)
        if visitor_wins > 0:
            vwpct = round(visitor_wins / (visitor_wins + visitor_losses), 3)
        self.team_stats = {'HWins': home_wins, 'HLosses': home_losses, 'HGames': home_wins + home_losses, 'HWPct': hwpct, 'HRuns': home_runs, 
                'VWins': visitor_wins, 'VLosses': visitor_losses, 'VGames': visitor_wins + visitor_losses, 'VWPct': vwpct, 'VRuns': visitor_runs}
        return self.team_stats
    
    # Compares the head to head record of the two teams
    def head_to_head(self):
        end_date = get_prior_date(self.date)
        start_date = end_date[:4] + '0101'
        home_wins, visitor_wins = 0, 0
        for gameid in GAMES:
            game = GAMES[gameid]
            if game.date <= end_date and game.date >= start_date and (self.home in (game.home, game.visitor) and self.visitor in (game.home, game.visitor)):
                if self.home == game.home and game.home_win:
                    home_wins += 1
                elif self.home == game.visitor and not game.home_win:
                    home_wins += 1

                if self.visitor == game.home and game.home_win:
                    visitor_wins += 1
                elif self.visitor == game.visitor and not game.home_win:
                    visitor_wins += 1
        self.h2h_totals = {'HWins': home_wins, 'VWins': visitor_wins}
        return self.h2h_totals
    
    def team_batting_stats(self):
        home_stats, visitor_stats, results = dict(), dict(), dict()
        end_date = get_prior_date(self.date)
        # Goes through each player in the STARTING lineup
        for i in range(len(self.home_starting_lineup)):
            # 0 is None, 1 is the pitcher
            if i > 1:
                # Collects batting totals
                htotals, vtotals = self.home_starting_lineup[i].get_totals(end_date), self.visitor_starting_lineup[i].get_totals(end_date)
                # Sums each statistic
                for hstat, vstat in zip(htotals, vtotals):
                    if hstat not in home_stats:
                        home_stats[hstat] = 0
                        visitor_stats[vstat] = 0
                    home_stats[hstat] += htotals[hstat] 
                    visitor_stats[vstat] += vtotals[vstat]

        # Find difference between home and away stats
        for i in home_stats:
            if i not in results:
                results[i] = 0
            results[i] = home_stats[i] - visitor_stats[i]
        self.team_batting_comp = results
        return results