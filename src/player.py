from const import *

class Player:
    def __init__(self, info):
        info = info.split(',')
        self.id = info[0]
        self.name = f'{info[2]} {info[1]}'
        self.bats = info[3]
        self.throws = info[4]
        self.team = info[5]
        self.pos = info[6]
        self.stats = {'PA': 0, 'AB': 0, 'H': 0, 'S': 0, 'D': 0, 'T': 0, 'HR': 0, 'BB': 0, 'K': 0, 'RBI': 0, 'SB': 0, 'CS': 0, 'SF': 0, 'SH': 0, 'HBP': 0, 'ROE': 0, 'G': 0, 'S': 0, 'IP': 0, 'OP': 0, 'ER': 0, 'HR': 0, 'BB': 0, 'H': 0, 'R': 0, 'HBP': 0, 'K': 0, 'BF': 0, 'P': 0}
        self.game_stats = dict()
        for stat in self.stats:
            self.game_stats[stat] = 0

    # Gets the player statistics between two dates
    def get_totals(self, end_date='20231231', start_date=None):
        year = end_date[0:4]
        if start_date == None:
            start_date = year + '0101'

        self.reset_stats()
        for gameid in GAMES[year]:
            game = GAMES[year][gameid]
            if self.id in game.player_stats and game.date <= end_date and game.date >= start_date:
                for stat in self.stats:
                    if stat not in self.stats:
                        self.stats[stat] = 0
                    #print(game.player_stats[self.id])
                    self.stats[stat] += game.player_stats[self.id][stat]
        self.stats['IP'] = self.op_to_ip(self.stats['OP'])
        return self.stats

    # Alters a given stat
    def inc_game_stat(self, game, stats: list, quantities: list):
        if len(stats) != len(quantities):
            print('Invalid number of stats compared to quantities, player inc_game_stat')
            print(stats)
            return False
        for stat, quantity in zip(stats, quantities):
            #self.game_stats[stat] += quantity
            if stat not in game.player_stats[self.id]:
                game.player_stats[self.id][stat] = 0
            game.player_stats[self.id][stat] += quantity

    # Adds all game stats to 'perm' stats
    def add_game_stats(self, game):
        for stat in self.game_stats:
            #self.stats[stat] += self.game_stats[stat]
            pass

    # Reset Functions:
    def reset_stats(self):
        for stat in self.stats:
            self.stats[stat] = 0

    def reset_game_stats(self):
        for stat in self.game_stats:
            self.game_stats[stat] = 0

    def op_to_ip(self, op):
        if op == 0:
            return 0
        return round(op / 3, 2)

    def __repr__(self):
        return f'Pitcher object {self.name}, a {self.pos} for {self.team} - ID: {self.id}'