from zlib import crc32

def test_1():
    # s = bytes().fromhex('010210')
    # print(crc32(s.encode('utf-8')))

    s = bytes().fromhex('010210')
    print(hex(crc32(s)))