from const import *

class Player():
    def __init__(self, line):
        info = line.split(',')
        self.id = info[0]
        self.name = info[2] + ' ' + info[1]
        self.bats = info[3]
        self.throws = info[4]
        self.team = info[5]
        self.pos = info[6]
        self.reset_stats()
        self.reset_temp_stats()

    def add_temp_stat(self, stat, quantity):
        # Convert to [stat] list to make it easier to add multiple stats?
        if stat not in self.temp_stats:
            print(f'{stat} not in {self.__repr__()}\'s stats.')
            return False
        self.temp_stats[stat] += quantity

    def inc_total_stats(self):
        for stat in self.temp_stats:
            self.totals[stat] += self.temp_stats[stat]

    def reset_stats(self):
        self.totals = {'PA': 0, 'ABs': 0, 'Hits': 0, 'Singles': 0, 'Doubles': 0, 'Triples': 0, 'Home Runs': 0, 'Strikeouts': 0, 'Walks': 0, 'Stolen Bases': 0, 'Games': 1, 'Runs': 0, 'RBI': 0}

    def reset_temp_stats(self):
        # Add specific stats like sac flies, popouts, etc?
        self.temp_stats = {'PA': 0, 'ABs': 0, 'Hits': 0, 'Singles': 0, 'Doubles': 0, 'Triples': 0, 'Home Runs': 0, 'Strikeouts': 0, 'Walks': 0, 'Stolen Bases': 0, 'Games': 1, 'Runs': 0, 'RBI': 0}
    
    def get_batting_totals(self):
        # Use totals and loop through games like we did before
        pass

    def __repr__(self):
        return f'Player object of {self.name} on {self.team} with id {self.id}'