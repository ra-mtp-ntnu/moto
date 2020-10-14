import socket
import struct
import numpy as np

robot_ip = "192.168.255.200"

state_server_port = 50241

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((robot_ip, state_server_port))

while True:
    data = client.recv(1024)
    
    # Prefix
    length = struct.unpack("i", data[:4])
    # Header
    msg_type, comm_type, reply_type = struct.unpack("iii", data[4:16])
    # Body
    if msg_type == 15:
        # SmBodyJointFeedback
        groupno, valid_fields, time = struct.unpack("iif", data[16:28])
        pos_vel_acc = struct.unpack("f"*30, data[28:148])
        pos = pos_vel_acc[:10]
        vel = pos_vel_acc[10:20]
        acc = pos_vel_acc[20:30]
