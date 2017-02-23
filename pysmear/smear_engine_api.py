# API for playing the card game smear

import sys
from threading import Thread, Event
import Queue
from game_manager import SmearGameManager
from player import *
#from stats import SmearStats

def play_game_as_thread(smear, thread_stop_request):
    while not smear.is_game_over() and not thread_stop_request.isSet():
        print "Playing another hand"
        try:
            smear.play_hand()
        except:
            e = sys.exc_info()[0]
            print "Game encountered a fatal error: {}".format(str(e))
    if thread_stop_request.isSet():
        print "Thread was quit forcefully, game is not finished"
    else:
        print "Game is finished, exiting thread"


class SmearEngineApi:
    def __init__(self, debug=False):
        self.debug = debug
        self.desired_players = 0
        self.desired_human_players = 0
        self.smear = None
        self.thread = None
        self.cleanup_thread = None
        self.timeout_after = 600
        self.game_timeout = 36000
        self.thread_stop_request = Event()
        self.number_of_interactive_players = 0
        self.players_who_are_finished = []


    def create_new_game(self, num_players, num_human_players, cards_to_deal=6, score_to_play_to=11):
        self.smear = SmearGameManager(cards_to_deal=cards_to_deal, score_to_play_to=score_to_play_to, debug=self.debug)
        self.desired_players = num_players
        self.desired_human_players = num_human_players


    def add_player(self, player_id, interactive=False):
        if interactive:
            self.smear.add_player(InteractivePlayer(player_id, debug=self.debug, stop_request=self.thread_stop_request))
            self.number_of_interactive_players += 1
        else:
            self.smear.add_player(Player(player_id, debug=self.debug))


    def all_players_added(self):
        return self.desired_players == len(self.smear.get_players())


    def all_human_players_joined(self):
        return self.desired_human_players == self.number_of_interactive_players


    def get_desired_number_of_players(self):
        return self.desired_players


    def get_desired_number_of_human_players(self):
        return self.desired_human_players


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

        # Start a thread to play the game in the background
        self.thread = Thread(target=play_game_as_thread, args = ( self.smear, self.thread_stop_request,  ))
        self.thread.daemon = True
        self.thread.start()


    def player_is_finished(self, player_name):
        ready_to_delete = False
        if player_name not in self.players_who_are_finished:
            self.players_who_are_finished.append(player_name)
        if len(self.players_who_are_finished) == self.number_of_interactive_players:
            ready_to_delete = True
        return ready_to_delete


    def finish_game(self):
        if self.debug:
            print "Finishing game"
        self.thread_stop_request.set()
        self.thread.join()

    
    def get_hand_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return None
        cards = player.get_hand()
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
        bid_info = player.get_bid_info()
        if bid_info == None:
            return None

        # populate the username since we have that info here
        player_id = bid_info["bidder"]
        if type(0) == type(player_id):
            player_name = self.smear.get_players()[player_id].name
            bid_info["bidder"] = player_name
            for i in range(0, len(bid_info["all_bids"])):
                player_id = bid_info["all_bids"][i]["username"]
                if type(0) == type(player_id):
                    player_name = self.smear.get_players()[player_id].name
                    bid_info["all_bids"][i]["username"] = player_name
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
        player_id = 0
        bids_are_in = self.smear.all_bids_are_in(hand_id)
        if not bids_are_in:
            return None

        high_bid_info = self.smear.get_high_bid_info(hand_id)
        high_bid_info['force_two'] = False

        # populate the usernames since we have that info here
        player_id = high_bid_info["bidder"]
        if type(0) == type(player_id):
            high_bid_info['bidder'] = self.smear.get_players()[player_id].name

        for i in range(0, len(high_bid_info["all_bids"])):
            player_id = high_bid_info["all_bids"][i]["username"]
            if type(0) == type(player_id):
                player_name = self.smear.get_players()[player_id].name
                high_bid_info["all_bids"][i]["username"] = player_name

        return high_bid_info


    def get_trump(self):
        trump = self.smear.get_trump()
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
        playing_info = player.get_playing_info()
        if playing_info == None:
            return playing_info

        # populate the usernames since we have that info here
        for i in range(0, len(playing_info["cards_played"])):
            player_id = playing_info["cards_played"][i]["username"]
            if type(0) == type(player_id):
                player_name = self.smear.get_players()[player_id].name
                playing_info["cards_played"][i]["username"] = player_name

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


    def get_trick_results_for_player(self, player_name):
        player = None
        for player_itr in self.smear.get_players():
            if player_itr.name == player_name:
                player = player_itr
        if player == None:
            print "Error: unable to find {}".format(player_name)
            return None
        trick_results = player.get_results_of_trick()
        if trick_results == None:
            return None

        # populate the usernames since we have that info here
        player_id = trick_results["winner"]
        if type(0) == type(player_id):
            player_name = self.smear.get_players()[player_id].name
            trick_results["winner"] = player_name
            for i in range(0, len(trick_results["cards_played"])):
                player_id = trick_results["cards_played"][i]["username"]
                if type(0) == type(player_id):
                    player_name = self.smear.get_players()[player_id].name
                    trick_results["cards_played"][i]["username"] = player_name

        return trick_results


    def get_hand_results(self, hand_id):
        args = ( hand_id, )
        hand_results = self.smear.get_hand_results(hand_id)
        if hand_results == None:
            return hand_results

        # populate the usernames since we have that info here
        for key, value in hand_results.items():
            if "winner" in key:
                player_id = value
                if type(0) == type(player_id):
                    player_name = self.smear.get_players()[player_id].name
                    hand_results[key] = player_name
            elif "player_infos" == key:
                for pinfo in value:
                    player_id = pinfo["username"]
                    if type(0) == type(player_id):
                        player_name = self.smear.get_players()[player_id].name
                        pinfo["username"] = player_name
            
        return hand_results


