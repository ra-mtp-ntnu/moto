from moto import Moto


robot = Moto("192.168.255.200")

while True:
    print(robot.position)

    