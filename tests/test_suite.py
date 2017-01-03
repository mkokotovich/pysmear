import unittest

from test_bidding_logic import TestBiddingLogic

TESTS = [ TestBiddingLogic ]


def main():
    """"""
    suite = unittest.TestSuite()
    runner = unittest.TextTestRunner()
    for test in TESTS:
        suite.addTest(unittest.makeSuite(test))
    runner.run(suite)


if __name__ == '__main__':
   main()
