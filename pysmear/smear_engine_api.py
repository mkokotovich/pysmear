# API for playing the card game smear

import sys
from game_manager import SmearGameManager
from player import *
#from stats import SmearStats


class SmearEngineApi:
    def __init__(self, debug=False):
        self.debug = debug
        self.desired_players = 0
        self.smear = None
        #self.smear_stats = SmearStats()

    def create_new_game(self, num_players, cards_to_deal=6):
        self.smear = SmearGameManager(cards_to_deal, debug=self.debug)
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
        self.smear.reset_game()
        self.smear.start_game()


    def play_hand(self):
        while not self.smear.is_game_over():
            self.smear.play_hand()
            #for player in self.smear.get_players():
                #self.smear_stats.add_game_status(self.smear.number_of_hands, player.name, player.get_card_count(), player.number_of_cards())
            if self.debug:
                print self.smear
        if self.debug:
            print self.smear.post_game_summary()
        #self.smear_stats.finalize_game(self.smear.number_of_hands, self.smear.get_winner())

    def run(self, num_games=1):
        sys.stdout.write("Running simulation")
        for n in range(0, num_games):
            sys.stdout.write(".")
            sys.stdout.flush()
            self.play_game()
        sys.stdout.write("\n")

    #def stats(self):
        #return self.smear_stats.summarize()
