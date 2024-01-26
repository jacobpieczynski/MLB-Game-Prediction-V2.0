from const import *

class Pitcher:
    def __init__(self, info):
        info = info.split(',')
        self.id = info[0]
        self.name = f'{info[2]} {info[1]}'
        self.bats = info[3]
        self.throws = info[4]
        self.team = info[5]
        self.pos = info[6]

    # Gets the player statistics between two dates
    def get_totals(self, start_date, end_date):
        pass

    # Alters a given stat
    def inc_game_stat(self, stats: list, quantities: list):
        if len(stats) != len(quantities):
            print('Invalid number of stats compared to quantities, player inc_game_stat')
            return False
        for stat, quantity in stats, quantities:
            self.game_stats[stat] += quantities[quantity]

    # Adds all game stats to 'perm' stats
    def add_game_stats(self):
        for stat in self.game_stats:
            self.stats[stat] += self.game_stats[stat]

    # Reset Functions:
    def reset_stats(self):
        for stat in self.stats:
            self.stats[stat] = 0

    def reset_game_stats(self):
        for stat in self.game_stats:
            self.game_stats[stat] = 0

    def __repr__(self):
        return f'Pitcher object {self.name}, a {self.pos} for {self.team} - ID: {self.id}'