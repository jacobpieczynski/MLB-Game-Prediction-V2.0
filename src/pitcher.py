from const import *

class Pitcher():
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

    def add_temp_stat(self, stat, quantity=1):
        if stat not in self.temp_stats:
            print(f'{stat} not in {self.__repr__()}\'s stats.')
            return False
        self.temp_stats[stat] += quantity

    def inc_total_stats(self):
        for stat in self.temp_stats:
            if stat == 'OP':
                self.totals['IP'] += self.convert_op_ip(self.temp_stats['OP'])
            self.totals[stat] += self.temp_stats[stat]

    def reset_stats(self):
        self.totals = {'Appearances': 1, 'Wins': 0, 'Losses': 0, 'Starts': 0, 'ER': 0, 'OP': 0, 'IP': 0, 'SOs': 0, 'Hits': 0, 'Walks': 0, 'HRs': 0, 'HBP': 0, 'BF': 0}

    def reset_temp_stats(self):
        # Add wild pitches, intentional walks, batters faced? More specific stats like # of popouts, strikes looking, etc.? Calc GameScore stat?
        self.temp_stats = {'Appearances': 1, 'Wins': 0, 'Losses': 0, 'Starts': 0, 'ER': 0, 'OP': 0, 'SOs': 0, 'Hits': 0, 'Walks': 0, 'HRs': 0, 'HBP': 0, 'BF': 0}

    # Convert outs pitched to the more commonly used "Innings Pitched"
    def convert_op_ip(op):
        # 7 = 2 1/3
        partial = op % 3
        return ((op - partial) / 3) + round(partial / 3, 2)
    
    def get_pitching_totals(self):
        # Use totals and loop through games like we did before
        # For game in games
        # if player in players_in_game
        #   simulate game
        # After loop
        # Return self.totals
        pass

    def __repr__(self):
        return f'Pitcher object of {self.name} on {self.team} with id {self.id}'