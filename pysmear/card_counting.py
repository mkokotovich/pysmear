# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS
from smear_utils import SmearUtils as utils

import operator


# A class that counts cards and can be used to aid playing logic
class CardCounting:
    def __init__(self, num_players, debug=False):
        self.num_players = num_players
        self.debug = debug
        self.suits = [ "Trump", "Spades", "Clubs", "Hearts", "Diamonds" ]

        # Tracks which cards have been played, a dict of lists
        self.cards_played = {}

        # Tracks which players are known to be out of a suit, a dict of dicts
        self.player_out_of_cards = {}

        self.reset_for_next_hand()


    def reset_for_next_hand(self):
        for suit in self.suits:
            self.cards_played[suit] = []

        for i in range(0, self.num_players):
            self.player_out_of_cards[i] = {}
            for suit in self.suits:
                self.player_out_of_cards[i][suit] = False


    def card_was_played(self, player_id, card, current_trick):
        # Update the list of cards played
        if utils.is_trump(card, current_trick.trump):
            self.cards_played["Trump"].append(card)
            if len(self.cards_played["Trump"]) == 14:
                # If all trump has been played, everyone is out
                for i in range(0, self.num_players):
                    self.player_out_of_cards[i]["Trump"] == True
        else:
            self.cards_played[card.suit].append(card)
            if len(self.cards_played[card.suit]) == 13 if not self.jick_suit_for(current_trick.trump) == card.suit else 12:
                # If all cards of this suit have been played (only 12 cards for the jick suit), everyone is out
                for i in range(0, self.num_players):
                    self.player_out_of_cards[i][card.suit] == True

        # Update if the player is out of the suit
        if current_trick.lead_suit == "Trump":
            if not utils.is_trump(card, current_trick.trump):
                self.player_out_of_cards[player_id]["Trump"] = True
        else:
            if not utils.is_trump(card, current_trick.trump) and card.suit is not current_trick.lead_suit:
                # If player is trumping in, can't tell if he/she is out of lead_suit
                # So if it isn't trump, and isn't the lead_suit, must be out of lead_suit
                self.player_out_of_cards[player_id][card.suit] = True

    
    def jick_suit_for(self, suit):
        if suit == "Spades":
            return "Clubs"
        elif suit == "Clubs":
            return "Spades"
        elif suit == "Hearts":
            return "Diamonds"
        elif suit == "Diamonds":
            return "Hearts"
        else:
            return "Unknown"
        

    def highest_card_still_out(self, suit, is_trump):
        card = pydealer.Card("Ace", suit)
        lookup_suit = suit
        if is_trump:
            lookup_suit = "Trump"
        for entry in sorted(POKER_RANKS["values"].items(), key=operator.itemgetter(1), reverse=True):
            value = entry[0]
            if value == "Joker":
                # We don't play with Jokers for now
                continue
            if value == "10":
                # Last card was jack, force this card to be Jick, and still run the loop for 10
                card.value = "Jack"
                card.suit = self.jick_suit_for(suit)
                if card not in self.cards_played[lookup_suit]:
                    return card
                card.suit = suit
            card.value = value
            if card not in self.cards_played[lookup_suit]:
                return card
        return None


    # Returns true if it is known that no one else (besides teammates) in the trick can take this card
    def safe_to_play(self, player_id, card, current_trick, teams):
        # How many players still need to play in the trick, -1 to account for self
        remaining_num_players = self.num_players - len(current_trick.cards) - 1
        highest_of_suit = False

        # First check to see if it is the highest remaining card
        if utils.is_trump(card, current_trick.trump):
            if card == self.highest_card_still_out(current_trick.trump, True):
                # If this is highest remaining Trump, it is definitely safe
                return True
        else:
            if card == self.highest_card_still_out(card.suit, False):
                highest_of_suit = True

        # For each remaining player:
        for i in range(0, remaining_num_players):
            next_player = (player_id + 1) % self.num_players
            if utils.is_on_same_team(player_id, next_player, teams):
                # This is a teammate
                continue
            elif utils.is_trump(card, current_trick.trump):
                # If we don't have the highest remaining trump, then we need everyone after
                # us to be out of trump
                if self.player_out_of_cards[next_player]["Trump"]:
                    continue
            elif highest_of_suit:
                # If we have the highest left of that suit, then we need everyone after 
                # us to be out of trump
                if self.player_out_of_cards[next_player]["Trump"]:
                    continue
            else:
                # If we don't have the highest of the suit and we don't have trump, we need
                # everyone after us to be out of trump and that suit
                if self.player_out_of_cards[next_player]["Trump"] and self.player_out_of_cards[next_player][card.suit]:
                    continue
            # If we made it through the if/else's, that means this player could have cards that can take ours
            return False

        # If we have made it this far, and it beats the current_winning_card
        # (or the current_winning_card belongs to a teammate) then it is safe
        if utils.is_on_same_team(player_id, current_trick.current_winning_id, teams):
            return True
        return utils.is_new_card_higher(current_trick.current_winning_card, card, current_trick.trump)


    def jack_or_jick_still_out(self):
        jboys = 0
        for card in self.cards_played["Trump"]:
            if card.value == "Jack":
                jboys += 1
        return jboys < 2

