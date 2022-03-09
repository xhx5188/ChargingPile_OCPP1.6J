import logging
import hashlib


def get_authkey(cpRandom: str):
    id = "11223344"+cpRandom
    id = bytes.fromhex(id)
    passwd = b'\x02\x06\x48\x94\x4d\xd5\xb2\xc0\xf9\x7a\x8f\x7f\x30\x99\x09\xe2\x47\xb0\x28\x29\x5a\xf6\x8a\x78\xd1\xcd\xc6\xae\x1a\x11\x2c\x23'
    salt = "3d90-a7ef-8426b1c5".encode('utf-8')
    WIFI_MAC = "AA:BB:CC:DD:EE:FF".encode('utf-8')
    m = ":".encode('utf-8')
    data = id + m + passwd + m + salt + m + WIFI_MAC
    logging.info("鉴权文本：%s" % data)
    logging.info("16进制鉴权文本：%s" % data.hex())

    sha256 = hashlib.sha256()
    sha256.update(data)
    res = sha256.hexdigest()
    return res


def get_sign(data):
    hsobj = hashlib.sha256()
    hsobj.update(data)
    return hsobj.hexdigest()


def test():
    print()
    print(get_authkey("11"))
    id = "11223344" + "aabbccdd"
    id = bytes.fromhex(id)
    logging.info(id)