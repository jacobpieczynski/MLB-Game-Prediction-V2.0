from const import *
from pitcher import Pitcher
from player import Player

class Game:
    def __init__(self, data):
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
            elif line[0] == 'data':
                pass
            else:
                # TODO: Account for radj and badj
                pass
            
    def parse_play(self, play, batter, pitcher):
        # 'Simple Plays'
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
            print(play)
        # TODO: How to treat new innings
        if self.op == 3:
            self.op = 0

    # Handles base movement and increments runs if someone scores
    # TODO: does it matter? Do we need to track score like this?
    def adv_bases(self, mvmt):
        pass
