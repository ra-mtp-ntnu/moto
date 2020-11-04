import logging
from moto.simulator.moto_simulator import MotoSimulator, ControlGroupSim

def main():
    logging.basicConfig(level=logging.DEBUG)
    
    sim = MotoSimulator("localhost", [ControlGroupSim(0, 6, [0.0, 1.0, 2.0, 3.0, 4.0, 5.0])])
    sim.start()

    while True:
        pass


if __name__ == "__main__":
    main()

