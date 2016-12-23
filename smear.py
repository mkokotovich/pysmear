# Simulator for the card game smear

import pydealer
import sys
from pydealer.const import POKER_RANKS
#from stats import SmearStats

class CardCount:
    def __init__(self):
        self.counts = {
            "Ace": 0,
            "King": 0,
            "Queen": 0,
            "Jack": 0,
            "10": 0,
            "9": 0,
            "8": 0,
            "7": 0,
            "6": 0,
            "5": 0,
            "4": 0,
            "3": 0,
            "2": 0,
        }

    def add_card(self, card):
        self.counts[card.value] += 1

    def remove_card(self, card):
        self.counts[card.value] -= 1

    def get_count(self, card_str):
        return self.counts[card_str]

    def get_total(self):
        return sum(self.counts.values())

    def get_count_dict(self):
        return self.counts


class Player:
    def __init__(self, player_id, initial_cards=None):
        self.reset()
        if initial_cards:
            self.hand += initial_cards
            for card in initial_cards:
                self.card_count.add_card(card)
        self.name = "player{}".format(player_id)
        self.bid = 0
        self.is_bidder = False

    def reset(self):
        self.hand = pydealer.Stack()
        self.pile = pydealer.Stack()
        self.card_count = CardCount()
        self.bid = 0
        self.have_bid = False

    def set_initial_cards(self, initial_cards):
        self.hand = pydealer.Stack()
        self.hand += initial_cards
        for card in initial_cards:
            self.card_count.add_card(card)

    def receive_dealt_card(self, dealt_card):
        self.hand += dealt_card
        self.card_count.add_card(dealt_card[0])

    def get_card_count(self):
        return self.card_count.get_count_dict()

    def number_of_cards(self):
        return self.card_count.get_total()

    def print_cards(self, debug=False):
        msg = "Player {} hand: {}".format(self.name, len(self.hand))
        msg += "\n"
        if debug:
            msg += str(self.hand)
        msg += "Player {} pile: {}".format(self.name, len(self.pile))
        if debug:
            msg += "\n"
            msg += str(self.pile)
        return msg

    # Returns a single card
    # TODO: Will need to be updated with logic
    def play_card(self, current_hand):
        if self.hand.size == 0:
            return None
        
        pool = self.hand.find(current_hand.trump, sort=True, ranks=POKER_RANKS)
        if len(pool) == 0 and len(current_hand.current_trick.cards.values()) != 0:
            # No trump, and someone else lead this trick. We need to follow suit
            pool = self.hand.find(current_hand.current_trick.lead_suit, sort=True, ranks=POKER_RANKS)
        if len(pool) == 0:
            # Can't follow suit, just pick from anything
            self.hand.sort(ranks=POKER_RANKS)
            self.hand.reverse()
            pool=[0]

        card_to_play = self.hand[pool[-1]]
        del self.hand[pool[-1]]
        self.card_count.remove_card(card_to_play)
        return card_to_play

    def has_cards(self):
        return self.hand.size != 0

    def declare_bid(self, other_bids, force_two=False):
        # TODO: this
        self.bid = 2
        return self.bid

    def get_trump(self):
        # TODO: this
        return "Spades"

    def calculate_game_score(self):
        # TODO: this
        return self.pile.size

    def calculate_score(self):
        # TODO: this
        return len(self.pile.find('Ace'))

    def add_cards_to_pile(self, cards):
        self.pile += cards
        for card in cards:
            self.card_count.add_card(card)

    def __str__(self):
        return self.print_cards(False)


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
        if card.suit == self.current_winning_card.suit:
            is_higher = POKER_RANKS["values"][card.value] > POKER_RANKS["values"][self.current_winning_card.value]
            if self.debug:
                print "Suit is same ({}), {} is higher than {}".format(card.suit, str(card) if is_higher else str(self.current_winning_card), str(self.current_winning_card) if is_higher else str(card))
        else:
            is_higher = card.suit == self.trump
            if self.debug:
                if is_higher:
                    print "Suit is different, and {} is trump".format(str(card))
                else:
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
        for i in range(0, self.num_players):
            game_score = self.players[i].calculate_game_score()
            if current_winning_score < game_score:
                current_winning_score = game_score
                current_winner_ids = [ i ]
            elif current_winning_score == game_score:
                current_winner_ids.append(i)
            self.scores[i] = self.players[i].calculate_score()
        # No ties for game, there is just no winner then
        if len(current_winner_ids) == 1:
            self.scores[current_winner_ids[0]] += 1
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

    def get_bids(self, dealer_id):
        self.current_hand.bid = 0
        self.current_hand.bidder = 0
        # Will actually bid last
        current_bidder = dealer_id
        for i in range(0, self.num_players):
            current_bidder = self.next_player_id(current_bidder)
            bid = self.players[current_bidder].declare_bid(self.current_hand.bid, force_two=(current_bidder==dealer_id))
            if self.debug:
                print "{} bid {} and has {}".format(self.players[current_bidder].name, bid, str(self.players[current_bidder].hand))
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
            print "{} won {}".format(self.players[winner_id].name, " ".join(x.abbrev for x in cards))


class SmearGameManager:
    def __init__(self, num_players=2, cards_to_deal=6, score_to_play_to=11, debug=False):
        self.num_players = num_players
        self.cards_to_deal = cards_to_deal
        self.players = {}
        self.initialize_players()
        self.debug = debug
        self.game_over = False
        self.winning_score = 0
        self.scores = {}
        self.score_to_play_to = score_to_play_to
        self.current_hand = SmearHandManager(self.players, self.cards_to_deal, debug)
        self.dealer = 0

    def initialize_players(self):
        for i in range(0, self.num_players):
            self.players[i] = Player(i)

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

# TODO: Write better logic for winning by two and bidder-goes-out
    def update_scores(self, hand_scores):
        if self.debug:
            print "Current score: {}".format(str(self.scores))
            print "Score of last hand: {}".format(str(hand_scores))
        new_scores = {x: self.scores.get(x, 0) + hand_scores.get(x, 0) for x in set(self.scores).union(hand_scores)}
        self.scores = new_scores
        if self.debug:
            print "New scores: {}".format(str(self.scores))
        if max(self.scores.values()) >= self.score_to_play_to:
            self.winning_score = max(self.scores.values())
            self.game_over = True
            if self.debug:
                print "Game over with a winning score of {}".format(self.winning_score)

    def __str__(self):
        msg = ""
        for i in range(0, self.num_players):
            msg += str(self.players[i]) + "\n"
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
        self.smear = SmearGameManager(num_players=2, cards_to_deal=6, debug=debug)
        #self.smear_stats = SmearStats()

    def play_game(self):
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
