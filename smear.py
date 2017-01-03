# Simulator for the card game smear

import pydealer
import sys
from pydealer.const import POKER_RANKS
from bidding_logic import *
from playing_logic import *
from player import Player
from trick import Trick
from smear_utils import SmearUtils as utils
#from stats import SmearStats



# Everything regarding the state of a hand, so a player can look at this and chose a card to play
class SmearHand:
    def __init__(self, num_players, debug=False):
        self.num_players = num_players
        self.trump = ""
        self.bid = 0
        self.bidder = 0
        self.first_player = 0
        self.debug = debug
        self.current_trick = Trick(self.trump, debug)

    def set_trump(self, trump):
        self.trump = trump
        self.current_trick.trump = trump

    def add_card(self, player_id, card):
        if card is not None:
            self.current_trick.add_card(player_id, card)

    def prepare_for_next_trick(self):
        self.current_trick = Trick(self.trump, self.debug)


# A hand is one deal, play until all cards are out, and tally the score iteration
class SmearHandManager:
    def __init__(self, players_dict, cards_to_deal=6, debug=False):
        self.players = players_dict
        self.num_players = len(players_dict.values())
        self.cards_to_deal = cards_to_deal
        self.deck = pydealer.Deck(ranks=POKER_RANKS)
        if self.num_players * cards_to_deal > self.deck.size:
            raise ValueError("num_players ({}) times cards_to_deal ({}) is larger than the size of the deck ({})".format(self.num_players, cards_to_deal, deck.size))
        self.reset_players()
        self.current_hand = SmearHand(self.num_players, debug)
        self.scores = {}
        self.debug = debug

    def reset_players(self):
        for i in range(0, self.num_players):
            self.players[i].reset()

    def deal_new_deck(self):
        self.deck = pydealer.Deck(ranks=POKER_RANKS)
        self.deck.shuffle()
        for j in range(0, self.cards_to_deal):
            for i in range(0, self.num_players):
                self.players[i].receive_dealt_card(self.deck.deal(1))

    def reset_for_next_hand(self):
        self.reset_players()
        self.deal_new_deck()
        self.current_hand = SmearHand(self.num_players, self.debug)
        self.scores = {}

    def is_hand_over(self):
        return not self.players[0].has_cards()

    def get_scores(self):
        if not self.is_hand_over():
            print "Hand isn't over yet"
            return None
        self.scores = {}
        current_winner_ids = []
        current_winning_score = 0
        current_high_id = 0
        current_high = None
        current_low_id = 0
        current_low = None
        for i in range(0, self.num_players):
            game_score = self.players[i].calculate_game_score()
            if current_winning_score < game_score:
                current_winning_score = game_score
                current_winner_ids = [ i ]
            elif current_winning_score == game_score:
                current_winner_ids.append(i)
            high = self.players[i].get_high_trump_card(self.current_hand.trump)
            if (not high == None) and (current_high == None or current_high.lt(high.value, ranks=POKER_RANKS)):
                current_high = high
                current_high_id = i
            low = self.players[i].get_low_trump_card(self.current_hand.trump)
            if (not low == None) and (current_low == None or current_low.gt(low.value, ranks=POKER_RANKS)):
                current_low = low
                current_low_id = i
            self.scores[i] = self.players[i].get_jacks_and_jicks_count(self.current_hand.trump)
        # No ties for game, there is just no winner then
        if len(current_winner_ids) == 1:
            self.scores[current_winner_ids[0]] += 1
            if self.debug:
                print "{} won game with {} points".format(self.players[current_winner_ids[0]].name, current_winning_score)
        elif self.debug:
            print "No one won game, there was a tie at {} points between {}".format(current_winning_score, ", ".join(self.players[x].name for x in current_winner_ids))
        self.scores[current_high_id] += 1
        if self.debug:
            print "{} won high with a {}".format(self.players[current_high_id].name, current_high)
        self.scores[current_low_id] += 1
        if self.debug:
            print "{} won low with a {}".format(self.players[current_low_id].name, current_low)
        # Check to see if bidder was set
        if self.scores[self.current_hand.bidder] < self.current_hand.bid:
            if self.debug:
                print "{} bid {} and only got {}: is set!".format(self.players[self.current_hand.bidder].name, self.current_hand.bid, self.scores[self.current_hand.bidder])
            self.scores[self.current_hand.bidder] = -self.current_hand.bid

        return self.scores

    def get_players(self):
        return self.players.values()

    def post_hand_summary(self):
        msg = ""
        for i in range(0, self.num_players):
            msg +=  "{} received {} points\n".format(self.players[i].name, self.scores[i])
        return msg

    def __str__(self):
        msg = ""
        for i in range(0, self.num_players):
            msg += str(self.players[i]) + "\n"
        return msg

    def next_player_id(self, current_id):
        next_id = current_id + 1
        if next_id == self.num_players:
            next_id = 0
        return next_id

    # TODO: handle forced two set
    def get_bids(self, dealer_id):
        self.current_hand.bid = 0
        self.current_hand.bidder = 0
        # Will actually bid last
        current_bidder = dealer_id
        for i in range(0, self.num_players):
            current_bidder = self.next_player_id(current_bidder)
            bid = self.players[current_bidder].declare_bid(self.current_hand, force_two=(current_bidder==dealer_id))
            if self.debug:
                print "{} bid {} and has {}".format(self.players[current_bidder].name, bid, " ".join(x.abbrev for x in self.players[current_bidder].hand))
            if bid > self.current_hand.bid:
                self.current_hand.bid = bid
                self.current_hand.bidder = current_bidder
        self.current_hand.first_player = self.current_hand.bidder
        if self.debug:
            print "{} has the highest bid of {}".format(self.players[self.current_hand.bidder].name, self.current_hand.bid)

    def reveal_trump(self):
        self.current_hand.set_trump(self.players[self.current_hand.bidder].get_trump())
        if self.debug:
            print "{} picks {} to be trump".format(self.players[self.current_hand.bidder].name, self.current_hand.trump)

    def play_trick(self):
        current_player = self.current_hand.first_player
        for i in range(0, self.num_players):
            card = self.players[current_player].play_card(self.current_hand)
            if self.debug:
                print "{}: {}".format(self.players[current_player].name, str(card))
            self.current_hand.add_card(current_player, card)
            current_player = self.next_player_id(current_player)
        # Give all cards to winner
        cards = self.current_hand.current_trick.get_all_cards_as_stack()
        winner_id = self.current_hand.current_trick.get_winner_id()
        self.players[winner_id].add_cards_to_pile(cards)
        self.current_hand.prepare_for_next_trick()
        self.current_hand.first_player = winner_id
        if self.debug:
            print "{} won {}\n".format(self.players[winner_id].name, " ".join(x.abbrev for x in cards))


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
