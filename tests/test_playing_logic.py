import unittest
import sys

sys.path.insert(0, "..")
import pysmear.playing_logic
import pydealer

class TestPlayingLogic(unittest.TestCase):
    def setUp(self):
        self.pl = pysmear.playing_logic.JustGreedyEnough()
        self.lead_suit = "Spades"
        self.trump = "Spades"
        self.six_hearts = pydealer.Card("6", "Hearts")
        self.seven_hearts = pydealer.Card("7", "Hearts")
        self.nine_clubs = pydealer.Card(value="9", suit="Clubs")
        self.jack_clubs = pydealer.Card("Jack", "Clubs")
        self.queen_diamonds = pydealer.Card(value="Queen", suit="Diamonds")

        self.ace_spades = pydealer.Card("Ace", "Spades")
        self.two_diamonds = pydealer.Card("2", "Diamonds")
        self.queen_hearts = pydealer.Card("Queen", "Hearts")
        self.seven_clubs = pydealer.Card("7", "Clubs")
        self.two_spades = pydealer.Card("2", "Spades")
        self.cards = [self.six_hearts, self.seven_hearts, self.nine_clubs, self.jack_clubs, self.queen_diamonds]
        self.my_hand = pydealer.Stack(cards=self.cards)

    def test_find_lowest_card_index_when_trump_is_lead(self):
        self.cards = [self.six_hearts, self.seven_hearts, self.nine_clubs, self.jack_clubs, self.queen_diamonds]
        self.my_hand = pydealer.Stack(cards=self.cards)
        index = self.pl.find_lowest_card_index(self.my_hand, self.lead_suit, self.trump)
        self.assertEqual(self.my_hand[index], self.jack_clubs)

    def test_find_lowest_card_index_when_trump_is_lead_returns_lowest_trump(self):
        self.cards = [self.six_hearts, self.two_spades, self.nine_clubs, self.jack_clubs, self.queen_diamonds]
        self.my_hand = pydealer.Stack(cards=self.cards)
        index = self.pl.find_lowest_card_index(self.my_hand, self.lead_suit, self.trump)
        self.assertEqual(self.my_hand[index], self.two_spades)
