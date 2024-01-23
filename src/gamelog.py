from const import *

class GameLog:
    def __init__(self, game):
        self.metadata = self.parse_gl_data(game)
        self.date = self.metadata['date']
        self.home = self.metadata['home']
        self.visitor = self.metadata['visitor']
        self.home_score = self.metadata['hscore']
        self.visitor_score = self.metadata['vscore']

    def parse_gl_data(self, game):
        data = game.split(',')
        metadata = dict()
        # Use zip to iterate over CATEGORIES and data simultaneously
        for category, value in zip(CATEGORIES, data):
            metadata[category] = value.strip('"')
        # Check if there are extra elements in data
        if len(data) > len(CATEGORIES):
            metadata['misc'] = data[len(CATEGORIES):]
        return metadata

    def __repr__(self):
        return f"Game on {self.date} with {self.visitor} at {self.home}"