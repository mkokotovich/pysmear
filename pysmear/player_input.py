import pydealer
import math
from pydealer.const import POKER_RANKS
from smear_utils import SmearUtils as utils
from bidding_logic import *
from playing_logic import *
import json

class PlayerInput(SmearBiddingLogic, SmearPlayingLogic):

    def convert_bid_info_to_dict(self, current_hand, my_hand, force_two):
        bid_info = {}
        bid_info['force_two'] = force_two
        bid_info['num_players'] = current_hand.num_players
        bid_info['current_bid'] = current_hand.bid
        bid_info['my_hand'] = [ card.abbrev for card in my_hand ]
        return bid_info

    def send_bid_info_to_player(self, current_hand, my_hand, force_two):
        bid_info = self.convert_bid_info_to_dict(current_hand, my_hand, force_two)
        bid_json = json.dumps(bid_info)
        print bid_json

    def get_bid_from_player(self):
        return 2, "Spades"

    def declare_bid(self, current_hand, my_hand, force_two=False):
        bid = 0
        bid_trump = ""
        self.send_bid_info_to_player(current_hand, my_hand, force_two)
        bid, bid_trump = self.get_bid_from_player()
        return bid, bid_trump

    def convert_playing_info_to_dict(self, current_hand, my_hand):
        playing_info = {}
        playing_info['trump'] = current_hand.trump
        playing_info['current_trick'] = [ card.abbrev for card in current_hand.current_trick.cards ]
        playing_info['current_winning_card'] = current_hand.current_trick.current_winning_card.abbrev if current_hand.current_trick.current_winning_card is not None else "None"
        playing_info['lead_suit'] = current_hand.current_trick.lead_suit
        playing_info['my_hand'] = [ card.abbrev for card in my_hand ]
        return playing_info

    def send_playing_info_to_player(self, current_hand, my_hand):
        playing_info = self.convert_playing_info_to_dict(current_hand, my_hand)
        playing_json = json.dumps(playing_info)
        print playing_json

    def get_card_index_from_player(self):
        return 0

    def choose_card(self, current_hand, my_hand):
        self.send_playing_info_to_player(current_hand, my_hand)
        card_index = self.get_card_index_from_player()
        return card_index
