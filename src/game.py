from const import *

class Game:
    def __init__(self, data):
        self.hi = 1
        print(data)
        self.id = data[0][3:-1]
        print(self.id)
        # REMEMBER TO SET CONNECTION TO GameLog obj
        self.GameLog = None