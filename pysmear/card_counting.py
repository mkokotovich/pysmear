# Simulator for the card game smear

import pydealer
from smear_utils import SmearUtils as utils


# A class that counts cards and can be used to aid playing logic
class CardCounting:
    def __init__(self, num_players, debug=False):
        self.num_players = num_players
        self.debug = debug
        self.player_has_trump = {}
        self.reset()


    def reset(self):
        for i in range(0, self.num_players):
            self.player_has_trump[i] = 0


    def update(self, player_id, card, current_hand):
        pass
