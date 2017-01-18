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
        self.timeout_after = 600

    def wait_for_valid_output(self, function_to_call, debug_message=None):
        sleep_interval = 5
        time_waited = 0
        ret = function_to_call()
        while (ret == None or ret == False) and time_waited < self.timeout_after:
            #sleep and check again
            if self.debug:
                print "Sleeping: {}".format(debug_message)
            time.sleep(sleep_interval)
            time_waited += sleep_interval
            ret = function_to_call()
        if time_waited >= self.timeout_after:
            print "Calling {} ({}) took too long, giving up.".format(str(function_to_call), debug_message)
        return ret


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
        if self.debug:
            print "Finishing game"
        self.thread.join()

    
    def get_hand_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return None
        cards = self.wait_for_valid_output(player.get_hand, debug_message="Waiting for {}'s hand to be available".format(player_name))
        return cards


    def get_hand_id(self):
        return self.smear.get_hand_id()


    def get_bid_info_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return None
        bid_info = self.wait_for_valid_output(player.get_bid_info, debug_message="Waiting for {}'s bid_info to be available".format(player_name))
        if bid_info == None:
            return None

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
            print "Error: unable to find {}".format(player_name)
            return False
        player.save_bid(bid)
        return True


    def get_high_bid(self, hand_id):
        high_bid = 0
        player_id = 0
        username = ""
        bids_are_in = self.wait_for_valid_output(self.smear.all_bids_are_in, debug_message="Waiting for all bids to come in")
        if not bids_are_in:
            return None, None
        high_bid, player_id = self.smear.get_bid_and_bidder(hand_id)
        if player_id is not None:
            username = self.smear.get_players()[player_id].name
        return high_bid, username


    def get_trump(self):
        trump = self.wait_for_valid_output(self.smear.get_trump, debug_message="Waiting for trump to be selected")
        return trump


    def submit_trump_for_player(self, player_name, trump):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return False
        if not player.save_trump(trump):
            print "Error: unable to submit trump {}".format(trump)
            return False
        return True


    def get_playing_info_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return None
        playing_info = self.wait_for_valid_output(player.get_playing_info, debug_message="Waiting for {}'s playing_info to be available".format(player_name))
        return playing_info


    def submit_card_to_play_for_player(self, player_name, card_to_play):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return False
        if not player.save_card_to_play(card_to_play):
            print "Error: unable to play {}, likely couldn't find the card in hand".format(str(card_to_play))
            return False
        return True
