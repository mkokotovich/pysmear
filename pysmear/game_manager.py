# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS
from hand import *
from player import Player
from smear_exceptions import *
from score_graph import ScoreGraphManager


class SmearGameManager:
    def __init__(self, num_players=0, cards_to_deal=6, score_to_play_to=11, debug=False, num_teams=0, graph_prefix=None, static_dir=None):
        self.num_players = num_players
        self.num_teams = num_teams
        self.cards_to_deal = cards_to_deal
        self.players = {}
        self.debug = debug
        self.game_over = False
        self.winning_score = 0
        self.scores = {}
        self.score_to_play_to = score_to_play_to
        self.hand_manager = None
        self.dealer = 0
        self.all_hand_results = {}
        self.all_high_bid_infos = {}
        self.bidding_is_finished = False
        self.trump_revealed = False
        self.forced_two_set = False
        self.score_graph = ScoreGraphManager(self.score_to_play_to)
        self.graph_prefix = graph_prefix
        self.static_dir = static_dir

    def initialize_default_players(self):
        for i in range(0, self.num_players):
            self.players[i] = Player("player{}".format(i), debug=self.debug)

    def reset_players(self):
        for i in range(0, self.num_players):
            self.players[i].reset()

    def add_player(self, player):
        for existing_player in self.players.values():
            if existing_player.name == player.name:
                raise SmearUserHasSameName("The name {} is already taken, choose a different name".format(player.name))
        if self.debug:
            print("Adding {} with index {}".format(player.name, self.num_players))
        self.players[self.num_players] = player
        player.set_player_id(self.num_players)
        if self.num_teams is not 0:
            player.set_team_id(self.num_players % self.num_teams)
        self.num_players += 1

    def reset_game(self):
        self.reset_players()
        self.score_graph.reset()
        self.scores = {}
        self.game_over = False
        self.winning_score = 0
        self.dealer = 0

    def start_game(self):
        self.hand_manager = SmearHandManager(self.players, self.cards_to_deal, self.debug)
        self.start_next_hand()
        self.save_score_graph([0]*self.num_players)

    def is_game_over(self):
        return self.game_over

    def get_hand_id(self):
        return self.hand_manager.current_hand_id

    def all_bids_are_in(self, hand_id):
        if hand_id == self.hand_manager.current_hand_id:
            return self.hand_manager.all_bids_are_in
        else:
            return True

    def get_trump(self):
        trump = self.hand_manager.current_hand.trump
        if len(trump) == 0:
            trump = None
        return trump

    def get_bid_and_bidder(self, hand_id):
        if self.hand_manager.current_hand_id == hand_id and not self.hand_manager.forced_two_set:
            return self.hand_manager.current_hand.bid, self.hand_manager.current_hand.bidder
        else:
            # This would happen if the dealer was forced to take a two-set and then next hand was dealt
            return 0, None

    def get_hand_results(self, hand_id):
        results = self.all_hand_results[hand_id]
        return results

    def set_next_dealer(self):
        self.dealer = self.dealer + 1
        if self.dealer == self.num_players:
            self.dealer = 0

    def get_winners(self):
        winners = []
        for i in range(0, self.num_players):
            if self.scores[i] == self.winning_score:
                winners.append(self.players[i].name)
        return winners

    def get_players(self):
        return self.players.values()

    def get_player_or_team_names(self):
        if self.num_teams == 0:
            return [ x.name for x in self.players.values() ]
        else:
            team_names = [
                    "Blue team",
                    "Orange team",
                    "Plum team",
                    "Sienna team"
                    ]
            return [ team_names[x] for x in range(0, self.num_teams) ]

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

