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
        self.simulate_game()

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
                self.players_in_game.append(PITCHERS[playerid])
            else:
                if is_home:
                    self.home_lineup[field_pos] = PLAYERS[playerid]
                else:
                    self.visitor_lineup[field_pos] = PLAYERS[playerid]
                PLAYERS[playerid].reset_game_stats()
                self.players_in_game.append(PLAYERS[playerid])   

    # Loops through the plays and parses them/collects statistics accordingly
    def simulate_game(self):
        self.bases = [None] * 4
        self.op = 0
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
                if is_home:
                    pitcher = self.visitor_lineup[1]
                else:
                    pitcher = self.home_lineup[1]
                pitcher.inc_game_stat(['P'], [total_pitches])
                self.parse_play(play, batter, pitcher)
            # When a player is substituted for another
            elif line[0] == 'sub':
                # TODO: The numbers are in the standard notation, with designated hitters being identified as position 10. On sub records 11 indicates a pinch hitter and 12 is used for a pinch runner. When a player pinch hits or pinch runs for the DH, that player automatically becomes the DH, so no 'sub' record is included to identify the new DH.
                #['sub', 'gonzv001', '"Victor Gonzalez"', '1', '0', '1']
                playerid = line[1]
                playername = line[2]
                is_home = int(line[3]) == 1
                bat_pos = int(line[4])
                field_pos = int(line[5])
                # TODO: TEMP - adjust to account for pinch runners and hitters
                if field_pos >= 10:
                    field_pos = 10
                # TODO: adjust for end of a pitcher's outing
                # Field pos 1 is a pitcher
                if field_pos == 1:
                    # CHecks for players being subbed as pitchers
                    if playerid not in PITCHERS:
                        PITCHERS[playerid] = Pitcher(f'{playerid},{playername.split(" ")[1]},{playername.split(" ")[0]},,,,{field_pos}')
                    # If being subbed in as a pitcher, the bat pos will be 0, otherwise they are subbed in as bothj a pitcher and batter (usually extra innings)
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
                else:
                    # Checks for pitchers being subbed as players
                    if playerid not in PLAYERS:
                        PLAYERS[playerid] = Player(f'{playerid},{playername.split(" ")[1]},{playername.split(" ")[0]},,,,{field_pos}')
                    if is_home:
                        self.home_lineup[field_pos] = PLAYERS[playerid]
                    else:
                        self.visitor_lineup[field_pos] = PLAYERS[playerid]
            # Tracks a the ER of each pitcher
            elif line[0] == 'com':
                if self.com:
                    print(line)
            elif line[0] == 'data':
                pass
            else:
                # TODO: Account for radj and badj
                pass
            
    def parse_play(self, play, batter, pitcher):
        self.com = False # TODO: TEMP
        # 'Simple Plays'
        simple = play.split('/')[0]
        mod, runners = None, None
        if '/' in play:
            mod = play.split('.')[0].split('/')[1:]
        if '.' in play:
            runners = play.split('.')[1:]

        # Number beginning a simple play represents a ground/line out
        if simple[0].isnumeric():
            # Parenthesis represents a double play, with the character inside the parenthesis representing the baserunner out
            if '(' in simple:
                runner = simple.split(')')[0][-1]
                # 'B' - If the putout is made at a base not normally covered by the fielder the base runner, batter in this example, is given explicitly.
                #if runner != 'B':
                # If the last digit is a number, it represents a double play
                if simple[-1].isnumeric():
                    self.bases[int(runner)] = None
                    #print(f'Double play, {runner} out as well as batter - {play}')
                    pitcher.inc_game_stat(['OP', 'BF'], [2, 1])
                else:
                    # Runner in parenthesis represents a force out - B in parenthesis is the batter, so empty base is implied
                    if runner.isnumeric():
                        self.bases[int(runner)] = None
                        #print(f'Force out at, {runner} out - {play}')
                    #else:
                        #print(f'Unusual fo, batter out - {play}')
                    pitcher.inc_game_stat(['OP', 'BF'], [2, 1])
            else:
                #print(f'Pop/lineout, batter out - {play}')
                pitcher.inc_game_stat(['OP', 'BF'], [1, 1])
            batter.inc_game_stat(['PA', 'AB'], [1, 1])
        # Interference by a player resulting in batter going to 1 and all others advancing
        elif 'C/E' in play:
            batter.inc_game_stat(['PA'], [1])
            pitcher.inc_game_stat(['BF'], [1])
            self.adv_bases()
            #print(f'Interference, all runners advance - {play}')
        # Single
        elif simple.startswith('S'):
            batter.inc_game_stat(['S', 'PA', 'AB', 'H'], [1, 1, 1, 1])
            pitcher.inc_game_stat(['H', 'BF'], [1, 1])
            self.adv_bases()
        # Double
        elif simple.startswith('D') or simple.startswith('DGR'):
            batter.inc_game_stat(['D', 'PA', 'AB', 'H'], [1, 1, 1, 1])
            pitcher.inc_game_stat(['H', 'BF'], [1, 1])
            self.adv_bases()
        # Triple
        elif simple.startswith('T'):
            batter.inc_game_stat(['T', 'PA', 'AB', 'H'], [1, 1, 1, 1])
            pitcher.inc_game_stat(['H', 'BF'], [1, 1])
            self.adv_bases()
        # Fielding Error
        elif simple.startswith('E') and simple[1].isnumeric():
            batter.inc_game_stat(['PA', 'AB'], [1, 1])
            pitcher.inc_game_stat(['BF'], [1])
        # Fielders choice - batter goes to first, another runner is attempted to get out
        elif simple.startswith('FC'):
            batter.inc_game_stat(['AB', 'PA'], [1, 1])
            pitcher.inc_game_stat(['BF'], [1])
            # TODO: make sure to treat outs for the pitcher
            self.adv_bases()
        elif 'H/' in play or simple.startswith('HR'):
            batter.inc_game_stat(['HR', 'AB', 'PA', 'H'], [1, 1, 1, 1])
            pitcher.inc_game_stat(['HR', 'R', 'BF'], [1, 1, 1])
            self.adv_bases()
        # Hit by Pitch
        elif simple.startswith('HP'):
            batter.inc_game_stat(['HBP', 'PA', 'AB'], [1, 1, 1])
            pitcher.inc_game_stat(['HBP', 'BF'], [1, 1])
            self.adv_bases()
        # K + something represents a strikout plus another event
        elif simple.startswith('K+') or (simple.startswith('K') and '+' in simple):
            # TODO: Treat strikeout edge cases
            pass
        elif simple.startswith('K'):
            batter.inc_game_stat(['K', 'PA', 'AB'], [1, 1, 1])
            pitcher.inc_game_stat(['K', 'OP', 'BF'], [1, 1, 1])
        elif simple.startswith('W+') or (simple.startswith('W') and '+' in simple):
            # TODO: treat walk edge cases
            pass
        elif simple.startswith('I') or simple.startswith('IW') or simple.startswith('W'):
            batter.inc_game_stat(['BB', 'PA'], [1, 1])
            pitcher.inc_game_stat(['BB', 'BF'], [1, 1])
        # Balk
        elif simple.startswith('BK'):
            # TODO: treat balks, advance all runners
            self.adv_bases()
            pass
        # Player caught stealing
        elif simple.startswith('CS'):
            base = simple[2]
            # TODO: treat caught stealing, general base running
        # Defensive indifference, runner allowed to steal
        elif simple.startswith("DI"):
            # TODO: treat defensive indifference, advance runner
            pass
        elif simple.startswith('PB') or simple.startswith('WP'):
            #TODO: passed ball/wild pitch, not a batter stat but runners may have advanced.
            pass
        elif simple.startswith('PO'):
            # Error, runner advances
            if '(E' in simple:
                # TODO: account for the error
                self.adv_bases()
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
            # Runner picked off, base represets the base they were at
            else:
                base = simple[2]
                if base == 'H':
                    self.bases[3] = None
                else:
                    self.bases[int(base) - 1] = None
                pitcher.inc_game_stat(['OP'], [1])
        # Stolen Base
        elif simple.startswith('SB'):
            steals = simple.split(';')
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
        elif simple.startswith('OA'):
            print(play)
            self.com = True
        else:
            print(f'MISSED CASE: {play}')

        """
        if '/' not in play and '.' not in play:
            if play == 'W':
                batter.inc_game_stat(['BB', 'PA'], [1, 1])
                pitcher.inc_game_stat(['BB', 'BF'], [1, 1])
                self.bases[1] = batter
            elif play == 'K':
                batter.inc_game_stat(['SO', 'PA', 'AB'], [1, 1, 1])
                pitcher.inc_game_stat(['OP', 'SO', 'BF'], [1, 1, 1])
                self.op += 1
            elif play == 'HP':
                batter.inc_game_stat(['HBP', 'PA'], [1, 1])
                pitcher.inc_game_stat(['HBP', 'BF'], [1, 1])
                self.adv_bases(1)
        """
        #print(f'Simple: {simple}, mod {mod}, run mvmt {runners}, full {play}')
        # TODO: How to treat new innings
        if self.op == 3:
            self.op = 0

    # Handles base movement and increments runs if someone scores
    # TODO: does it matter? Do we need to track score like this?
    def adv_bases(self, mvmt=1):
        pass
