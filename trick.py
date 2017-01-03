# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS
from smear_utils import SmearUtils as utils
#from stats import SmearStats


class Trick:
    def __init__(self, trump, debug=False):
        self.cards = {}
        self.trump = trump 
        self.lead_suit = ""
        self.current_winner_id = 0
        self.current_winning_card = None
        self.debug = debug

    def is_new_card_higher(self, card):
        is_higher = False
        if utils.is_trump(self.current_winning_card, self.trump):
            # Current winning card is trump
            if utils.is_trump(card, self.trump):
                # New card is also trump
                if card.suit == self.current_winning_card.suit:
                    # Neither are Jicks, just compare
                    is_higher = POKER_RANKS["values"][card.value] > POKER_RANKS["values"][self.current_winning_card.value]
                    if self.debug:
                        print "Both cards are trump, {} is higher than {}".format(str(card) if is_higher else str(self.current_winning_card), str(self.current_winning_card) if is_higher else str(card))
                else:
                    # One of the cards is the jick
                    if card.suit != self.trump:
                        # The card is a jick, if the current_winning_card is a Jack or higher it wins
                        is_higher = not POKER_RANKS["values"][self.current_winning_card.value] > POKER_RANKS["values"]["10"]
                        if self.debug:
                            print "{} is jick and {} higher than {}".format(str(card), "is" if is_higher else "is not", str(self.current_winning_card))
                    else:
                        # The current_winning_card is a jick
                        is_higher = POKER_RANKS["values"][card.value] > POKER_RANKS["values"]["10"]
                        if self.debug:
                            print "Both cards are trump (current_winning is jick), {} is higher than {}".format(str(card) if is_higher else str(self.current_winning_card), str(self.current_winning_card) if is_higher else str(card))
            else:
                # New card is not trump, but current is
                if self.debug:
                    print "{} is not trump, and current winning card {} is".format(str(card), str(self.current_winning_card))
                is_higher = False
        elif utils.is_trump(card, self.trump):
            if self.debug:
                print "{} is trump, and current winning card {} is not".format(str(card), str(self.current_winning_card))
            is_higher = True
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
        if len(self.cards.values()) == 0:
            # This is the first card
            self.lead_suit = card.suit
            self.current_winning_card = card
            self.current_winner_id = player_id
        elif self.is_new_card_higher(card):
            self.current_winning_card = card
            self.current_winner_id = player_id
        self.cards[player_id] = card

    def get_winner_id(self):
        return self.current_winner_id

    def get_all_cards_as_stack(self):
        stack = pydealer.Stack()
        for x in self.cards.values():
            stack += [x]
        return stack
