# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS
from smear_utils import SmearUtils as utils
#from stats import SmearStats


class Trick:
    def __init__(self, trump, debug=False):
        # This list is in order of cards played
        self.cards = []
        self.trump = trump 
        self.lead_suit = ""
        self.current_winner_id = 0
        self.current_winning_card = None
        self.debug = debug

    def is_new_card_higher(self, card):
        is_higher = False
        if utils.is_trump(self.current_winning_card, self.trump) or utils.is_trump(card, self.trump):
            # At least one of the cards is trump, compare to new card
            is_higher = not utils.is_less_than(card, self.current_winning_card, self.trump)
            if self.debug:
                print "At least one card is trump, {} is higher than {}".format(str(card) if is_higher else str(self.current_winning_card), str(self.current_winning_card) if is_higher else str(card))
        elif card.suit == self.current_winning_card.suit:
            # Both are not trump, but are the same suit
            is_higher = POKER_RANKS["values"][card.value] > POKER_RANKS["values"][self.current_winning_card.value]
            if self.debug:
                print "Suit is same ({}), {} is higher than {}".format(card.suit, str(card) if is_higher else str(self.current_winning_card), str(self.current_winning_card) if is_higher else str(card))
        else:
            # card is a different suit, and not trump, so is not higher
            is_higher = False
            if self.debug:
                print "Suit is different, {} was unable to follow suit".format(str(card))

        return is_higher

    def add_card(self, player_id, card):
        if len(self.cards) == 0:
            # This is the first card
            self.lead_suit = card.suit
            self.current_winning_card = card
            self.current_winner_id = player_id
        elif self.is_new_card_higher(card):
            self.current_winning_card = card
            self.current_winner_id = player_id
        self.cards.append(card)

    def get_winner_id(self):
        return self.current_winner_id

    def get_all_cards_as_stack(self):
        stack = pydealer.Stack()
        for x in self.cards:
            stack += [x]
        return stack
