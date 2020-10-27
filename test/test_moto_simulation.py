import logging
from moto.simulator.moto_simulator import MotoSimulator

def main():
    logging.basicConfig(level=logging.DEBUG)
    sim = MotoSimulator()
    sim.start()

    while True:
        pass


if __name__ == "__main__":
    main()

