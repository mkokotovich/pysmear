# Simulator for the card game smear

import pydealer
import sys
import math
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


class SmearUtils():
    def __init__(self):
        self.jack_hearts = pydealer.Card(value="Jack", suit="Hearts")
        self.jack_spades = pydealer.Card(value="Jack", suit="Spades")
        self.jack_diamonds = pydealer.Card(value="Jack", suit="Diamonds")
        self.jack_clubs = pydealer.Card(value="Jack", suit="Clubs")

    def is_trump(self, card, trump):
        card_is_trump = False
        if card.suit == trump:
            return True
        elif trump == "Spades":
            return self.jack_clubs == card
        elif trump == "Clubs":
            return self.jack_spades == card
        elif trump == "Hearts":
            return self.jack_diamonds == card
        elif trump == "Diamonds":
            return self.jack_hearts == card
        return card_is_trump

    def insert_card_into_sorted_index_list(self, indices, stack, card_index):
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
    def get_trump_indices(self, trump, stack):
        trump_indices = stack.find(trump, sort=True, ranks=POKER_RANKS)
        jick = None
        if trump == "Spades":
            jick = self.jack_clubs
        elif trump == "Clubs":
            jick = self.jack_spades
        elif trump == "Hearts":
            jick = self.jack_diamonds
        elif trump == "Diamonds":
            jick = self.jack_hearts
        if jick in stack:
            insert_card_into_sorted_index_list(trump_indices, stack, stack.find(jick))
        return trump_indices


utils = SmearUtils()
        
class SmearBiddingLogic:
    def __init__(self, debug=False):
        self.debug = debug
        self.suits = ["Spades", "Clubs", "Diamonds", "Hearts"]


    def declare_bid(self, current_hand, my_hand, force_two=False):
        pass


# TODO: write more and better versions of these
class BasicBidding(SmearBiddingLogic):
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
        cards_in_play = (num_players-1)*len(my_hand)
        percent_someone_else_has_high = other_possible_highs/float(cards_in_play)
        exp_points = 1 * (1 - percent_someone_else_has_high)

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
        cards_in_play = (num_players-1)*len(my_hand)
        percent_someone_else_has_low = other_possible_lows/float(cards_in_play)
        exp_points = 1 * (1 - percent_someone_else_has_low)

        return exp_points


    # TODO - improve
    def expected_points_from_game(self, num_players, my_hand, suit):
        exp_points = 0
        my_trump = utils.get_trump_indices(suit, my_hand)
        if len(my_trump) == 0:
            return 0
        exp_points = 0.2 * len(my_trump)
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
        exp_points = jacks_and_jicks
        return exp_points

    def declare_bid(self, current_hand, my_hand, force_two=False):
        bid = 0
        bid_trump = None

        for suit in self.suits:
            tmp_bid = 0
            tmp_bid += self.expected_points_from_high(current_hand.num_players, my_hand, suit)
            tmp_bid += self.expected_points_from_low(current_hand.num_players, my_hand, suit)
            tmp_bid += self.expected_points_from_game(current_hand.num_players, my_hand, suit)
            tmp_bid += self.expected_points_from_jack_and_jick(current_hand.num_players, my_hand, suit)
            if tmp_bid > bid:
                bid, bid_trump = tmp_bid, suit

        if force_two:
            if bid < 2 and bid > 1:
                # Go for it
                bid = 2
            else:
                # Too low, take the set:
                bid = 0

        return math.floor(bid), bid_trump

class SmearPlayingLogic:
    def __init__(self, debug=False):
        self.debug = debug

    def choose_card(self, current_hand, my_hand):
        pass

