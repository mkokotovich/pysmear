# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS
from hand import *
from player import Player


class SmearGameManager:
    def __init__(self, num_players=0, cards_to_deal=6, score_to_play_to=11, debug=False):
        self.num_players = num_players
        self.cards_to_deal = cards_to_deal
        self.players = {}
        self.debug = debug
        self.game_over = False
        self.winning_score = 0
        self.scores = {}
        self.score_to_play_to = score_to_play_to
        self.hand_manager = None
        self.dealer = 0

    def initialize_default_players(self):
        for i in range(0, self.num_players):
            self.players[i] = Player("player{}".format(i), debug=self.debug)

    def reset_players(self):
        for i in range(0, self.num_players):
            self.players[i].reset()

    def add_player(self, player):
        self.players[self.num_players] = player
        self.num_players += 1

    def reset_game(self):
        self.reset_players()
        self.scores = {}
        self.game_over = False
        self.winning_score = 0
        self.dealer = 0

    def start_game(self):
        self.hand_manager = SmearHandManager(self.players, self.cards_to_deal, self.debug)

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

# TODO: Write better logic for winning by two and ties
    def update_scores(self, hand_scores, bidder):
        if self.debug:
            print "Current score:\n{}".format(self.format_scores(self.scores))
            print "Score of last hand:\n{}".format(self.format_scores(hand_scores))
        new_scores = {x: self.scores.get(x, 0) + hand_scores.get(x, 0) for x in set(self.scores).union(hand_scores)}
        self.scores = new_scores
        if self.debug:
            print "New scores:\n{}".format(self.format_scores(self.scores))
        if max(self.scores.values()) >= self.score_to_play_to:
            if self.scores[bidder] >= self.score_to_play_to:
                # Bidder always goes out, regardless of who had the higher score
                self.winning_score = self.scores[bidder]
            else:
                self.winning_score = max(self.scores.values())
            self.game_over = True
            if self.debug:
                print "Game over with a winning score of {}".format(self.winning_score)

    def __str__(self):
        msg = ""
        return msg

    def play_hand(self):
        self.hand_manager.reset_for_next_hand()
        forced_two_set = self.hand_manager.get_bids(self.next_dealer())
        if forced_two_set:
            # Forced set, dealer get_scores() will return appropriately
            if self.debug:
                print "Dealer ({}) was forced to take a two set".format(self.players[self.dealer].name)
        else:
            # Play hand
            self.hand_manager.reveal_trump()
            while not self.hand_manager.is_hand_over():
                self.hand_manager.play_trick()
        # Update scores
        self.update_scores(self.hand_manager.get_scores(self.dealer), self.hand_manager.current_hand.bidder)
