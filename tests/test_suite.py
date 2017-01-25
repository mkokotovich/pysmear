import unittest

from test_bidding_logic import TestBiddingLogic
from test_smear_engine_api import TestSmearEngineApi

TESTS = [ TestBiddingLogic, TestSmearEngineApi ]


def main():
    """"""
    suite = unittest.TestSuite()
    runner = unittest.TextTestRunner()
    for test in TESTS:
        suite.addTest(unittest.makeSuite(test))
    runner.run(suite)


if __name__ == '__main__':
   main()
