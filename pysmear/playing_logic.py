# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS
from pydealer.tools import sort_cards
from smear_utils import SmearUtils as utils
from card_counting import CardCounting

rank_values = POKER_RANKS

class SmearPlayingLogic:
    def __init__(self, debug=False):
        self.debug = debug

    def choose_card(self, current_hand, card_counting_info, my_hand):
        pass

# TODO: write more and better versions of these
class JustGreedyEnough(SmearPlayingLogic):
    def find_lowest_card_index_to_beat(self, my_hand, card_to_beat, lead_suit, trump):
        lowest_index = None
        if utils.is_trump(card_to_beat, trump):
            # Card to beat is trump, see if I have a higher trump
            my_trump = utils.get_trump_indices(trump, my_hand)
            for idx in my_trump:
                if utils.is_less_than(card_to_beat, my_hand[idx], trump):
                    lowest_index = idx
        elif card_to_beat.suit == lead_suit:
            my_trump = utils.get_trump_indices(trump, my_hand)
            if len(my_trump) != 0:
                # Card to beat isn't trump, but I have trump. Play my lowest trump
                lowest_index = my_trump[0]
            else:
                matching_idxs = my_hand.find(card_to_beat.suit, sort=True, ranks=rank_values)
                for idx in matching_idxs:
                    # Play the lowest card in the matching suit that will beat the card to beat
                    if my_hand[idx].gt(card_to_beat, ranks=rank_values):
                        lowest_index = idx
        else:
            # Card to beat isn't trump and isn't the lead suit, this doesn't make sense
            print "Error: card to beat seems incorrect: {}".format(card_to_beat)
        return lowest_index
        
    def find_strongest_card(self, my_hand, trump):
        my_trump = utils.get_trump_indices(trump, my_hand)
        strongest_idx = None
        if len(my_trump) != 0:
            strongest_idx = my_trump[-1]
        else:
            my_hand.sort(ranks=rank_values)
            strongest_idx = len(my_hand) - 1
        return strongest_idx

    def find_lowest_card_index(self, my_hand, lead_suit, trump):
        lowest_index = None
        lowest_trump_index = None
        # First try following suit.
        my_hand.sort(ranks=rank_values)
        indices = []
        if lead_suit == "Trump":
            indices = utils.get_trump_indices(trump, my_hand)
            indices.reverse()
        else:
            indices = my_hand.find(lead_suit, sort=True, ranks=rank_values)
        if len(indices) == 0:
            indices = range(0, len(my_hand))
        for idx in indices:
            if utils.is_trump(my_hand[idx], trump) and lowest_trump_index == None:
                lowest_trump_index = idx
            else:
                lowest_index = idx
                break
        if lowest_index == None:
            lowest_index = lowest_trump_index
        return lowest_index

    def choose_card(self, current_hand, card_counting_info, my_hand):
        idx = 0
        if len(current_hand.current_trick.cards) == 0:
            # I'm the first player. Choose my strongest card
            idx = self.find_strongest_card(my_hand, current_hand.trump)
        else:
            # Otherwise choose the lowest card to beat the current highest card
            idx = self.find_lowest_card_index_to_beat(my_hand, current_hand.current_trick.current_winning_card, current_hand.current_trick.lead_suit, current_hand.trump)
            if idx == None:
                # If we can't beat it, then just play the lowest card, following suit as needed
                idx = self.find_lowest_card_index(my_hand, current_hand.current_trick.lead_suit, current_hand.trump)

        return idx
