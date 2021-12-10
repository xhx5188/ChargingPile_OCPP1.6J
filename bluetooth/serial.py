import serial
import logging
import yaml


class Serial():
  def __init__(self, path="../../config.yaml", timeout=0.5):
    with open(path, 'r') as f:
      cfg = yaml.safe_load(f)
      com = cfg['bluetooth']['com']
      bps = cfg['bluetooth']['bps']

    try:
       self.main_engine = serial.Serial(port=com, baudrate=bps, timeout=timeout)
    except Exception as e:
      logging.error("串口%s打开异常:%s", (com, e))


  def print_dev_info(self):
    logging.info(self.main_engine.name) #设备名字
    logging.info(self.main_engine.port)#读或者写端口
    logging.info(self.main_engine.baudrate)#波特率
    logging.info(self.main_engine.bytesize)#字节大小
    logging.info(self.main_engine.parity)#校验位
    logging.info(self.main_engine.stopbits)#停止位
    logging.info(self.main_engine.timeout)#读超时设置
    logging.info(self.main_engine.writeTimeout)#写超时
    logging.info(self.main_engine.xonxoff)#软件流控
    logging.info(self.main_engine.rtscts)#软件流控
    logging.info(self.main_engine.dsrdtr)#硬件流控
    logging.info(self.main_engine.interCharTimeout)#字符间隔超时


  def open_engine(self):
    self.main_engine.open()


  def close_engine(self):
    self.main_engine.close()
    logging.info(self.main_engine.is_open) # 检验串口是否打开


  def read_size(self,size):
    return self.main_engine.read(size=size)


  def read_line(self):
    return self.main_engine.readline()


  def send_hex_data(self, hex_data: str):
    data = bytes.fromhex(hex_data)
    self.main_engine.write(data)


  def send_at(self, cmd: str):
    data = bytes(cmd, 'utf-8')
    self.main_engine.write(data)


  def send_lines(self, buffer):
    self.main_engine.writelines(buffer)

  # 其它示例
  # self.main_engine.write(chr(0x06).encode("utf-8")) # 十六制发送一个数据
  # print(self.main_engine.read().hex()) # # 十六进制的读取读一个字节
  # print(self.main_engine.read())#读一个字节
  # print(self.main_engine.read(10).decode("gbk"))#读十个字节
  # print(self.main_engine.readline().decode("gbk"))#读一行
  # print(self.main_engine.readlines())#读取多行，返回列表，必须匹配超时（timeout)使用
  # print(self.main_engine.in_waiting)#获取输入缓冲区的剩余字节数
  # print(self.main_engine.out_waiting)#获取输出缓冲区的字节数
  # print(self.main_engine.readall())#读取全部字符。



def test_1():
  engine = Serial(path="../config.yaml")
  engine.send_hex_data("41540D0A")
  s = "111"
  while s:
    l = engine.read_line()
    s = str(l, 'utf-8')
    logging.info(s)
    if "OK" in s:
      break


def test_2():
  at = "AT\r\n"
  engine = Serial(path="../config.yaml")
  engine.send_at(at)
  print(engine.read_line())
  print(engine.read_line())
  print(engine.read_line())
  print(engine.read_line())
  print(engine.read_line())