# TODO: Write better logic for winning by two and ties
    def update_scores(self, hand_scores, bidder):
        if self.debug:
            print "Current score:\n{}".format(self.format_scores(self.scores))
            print "Score of last hand:\n{}".format(self.format_scores(hand_scores))
        new_scores = {x: self.scores.get(x, 0) + hand_scores.get(x, 0) for x in set(self.scores).union(hand_scores)}
        self.scores = new_scores
        if self.debug:
            print "New scores:\n{}".format(self.format_scores(self.scores))
        if max(self.scores.values()) >= self.score_to_play_to:
            if self.scores[bidder] >= self.score_to_play_to:
                # Bidder always goes out, regardless of who had the higher score
                self.winning_score = self.scores[bidder]
            else:
                self.winning_score = max(self.scores.values())
            self.game_over = True
            if self.debug:
                print "Game over with a winning score of {}".format(self.winning_score)

    def __str__(self):
        msg = ""
        return msg

    def generate_player_infos(self):
        player_infos = []
        for i in range(0, self.num_players):
            player_info = {}
            player_info["username"] = self.players[i].name
            player_info["score"] = self.scores[i]
            player_info["game_points"] = self.players[i].calculate_game_score()
            player_infos.append(player_info)
        return player_infos

    def get_high_bid_info(self, hand_id):
        return self.all_high_bid_infos[hand_id]

    def save_high_bid_info(self):
        bid_info = {}
        bid_info["current_bid"] = self.hand_manager.current_hand.bid
        bid_info["bidder"] = self.hand_manager.current_hand.bidder
        bid_info["all_bids"] = self.hand_manager.current_hand.get_all_bids()
        self.all_high_bid_infos[self.hand_manager.current_hand_id] = bid_info


    # Needs to be called only once per hand
    def start_next_hand(self):
        self.hand_manager.reset_for_next_hand()
        self.set_next_dealer()
        self.forced_two_set = False
        self.bidding_is_finished = False
        self.trump_revealed = False


    # Can be called repeatedly
    def continue_bidding(self):
        self.forced_two_set = self.hand_manager.get_bids(self.dealer)
        self.save_high_bid_info()
        if self.forced_two_set:
            # Forced set, dealer get_scores() will return appropriately
            if self.debug:
                print "Dealer ({}) was forced to take a two set".format(self.players[self.dealer].name)


    # Save a new graph
    def save_score_graph(self, current_scores, game_is_over=False):
        if self.static_dir is None or self.graph_prefix is None:
            return
        hand_id = self.hand_manager.current_hand_id
        if game_is_over:
            hand_id = "final"
        filename = "{}/{}_hand{}.png".format(self.static_dir, self.graph_prefix, hand_id)

        self.score_graph.export_graph(self.graph_prefix, filename, current_scores, self.get_player_or_team_names())
    

    # Needs to be called only once per hand
    def finish_hand(self):
        # Update scores
        self.update_scores(self.hand_manager.get_scores(self.dealer), self.hand_manager.current_hand.bidder)
        # Save hand results
        self.all_hand_results[self.hand_manager.current_hand_id] = self.hand_manager.hand_results
        # Add whether or not the game is over
        self.all_hand_results[self.hand_manager.current_hand_id]["is_game_over"] = self.is_game_over()
        # Add current scores at the end of the hand
        self.all_hand_results[self.hand_manager.current_hand_id]["player_infos"] = self.generate_player_infos()


    # Can be called repeatedly
    # Returns False if it needs to be called again
    # Returns True if the game is finished
    def play_game_async(self):
        try:
            if not self.bidding_is_finished:
                self.continue_bidding()
                self.bidding_is_finished = True
            if not self.forced_two_set:
                # Only play the hand if the dealer wasn't forced to take a two set
                if not self.trump_revealed:
                    self.hand_manager.reveal_trump()
                    self.trump_revealed = True
                while not self.hand_manager.is_hand_over():
                    # Play trick
                    self.hand_manager.play_trick()
        except SmearNeedInput as e:
            if self.debug:
                print "Stopping to allow input: {}".format(e.strerror)
            return False

        # Hand is finished, calculate scores and log the results
        self.finish_hand()

        # Start the next hand
        game_is_over = False
        if not self.is_game_over():
            self.start_next_hand()
        else:
            game_is_over = True

        # Save a new graph
        self.save_score_graph(self.scores, game_is_over)

        return game_is_over
