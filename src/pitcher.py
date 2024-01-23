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

    def reset_stats(self):
        self.appearances = 0

    def __repr__(self):
        return f'Pitcher object of {self.name} on {self.team} with id {self.id}'