import logging
import time
import socket
import yaml
# from connector.serial import Serial
#
# class Connector():
#     serial = None
#     def __init__(self):
#         yaml_file = "../../config.yaml"
#         with open(yaml_file, 'r') as f:
#             cfg = yaml.safe_load(f)
#             connector = cfg['connector']
#             Connector.serial = Serial(connector['com'], connector['bps'])
#
#     @classmethod
#     def slot(self):
#         Connector.serial.send_hex_data("a00101a2")
#
#     @classmethod
#     def unslot(self):
#         Connector.serial.send_hex_data("a00100a1")
#
#
# def test_11():
#     Connector()
#     Connector.unslot()
#
# def test_22():
#     Connector()
#     Connector.slot()


class Connector():
    @classmethod
    def slot(self):
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        s.connect(("10.10.41.44", 8080))
        data = bytes.fromhex("a00101a2")
        s.send(data)
        s.close()

    @classmethod
    def unslot(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("10.10.41.44", 8080))
        data = bytes.fromhex("a00100a1")
        s.send(data)
        s.close()