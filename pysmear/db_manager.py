from pymongo import MongoClient
import pytz
from datetime import datetime

class DbManager():

    def __init__(self, hostname="localhost", port=27017, client=None, debug=False):
        if client == None:
            self.client = MongoClient("{}:{}".format(hostname, port))
        else:
            self.client = client
        self.debug = debug
        self.db = self.client.smear
        self.current_game_record = self.init_game_record()
        self.current_hand_record = self.init_game_record()
        self.current_bid_record = None
        self.player_map = {}
        self.game_id = None


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
        bid_record['points_lost'] = None
        return bid_record


    def create_game(self, points_to_play_to, num_teams):
        self.current_game_record['points_to_play_to'] = points_to_play_to
        self.current_game_record['num_teams'] = num_teams


    def lookup_or_create_player(self, username, email):
        player_found_by_email = False
        if email:
            find_result = self.db.players.find({'email': email})
            if find_result.count() != 0:
                player_found_by_email = True
                if self.debug:
                    print "Found {} by email: {}".format(username, email)
                if 'username' not in find_result[0] or find_result[0]['username'] != username:
                    if self.debug:
                        print "Updating username to {}".format(username)
                    player_record = dict(find_result[0])
                    player_record['username'] = username
                    self.db.players.update({'_id':player_record['_id']}, player_record)

        if not player_found_by_email:
            if self.debug:
                print "Could not find {} by email".format(username)
            find_result = self.db.players.find({'username': username})
        player_id = None
        if find_result.count() != 0:
            player_id = find_result[0]['_id']
        else:
            player_record = {}
            player_record["username"] = username
            if email:
                player_record["email"] = email
            if self.debug:
                print "Could not find {}, inserting into player database".format(username)
            insert_result = self.db.players.insert_one(player_record)
            if not insert_result.acknowledged:
                print "Error: unable to create user {} in database".format(username)
                return None
            player_id = insert_result.inserted_id
        return player_id


    def add_player(self, username, email=None):
        player_id = self.lookup_or_create_player(username, email)
        self.current_game_record['players'].append(player_id)
        self.player_map[username] = player_id


    def add_game_to_db_for_first_time(self):
        self.current_game_record['date_played'] = datetime.now(pytz.utc)
        insert_result = self.db.games.insert_one(self.current_game_record)
        if not insert_result.acknowledged:
            print "Error: unable to create game in database"
            return
        self.game_id = insert_result.inserted_id


    def add_new_bid(self, username, bidders_hand, bid, high_bid, is_high_bid):
        # Create bid record
        new_bid = self.init_bid_record()
        new_bid['game'] = self.game_id
        new_bid['player'] = self.player_map[username]
        new_bid['bidders_hand'] = bidders_hand
        new_bid['bid_so_far'] = None #TODO
        new_bid['bid'] = bid
        new_bid['high_bid'] = high_bid
        # Will be added after hand is completed
        new_bid['points_won'] = None
        new_bid['points_lost'] = None

        # Add bid to database
        insert_result = self.db.bids.insert_one(new_bid)
        if not insert_result.acknowledged:
            print "Error: unable to create bid of {} for {} in database".format(bid, username)
            return

        # Add bid to hand
        self.current_hand_record['bids'].append(insert_result.inserted_id)
        if is_high_bid:
            self.current_bid_record = new_bid
            self.current_hand_record['high_bid'] = insert_result.inserted_id


    def create_new_hand(self):
        self.current_hand_record = self.init_hand_record()
        self.current_hand_record['players'] = list(self.current_game_record['players'])


    def finalize_hand_creation(self, dealer_forced_two_set):
        if dealer_forced_two_set:
            self.current_hand_record['dealer_forced_two_set'] = self.player_map[dealer_forced_two_set]
        # Add hand to database
        insert_result = self.db.hands.insert_one(self.current_hand_record)
        if not insert_result.acknowledged:
            print "Error: unable to create bid of {} for {} in database".format(bid, username)
            return
        self.current_game_record['hands'].append(insert_result.inserted_id)


    def convert_usernames_to_object_ids(self, results):
        for player_result in results:
            player_id = self.player_map[player_result["player"]]
            player_result["player"] = player_id
        return results


    def publish_hand_results(self, points_won, points_lost, results, overall_winners):
        if overall_winners:
            # Game is over
            self.current_game_record["winners"] = overall_winners
            self.current_game_record["results"] = self.convert_usernames_to_object_ids(results)
        self.current_bid_record["points_won"] = points_won
        self.current_bid_record["points_lost"] = points_lost
        self.db.bids.update({'_id':self.current_bid_record['_id']}, self.current_bid_record)
        self.db.games.update({'_id':self.current_game_record['_id']}, self.current_game_record)
