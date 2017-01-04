import pydealer
import math
from pydealer.const import POKER_RANKS
from smear_utils import SmearUtils as utils
from bidding_logic import *
from playing_logic import *

class PlayerInput(SmearBiddingLogic, SmearPlayingLogic):
    def send_bid_info_to_player(self, current_hand, my_hand, force_two):
        pass

    def get_bid_from_player(self):
        return 2, "Spades"

    def declare_bid(self, current_hand, my_hand, force_two=False):
        bid = 0
        bid_trump = ""
        self.send_bid_info_to_player(current_hand, my_hand, force_two)
        bid, bid_trump = self.get_bid_from_player()
        return bid, bid_trump

    def send_playing_info_to_player(self, current_hand, my_hand):
        pass

    def get_card_index_from_player(self):
        return 0

    def choose_card(self, current_hand, my_hand):
        self.send_playing_info_to_player(current_hand, my_hand)
        card_index = self.get_card_index_from_player()
        return card_index
