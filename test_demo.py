# -*- coding: UTF-8 -*-

# from dateutil.parser import parse
# a = parse('2021-11-22T09:59:19.000Z')
# b = parse('2021-11-22T10:59:19.000Z')
# print((b - a).seconds)
import hashlib
import logging
import time
from datetime import datetime


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

def test_5():
    # b = b'+NOTIFY:0,3,6,20,U\xaa\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\xc2\xfa\xfe\xc0\xdc\xef\xc7\r\n'
    # # b = str(b, 'gbk')
    # b = b.decode('utf-8')
    print("*" * 100)
    print(b'\x31'.decode('utf-8', "ignore"))


def test_6():
    sha256 = hashlib.sha256()
    data = "asd"
    sha256.update(data.encode())
    res = sha256.hexdigest()
    print("sha256加密结果:", res)
    return res

def test_7():
    hash = hashlib.sha256()
    key = b'\x02\x06\x48\x94\x4d\xd5\xb2\xc0\xf9\x7a\x8f\x7f\x30\x99\x09\xe2\x47\xb0\x28\x29\x5a\xf6\x8a\x78\xd1\xcd\xc6\xae\x1a\x11\x2c\x23'
    # data = "123"
    # hash.update(data.encode('utf-8'))
    hash.update(key)
    print(hash.hexdigest().upper())



from hashlib import sha256
import hmac

def get_sign(data):

    #sha256加密有2种
    hsobj = sha256()
    hsobj.update(data)
    return hsobj.hexdigest().upper()

    # return hmac.new(key, data, digestmod=sha256).hexdigest().upper()

#723CA6C4AFF62F72B80AB138A643A63C7AD4089EDC20D60458E266BDEEFE4518
def test_8():
    data = b'11111111:11111111111111111111111111111111:111111111111111111:11111111111111111'
    print()
    print(get_sign(data))

def test_9():
    data = b'\x311'
    print()
    print(get_sign(data))

    data = b'11'
    print(get_sign(data))

def test_10():
    id = "44332211b5e2ae63".encode('utf-8')
    logging.info(type(id))
    passwd = b'\x02\x06\x48\x94\x4d\xd5\xb2\xc0\xf9\x7a\x8f\x7f\x30\x99\x09\xe2\x47\xb0\x28\x29\x5a\xf6\x8a\x78\xd1\xcd\xc6\xae\x1a\x11\x2c\x23'
    logging.info(type(passwd))
    salt = "3d90-a7ef-8426b1c5".encode('utf-8')
    WIFI_MAC = "AA:BB:CC:DD:EE:FF".encode('utf-8')
    data = id+passwd+salt+WIFI_MAC
    logging.info(data)
    logging.info(type(data))

    sha256 = hashlib.sha256()
    sha256.update(data)
    res = sha256.hexdigest()
    logging.info("sha256加密结果:%s", res)
    return res

def test_11():
    print(isinstance("11".encode('utf-8'), (bytes, bytearray)))
    print(isinstance("11", (bytes, bytearray)))
    a = "cb3c5120e58c17a551f4751ab67484d5c92816b37796f03f08e671db9fce4a26"
    new_a = ""
    while a is not "":
        new_a += a[-2]+a[-1]
        a = a[:-2]
    print(new_a)
    print(len(new_a))

def test_12():
    a = b'123\x34\x35'
    print(a.hex())
    print(get_sign(a))
    print(get_sign(b'\x31\x32\x33\x34\x35'))

    data = b'\x11\x22\x33\x44\xc8\xc2\xad\x41\x3a\x02\x06\x48\x94\x4d\xd5\xb2\xc0\xf9\x7a\x8f\x7f\x30\x99\x09\xe2\x47\xb0\x28\x29\x5a\xf6\x8a\x78\xd1\xcd\xc6\xae\x1a\x11\x2c\x23\x3a\x33\x64\x39\x30\x2d\x61\x37\x65\x66\x2d\x38\x34\x32\x36\x62\x31\x63\x35\x3a\x41\x41\x3a\x42\x42\x3a\x43\x43\x3a\x44\x44\x3a\x45\x45\x3a\x46\x46'
    print(get_sign(data))

def test_aa(event_loop):
    print("我爱中国")