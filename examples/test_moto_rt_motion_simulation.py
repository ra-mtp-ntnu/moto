import logging
from threading import Lock

from moto.sim.realtime_motion_server_sim import RealTimeMotionServerSim


def main():
    logging.basicConfig(level=logging.DEBUG)

    sim = RealTimeMotionServerSim()
    sim.start()

    while True:
        pass



if __name__ == "__main__":
    main()
