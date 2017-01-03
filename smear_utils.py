# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS

jack_hearts = pydealer.Card(value="Jack", suit="Hearts")
jack_spades = pydealer.Card(value="Jack", suit="Spades")
jack_diamonds = pydealer.Card(value="Jack", suit="Diamonds")
jack_clubs = pydealer.Card(value="Jack", suit="Clubs")

class SmearUtils():
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
