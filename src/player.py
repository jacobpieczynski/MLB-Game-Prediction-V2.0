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

    def __repr__(self):
        return f'Player object {self.name}, a {self.pos} for {self.team} - ID: {self.id}'