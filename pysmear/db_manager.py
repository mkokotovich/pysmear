from pymongo import MongoClient

class DbManager():

    def __init__(self, hostname="localhost", port=27017):
        self.client = MongoClient("{}:{}".format(hostname, port))
        self.db = self.client.smear
        self.game_record = self.init_game_record()
        self.player_map = {}


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
