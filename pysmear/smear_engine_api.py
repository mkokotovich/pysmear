# API for playing the card game smear

import sys
from threading import Thread
from game_manager import SmearGameManager
from player import *
#from stats import SmearStats

def play_game_as_thread(smear):
    smear.play_hand()
    #while not smear.is_game_over():
    #    smear.play_hand()

class SmearEngineApi:
    def __init__(self, debug=False):
        self.debug = debug
        self.desired_players = 0
        self.smear = None
        self.thread = None
        #self.smear_stats = SmearStats()

    def create_new_game(self, num_players, cards_to_deal=6):
        self.smear = SmearGameManager(cards_to_deal=cards_to_deal, debug=self.debug)
        self.desired_players = num_players


    def add_player(self, player_id, interactive=False):
        if interactive:
            self.smear.add_player(InteractivePlayer(player_id, debug=self.debug))
        else:
            self.smear.add_player(Player(player_id, debug=self.debug))


    def all_players_added(self):
        return self.desired_players == len(self.smear.get_players())


    def get_number_of_players(self):
        return self.desired_players


    def get_player_names(self):
        names = [ x.name for x in self.smear.get_players() ]
        return names


    def start_game(self):
        if self.debug:
            print "\n\n Starting game \n"
        if not self.all_players_added():
            print "Error: Can't start game before all players are added"
            return
        print "Number of players: " + str(len(self.smear.get_players()))
        self.smear.reset_game()
        self.smear.start_game()
        self.thread = Thread(target=play_game_as_thread, args = ( self.smear, ))
        self.thread.start()


    def finish_game(self):
        self.thread.join()

    
    def get_hand_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            return None
        cards = player.get_hand()
        while len(cards) == 0:
            time.sleep(5)
            cards = player.get_hand()
        return cards


    def get_bid_info_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            return None
        bid_info = player.get_bid_info()
        while bid_info == None:
            time.sleep(5)
            bid_info = player.get_bid_info()
        # populate the username since we have that info here
        player_id = bid_info["bidder"]
        player_name = self.smear.get_players()[player_id].name
        bid_info["bidder"] = player_name
        return bid_info


    def submit_bid_for_player(self, player_name, bid):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            return None
        player.save_bid(bid)


    def get_high_bid(self):
        high_bid = 0
        player_id = 0
        username = ""
        while not self.smear.all_bids_are_in():
            time.sleep(5)
        high_bid, player_id = self.smear.get_bid_and_bidder()
        username = self.smear.get_players()[player_id].name
        return high_bid, username
