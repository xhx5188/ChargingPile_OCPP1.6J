import os

import serial
import logging

class Serial():
  #初始化
  def __init__(self, com, bps=9600, timeout=1):
    self.port = com
    self.bps = bps
    self.timeout =timeout

    try:
      # 打开串口，并得到串口对象
       self.main_engine = serial.Serial(port=com, baudrate=bps, timeout=timeout)
      # 判断是否打开成功
       if (self.main_engine.is_open):
        Ret = True
    except Exception as e:
      logging.info("串口%s打开异常:%s", (self.port, e))

  # 打印设备基本信息
  def print_name(self):
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

  #打开串口
  def open_engine(self):
    self.main_engine.open()

  #关闭串口
  def close_engine(self):
    self.main_engine.close()
    logging.info(self.main_engine.is_open) # 检验串口是否打开

  #接收指定大小的数据
  def read_size(self,size):
    return self.main_engine.read(size=size)

  #接收一行数据
  # 使用readline()时应该注意：打开串口时应该指定超时，否则如果串口没有收到新行，则会一直等待。
  # 如果没有超时，readline会报异常。
  def read_line(self):
    return self.main_engine.readline()

  def send_hex_data(self, hex_data: str):
    data = bytes.fromhex(hex_data)
    self.main_engine.write(data)
  #更多示例
  # self.main_engine.write(chr(0x06).encode("utf-8")) # 十六制发送一个数据
  # print(self.main_engine.read().hex()) # # 十六进制的读取读一个字节
  # print(self.main_engine.read())#读一个字节
  # print(self.main_engine.read(10).decode("gbk"))#读十个字节
  # print(self.main_engine.readline().decode("gbk"))#读一行
  # print(self.main_engine.readlines())#读取多行，返回列表，必须匹配超时（timeout)使用
  # print(self.main_engine.in_waiting)#获取输入缓冲区的剩余字节数
  # print(self.main_engine.out_waiting)#获取输出缓冲区的字节数
  # print(self.main_engine.readall())#读取全部字符。


def get_path():
  return os.getcwd()
