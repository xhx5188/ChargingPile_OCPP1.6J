import time
import yaml
from connector.serial import Serial

def test_1():
  engine = Serial("COM4", 9600, 0.5)
  # 打开继电器
  engine.send_hex_data("a00101a2")
  time.sleep(1)


def test_2():
  engine = Serial("COM4", 9600, 0.5)
  # 关闭继电器
  engine.send_hex_data("a00100a1")
