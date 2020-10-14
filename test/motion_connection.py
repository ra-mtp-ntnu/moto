
import socket
import struct
import numpy as np

robot_ip = "192.168.255.200"

motion_server_port = 50240

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((robot_ip, motion_server_port))


header = struct.pack("iii", 2001, 2, 0)
body = struct.pack("iii"+"f"*10, 0, 42, 200112, *np.zeros(10))
prefix = struct.pack("i", len(header) + len(body) + 4)

msg = prefix + header + body



client.send(msg)

data = client.recv(1024)

# Prefix
length = struct.unpack("i", data[:4])
# Header
msg_type, comm_type, reply_type = struct.unpack("iii", data[4:16])

if msg_type == 2002:

    groupno, sequence, command, result= struct.unpack("iiii", data[16:32])

    print(groupno)
    print(command)
    print(result)



