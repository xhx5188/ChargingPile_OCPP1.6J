import logging
import hashlib


def get_authkey(cpRandom: str):
    id = "44332211"+cpRandom
    id = bytes.fromhex(id)
    passwd = b'\x02\x06\x48\x94\x4d\xd5\xb2\xc0\xf9\x7a\x8f\x7f\x30\x99\x09\xe2\x47\xb0\x28\x29\x5a\xf6\x8a\x78\xd1\xcd\xc6\xae\x1a\x11\x2c\x23'
    salt = "3d90-a7ef-8426b1c5".encode('utf-8')
    WIFI_MAC = "AA:BB:CC:DD:EE:FF".encode('utf-8')
    m = ":".encode('utf-8')
    data = id + m + passwd + m + salt + m + WIFI_MAC
    logging.info(data)

    sha256 = hashlib.sha256()
    sha256.update(data)
    res = sha256.hexdigest()
    return res

def test_1():
    data = b'443322117e29a2af\x02\x06H\x94M\xd5\xb2\xc0\xf9z\x8f\x7f0\x99\t\xe2G\xb0()Z\xf6\x8ax\xd1\xcd\xc6\xae\x1a\x11,#3d90-a7ef-8426b1c5AA:BB:CC:DD:EE:FF'
    sha256 = hashlib.sha256()
    sha256.update(data)
    res = sha256.hexdigest()
    logging.info(res)

def test_2():
    id = "44332211"
    id = bytes.fromhex(id)
    logging.info(id)

def get_sign(data):

    #sha256加密有2种
    hsobj = hashlib.sha256()
    hsobj.update(data)
    return hsobj.hexdigest()

def test_3():
    data= b'\x11\x22\x33\x44\x0d\x69\x67\x64\x02\x06H\x94M\xd5\xb2\xc0\xf9z\x8f\x7f0\x99\t\xe2G\xb0()Z\xf6\x8ax\xd1\xcd\xc6\xae\x1a\x11,#3d90-a7ef-8426b1c5AA:BB:CC:DD:EE:FF'
    # data = b'\x30\x31\x32\x33' #1be2e452b46d7a0d9656bbb1f768e8248eba1b75baed65f5d99eafa948899a6a
    print()
    print(get_sign(data))