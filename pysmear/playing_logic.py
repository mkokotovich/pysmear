# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS
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



# TODO
class CautiousTaker(SmearPlayingLogic):

    def get_A_K_Q_of_trump(self, my_hand, trump):
        ret = None
        indices = utils.get_trump_indices(trump, my_hand)
        if len(indices) is not 0 and my_hand[indices[-1]].value in "Ace King Queen":
            ret = indices[-1]
        return ret


    def get_lowest_trump(self, my_hand, trump):
        ret = None
        indices = utils.get_trump_indices(trump, my_hand)
        if len(indices) is not 0:
            ret = indices[-1]
        return ret


    def get_A_K_Q_J_of_off_suit(self, my_hand, trump):
        ret = None
        tmp_hand = pydealer.Stack(my_hand)
        # Sorts lowest to highest
        tmp_hand.sort(ranks=rank_values)
        # Now highest to lowest
        tmp_hand.reverse()
        for card in tmp_hand:
            if utils.is_trump(card, trump):
                # Skip all trump
                continue
            if card.value in "Ace King Queen Jack":
                # If it is a A, K, Q, or J, then find its index in my_hand
                ret = my_hand.find(card.abbrev)[0]
                break
        return ret


    def get_below_10_of_off_suit(self, my_hand, trump):
        ret = None
        tmp_hand = pydealer.Stack(my_hand)
        # Sorts lowest to highest
        tmp_hand.sort(ranks=rank_values)
        for card in tmp_hand:
            if utils.is_trump(card, trump):
                # Skip all trump
                continue
            elif card.value in "Ace King Queen Jack 10":
                # If it is a A, K, Q, J, or 10, skip it
                continue
            else:
                ret = my_hand.find(card.abbrev)[0]
                break
        return ret


    def get_any_card(self, my_hand):
        # We should only be calling this if we can only play an off-suit 10
        ret = None
        if len(my_hand) > 0:
            ret = 0
        return ret


    def choose_card(self, current_hand, card_counting_info, my_hand):
        idx = 0
        # First player, leading the trick...
        if len(current_hand.current_trick.cards) == 0:
            # Play A, K, Q of trump
            idx = self.get_A_K_Q_of_trump(my_hand, current_hand.trump)
            if idx is None and len(my_hand) == 6:
                # (If bidder and this is first trick, play lowest trump)
                idx = self.get_lowest_trump(my_hand, current_hand.trump)
            # Play A, K, Q, J of other suits
            if idx is None:
                idx = self.get_A_K_Q_J_of_off_suit(my_hand, current_hand.trump)
            # Play low of other suit
            if idx is None:
                idx = self.get_below_10_of_off_suit(my_hand, current_hand.trump)
            # Play lowest trump
            if idx is None:
                idx = self.get_lowest_trump(my_hand, current_hand.trump)
            # Play anything (should be just 10 off suit at this point)
            if idx is None:
                idx = self.get_any_card(my_hand)
        else:
            # Not the first player
            # If I can take a Jack or Jick, take it
            # If I can take a 10, take it
            # If there are high trump still out but I can safely take home my jack or jick, play it
            # If I can take the trick with a non-trump, take it
            # If there is a face card and I have two or more low trump, take it
            # Play a loser
            # Play lowest trump
            idx = self.find_lowest_card_index_to_beat(my_hand, current_hand.current_trick.current_winning_card, current_hand.current_trick.lead_suit, current_hand.trump)
            if idx == None:
                # If we can't beat it, then just play the lowest card, following suit as needed
                idx = self.find_lowest_card_index(my_hand, current_hand.current_trick.lead_suit, current_hand.trump)

        return idx
