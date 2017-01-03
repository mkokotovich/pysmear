# Simulator for the card game smear

import pydealer
import sys
from pydealer.const import POKER_RANKS
from bidding_logic import *
from playing_logic import *
from player import Player
from trick import Trick
from hand import *
from game_manager import SmearGameManager

from smear_utils import SmearUtils as utils
#from stats import SmearStats


class SmearSimulator:
    def __init__(self, debug=False):
        self.debug = debug
        self.smear = SmearGameManager(num_players=3, cards_to_deal=6, debug=debug)
        #self.smear_stats = SmearStats()

    def play_game(self):
        if self.debug:
            print "\n\n Starting game \n"
        self.smear.reset_game()
        #self.smear_stats.add_new_game()
        #for player in self.smear.get_players():
            #self.smear_stats.add_game_status(self.smear.number_of_hands, player.name, player.get_card_count(), player.number_of_cards())
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

def main():
    num_runs = 1
    print "Setting up..."
    sim = SmearSimulator(debug=True)
    if len(sys.argv) > 1:
        num_runs = int(sys.argv[1])
    sim.run(num_runs)
    print "Generating stats..."
    #print sim.stats()

if __name__ == "__main__":
    main()
