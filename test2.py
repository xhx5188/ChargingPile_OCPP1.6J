
# from dateutil.parser import parse
# a = parse('2021-11-22T09:59:19.000Z')
# b = parse('2021-11-22T10:59:19.000Z')
# print((b - a).seconds)
import logging
import time
from datetime import datetime

from connector.serial import get_path


def test_2():
    s="68 65 6c 6c 6f"
    print("".join([chr(i) for i in [int(b, 16) for b in s.split(' ')]]))


def hextostr(list):#list为整数表示的列表
    hexstr=''
    for item in list:
        temp=hex(item)#先转换为字符串，例如100转换为'0x64'
        if len(temp)==3:
            hexstr=hexstr+'0'+temp[2]#一个16进制数以两个字符表示，如0x06对应的字符串为'06'而不是'6';
        else:
            hexstr=hexstr+temp[2]+temp[3]
    print("hexstr=%s" % hexstr)
    strsend=hexstr.decode('hex')#以unicode码的形式写到串口
    return strsend

def test_3():
    # print(hextostr([16, 17]))
    a = '3132333435'
    a_bytes = bytes.fromhex(a)
    print(a_bytes)
    aa = a_bytes.hex()
    print(aa)
    print(type(aa))

def test_4():
    from dateutil.parser import parse
    logging.info(type(time.time()))
    time1 = parse(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z'))

    time.sleep(2)
    time2 = parse(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.123Z'))

    interval = (time2 - time1).seconds
    print("3333")
    print(interval)

