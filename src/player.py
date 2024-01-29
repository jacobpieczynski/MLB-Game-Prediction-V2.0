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
        self.stats = {'PA': 0, 'AB': 0, 'H': 0, 'S': 0, 'D': 0, 'T': 0, 'HR': 0, 'BB': 0, 'K': 0, 'RBI': 0, 'SB': 0, 'CS': 0, 'Sac': 0, 'HBP': 0}
        self.game_stats = dict()
        for stat in self.stats:
            self.game_stats[stat] = 0

    # Gets the player statistics between two dates
    def get_totals(self, start_date='20230101', end_date='20231231'):
        self.reset_stats()
        for gameid in GAMES:
            game = GAMES[gameid]
            if self.id in game.players_in_game and game.date <= end_date and game.date >= start_date:
                game.simulate_game()
        return self.stats

    # Alters a given stat
    def inc_game_stat(self, stats: list, quantities: list):
        if len(stats) != len(quantities):
            print('Invalid number of stats compared to quantities, player inc_game_stat')
            print(stats)
            return False
        for stat, quantity in zip(stats, quantities):
            self.game_stats[stat] += quantity

    # Adds all game stats to 'perm' stats
    def add_game_stats(self):
        for stat in self.game_stats:
            self.stats[stat] += self.game_stats[stat]

    # Reset Functions:
    def reset_stats(self):
        for stat in self.stats:
            self.stats[stat] = 0

    def reset_game_stats(self):
        if self.id == 'carrc005':
            print(f'{self.id} GAME: {self.game_stats["D"]}') # TODO: REmove this line
        for stat in self.game_stats:
            self.game_stats[stat] = 0

    def __repr__(self):
        return f'Player object {self.name}, a {self.pos} for {self.team} - ID: {self.id}'