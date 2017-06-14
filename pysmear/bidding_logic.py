# Simulator for the card game smear

import pydealer
import math
from pydealer.const import POKER_RANKS
from smear_utils import SmearUtils as utils

class SmearBiddingLogic(object):
    def __init__(self, debug=False):
        self.debug = debug
        self.suits = ["Spades", "Clubs", "Diamonds", "Hearts"]


    def choose(self, n, k):
        """
        A fast way to calculate binomial coefficients by Andrew Dalke (contrib).
        """
        if 0 <= k <= n:
            ntok = 1
            ktok = 1
            for t in xrange(1, min(k, n - k) + 1):
                ntok *= n
                ktok *= t
                n -= 1
            return ntok // ktok
        else:
            return 0


    def calculate_bid(self, current_hand, my_hand, force_two=False):
        pass

    def declare_bid(self):
        pass

    def declare_trump(self):
        pass


# TODO: write more and better versions of these
class BasicBidding(SmearBiddingLogic):
    def __init__(self, debug=False):
        super(BasicBidding, self).__init__(debug)
        self.trump = ""
        self.bid = 0

    def expected_points_from_high(self, num_players, my_hand, suit):
        exp_points = 0
        my_trump = utils.get_trump_indices(suit, my_hand)
        if len(my_trump) == 0:
            return 0
        high_trump = my_hand[my_trump[-1]]
        high_rank = 0
        if high_trump.suit == suit:
            high_rank = POKER_RANKS["values"][high_trump.value]
            if high_rank > 9:
                # Add one to account for jick
                high_rank += 1
        else:
            # jick
            high_rank = 10
        other_possible_highs = 14 - high_rank
        remaining_cards_in_deck = 52 - len(my_hand)
        percent_that_no_one_else_has_high = 1.0
        for i in range(0, num_players-1):
            if (remaining_cards_in_deck - other_possible_highs) < len(my_hand):
                percent_that_no_one_else_has_high = 0
                break
            percent_that_no_one_else_has_high *= self.choose(remaining_cards_in_deck - other_possible_highs, len(my_hand))/float(self.choose(remaining_cards_in_deck, len(my_hand)))
            remaining_cards_in_deck -= len(my_hand)
        exp_points = 1 * percent_that_no_one_else_has_high
        if self.debug:
            print "{} exp points high: {}".format(suit, exp_points)

        return exp_points


    def expected_points_from_low(self, num_players, my_hand, suit):
        exp_points = 0
        my_trump = utils.get_trump_indices(suit, my_hand)
        if len(my_trump) == 0:
            return 0
        low_trump = my_hand[my_trump[0]]
        low_rank = 0
        if low_trump.suit == suit:
            low_rank = POKER_RANKS["values"][low_trump.value]
            if low_rank > 9:
                # Add one to account for jick
                low_rank += 1
        else:
            # jick
            low_rank = 10
        other_possible_lows = low_rank - 1
        remaining_cards_in_deck = 52 - len(my_hand)
        percent_that_no_one_else_has_low = 1.0
        for i in range(0, num_players-1):
            if (remaining_cards_in_deck - other_possible_lows) < len(my_hand):
                percent_that_no_one_else_has_low = 0
                break
            percent_that_no_one_else_has_low *= self.choose(remaining_cards_in_deck - other_possible_lows, len(my_hand))/float(self.choose(remaining_cards_in_deck, len(my_hand)))
            remaining_cards_in_deck -= len(my_hand)
        exp_points = 1 * percent_that_no_one_else_has_low
        if self.debug:
            print "{} exp points low: {}".format(suit, exp_points)

        return exp_points


    # TODO - improve
    def expected_points_from_game(self, num_players, my_hand, suit):
        exp_points = 0
        my_trump = utils.get_trump_indices(suit, my_hand)
        if len(my_trump) == 0:
            return 0
        exp_points = 0.2 * len(my_trump)
        if self.debug:
            print "{} exp points game: {}".format(suit, exp_points)
        return exp_points


    # TODO - improve
    def expected_points_from_jack_and_jick(self, num_players, my_hand, suit):
        exp_points = 0
        jacks_and_jicks = 0
        my_trump = utils.get_trump_indices(suit, my_hand)
        if len(my_trump) == 0:
            return 0
        for idx in my_trump:
            if my_hand[idx].value == "Jack":
                jacks_and_jicks += 1
        exp_points = jacks_and_jicks*0.75
        if self.debug:
            print "{} exp points jack jick: {}".format(suit, exp_points)
        return exp_points

    def calculate_bid(self, current_hand, my_hand, force_two=False):
        bid = 0
        bid_trump = None

        if self.debug:
            print "Hand: {}".format(" ".join(x.abbrev for x in my_hand))
        for suit in self.suits:
            tmp_bid = 0
            tmp_bid += self.expected_points_from_high(current_hand.num_players, my_hand, suit)
            tmp_bid += self.expected_points_from_low(current_hand.num_players, my_hand, suit)
            tmp_bid += self.expected_points_from_game(current_hand.num_players, my_hand, suit)
            tmp_bid += self.expected_points_from_jack_and_jick(current_hand.num_players, my_hand, suit)
            if self.debug:
                print "{} tmp_bid: {}".format(suit, tmp_bid)
            if tmp_bid > bid:
                bid, bid_trump = tmp_bid, suit

        if bid < 2:
            if current_hand.bid < 2 and force_two and bid > 0.3:
                # Go for it, otherwise we get set
                if self.debug:
                    print "Forced to bid two in order to avoid an automatic set"
                bid = 2
            else:
                bid = 0

        self.bid = int(math.floor(bid))

        if self.bid <= current_hand.bid:
            # We have to bid greater than current bid
            self.bid = 0
        self.trump = bid_trump


    def declare_bid(self):
        return self.bid


    def declare_trump(self):
        return self.trump
