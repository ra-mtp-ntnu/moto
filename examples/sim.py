from moto.sim.motosim import ControlGroupSim, MotoSim



m = MotoSim("localhost", [ControlGroupSim(0, 6, [0.0] * 6)])
m.start()


