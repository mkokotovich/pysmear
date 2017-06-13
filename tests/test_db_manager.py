import unittest
import sys

sys.path.insert(0, "..")
import pysmear.db_manager

class TestDbManager(unittest.TestCase):
    def setUp(self):
        self.dbm = pysmear.db_manager.DbManager()
        self.clear_database_and_dbm()

    def clear_database_and_dbm(self):
        self.dbm.db.players.drop()
        self.dbm.game_record = self.dbm.init_game_record()

    def assert_user_is_in_users(self, username):
        find_result = self.dbm.db.players.find({'username': username})
        self.assertEqual(find_result.count(), 1)
        return find_result[0]['_id']

    def test_create_game(self):
        self.dbm.create_game(11, 0)
        self.assertEqual(self.dbm.game_record['points_to_play_to'], 11)
        self.assertEqual(self.dbm.game_record['num_teams'], 0)

    def test_add_player_with_new_player(self):
        self.clear_database_and_dbm()
        self.dbm.add_player("new_player")
        player_id = self.assert_user_is_in_users("new_player")
        dbm_players = self.dbm.game_record['players']
        self.assertEqual(len(dbm_players), 1)
        self.assertEqual(dbm_players[0], player_id)
        self.assertEqual(self.dbm.player_map["new_player"], player_id)

    def test_add_player_with_repeat_player(self):
        self.clear_database_and_dbm()
        username = "repeat_player"
        insert_result = self.dbm.db.players.insert_one({'username': username})
        inserted_player_id = insert_result.inserted_id
        self.dbm.add_player(username)
        player_id = self.assert_user_is_in_users(username)
        self.assertEqual(inserted_player_id, player_id)
        dbm_players = self.dbm.game_record['players']
        self.assertEqual(len(dbm_players), 1)
        self.assertEqual(dbm_players[0], player_id)
        self.assertEqual(self.dbm.player_map[username], player_id)
