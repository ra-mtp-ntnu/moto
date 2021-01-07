import socket
import time

from moto.simple_message import *

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 50243))

req = SimpleMessage(
    Header(MsgType.MOTO_MOTION_CTRL, CommType.SERVICE_REQUEST, ReplyType.INVALID),
    MotoMotionCtrl(-1, -1, CommandType.START_REALTIME_MOTION_MODE),
)
client.send(req.to_bytes())

res = SimpleMessage.from_bytes(client.recv(1024))
print(res)

time.sleep(3)

req = SimpleMessage(
    Header(MsgType.MOTO_MOTION_CTRL, CommType.SERVICE_REQUEST, ReplyType.INVALID),
    MotoMotionCtrl(-1, -1, CommandType.STOP_REALTIME_MOTION_MODE),
)
client.send(req.to_bytes())

res = SimpleMessage.from_bytes(client.recv(1024))
print(res)
