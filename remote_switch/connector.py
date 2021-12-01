import socket
import time

# s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
# s.connect(("10.10.41.44", 8080))
# data = bytes.fromhex("a00101a2")
# s.send(data)
# s.close()

# time.sleep(6)
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("10.10.41.44", 8080))
data = bytes.fromhex("a00100a1")
s.send(data)
s.close()


