import unittest
import sys

sys.path.insert(0, "..")
import pysmear.playing_logic
import pydealer

class TestJustGreedyEnoughPlayingLogic(unittest.TestCase):
    def setUp(self):
        self.pl = pysmear.playing_logic.JustGreedyEnough()
        self.lead_suit = "Spades"
        self.trump = "Spades"
        self.six_hearts = pydealer.Card("6", "Hearts")
        self.seven_hearts = pydealer.Card("7", "Hearts")
        self.nine_clubs = pydealer.Card(value="9", suit="Clubs")
        self.jack_clubs = pydealer.Card("Jack", "Clubs")
        self.queen_diamonds = pydealer.Card(value="Queen", suit="Diamonds")

        self.two_hearts = pydealer.Card("2", "Hearts")
        self.seven_diamonds = pydealer.Card("7", "Diamonds")
        self.ten_clubs = pydealer.Card("10", "Clubs")
        self.queen_spades = pydealer.Card("Queen", "Spades")
        self.ace_diamonds = pydealer.Card("Ace", "Diamonds")

        self.two_diamonds = pydealer.Card("2", "Diamonds")
        self.queen_hearts = pydealer.Card("Queen", "Hearts")
        self.seven_clubs = pydealer.Card("7", "Clubs")
        self.two_spades = pydealer.Card("2", "Spades")
        self.cards = [self.six_hearts, self.seven_hearts, self.nine_clubs, self.jack_clubs, self.queen_diamonds]
        self.my_hand = pydealer.Stack(cards=self.cards)

    def test_find_lowest_card_index_when_trump_is_lead(self):
        self.cards = [self.six_hearts, self.seven_hearts, self.nine_clubs, self.jack_clubs, self.queen_diamonds]
        self.lead_suit = "Trump"
        self.my_hand = pydealer.Stack(cards=self.cards)
        index = self.pl.find_lowest_card_index(self.my_hand, self.lead_suit, self.trump)
        self.assertEqual(self.my_hand[index], self.jack_clubs)

    def test_find_lowest_card_index_when_trump_is_lead_returns_lowest_trump(self):
        self.cards = [self.six_hearts, self.two_spades, self.nine_clubs, self.jack_clubs, self.queen_diamonds]
        self.lead_suit = "Trump"
        self.my_hand = pydealer.Stack(cards=self.cards)
        index = self.pl.find_lowest_card_index(self.my_hand, self.lead_suit, self.trump)
        self.assertEqual(self.my_hand[index], self.two_spades)

    def test_find_lowest_card_index_handles_jick_being_lead(self):
        self.trump = "Clubs"
        self.cards = [self.two_hearts, self.seven_diamonds, self.ten_clubs, self.queen_spades, self.ace_diamonds]
        self.my_hand = pydealer.Stack(cards=self.cards)
        self.lead_suit = "Trump"
        index = self.pl.find_lowest_card_index(self.my_hand, self.lead_suit, self.trump)
        self.assertEqual(self.my_hand[index], self.ten_clubs)

    def test_find_lowest_card_index_returns_lowest_when_unable_to_follow_suit(self):
        self.trump = "Spades"
        self.cards = [self.six_hearts, self.two_hearts, self.seven_clubs, self.ten_clubs]
        self.my_hand = pydealer.Stack(cards=self.cards)
        self.lead_suit = "Diamonds"
        index = self.pl.find_lowest_card_index(self.my_hand, self.lead_suit, self.trump)
        self.assertEqual(self.my_hand[index], self.two_hearts)


class TestCautiousTakerPlayingLogic(unittest.TestCase):
    def setUp(self):
        self.pl = pysmear.playing_logic.CautiousTaker()
        self.lead_suit = "Spades"
        self.trump = "Spades"
        self.six_hearts = pydealer.Card("6", "Hearts")
        self.seven_hearts = pydealer.Card("7", "Hearts")
        self.nine_clubs = pydealer.Card(value="9", suit="Clubs")
        self.jack_clubs = pydealer.Card("Jack", "Clubs")
        self.queen_diamonds = pydealer.Card(value="Queen", suit="Diamonds")

        self.two_hearts = pydealer.Card("2", "Hearts")
        self.seven_diamonds = pydealer.Card("7", "Diamonds")
        self.ten_clubs = pydealer.Card("10", "Clubs")
        self.queen_spades = pydealer.Card("Queen", "Spades")
        self.ace_diamonds = pydealer.Card("Ace", "Diamonds")
        self.ace_spades = pydealer.Card("Ace", "Spades")
        self.seven_spades = pydealer.Card("7", "Spades")

        self.two_diamonds = pydealer.Card("2", "Diamonds")
        self.queen_hearts = pydealer.Card("Queen", "Hearts")
        self.seven_clubs = pydealer.Card("7", "Clubs")
        self.two_spades = pydealer.Card("2", "Spades")
        self.cards = [self.six_hearts, self.seven_hearts, self.nine_clubs, self.jack_clubs, self.queen_diamonds]
        self.my_hand = pydealer.Stack(cards=self.cards)

    def test_get_A_K_Q_of_trump_with_A_Q(self):
        self.trump = "Spades"
        self.cards = [self.six_hearts, self.ace_spades, self.two_hearts, self.queen_spades, self.seven_clubs] 
        self.my_hand = pydealer.Stack(cards=self.cards)
        index = self.pl.get_A_K_Q_of_trump(self.my_hand, self.trump)
        self.assertEqual(self.my_hand[index], self.ace_spades)

    def test_get_A_K_Q_of_trump_with_small_trump(self):
        self.trump = "Spades"
        self.cards = [self.six_hearts, self.two_hearts, self.seven_spades, self.ten_clubs]
        self.my_hand = pydealer.Stack(cards=self.cards)
        index = self.pl.get_A_K_Q_of_trump(self.my_hand, self.trump)
        self.assertEqual(None, index)

    def test_get_A_K_Q_of_trump_with_no_trump(self):
        self.trump = "Spades"
        self.cards = [self.six_hearts, self.two_hearts, self.seven_clubs, self.ten_clubs]
        self.my_hand = pydealer.Stack(cards=self.cards)
        index = self.pl.get_A_K_Q_of_trump(self.my_hand, self.trump)
        self.assertEqual(None, index)

