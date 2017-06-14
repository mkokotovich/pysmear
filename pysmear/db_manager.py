from pymongo import MongoClient
import pytz
from datetime import datetime

class DbManager():

    def __init__(self, hostname="localhost", port=27017, client=None):
        if client == None:
            self.client = MongoClient("{}:{}".format(hostname, port))
        else:
            self.client = client
        self.db = self.client.smear
        self.game_record = self.init_game_record()
        self.current_hand_record = self.init_game_record()
        self.player_map = {}
        self.game_id = None
        self.current_bid_id = None


    def init_game_record(self):
        game_record = {}
        game_record['date_played'] = None
        game_record['points_to_play_to'] = None
        game_record['num_teams'] = None
        game_record['players'] = []
        game_record['hands'] = []
        game_record['winners'] = []
        game_record['results'] = []
        return game_record


    def init_hand_record(self):
        hand_record = {}
        hand_record['bids'] = []
        hand_record['high_bid'] = None
        hand_record['players'] = []
        hand_record['dealer_forced_two_set'] = None
        return hand_record


    def init_bid_record(self):
        bid_record = {}
        bid_record['game'] = None
        bid_record['player'] = None
        bid_record['bidders_hand'] = []
        bid_record['bid_so_far'] = None
        bid_record['bid'] = None
        bid_record['high_bid'] = None
        bid_record['points_won'] = None


    def create_game(self, points_to_play_to, num_teams):
        self.game_record['points_to_play_to'] = points_to_play_to
        self.game_record['num_teams'] = num_teams


    def lookup_or_create_player(self, username):
        find_result = self.db.players.find({'username': username})
        player_id = None
        if find_result.count() != 0:
            player_id = find_result[0]['_id']
        else:
            insert_result = self.db.players.insert_one({'username': username})
            if not insert_result.acknowledged:
                print "Error: unable to create user {} in database".format(username)
                return None
            player_id = insert_result.inserted_id
        return player_id


    def add_player(self, username):
        player_id = self.lookup_or_create_player(username)
        self.game_record['players'].append(player_id)
        self.player_map[username] = player_id


    def add_game_to_db_for_first_time(self):
        self.game_record['date_played'] = datetime.now(pytz.utc)
        insert_result = self.db.games.insert_one(self.game_record)
        if not insert_result.acknowledged:
            print "Error: unable to create game in database"
            return
        self.game_id = insert_result.inserted_id


    def add_new_bid(self, username, bidders_hand, bid, high_bid, is_high_bid):
        # Create bid record
        new_bid = init_bid_record()
        new_bid['game'] = self.game_id
        new_bid['player'] = self.player_map[username]
        new_bid['bidders_hand'] = bidders_hand
        new_bid['bid_so_far'] = None #TODO
        new_bid['bid'] = bid
        new_bid['high_bid'] = high_bid
        new_bid['points_won'] = None # Will be added after hand is completed

        # Add bid to database
        insert_result = self.db.bids.insert_one(new_bid)
        if not insert_result.acknowledged:
            print "Error: unable to create bid of {} for {} in database".format(bid, username)
            return

        # Add bid to hand
        self.current_hand_record['bids'].append(insert_result.inserted_id)
        if is_high_bid:
            self.current_bid_id = insert_result.inserted_id
            self.current_hand_record['high_bid'] = insert_result.inserted_id


    def create_new_hand(self):
        self.current_hand_record = self.init_hand_record()
        self.current_hand_record['players'] = list(self.game_record['players'])


    def finalize_hand(self, dealer_forced_two_set):
        if dealer_forced_two_set:
            self.current_hand_record['dealer_forced_two_set'] = self.player_map[dealer_forced_two_set]
        # Add hand to database
        insert_result = self.db.hands.insert_one(self.current_hand_record)
        if not insert_result.acknowledged:
            print "Error: unable to create bid of {} for {} in database".format(bid, username)
            return
        self.game_record['hands'].append(insert_result.inserted_id)
