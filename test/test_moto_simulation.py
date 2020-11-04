import logging

from motosim.motosim import MotoSim, ControlGroupSim


def main():
    logging.basicConfig(level=logging.DEBUG)

    sim = MotoSim(
        "localhost",
        [
            ControlGroupSim(0, 6, [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]),
            ControlGroupSim(1, 2, [0.0, 1.0]),
        ],
    )
    sim.start()

    while True:
        pass


if __name__ == "__main__":
    main()
