# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS

jack_hearts = pydealer.Card(value="Jack", suit="Hearts")
jack_spades = pydealer.Card(value="Jack", suit="Spades")
jack_diamonds = pydealer.Card(value="Jack", suit="Diamonds")
jack_clubs = pydealer.Card(value="Jack", suit="Clubs")

class SmearUtils():
    # Returns the value of card_lhs < card_rhs, following the rules of trump
    @staticmethod
    def is_less_than(card_lhs, card_rhs, trump):
        less_than = False
        if SmearUtils.is_trump(card_lhs, trump) and not SmearUtils.is_trump(card_rhs, trump):
            # lhs is trump and rhs isn't, return false
            less_than = False
        elif not SmearUtils.is_trump(card_lhs, trump) and SmearUtils.is_trump(card_rhs, trump):
            # lhs is not trump and rhs is, return true
            less_than = True
        elif SmearUtils.is_trump(card_lhs, trump):
            # Both are trump
            if card_lhs.suit == card_rhs.suit:
                # Neither are Jicks, just compare
                less_than = POKER_RANKS["values"][card_lhs.value] < POKER_RANKS["values"][card_rhs.value]
            else:
                # One of the cards is the jick
                if card_lhs.suit != self.trump:
                    # card_lhs is a jick, lhs is less than rhs if rhs is greater than or equal to a jack
                    less_than = POKER_RANKS["values"][card_rhs.value] >= POKER_RANKS["values"]["Jack"]
                else:
                    # card_rhs is a jick, lhs is less than rhs if lhs is less than or equal to a 10
                    less_than = POKER_RANKS["values"][card_lhs.value] <= POKER_RANKS["values"]["10"]
        else:
            # Neither are trump, just compare values (although this isn't how tricks are taken)
            print "Warning, comparing cards with different suits"
            less_than = POKER_RANKS["values"][card_lhs.value] < POKER_RANKS["values"][card_rhs.value]


    @staticmethod
    def is_trump(card, trump):
        card_is_trump = False
        if card.suit == trump:
            return True
        elif trump == "Spades":
            return jack_clubs == card
        elif trump == "Clubs":
            return jack_spades == card
        elif trump == "Hearts":
            return jack_diamonds == card
        elif trump == "Diamonds":
            return jack_hearts == card
        return card_is_trump


    @staticmethod
    def insert_card_into_sorted_index_list(indices, stack, card_index):
        # Assumes sorted from smallest to largest
        for i in range(0, len(indices)):
            # Loop through indices, comparing card in stack at that index to
            # card in stack at card_index
            if stack[indices[i]].lt(stack[card_index], ranks=POKER_RANKS):
                # New card is larger, keep going
                continue
            else:
                # New card is smaller, insert here
                indices.insert(i, card_index)
                break


    # Sorted from smallest to largest
    @staticmethod
    def get_trump_indices(trump, stack):
        trump_indices = stack.find(trump, sort=True, ranks=POKER_RANKS)
        jick = None
        if trump == "Spades":
            jick = jack_clubs
        elif trump == "Clubs":
            jick = jack_spades
        elif trump == "Hearts":
            jick = jack_diamonds
        elif trump == "Diamonds":
            jick = jack_hearts
        if jick in stack:
            insert_card_into_sorted_index_list(trump_indices, stack, stack.find(jick))
        return trump_indices
