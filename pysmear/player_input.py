import pydealer
import math
from pydealer.const import POKER_RANKS
from smear_utils import SmearUtils as utils
from bidding_logic import *
from playing_logic import *
import json
import time

class PlayerInput(SmearBiddingLogic, SmearPlayingLogic):
    def __init__(self, debug):
        self.debug = debug
        self.reset()

    def reset(self):
        self.bid_info = {}
        self.player_bid = None 
        self.player_bid_trump = None
        self.playing_info = {}
        self.playing_card_index = 0


    def convert_bid_info_to_dict(self, current_hand, force_two):
        bid_info = {}
        bid_info['force_two'] = force_two
        bid_info['current_bid'] = current_hand.bid
        #bid_info['bidder'] = current_hand.players[current_hand.bidder].name
        bid_info['bidder'] = current_hand.bidder
        return bid_info

    def save_bid_info(self, current_hand, force_two):
        self.bid_info = self.convert_bid_info_to_dict(current_hand, force_two)
        # TODO: remove this later
        self.save_bid(2, "Spades")

    def get_bid_info(self):
        return self.bid_info

    def save_bid(self, bid, bid_trump):
        self.player_bid = bid
        self.player_bid_trump = bid_trump

    def get_bid_from_player(self):
        while self.player_bid == None or self.player_bid_trump == None:
            time.sleep(5)
        return self.player_bid, self.player_bid_trump

    def declare_bid(self, current_hand, my_hand, force_two=False):
        bid = 0
        bid_trump = ""
        self.save_bid_info(current_hand, force_two)
        bid, bid_trump = self.get_bid_from_player()
        return bid, bid_trump

    def convert_playing_info_to_dict(self, current_hand, my_hand):
        playing_info = {}
        playing_info['trump'] = current_hand.trump
        playing_info['current_trick'] = [ card.abbrev for card in current_hand.current_trick.cards ]
        playing_info['current_winning_card'] = current_hand.current_trick.current_winning_card.abbrev if current_hand.current_trick.current_winning_card is not None else "None"
        playing_info['lead_suit'] = current_hand.current_trick.lead_suit
        playing_info['my_hand'] = [ { "suit": card.suit, "value": card.value} for card in my_hand ]
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