# TODO: write more and better versions of these
class JustGreedyEnough(SmearPlayingLogic):
    def find_lowest_card_index_to_beat(self, my_hand, card_to_beat, lead_suit, trump):
        lowest_index = None
        if utils.is_trump(card_to_beat, trump):
            # Card to beat is trump, see if I have a higher trump
            my_trump = utils.get_trump_indices(trump, my_hand)
            for idx in my_trump:
                if my_hand[idx].gt(card_to_beat.value, ranks=POKER_RANKS):
                    lowest_index = idx
        elif card_to_beat.suit == lead_suit:
            my_trump = utils.get_trump_indices(trump, my_hand)
            if len(my_trump) != 0:
                # Card to beat isn't trump, but I have trump. Play my lowest trump
                lowest_index = my_trump[0]
            else:
                matching_idxs = my_hand.find(card_to_beat.suit, sort=True, ranks=POKER_RANKS)
                for idx in matching_idxs:
                    # Play the lowest card in the matching suit that will beat the card to beat
                    if my_hand[idx].gt(card_to_beat.value, ranks=POKER_RANKS):
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
            my_hand.sort(ranks=POKER_RANKS)
            strongest_idx = len(my_hand) - 1
        return strongest_idx

    def find_lowest_card_index(self, my_hand, lead_suit, trump):
        lowest_index = None
        lowest_trump_index = None
        # First try following suit
        my_hand.sort(ranks=POKER_RANKS)
        indices = my_hand.find(lead_suit, sort=True, ranks=POKER_RANKS)
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

    def choose_card(self, current_hand, my_hand):
        idx = 0
        if len(current_hand.current_trick.cards.values()) == 0:
            # I'm the first player. Choose my strongest card
            idx = self.find_strongest_card(my_hand, current_hand.trump)
        else:
            # Otherwise choose the lowest card to beat the current highest card
            idx = self.find_lowest_card_index_to_beat(my_hand, current_hand.current_trick.current_winning_card, current_hand.current_trick.lead_suit, current_hand.trump)
            if idx == None:
                # If we can't beat it, then just play the lowest card, following suit as needed
                idx = self.find_lowest_card_index(my_hand, current_hand.current_trick.lead_suit, current_hand.trump)

        card_to_play = my_hand[idx]
        del my_hand[idx]
        return card_to_play


class Player:
    def __init__(self, player_id, initial_cards=None):
        self.reset()
        if initial_cards:
            self.hand += initial_cards
            for card in initial_cards:
                self.card_count.add_card(card)
        self.name = "player{}".format(player_id)
        self.bid = 0
        self.bid_trump = None
        self.is_bidder = False
        self.playing_logic = JustGreedyEnough()
        self.bidding_logic = BasicBidding()

    def reset(self):
        self.hand = pydealer.Stack()
        self.pile = pydealer.Stack()
        self.card_count = CardCount()
        self.bid = 0
        self.bid_trump = None
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
    def play_card(self, current_hand):
        if self.hand.size == 0:
            return None
        card_to_play = self.playing_logic.choose_card(current_hand, self.hand)
        self.card_count.remove_card(card_to_play)
        return card_to_play

    def has_cards(self):
        return self.hand.size != 0

    def declare_bid(self, current_hand, force_two=False):
        self.bid, self.bid_trump = self.bidding_logic.declare_bid(current_hand, self.hand, force_two)
        return self.bid

    def get_trump(self):
        return self.bid_trump

    def calculate_game_score(self):
        game_score = 0
        for card in self.pile:
            if card.value == "10":
                game_score += 10
            if card.value == "Ace":
                game_score += 4
            elif card.value == "King":
                game_score += 3
            elif card.value == "Queen":
                game_score += 2
            elif card.value == "Jack":
                game_score += 1
        return game_score

    def get_high_trump_card(self, trump):
        high_trump = None
        my_trump = utils.get_trump_indices(trump, self.pile)
        if len(my_trump) != 0:
            high_trump = self.pile[my_trump[-1]]
        return high_trump

    def get_low_trump_card(self, trump):
        low_trump = None
        my_trump = utils.get_trump_indices(trump, self.pile)
        if len(my_trump) != 0:
            low_trump = self.pile[my_trump[0]]
        return low_trump

    def get_jacks_and_jicks_count(self, trump):
        my_trump = utils.get_trump_indices(trump, self.pile)
        points = 0
        for idx in my_trump:
            if self.pile[idx].value == "Jack":
                points += 1
        return points

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
