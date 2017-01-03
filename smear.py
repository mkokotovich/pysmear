# Simulator for the card game smear

import pydealer
import sys
from pydealer.const import POKER_RANKS
from bidding_logic import *
from playing_logic import *
from player import Player
from trick import Trick
from hand import *

from smear_utils import SmearUtils as utils
#from stats import SmearStats



class SmearGameManager:
    def __init__(self, num_players=2, cards_to_deal=6, score_to_play_to=11, debug=False):
        self.num_players = num_players
        self.cards_to_deal = cards_to_deal
        self.players = {}
        self.debug = debug
        self.initialize_players()
        self.game_over = False
        self.winning_score = 0
        self.scores = {}
        self.score_to_play_to = score_to_play_to
        self.current_hand = SmearHandManager(self.players, self.cards_to_deal, debug)
        self.dealer = 0

    def initialize_players(self):
        for i in range(0, self.num_players):
            self.players[i] = Player(i, debug=self.debug)

    def reset_game(self):
        self.initialize_players()
        self.scores = {}
        self.game_over = False
        self.winning_score = 0
        self.current_hand = SmearHandManager(self.players, self.cards_to_deal, self.debug)
        self.dealer = 0

    def is_game_over(self):
        return self.game_over

    def next_dealer(self):
        self.dealer = self.dealer + 1
        if self.dealer == self.num_players:
            self.dealer = 0
        return self.dealer

    def get_winners(self):
        winners = []
        for i in range(0, self.num_players):
            if self.scores[i] == self.winning_score:
                winners.append(self.players[i].name)
        return winners

    def get_players(self):
        return self.players.values()

    def post_game_summary(self):
        msg = ""
        winners = self.get_winners()
        for winner in winners:
            msg += "{} won".format(winner)
            msg += '\n'
        for i in range(0, self.num_players):
            msg += "{} finished with {} points".format(self.players[i].name, self.scores[i])
            msg += '\n'
        return msg
    
    def format_scores(self, scores):
        msg = ""
        for i in range(0, self.num_players):
            msg += "{}: {}".format(self.players[i].name, scores[i] if len(scores) != 0 else 0)
            if i < self.num_players - 1:
                msg += "\n"
        return msg

# TODO: Write better logic for winning by two and bidder-goes-out
    def update_scores(self, hand_scores):
        if self.debug:
            print "Current score:\n{}".format(self.format_scores(self.scores))
            print "Score of last hand:\n{}".format(self.format_scores(hand_scores))
        new_scores = {x: self.scores.get(x, 0) + hand_scores.get(x, 0) for x in set(self.scores).union(hand_scores)}
        self.scores = new_scores
        if self.debug:
            print "New scores:\n{}".format(self.format_scores(self.scores))
        if max(self.scores.values()) >= self.score_to_play_to:
            self.winning_score = max(self.scores.values())
            self.game_over = True
            if self.debug:
                print "Game over with a winning score of {}".format(self.winning_score)

    def __str__(self):
        msg = ""
        return msg

    def play_hand(self):
        self.current_hand.reset_for_next_hand()
        self.current_hand.get_bids(self.next_dealer())
        self.current_hand.reveal_trump()
        while not self.current_hand.is_hand_over():
            self.current_hand.play_trick()
        self.update_scores(self.current_hand.get_scores())


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
