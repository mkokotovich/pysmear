# Simulator for the card game smear

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/pydealer")

from pysmear import smear_simulator

def main():
    one_test=False
    one_test=True
    if one_test:
        num_runs = 1
        print "Setting up..."
        sim = smear_simulator.SmearSimulator(debug=True)
    else:
        num_runs = 100
        print "Setting up..."
        sim = smear_simulator.SmearSimulator(debug=False)
    if len(sys.argv) > 1:
        num_runs = int(sys.argv[1])
    sim.run(num_runs)
    print "Generating stats..."
    print sim.stats()

if __name__ == "__main__":
    main()
